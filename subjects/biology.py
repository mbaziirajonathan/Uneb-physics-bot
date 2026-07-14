import streamlit as st
from groq import Groq
from assets.svg_sprites import render_svg

def run(level):
    st.subheader(f"Biology - {level}")
    topics = {
        "S1": ["Select Topic", "Introduction to Biology", "Cell Structure", "Animal Cell", "Plant Cell", "Photosynthesis"],
        "S2": ["Select Topic", "Heart and Circulation", "Respiration in Humans", "Excretion", "Reproduction in Humans"],
        "S3": ["Select Topic", "DNA and Genetics", "Neuron and Nervous System", "Kidney and Excretion", "Ecology"],
        "S4": ["Select Topic", "Brain", "Human Genetics", "Evolution", "Immunity and Disease", "Biotechnology"]
    }
    diagram_map = {
        "S1": {"Animal Cell": "animal_cell", "Photosynthesis": "photosynthesis"},
        "S2": {"Heart and Circulation": "heart"},
        "S3": {"DNA and Genetics": "dna", "Neuron and Nervous System": "neuron"}
    }

    topic = st.selectbox("Select Biology Topic", topics[level], key=f"bio_{level}")
    if topic == "Select Topic": return

    if st.button("Generate Lesson", type="primary", key=f"btn_bio_{level}"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        with st.spinner("AI Teaching..."):
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": f"You are UNEB {level} Biology tutor. Use NCDC syllabus."}, {"role": "user", "content": f"Teach {topic} for {level}. Definition, Key points, Example, 1 question with answer"}])
            st.markdown("### 📝 EXPLANATION"); st.markdown(res.choices[0].message.content)

    if topic in diagram_map.get(level, {}):
        st.markdown("### 📊 DIAGRAM"); render_svg(diagram_map[level][topic])
