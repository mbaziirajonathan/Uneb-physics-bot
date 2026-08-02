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

# SIMPLE AUTH. Replace with real login later
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"])

if user_type == "Admin/Teacher":
    import admin
    admin.show_admin_portal()
else:
    import student
    student.show_student_portal()
