
import streamlit as st
from docx import Document
import openai
import os

# --- CONFIGURATION ---
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- SETUP ---
st.set_page_config(page_title="AI Compliance Assistant – Quality Area 1", layout="wide")
st.title("📘 AI Compliance Assistant – Quality Area 1")

st.markdown("""
Use this tool to review a Training and Assessment Strategy (TAS) document against Quality Area 1 of the Draft Standards for RTOs 2025.

**Focus:** Standards 1.1 to 1.8  
**Purpose:** Identify alignment, gaps, and provide improvement suggestions.
""")

# --- UPLOAD ---
uploaded_file = st.file_uploader("📄 Upload your TAS document (Word only)", type=["docx"])

# --- HELPER FUNCTIONS ---
def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    full_text = "\n".join([para.text for para in doc.paragraphs])
    return full_text

review_template = """
You are a senior RTO compliance advisor named Q1, reviewing a Training and Assessment Strategy (TAS) for compliance with Quality Area 1 of the 2025 Outcome Standards for RTOs.

Your task is to evaluate the document against the following clauses:
- 1.1: Training structure, pacing, mode of delivery, and student engagement
- 1.2: Industry consultation and evidence of current practice
- 1.3 to 1.5: Fit-for-purpose assessment and validation
- 1.6 and 1.7: Recognition of Prior Learning and Credit Transfer
- 1.8: Facilities, equipment, and resourcing

🔍 Be sure to extract and consider content presented in **tables**, not just paragraph text. Important details like assessment methods, tools, delivery modes, and validation processes are often included in tables. Do not mark a section as missing unless you have reviewed all document sections and tables.

📊 If the document contains a table titled 'Assessing Table' or similar, assume this contains the assessment methods, tools, and techniques used per unit of competency. Use this table as primary evidence for clause 1.3 to 1.5 unless otherwise stated. Summarize its adequacy in your findings.

📘 Use a professional and supportive tone. 
✅ Where gaps are found, provide specific improvement suggestions using dot points or short paragraphs. 
📌 At the end of each section, include a heading called **Recommended Actions**.

Now review the document content below and return your feedback structured by clause:
"""

# --- REVIEW LOGIC ---
if uploaded_file:
    with st.spinner("Reading and reviewing your TAS document..."):
        extracted_text = extract_text_from_docx(uploaded_file)
        prompt = review_template + extracted_text

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert in RTO compliance with deep knowledge of Quality Area 1 from the 2025 Outcome Standards."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            feedback = response.choices[0].message.content
            st.success("✅ Review complete. See feedback below:")
            st.text_area("Compliance Review Feedback", feedback, height=500)
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")

else:
    st.info("👆 Upload a TAS document to begin the review.")
