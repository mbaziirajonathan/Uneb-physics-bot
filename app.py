import streamlit as st

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

# LOGIN
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"])
password = st.sidebar.text_input("Password", type="password")

STUDENT_PASSWORD = st.secrets["STUDENT_PASSWORD"] # unebtest2026
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"] # admin256

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
        import admin
        admin.show_admin_portal()
    else:
        import student
        student.show_student_portal()
else:
    st.info("Please login to continue")
