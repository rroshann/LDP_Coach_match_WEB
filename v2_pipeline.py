# 2. LOAD & PARSE INPUTS
survey_df = pd.read_excel("class-students.xlsx")

# Extract resumes from PDF
def extract_resumes(pdf_path):
    resumes = {}
    reader = PyPDF2.PdfReader(pdf_path)
    current_text = ""
    current_id = None
    for page in reader.pages:
        text = page.extract_text()
        lines = text.split('\n')
        for line in lines:
            if line.startswith("Student") and line.split()[1].isdigit():
                if current_id and current_text:
                    resumes[current_id] = current_text.strip()
                current_id = line.split()[1]
                current_text = ""
            else:
                current_text += line + "\n"
    if current_id and current_text:
        resumes[current_id] = current_text.strip()
    return resumes

resume_dict = extract_resumes("resumes-class.pdf")

# Load coach data
coaches_info = docx2txt.process("coaches-info.docx")
coaches_bios = docx2txt.process("coaches-bios.docx")

def split_coaches(text):
    blocks = text.split("Coach_A")
    coach_profiles = {}
    for block in blocks[1:]:
        lines = block.strip().splitlines()
        alias = "Coach_A" + lines[0].strip()
        coach_profiles[alias] = "\n".join(lines[1:]).strip()
    return coach_profiles

coach_info_dict = split_coaches(coaches_info)
coach_bio_dict = split_coaches(coaches_bios)

coach_profiles = {
    k: (coach_info_dict.get(k, "") + "\n" + coach_bio_dict.get(k, "")).strip()
    for k in set(coach_info_dict) | set(coach_bio_dict)
}

# 3. EMBEDDING FUNCTION
def get_embedding(text, model="text-embedding-3-small"):
    response = openai.embeddings.create(
        input=[text],
        model=model
    )
    return response.data[0].embedding

# Embed coach profiles
coach_embeddings = {
    coach: get_embedding(profile)
    for coach, profile in tqdm(coach_profiles.items(), desc="Embedding coaches")
}

# Embed student profiles
student_profiles = {}
student_embeddings = {}

for _, row in tqdm(survey_df.iterrows(), total=len(survey_df), desc="Embedding students"):
    student_id = str(row.iloc[0])
    survey_response = "\n".join([f"{survey_df.columns[i]}: {row[i]}" for i in range(1, len(row))])
    resume_text = resume_dict.get(student_id, "")
    combined_text = survey_response + "\n" + resume_text
    student_profiles[student_id] = combined_text
    student_embeddings[student_id] = get_embedding(combined_text)

# 4. BUILD SIMILARITY MATRIX
similarity_matrix = {}

for student_id, s_emb in student_embeddings.items():
    sims = {
        coach: cosine_similarity([s_emb], [c_emb])[0][0]
        for coach, c_emb in coach_embeddings.items()
    }
    similarity_matrix[student_id] = sims

# 5. ASSIGN BEST COACHES WITH CONSTRAINTS
coach1_counts = defaultdict(int)
coach2_counts = defaultdict(int)
assigned_students = set()
results = []

# Ensure every coach gets at least one student as best_coach_1
coach_pool = list(coach_profiles.keys())
min_heap = [(similarity_matrix[s][c], s, c)
            for s in student_embeddings for c in coach_pool]
heapq.heapify(min_heap)
used_students_1 = set()
used_coaches_1 = set()

while coach_pool and min_heap:
    sim, s, c = heapq.heappop(min_heap)
    if c in coach_pool and s not in used_students_1:
        coach1_counts[c] += 1
        used_students_1.add(s)
        used_coaches_1.add(c)
        coach_pool.remove(c)
        results.append({
            "student_id": s,
            "best_coach_1": c,
            "_sim1": sim
        })

# Assign remaining students by similarity, limit max 7
remaining_students = [s for s in student_embeddings if s not in used_students_1]

for s in remaining_students:
    sorted_coaches = sorted(similarity_matrix[s].items(), key=lambda x: x[1], reverse=True)
    for c, sim in sorted_coaches:
        if coach1_counts[c] < 7:
            coach1_counts[c] += 1
            results.append({
                "student_id": s,
                "best_coach_1": c,
                "_sim1": sim
            })
            break

# Assign best_coach_2 with min 1, max 7 constraints
coach_pool_2 = list(coach_profiles.keys())
unassigned_2 = set(range(len(results)))
coach_heap_2 = [
    (similarity_matrix[r["student_id"]][c], idx, c)
    for idx, r in enumerate(results)
    for c in coach_profiles.keys() if c != r["best_coach_1"]
]
heapq.heapify(coach_heap_2)
used_students_2 = set()
used_coaches_2 = set()

while coach_pool_2 and coach_heap_2:
    sim, idx, c = heapq.heappop(coach_heap_2)
    student_id = results[idx]["student_id"]
    if c in coach_pool_2 and idx not in used_students_2:
        coach2_counts[c] += 1
        used_students_2.add(idx)
        used_coaches_2.add(c)
        coach_pool_2.remove(c)
        results[idx]["best_coach_2"] = c
        results[idx]["_sim2"] = sim

# Assign remaining best_coach_2
for idx, r in enumerate(results):
    if "best_coach_2" in r:
        continue
    s = r["student_id"]
    first = r["best_coach_1"]
    sorted_coaches = sorted(similarity_matrix[s].items(), key=lambda x: x[1], reverse=True)
    for c, sim in sorted_coaches:
        if c != first and coach2_counts[c] < 7:
            coach2_counts[c] += 1
            r["best_coach_2"] = c
            r["_sim2"] = sim
            break

# 6. GENERATE GPT REASONS
for r in tqdm(results, desc="Generating GPT reasons"):
    s_id = r["student_id"]
    s_text = student_profiles[s_id]

    for n in [1, 2]:
        coach_key = r[f"best_coach_{n}"]
        prompt = f"""
You are helping match MBA students with executive coaches. The following is a student's profile and a coach profile. Explain in 1–2 sentences why this coach is a good match.

[STUDENT PROFILE]
{s_text}

[COACH PROFILE]
{coach_profiles[coach_key]}
"""
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You generate reasons for matching students with coaches."},
                {"role": "user", "content": prompt}
            ]
        )
        reason = response.choices[0].message.content.strip()
        r[f"reason_{n}"] = reason

# 7. EXPORT
final_df = pd.DataFrame([
    {
        "student_id": r["student_id"],
        "best_coach_1": r["best_coach_1"],
        "reason_1": r["reason_1"],
        "best_coach_2": r["best_coach_2"],
        "reason_2": r["reason_2"]
    }
    for r in results
])

final_df.to_excel("student_coach_matches.xlsx", index=False)
print("✅ Matching complete with both coach constraints. Results saved to student_coach_matches.xlsx")
