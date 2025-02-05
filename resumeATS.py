import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Configure API with direct API key
genai.configure(api_key="AIzaSyDJKcWW9R-WogY5N4h1ZR50Roe9EizJIlQ")
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to get Gemini output
def get_gemini_output(prompt):
    response = model.generate_content([prompt])
    return response.text

# Function to read PDF
def read_pdf(uploaded_file):
    pdf_reader = PdfReader(uploaded_file)
    pdf_text = "".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    return pdf_text

# Function to extract skills from text
def extract_skills(text):
    prompt = f"""
    Extract the most relevant technical skills from the following text:
    {text}
    Return them as a comma-separated list.
    """
    skills_text = get_gemini_output(prompt)
    skills = [skill.strip().lower() for skill in re.split(r',|\n', skills_text) if skill.strip()]
    return set(skills)

# Function to calculate skill match score
def calculate_skill_match(resume_skills, job_skills):
    common_skills = resume_skills.intersection(job_skills)
    missing_skills = job_skills - resume_skills
    match_score = (len(common_skills) / len(job_skills)) * 100 if job_skills else 0
    return round(match_score, 2), common_skills, missing_skills

# Streamlit UI
st.set_page_config(page_title="TEJ-ResumeATS Pro", layout="wide")
st.title("TEJ-ResumeATS Pro")
st.subheader("Optimize Your Resume for Software Engineering Roles")

# File upload
upload_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

# Job description input
job_description = st.text_area("Enter the job description")

if st.button("Analyze Resume"):
    if upload_file and job_description:
        pdf_text = read_pdf(upload_file)
        resume_skills = extract_skills(pdf_text)
        job_skills = extract_skills(job_description)
        skill_match_score, common_skills, missing_skills = calculate_skill_match(resume_skills, job_skills)
        
        st.subheader("Analysis Results")
        st.write(f"**Extracted Skills from Resume:** {', '.join(resume_skills)}")
        st.write(f"**Extracted Skills from Job Description:** {', '.join(job_skills)}")
        st.write(f"**Common Skills:** {', '.join(common_skills)}")
        st.write(f"**Missing Skills (Consider Adding These):** {', '.join(missing_skills)}")
        st.write(f"**Skill Match Score:** {skill_match_score}%")
        
        if skill_match_score > 80:
            st.success("Great match! Your resume aligns well with the job description.")
        elif skill_match_score > 50:
            st.warning("Decent match. Consider adding more relevant skills.")
        else:
            st.error("Low match. Your resume needs significant improvement.")
    else:
        st.error("Please upload a resume and enter a job description.")
