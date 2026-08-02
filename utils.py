import streamlit as st
from fpdf import FPDF
import io
from gtts import gTTS
import base64

def create_pdf(content, title):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=True, align='C'); pdf.ln(5)
    for line in content.split('\n'): pdf.multi_cell(0, 10, txt=line)
    return pdf.output(dest='S').encode('latin-1')

def display_with_pdf(content, title):
    st.markdown(content)
    pdf_bytes = create_pdf(content, title)
    st.download_button("📥 Download PDF", pdf_bytes, f"{title}.pdf", "application/pdf")

def text_to_speech(text):
    tts = gTTS(text=text, lang='en'); fp = io.BytesIO(); tts.write_to_fp(fp)
    b64 = base64.b64encode(fp.getvalue()).decode()
    st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)
