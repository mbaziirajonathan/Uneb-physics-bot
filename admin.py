import streamlit as st
import pandas as pd
import ai_core
import utils
from streamlit_option_menu import option_menu

TAB_NAMES = [
"Admin Dashboard / RESULT ANALYZER", "Test Paper Generator", "NCDC Marking Guide Generator",
"Auto Marking Assistant", "Single Report Card", "BULK REPORT CARD PRINTER", "Lesson Plan + SOW",
"INSPECTOR FILE PACK", "S1-S6 FAILURE PREDICTOR", "BULK EXAMS GENERATOR",
"UNEB TREND ANALYZER", "FEE DEFAULTER PREDICTOR", "MOES EMIS REPORT", "PARENT WHATSAPP PORTAL"
]

def show_admin_portal():
    st.header("🏫 Admin/Teacher Portal")
    if st.button("Logout"):
        for key in st.session_state.keys(): del st.session_state[key]
        st.rerun()

    selected = option_menu(None, TAB_NAMES, menu_icon="cast", default_index=0, orientation="horizontal")

    if selected == "Admin Dashboard / RESULT ANALYZER":
        st.subheader("Dashboard")
        try:
            df = pd.read_json("usage_log.json")
            col1, col2 = st.columns(2)
            col1.metric("Total Activities", len(df)); col2.metric("Flagged Attempts", df['flagged'].sum())
            st.dataframe(df.tail(20))
        except: st.info("No data yet")

    elif selected == "Test Paper Generator":
        subject = st.selectbox("Subject", list(ai_core.UNEB_CURRICULUM_MAP.keys()))
        topic = st.text_input("Topic"); count = st.slider("Questions", 5, 50, 20)
        if st.button("Generate Test"): utils.display_with_pdf(ai_core.generate_exam_items(subject, topic, count), "Test Paper")

    elif selected == "Lesson Plan + SOW":
        subject = st.selectbox("Subject LP", list(ai_core.UNEB_CURRICULUM_MAP.keys()))
        topic = st.text_input("Topic LP"); duration = st.slider("Minutes", 40, 120, 80)
        if st.button("Generate Lesson Plan"): utils.display_with_pdf(ai_core.generate_lesson_plan(subject, topic, duration), "Lesson Plan")

    elif selected == "Single Report Card":
        name = st.text_input("Student Name"); scores = {s: st.number_input(s, 0, 100) for s in ["Math","English","Science"]}
        if st.button("Generate Report"): utils.display_with_pdf(ai_core.generate_report_card(name, scores), "Report Card")

    elif selected == "BULK EXAMS GENERATOR":
        subject = st.selectbox("Subject Bulk", list(ai_core.UNEB_CURRICULUM_MAP.keys())); level = st.selectbox("Level", ["S1","S2","S3","S4","S5","S6"])
        if st.button("Generate 20 Questions"): utils.display_with_pdf(ai_core.generate_exam_items(subject, f"All {level} Topics", 20), "Bulk Exam")

    else:
        st.subheader(selected)
        st.info("🚀 Coming in v1.1 - This tool is reserved for future update")
