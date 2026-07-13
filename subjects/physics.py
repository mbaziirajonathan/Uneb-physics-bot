import streamlit as st
import streamlit.components.v1 as components
import re

# FIX: Use relative import so it works on Streamlit Cloud
try:
    from.physics_diagrams import get_physics_diagram, calculate_physics
except ImportError:
    from physics_diagrams import get_physics_diagram, calculate_physics

def run(level):
    st.subheader(f"Physics - {level}")

    topics = {
        "S1": ["Select Physics Topic", "Measurement", "Density", "Forces", "Light", "Convex Lens", "Concave Lens", "Prism", "Total Internal Reflection"],
        "S2": ["Select Physics Topic", "Waves", "Sound Wave", "Doppler Effect"],
        "S3": ["Select Physics Topic", "Electric Field", "Magnetic Field", "Series Circuit", "Parallel Circuit", "Transformer"],
        "S4": ["Select Physics Topic", "Nuclear", "Photoelectric Effect"]
    }

    topic = st.selectbox("Select Physics Topic", topics[level], key=f"physics_topic_{level}")

    # ALSO check chat input
    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        last_user_msg = st.session_state.messages[-1]["content"]
        topic = last_user_msg # check chat for "draw convex lens"

    if topic == "Select Physics Topic":
        st.info("Select a topic to see diagram and explanation")
        return

    col1, col2 = st.columns([2,1])

    with col1:
        # 1. DRAW DIAGRAM FIRST
        svg = get_physics_diagram(topic)
        if svg:
            st.markdown("### DIAGRAM")
            components.html(svg, height=420, scrolling=False) # <- height must be > SVG height
            st.markdown("---")
        else:
            st.warning(f"No diagram found for '{topic}'. Try: 'draw convex lens'")

        # 2. AI EXPLANATION
        prompt = f"Explain {topic} for {level} UNEB Physics. Give formula, worked example, and 1 practice question [4 marks]."
        calc_result = calculate_physics(topic)

        if calc_result:
            st.markdown("### CALCULATOR")
            st.markdown(calc_result)
            st.markdown("---")

        with st.spinner("Generating UNEB lesson..."):
            from groq import Groq
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            SYSTEM_PROMPT = f"You are a UNEB {level} Physics tutor. If diagram was shown above, refer to it. End with TEACHER GROUND NOTES and AI DISCLAIMER."
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
        if st.button("Ask", key=f"physics_btn_{level}") and user_q:
            calc = calculate_physics(user_q)
            st.success(calc if calc else "Ask me to 'calculate force 10 5'")
