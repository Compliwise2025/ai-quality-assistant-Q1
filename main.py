
import streamlit as st
from docx import Document
import openai
import os
import fitz  # PyMuPDF for reading PDF files

# --- CONFIGURATION ---
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- SETUP ---
st.set_page_config(page_title="Q1 Compliance Assistant – UOC Checker", layout="wide")
st.title("📘 Q1 Compliance Assistant – Compare UOC with TAS")

st.markdown("""
Upload a TAS document and one or more Unit of Competency (UOC) files. Q1 will extract key details from each UOC and verify if the TAS accurately reflects:

- Unit code and title
- Usage recommendation
- Release number
- Application
- Pre-requisite unit
- Foundation skills
- Assessment conditions
""")

# --- UPLOAD ---
tas_file = st.file_uploader("📄 Upload TAS document (Word only)", type=["docx"])
uoc_files = st.file_uploader("📑 Upload one or more UOC documents (PDF)", type=["pdf"], accept_multiple_files=True)

# --- HELPERS ---
def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(file):
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join([page.get_text() for page in pdf])

# --- PROMPT TEMPLATE ---
uoc_check_prompt = """
You are Q1, a senior RTO compliance assistant. Your task is to compare the following Unit of Competency with a TAS document and identify whether the TAS includes or aligns with the following key details from the UOC:

- Unit code and title
- Usage recommendation
- Release number
- Application
- Pre-requisite unit
- Foundation skills
- Assessment conditions

For each field, state whether it is addressed in the TAS. If something is missing, suggest what could be added.

Return your response structured clearly by unit.
"""

# --- LOGIC ---
if tas_file and uoc_files:
    with st.spinner("Reading and comparing documents..."):
        tas_text = extract_text_from_docx(tas_file)
        results = []
        for uoc in uoc_files:
            uoc_text = extract_text_from_pdf(uoc)
            full_prompt = uoc_check_prompt + f"\n\n---\nTAS Content:\n{tas_text}\n\n---\nUOC Content:\n{uoc_text}"
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert in RTO compliance and training product validation."},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.3
                )
                feedback = response.choices[0].message.content
                results.append(f"### Review for {uoc.name}\n\n{feedback}")
            except Exception as e:
                st.error(f"❌ An error occurred reviewing {uoc.name}: {e}")
        st.success("✅ UOC reviews completed:")
        for result in results:
            st.markdown(result)
else:
    st.info("👆 Please upload a TAS and at least one UOC PDF file to begin.")
