import streamlit as st
from groq import Groq

def render_svg(symbol_id): st.markdown(f'<svg width="350" height="180"><use href="assets/chemistry_sprite.svg#{symbol_id}"/></svg>', unsafe_allow_html=True)

def run(level):
    st.subheader(f"Chemistry - {level}")
    topics = {"S1": ["Select Topic", "Lab Apparatus", "Bunsen Burner", "States of Matter"], "S2": ["Select Topic", "Atomic Structure", "Titration", "Acids"], "S3": ["Select Topic", "Bonding", "Water Molecule", "Rates"], "S4": ["Select Topic", "Organic", "Alkane"]}
    diagram_map = {"S1": {"Bunsen Burner": "bunsen_burner"}, "S2": {"Atomic Structure": "atom", "Titration": "titration"}, "S3": {"Water Molecule": "water_molecule"}, "S4": {"Alkane": "alkane"}}
    topic = st.selectbox("Select Chemistry Topic", topics[level], key=f"chem_{level}")
    if topic == "Select Topic": return
    if st.button("Generate Lesson", key=f"btn_chem_{level}"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": f"You are UNEB {level} Chemistry tutor."}, {"role": "user", "content": f"Teach {topic}"}])
        st.markdown("### EXPLANATION"); st.markdown(res.choices[0].message.content)
    if topic in diagram_map.get(level, {}): st.markdown("### DIAGRAM"); render_svg(diagram_map[level][topic])
