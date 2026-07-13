import streamlit as st
from groq import Groq
from streamlit_mermaid import st_mermaid
import re

def extract_mermaid(text):
    """Finds ```mermaid... ``` in AI response"""
    match = re.search(r"```mermaid(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else None

def run(level):
    st.subheader(f"Physics - {level}")

    topics = {
        "S1": [
            "Select Topic", 
            "Measurement", "Length", "Mass", "Time", "Density", 
            "Forces", "Friction", "Pressure", "Energy", "Work and Power",
            "Light", "Reflection", "Refraction", "Convex Lens", "Concave Lens", 
            "Prism", "Total Internal Reflection", "Simple Microscope", "Human Eye"
        ],
        "S2": [
            "Select Topic", 
            "Waves", "Transverse Wave", "Longitudinal Wave", "Sound Wave", 
            "Speed of Sound", "Echo", "Doppler Effect", "Standing Wave",
            "Heat", "Temperature", "Expansion", "Gas Laws", "Pressure Law"
        ],
        "S3": [
            "Select Topic", 
            "Electric Field", "Electric Current", "Potential Difference", "Resistance", 
            "Ohm's Law", "Series Circuit", "Parallel Circuit", "Electric Power",
            "Magnetic Field", "Electromagnet", "Electric Motor", "Transformer", 
            "Electromagnetic Waves", "Radioactivity", "Half Life"
        ],
        "S4": [
            "Select Topic", 
            "Nuclear Physics", "Nuclear Fission", "Nuclear Fusion", "Photoelectric Effect", 
            "Wave-Particle Duality", "Solar Eclipse", "Lunar Eclipse", 
            "Electronics: Diode", "Electronics: Transistor", "Logic Gates", 
            "Satellites", "Gravitational Field"
        ]
    }

    topic = st.selectbox("Select Physics Topic", topics[level], key=f"physics_{level}")

    if topic == "Select Topic":
        st.info("Select a topic to generate AI lesson + diagram")
        return

    col1, col2 = st.columns([3, 1])

    with col1:
        if st.button("Generate Lesson", type="primary", key=f"btn_{level}"):
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                
                SYSTEM_PROMPT = f"""You are a UNEB {level} Physics tutor for Uganda. Use NCDC 2026 syllabus.
                RULE 1: Explain topic clearly with definition, formula, 1 worked example, 1 practice question [4 marks].
                RULE 2: If topic has a process, ray diagram, circuit, or cycle, you MUST output a Mermaid diagram in a ```mermaid``` code block.
                RULE 3: Keep Mermaid simple. Max 8 nodes. Use graph LR for ray diagrams
