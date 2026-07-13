import streamlit as st
import streamlit.components.v1 as components
from groq import Groq

# SAFE IMPORT: Won't crash app if diagrams fail
try:
    from diagrams_library.physics_diagrams import get_physics_diagram, calculate_physics
    DIAGRAMS_OK = True
except Exception as e:
    st.error(f"Diagram import failed: {e}")
    DIAGRAMS_OK = False
    def get_physics_diagram(x): return None
    def calculate_physics(x): return None

def run(level):
    st.subheader(f"Physics - {level}")

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
        # 1. DIAGRAM FIRST - THIS MUST SHOW
        if DIAGRAMS_OK:
            svg = get_physics_diagram(topic)
            if svg:
                st.markdown("### DIAGRAM")
                components.html(svg, height=450, scrolling=True) # scrolling=True fixes cloud block
                st.markdown("---")
            else:
                st.warning(f"No diagram for '{topic}' yet. Text lesson below.")

        # 2. CALCULATOR
        if DIAGRAMS_OK:
            calc_result = calculate_physics(topic)
            if calc_result:
                st.markdown("### CALCULATOR")
                st.markdown(calc_result)
                st.markdown("---")

        # 3. AI EXPLANATION - IN TRY BLOCK
        try:
            with st.spinner("Generating UNEB lesson..."):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                SYSTEM_PROMPT = f"You are a UNEB {level} Physics tutor for Uganda. Use NCDC 2026 syllabus. Explain clearly with definition, formula, worked example, and 1 practice question [4 marks]. If diagram was shown above, refer to it. End with 'TEACHER GROUND NOTES' and 'AI DISCLAIMER: Verify with UNEB teacher'."
                res = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": f"Explain {topic} for {level}"}],
                    max_tokens=1200,
                    temperature=0.3
                )
                st.markdown(res.choices[0].message.content)
        except Exception as e:
            st.error(f"AI Error: {e}. Diagram should still be above.")

    with col2:
        st.markdown("### Quick Tools")
        user_q = st.text_input("Ask Physics Qn or Calc", placeholder="calculate force 10 5", key=f"physics_q_{level}")
        if st.button("Ask", key=f"physics_btn_{level}") and user_q:
            if DIAGRAMS_OK:
                calc = calculate_physics(user_q)
                if calc:
                    st.success(calc)
                else:
                    st.info("Try: 'calculate speed 100 20'")
