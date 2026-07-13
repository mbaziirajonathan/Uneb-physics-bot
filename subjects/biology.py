import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
from diagrams_library.biology_diagrams import get_biology_diagram, calculate_biology

def run(level):
    st.subheader(f"Biology - {level}")

    topics = {
        "S1": ["Select Biology Topic", "Animal Cell", "Plant Cell", "Leaf", "Hand Lens", "Microscope", "Photosynthesis"],
        "S2": ["Select Biology Topic", "Heart", "Respiratory System", "Digestive System", "Circulatory System"],
        "S3": ["Select Biology Topic", "Neuron", "Kidney", "Photosynthesis", "DNA", "Enzymes"],
        "S4": ["Select Biology Topic", "Brain", "Eye", "Meiosis", "Genetics", "Ecology"]
    }

    topic = st.selectbox("Select Biology Topic", topics[level], key=f"bio_topic_{level}")

    if topic == "Select Biology Topic":
        st.info("Select a topic to see diagram and explanation")
        return

    col1, col2 = st.columns([2,1])

    with col1:
        svg = get_biology_diagram(topic)
        if svg:
            st.markdown("### DIAGRAM")
            components.html(svg, height=420, scrolling=False)
            st.markdown("---")

        calc_result = calculate_biology(topic)
        if calc_result:
            st.markdown("### CALCULATOR")
            st.markdown(calc_result)
            st.markdown("---")

        with st.spinner("Generating UNEB lesson..."):
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            SYSTEM_PROMPT = f"You are a UNEB {level} Biology tutor for Uganda. Use NCDC 2026 syllabus. Explain clearly with function, structure, and 1 practice question [4 marks]. If diagram shown above, label parts. End with TEACHER GROUND NOTES and AI DISCLAIMER."
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": f"Explain {topic} for {level}"}],
                max_tokens=1200,
                temperature=0.3
            )
            st.markdown(res.choices[0].message.content)

    with col2:
        st.markdown("### Quick Tools")
        user_q = st.text_input("Ask Biology Qn", placeholder="function of mitochondria", key=f"bio_q_{level}")
        if st.button("Ask", key=f"bio_btn_{level}") and user_q:
            calc = calculate_biology(user_q)
            st.success(calc if calc else "Ask me about any topic")
