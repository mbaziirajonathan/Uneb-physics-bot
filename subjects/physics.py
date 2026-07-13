import streamlit as st
import streamlit.components.v1 as components
from diagrams_library.physics_diagrams import get_physics_diagram, calculate_physics

def run(level):
    st.subheader(f"Physics - {level}")

    # TOPIC DROPDOWNS PER LEVEL - UNEB 2026
    topics = {
        "S1": ["Select Physics Topic", "Measurement", "Density", "Forces", "Pressure", "Energy", "Light", "Convex Lens", "Concave Lens", "Prism", "Total Internal Reflection", "Simple Microscope", "Human Eye"],
        "S2": ["Select Physics Topic", "Waves", "Sound Wave", "Standing Wave", "Doppler Effect", "Echo", "Heat", "Gas Laws"],
        "S3": ["Select Physics Topic", "Electric Field", "Magnetic Field", "EM Wave", "Series Circuit", "Parallel Circuit", "Transformer", "Radioactivity"],
        "S4": ["Select Physics Topic", "Nuclear", "Photoelectric Effect", "Solar Eclipse", "Electronics"]
    }

    topic = st.selectbox("Select Physics Topic", topics[level], key=f"physics_topic_{level}")

    if topic == "Select Physics Topic":
        st.info("Select a topic to see diagram and explanation")
        return

    col1, col2 = st.columns([2,1])

    with col1:
        # 1. TRY TO DRAW DIAGRAM FIRST
        svg = get_physics_diagram(topic)
        if svg:
            st.markdown("### DIAGRAM")
            components.html(svg, height=400)
            st.markdown("---")

        # 2. AI EXPLANATION + CALCULATOR
        st.markdown(f"### Explanation: {topic}")
        prompt = f"Explain {topic} for {level} UNEB Physics. Give formula, example, and practice question."

        calc_result = calculate_physics(prompt)
        if calc_result:
            st.markdown("### CALCULATOR")
            st.markdown(calc_result)
            st.markdown("---")

        with st.spinner("Generating UNEB lesson..."):
            from groq import Groq
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])

            SYSTEM_PROMPT = f"You are a UNEB {level} Physics tutor. Explain clearly with formula, worked example, and 1 practice question [4 marks]. End with TEACHER GROUND NOTES and AI DISCLAIMER."

            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
                max_tokens=1200,
                temperature=0.3
            )
            st.markdown(res.choices[0].message.content)

    with col2:
        st.markdown("### Quick Tools")
        user_q = st.text_input("Ask Physics Qn or Calc", key=f"physics_q_{level}")
        if st.button("Ask", key=f"physics_btn_{level}"):
            if user_q:
                calc = calculate_physics(user_q)
                if calc:
                    st.success(calc)
                else:
                    st.info("Ask me to 'calculate speed 100m 20s' or 'draw convex lens'")
