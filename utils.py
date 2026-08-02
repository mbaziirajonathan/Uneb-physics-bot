import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
from gtts import gTTS
import base64
from streamlit_mic_recorder import mic_recorder

def create_pdf(content, title):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(297.5, 800, title)
    c.setFont("Helvetica", 10)
    y = 770
    for line in content.split('\n'):
        c.drawString(40, y, line[:95])
        y -= 15
        if y < 50: c.showPage(); y = 770
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

def display_with_pdf(content, title):
    st.markdown(content)
    pdf_bytes = create_pdf(content, title)
    st.download_button("📥 Download PDF", pdf_bytes, f"{title}.pdf", "application/pdf")

def text_to_speech(text):
    tts = gTTS(text=text, lang='en'); fp = io.BytesIO(); tts.write_to_fp(fp)
    b64 = base64.b64encode(fp.getvalue()).decode()
    st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)

def voice_input():
    audio = mic_recorder(start_prompt="🎤 Speak", stop_prompt="⏹️ Stop", key="voice")
    return audio
