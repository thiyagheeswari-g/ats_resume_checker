# 📄 Smart ATS Resume Checker

Smart ATS is an **AI-powered Resume Analyzer** built with **Streamlit** and **Google Gemini API**.  
It evaluates your resume against a given job description using an **Applicant Tracking System (ATS)-style analysis**.  
The app provides:
- **ATS match score** (visual gauge meter + progress bar)
- **Missing keywords** (displayed as tags)
- **Profile summary suggestions**
- Modern **dark mode UI** with an interactive dashboard

---

## 🚀 Features
- **Gemini AI Integration** – Uses `gemini-1.5-pro` and automatically falls back to `gemini-1.5-flash` when quota is reached.
- **Dark Mode Dashboard** – Clean and modern UI design.
- **Gauge Meter Score** – Animated ATS match score visualization.
- **Keyword Insights** – Missing keywords shown as clickable tags.
- **Profile Summary Card** – Highlighted feedback for resume improvement.
- **Robust JSON Parsing** – Handles messy AI output and ensures data is displayed correctly.

---

## 🛠 Tech Stack
- **Frontend & Backend:** [Streamlit](https://streamlit.io/)
- **AI Model:** [Google Gemini API](https://ai.google.dev/)
- **PDF Processing:** [PyPDF2](https://pypi.org/project/PyPDF2/)
- **Environment Variables:** [python-dotenv](https://pypi.org/project/python-dotenv/)
- **Data Visualization:** [Plotly](https://plotly.com/python/)

---
## 📌 Author
Thiyagheeswari G 
