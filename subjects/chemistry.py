import streamlit as st
from groq import Groq
from assets.svg_sprites import render_svg

def run(level):
    st.subheader(f"Chemistry - {level}")
    topics = {
        "S1": ["Select Topic", "Lab Apparatus", "States of Matter", "Mixtures", "Elements"],
        "S2": ["Select Topic", "Atomic Structure", "The Periodic Table", "Titration", "Water"],
        "S3": ["Select Topic", "Chemical Bonding", "Rates of Reaction", "Extraction of Metals"],
        "S4": ["Select Topic", "Organic Chemistry", "Alkane", "Electrochemistry", "Industrial Chemistry"]
    }
    diagram_map = {"S2": {"Atomic Structure": "atom"}}

    topic = st.selectbox("Select Chemistry Topic", topics[level], key=f"chem_{level}")
    if topic == "Select Topic": return
    if st.button("Generate Lesson", type="primary", key=f"btn_chem_{level}"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        with st.spinner("AI Teaching..."):
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": f"You are UNEB {level} Chemistry tutor."}, {"role": "user", "content": f"Teach {topic} for {level}. Definition, Example, 1 question"}])
            st.markdown("### 📝 EXPLANATION"); st.markdown(res.choices[0].message.content)
    if topic in diagram_map.get(level, {}): st.markdown("### 📊 DIAGRAM"); render_svg(diagram_map[level][topic])
