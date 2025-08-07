# matcher_app.py

import streamlit as st
import openai
import os
import pandas as pd
import docx2txt
import PyPDF2
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import heapq
import time

# ========== AUTH ========== #
import streamlit as st

st.set_page_config(page_title="Student-Coach Matcher", page_icon="🔐")
st.title("🔐 LDP Student-Coach Matcher")

# Session state for authentication
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        if username.lower() == "ldp_team" and password == "LDP@123":
            st.session_state["authenticated"] = True
            st.success("✅ Login successful!")
            st.rerun()  # ✅ Correct method
        else:
            st.error("❌ Invalid username or password")
    st.stop()


# ========== OPENAI KEY ========== #
st.header("Step 1: Enter OpenAI API Key")
openai_key = st.text_input("OpenAI API Key", type="password")
if not openai_key:
    st.stop()
openai.api_key = openai_key

# ========== FILE UPLOADS ========== #
# ========== MATCHING VERSION ========== #
st.header("Step 2: Choose Matching Logic")

version = st.radio(
    "Which version do you want to run?",
    ["Version 1: Limit on Best Coach #1", "Version 2: Limit on Best Coach #1 and #2"]
)

# ========== FILE UPLOADS ========== #
st.header("Step 3: Upload Input Files")

resumes_file = st.file_uploader("Upload resumes-class.pdf", type=["pdf"])
students_file = st.file_uploader("Upload class-students.xlsx", type=["xlsx"])
bios_file = st.file_uploader("Upload coaches-bios.docx", type=["docx"])
info_file = st.file_uploader("Upload coaches-info.docx", type=["docx"])

if not all([resumes_file, students_file, bios_file, info_file]):
    st.stop()

# ========== MATCHING PIPELINE ========== #
run_button = st.button("🚀 Start Matching")

if run_button:
    with st.spinner("Running the matching pipeline..."):
        start_time = time.time()

        # Save uploaded files
        with open("resumes-class.pdf", "wb") as f: f.write(resumes_file.read())
        with open("class-students.xlsx", "wb") as f: f.write(students_file.read())
        with open("coaches-bios.docx", "wb") as f: f.write(bios_file.read())
        with open("coaches-info.docx", "wb") as f: f.write(info_file.read())

        if "Version 1" in version:
            from v1_pipeline import run_pipeline as run_v1
            run_v1()
        else:
            from v2_pipeline import run_pipeline as run_v2
            run_v2()


        # Export
        st.success("✅ Matching complete! Download below:")
        with open("student_coach_matches.xlsx", "rb") as f:
            st.download_button("📥 Download Results", f, file_name="student_coach_matches.xlsx")
