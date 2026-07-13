import streamlit as st
import pytz
from datetime import datetime
from groq import Groq

import subjects.physics as physics
import subjects.chemistry as chemistry
import subjects.biology as biology

# PASSWORD LOCK
def check_password():
    def password_entered():
        if st.session_state["password"] == "UNEB_TEST_2026":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔒 UNEB AI Tutor Login")
        st.text_input("Enter Password", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.title("🔒 UNEB AI Tutor Login")
        st.text_input("Enter Password", type="password", on_change=password_entered, key="password")
        st.error("❌ Incorrect Password")
        st.stop()

check_password()

st.set_page_config(page_title="UNEB AI Tutor - S1 to S4", page_icon="📚", layout="wide")
st.title("📚 UNEB AI Tutor")
st.caption("Physics | Chemistry | Biology | S1 - S4 | Uganda NCDC Syllabus")

tz = pytz.timezone('Africa/Kampala')
now = datetime.now(tz)
st.write(f"**Current Time in Uganda:** {now.strftime('%I:%M %p')}")
st.divider()

with st.sidebar:
    st.header("Settings")
    subject = st.radio("Choose Subject", ["Physics", "Chemistry", "Biology"], key="subject_select")
    level = st.selectbox("Choose Class Level", ["S1", "S2", "S3", "S4"], key="level_select")
    st.divider()

# BUG FIX: Pass BOTH subject and level to run function
if subject == "Physics": physics.run(level)
elif subject == "Chemistry": chemistry.run(level)
elif subject == "Biology": biology.run(level)

st.divider()
st.subheader("💬 Ask Any Question")
user_q = st.text_input("Type your question here:", key="chat_input")
if st.button("Ask AI") and user_q:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    with st.spinner("Thinking..."):
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": "You are UNEB S1-S4 tutor for Physics, Chemistry, Biology in Uganda."},
                      {"role": "user", "content": user_q}]
        )
        st.markdown(res.choices[0].message.content)

st.caption("Powered by Groq Llama-3.1 + Inline SVG Diagrams")
