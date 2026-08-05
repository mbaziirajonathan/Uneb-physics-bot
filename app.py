import streamlit as st

st.set_page_config(page_title="UNEB TUTOR TEST", layout="wide")
st.title("🎓 DIGITAL UNEB TUTOR 2026 - BOOT TEST 3.14")

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    st.success("Secrets OK")
except: 
    st.warning("Add GROQ_API_KEY to secrets")

if st.button("Test Groq"):
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        st.success("Groq works on Python 3.14")
    except Exception as e:
        st.error(f"Groq failed: {e}")

st.info("If this loads, the problem was pandas/pillow. We add them back later with cloud workarounds")
