import streamlit as st
from groq import Groq
from assets.svg_sprites import render_svg

def run(level):
    st.subheader(f"Physics - {level}")
    topics = {
        "S1": ["Select Topic", "Measurement", "Density", "Forces", "Pressure", "Convex Lens"],
        "S2": ["Select Topic", "Waves", "Heat", "Gas Laws", "Current Electricity"],
        "S3": ["Select Topic", "Electric Field", "Series Circuit", "Magnetic Field", "Radioactivity"],
        "S4": ["Select Topic", "Nuclear Physics", "Electronics", "AC Circuits"]
    }
    diagram_map = {"S1": {"Forces": "forces", "Convex Lens": "convex_lens"}}
    
    topic = st.selectbox("Select Physics Topic", topics[level], key=f"phy_{level}")
    if topic == "Select Topic": return
    if st.button("Generate Lesson", type="primary", key=f"btn_phy_{level}"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        with st.spinner("AI Teaching..."):
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": f"You are UNEB {level} Physics tutor."}, {"role": "user", "content": f"Teach {topic} for {level}. Definition, Formula, Example, 1 question"}])
            st.markdown("### 📝 EXPLANATION"); st.markdown(res.choices[0].message.content)
    if topic in diagram_map.get(level, {}): st.markdown("### 📊 DIAGRAM"); render_svg(diagram_map[level][topic])
