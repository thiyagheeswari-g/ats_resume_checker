import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import re
import ast
import plotly.graph_objects as go

# Load environment variables
load_dotenv()

# Configure Google API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ---------------- HELPER FUNCTIONS ---------------- #

# Fallback to different Gemini models if quota is hit
def get_gemini_response(input_text):
    for model_name in ["gemini-1.5-pro", "gemini-1.5-flash"]:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(input_text)
            return response.text, model_name
        except Exception as e:
            if "429" in str(e):
                st.warning(f"Quota limit reached for {model_name}, switching to next model...")
                continue
            else:
                raise e
    raise RuntimeError("All models failed due to quota or errors.")

# Read PDF text and trim if too long
def input_pdf_text(uploaded_file, max_chars=3000):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    text = text.strip()
    if len(text) > max_chars:
        st.warning(f"Resume text trimmed from {len(text)} to {max_chars} characters to fit token limits.")
        return text[:max_chars]
    return text

# Extract JSON from messy model output
def extract_json_from_text(text: str):
    try:
        return json.loads(text)
    except Exception:
        pass
    start = text.find('{')
    if start != -1:
        stack = []
        for i in range(start, len(text)):
            if text[i] == '{':
                stack.append('{')
            elif text[i] == '}':
                stack.pop()
                if not stack:
                    candidate = text[start:i+1]
                    try:
                        return json.loads(candidate)
                    except Exception:
                        cleaned = re.sub(r',\s*}', '}', candidate)
                        cleaned = re.sub(r',\s*\]', ']', cleaned)
                        try:
                            return json.loads(cleaned)
                        except Exception:
                            try:
                                return ast.literal_eval(cleaned)
                            except Exception:
                                break
    return None

# ---------------- PROMPT TEMPLATE ---------------- #
input_prompt = """
Act as a highly experienced ATS (Applicant Tracking System) with deep expertise in technology, software engineering, 
data science, data analysis, and big data engineering. Your task is to evaluate the following resume against the provided 
job description. The job market is highly competitive, so provide the best possible feedback for improving the resume.

Evaluate:
- Assign a JD Match percentage based on relevance.
- Identify missing keywords.
- Provide a concise, impactful profile summary.

Resume: {text}
Job Description: {jd}

Return the response in a single JSON string format:
{{"JD Match": "%", "MissingKeywords": [], "Profile Summary": ""}}
"""

# ---------------- PAGE STYLE ---------------- #
st.set_page_config(page_title="Smart ATS", page_icon="📄", layout="centered")
st.markdown("""
<style>
    .reportview-container {background-color: #0E1117; color: white;}
    .stTextInput>div>div>input, .stTextArea textarea {background-color: #262730; color: white;}
    .stFileUploader label {color: white;}
    .tag {
        display: inline-block;
        background-color: #1F77B4;
        color: white;
        padding: 5px 10px;
        margin: 5px;
        border-radius: 5px;
        font-size: 14px;
    }
    .card {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 8px;
        color: white;
        font-size: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ---------------- #
st.markdown("<h1 style='text-align:center; color:#4CAF50;'>📄 Smart ATS Resume Checker</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray;'>Optimize your resume for ATS success</p>", unsafe_allow_html=True)

# ---------------- INPUTS ---------------- #
jd = st.text_area("📌 Paste the Job Description", placeholder="Enter the job description here...")
uploaded_file = st.file_uploader("📂 Upload Your Resume (PDF)", type="pdf")

# ---------------- PROCESS ---------------- #
if st.button("🚀 Analyze Resume"):
    if uploaded_file and jd.strip():
        text = input_pdf_text(uploaded_file)
        final_prompt = input_prompt.format(text=text, jd=jd)

        try:
            raw_response, used_model = get_gemini_response(final_prompt)
            st.success(f"✅ Analysis complete using {used_model}")

            # Debug: see raw output
            with st.expander("🔍 View Raw Model Output (Debug)"):
                st.text_area("", raw_response, height=150)

            # Parse JSON
            try:
                result = json.loads(raw_response)
            except Exception:
                result = extract_json_from_text(raw_response)

            if not result:
                st.error("❌ Could not parse ATS response. Try refining the prompt.")
                st.stop()

            # ---------------- DISPLAY RESULTS ---------------- #
            score_str = result.get("JD Match", "0").replace("%", "").strip()
            try:
                score = int(score_str)
            except:
                score = 0

            st.markdown("## 📊 ATS Match Score")
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                title={'text': "ATS Match %", 'font': {'size': 24, 'color': 'white'}},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': 'white'},
                    'bar': {'color': "#4CAF50"},
                    'bgcolor': "black",
                    'steps': [
                        {'range': [0, 50], 'color': "red"},
                        {'range': [50, 75], 'color': "orange"},
                        {'range': [75, 100], 'color': "green"}
                    ]
                }
            ))
            fig.update_layout(paper_bgcolor="#0E1117", font={'color': "white"})
            st.plotly_chart(fig)

            st.markdown("## 🔍 Missing Keywords")
            missing_keywords = result.get("MissingKeywords", [])
            if missing_keywords:
                tags_html = "".join([f"<span class='tag'>{kw}</span>" for kw in missing_keywords])
                st.markdown(tags_html, unsafe_allow_html=True)
            else:
                st.success("✅ No missing keywords found!")

            st.markdown("## 📝 Profile Summary")
            summary = result.get("Profile Summary", "No summary provided.")
            st.markdown(f"<div class='card'>{summary}</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("⚠ Please upload a resume and paste a job description.")
