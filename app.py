import streamlit as st
import pytz
from datetime import datetime
from assets.svg_sprites import load_svg_sprite # LOAD SVG ONCE

import subjects.biology as biology
import subjects.chemistry as chemistry
import subjects.physics as physics

# 1. PASSWORD LOCK
def check_password():
    if st.session_state.get("password_correct", False): return
    st.title("🔒 UNEB AI Tutor Login")
    pwd = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if pwd == "UNEB_TEST_2026":
            st.session_state["password_correct"] = True; st.rerun()
        else: st.error("❌ Incorrect Password")
    st.stop()

check_password()
load_svg_sprite() # CRITICAL: LOAD SVG SPRITE FOR WHOLE APP

st.set_page_config(page_title="UNEB AI Tutor", page_icon="📚", layout="wide")
st.title("📚 UNEB AI Tutor")
st.caption("Physics | Chemistry | Biology | S1 - S4 | Uganda NCDC Syllabus")

tz = pytz.timezone('Africa/Kampala')
st.write(f"**Uganda Time:** {datetime.now(tz).strftime('%I:%M %p')}")
st.divider()

# 2. SIDEBAR
with st.sidebar:
    st.header("Settings")
    subject = st.radio("Choose Subject", ["Physics", "Chemistry", "Biology"])
    level = st.selectbox("Choose Class Level", ["S1", "S2", "S3", "S4"])

# 3. ROUTING - CALL THE CORRECT MODULE
if subject == "Physics": physics.run(level)
elif subject == "Chemistry": chemistry.run(level)
elif subject == "Biology": biology.run(level)

st.divider()
st.subheader("💬 Ask Any Question")
user_q = st.text_input("Type your question here:")
if st.button("Ask AI") and user_q:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    with st.spinner("Thinking..."):
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": "You are UNEB S1-S4 tutor."}, {"role": "user", "content": user_q}])
        st.markdown(res.choices[0].message.content)
