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
You are a senior RTO compliance advisor. Review the following TAS (Training and Assessment Strategy) document for compliance with Quality Area 1 of the 2025 Outcome Standards for RTOs.

Check for compliance against each of the following standards:
- 1.1: Training structure, pacing, mode of delivery, and student engagement
- 1.2: Industry consultation and evidence of current practice
- 1.3 to 1.5: Fit-for-purpose assessment and validation
- 1.6 and 1.7: Recognition of Prior Learning and Credit Transfer
- 1.8: Facilities, equipment, and resourcing

Evaluate the document’s compliance for each standard. Identify strengths, non-compliances or partial compliances, and suggest specific improvements.

TAS Document Content:
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
