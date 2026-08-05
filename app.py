import streamlit as st
import pandas as pd

st.set_page_config(page_title="UNEB TUTOR TEST", layout="wide")

st.title("🎓 DIGITAL UNEB TUTOR 2026 - BOOT TEST")

try:
    STUDENT_PASSWORD = st.secrets["STUDENT_PASSWORD"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
    GROQ_API_KEY_1 = st.secrets["GROQ_API_KEY_1"]
    st.success("Secrets loaded OK")
except Exception as e:
    st.error(f"Secrets error: {e}")
    st.stop()

user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"])
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if user_type == "Student" and password == STUDENT_PASSWORD: 
        st.session_state["role"] = "Student"
        st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD: 
        st.session_state["role"] = "Admin"
        st.rerun()
    elif password: 
        st.sidebar.error("Wrong password")

if st.session_state.get("role"):
    st.write(f"Logged in as: {st.session_state['role']}")
    st.write("App boots successfully. Streamlit 1.37.1 working")
else:
    st.info("Please login to continue")
