Here’s a clean and professional `README.md` file you can use for your repo that powers [https://ldpcoachmatch.streamlit.app/](https://ldpcoachmatch.streamlit.app/):

---

```markdown
# 🧠 LDP Student-Coach Matcher

This web app intelligently matches MBA students with executive coaches using OpenAI embeddings and similarity scoring. It's designed for non-technical users to securely upload inputs, generate matches, and download the results — all in a few clicks.

🔗 **Live App**: [ldpcoachmatch.streamlit.app](https://ldpcoachmatch.streamlit.app/)

---

## 🔐 Login Access

To ensure privacy and restricted access:

- **Username**: `LDP_team` (case-insensitive)
- **Password**: `LDP@123` (case-sensitive)

No sign-up or account creation required.

---

## 📁 Features

- 🔑 Secure login
- 🔐 OpenAI API key input (user-supplied)
- 📤 Upload interface for 4 input files:
  - `resumes-class.pdf`
  - `class-students.xlsx`
  - `coaches-bios.docx`
  - `coaches-info.docx`
- ⚙️ Two matching logic versions:
  - **v1**: Constraint only on `best_coach_1`
  - **v2**: Constraints on both `best_coach_1` and `best_coach_2`
- 🧠 GPT-powered reason generation for matches
- 📥 Downloadable results as `student_coach_matches.xlsx`
- ⏳ Progress indicators with estimated time remaining

---

## 🛠 How It Works

1. **Login** using the credentials above.
2. **Enter your OpenAI API key**.
3. **Choose Matching Version**: `v1` or `v2`.
4. **Upload all required files**.
5. Hit **Start Matching** – the system:
   - Extracts resumes
   - Embeds profiles using OpenAI
   - Computes similarities
   - Assigns coaches with fairness constraints
   - Generates GPT reasons for the match
6. **Download results** as an Excel file.

---

## 🧩 Technologies Used

- [Streamlit](https://streamlit.io/)
- [OpenAI API](https://platform.openai.com/)
- `pandas`, `numpy`, `docx2txt`, `PyPDF2`, `scikit-learn`, `heapq`, `tqdm`

---

## 🗂 File Structure

```

📁 ldp\_coach\_match\_web/
│
├── matcher\_app.py           # Main Streamlit app
├── v1\_pipeline.py           # Logic for v1 matching
├── v2\_pipeline.py           # Logic for v2 matching
├── requirements.txt         # Python dependencies
└── README.md                # You are here

```

---

## 📦 Deployment

This app is deployed on **Streamlit Community Cloud**.

To deploy your own:

1. Fork or clone this repo
2. Add your code to [Streamlit Cloud](https://streamlit.io/cloud)
3. Set up `requirements.txt`
4. Done!

---

## 👥 For LDP Internal Use Only

This tool is intended for use by the LDP team and should not be shared publicly.

---

## 📧 Questions?

Contact the project admin for issues, support, or feature enhancements.

```

---

Let me know if you’d like to:

* Add screenshots or GIFs of the UI
* Include setup instructions for running locally
* Make this private with GitHub access controls

I can generate the `requirements.txt` if you don’t already have it.
