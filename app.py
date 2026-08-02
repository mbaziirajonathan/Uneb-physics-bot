import streamlit as st
import sys
import os

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026", layout="wide", page_icon="🎓")

# LEGAL DISCLAIMER
st.sidebar.warning("""
⚠️ LEGAL NOTICE: DIGITAL UNEB TUTOR 2026
For learning, practice, and revision only as per NCDC Curriculum.
NOT for use during UNEB/End of term exams.
Misuse violates MOES Academic Integrity Policy.
Support: 256751040731
""")

st.title("🎓 DIGITAL UNEB TUTOR 2026")
st.subheader("S1 - S6 AI Learning & Teacher Management System")

# SAFE IMPORTS - WILL SHOW ERROR INSTEAD OF CRASHING
try:
    import admin
    import student
    import ai_core
    import utils
except ModuleNotFoundError as e:
    st.error(f"CRITICAL DEPLOYMENT ERROR: {e}")
    st.error("Fix: Make sure admin.py, student.py, ai_core.py, utils.py are in the SAME folder as app.py on GitHub")
    st.stop()

# LOGIN
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"])
password = st.sidebar.text_input("Password", type="password")

# LOAD SECRETS - WILL SHOW ERROR IF MISSING
try:
    STUDENT_PASSWORD = st.secrets["STUDENT_PASSWORD"] # unebtest2026
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"] # admin256
except KeyError:
    st.error("CRITICAL: STUDENT_PASSWORD and ADMIN_PASSWORD not found in Streamlit Cloud Secrets")
    st.stop()

if st.sidebar.button("Login"):
    if user_type == "Student" and password == STUDENT_PASSWORD:
        st.session_state["logged_in"] = True
        st.session_state["role"] = "Student"
        st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD:
        st.session_state["logged_in"] = True
        st.session_state["role"] = "Admin"
        st.rerun()
    elif password:
        st.sidebar.error("Wrong password")

if st.session_state.get("logged_in"):
    if st.session_state["role"] == "Admin":
        admin.show_admin_portal()
    else:
        student.show_student_portal()
else:
    st.info("Please login to continue")
