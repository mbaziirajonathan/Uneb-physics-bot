import streamlit as st
from groq import Groq

def render_svg(symbol_id): st.markdown(f'<svg width="350" height="180"><use href="assets/physics_sprite.svg#{symbol_id}"/></svg>', unsafe_allow_html=True)

def run(level):
    st.subheader(f"Physics - {level}")
    topics = {"S1": ["Select Topic", "Measurement", "Density", "Forces", "Pressure", "Energy", "Convex Lens"], "S2": ["Select Topic", "Waves", "Transverse Wave", "Sound", "Heat", "Gas Laws"], "S3": ["Select Topic", "Electric Field", "Series Circuit", "Magnetic Field"], "S4": ["Select Topic", "Nuclear Physics"]}
    diagram_map = {"S1": {"Forces": "forces", "Convex Lens": "convex_lens"}, "S2": {"Transverse Wave": "transverse_wave", "Gas Laws": "gas_law"}, "S3": {"Series Circuit": "series_circuit"}}
    topic = st.selectbox("Select Physics Topic", topics[level], key=f"phy_{level}")
    if topic == "Select Topic": return
    if st.button("Generate Lesson", key=f"btn_phy_{level}"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": f"You are UNEB {level} Physics tutor."}, {"role": "user", "content": f"Teach {topic} with definition, formula, example"}])
        st.markdown("### EXPLANATION"); st.markdown(res.choices[0].message.content)
    if topic in diagram_map.get(level, {}): st.markdown("### DIAGRAM"); render_svg(diagram_map[level][topic])
