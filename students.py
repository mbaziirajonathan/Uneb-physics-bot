import streamlit as st
import ai_core
import utils

STUDENT_TABS = ["Smart Learn", "Practicals Lab", "Quiz & Test Prep"]

def show_student_portal():
    st.header("📚 Student Portal - S1 to S6")
    tab1, tab2, tab3 = st.tabs(STUDENT_TABS)

    with tab1:
        st.subheader("Smart Learn: Ask, Learn, Research")
        uploaded_file = st.file_uploader("Upload notes/past paper for research", type=['txt','pdf','docx','jpg'])
        file_context = ""
        if uploaded_file: file_context = f"\nContext from uploaded file: {uploaded_file.name}"

        query = st.text_area("Ask anything or paste questions")
        if st.button("Get Answer"):
            if query:
                full_prompt = query + file_context
                result = ai_core.ask_smart_brain(full_prompt, "Student")
                utils.display_with_pdf(result, "Smart Answer")
                if st.checkbox("Listen"): utils.text_to_speech(result[:500])

    with tab2:
        st.subheader("Practicals Lab")
        subject = st.selectbox("Subject", list(ai_core.UNEB_CURRICULUM_MAP.keys()))
        topic = st.text_input("Topic for Practical")
        if st.button("Generate Practical"):
            result = ai_core.generate_practical(subject, topic)
            utils.display_with_pdf(result, "Practical")

    with tab3:
        st.subheader("Quiz & Test Prep")
        subject = st.selectbox("Subject Quiz", list(ai_core.UNEB_CURRICULUM_MAP.keys()), key="qsub")
        topic = st.text_input("Topic for Quiz")
        if st.button("Generate 10 Questions"):
            result = ai_core.generate_exam_items(subject, topic, 10)
            utils.display_with_pdf(result, "Quiz")
