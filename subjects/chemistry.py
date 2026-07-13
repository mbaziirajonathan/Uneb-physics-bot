import streamlit as st
import streamlit.components.v1 as components
from groq import Groq

try:
    from diagrams_library.chemistry_diagrams import get_chemistry_diagram, calculate_chemistry
    DIAGRAMS_OK = True
except Exception as e:
    st.error(f"Diagram import failed: {e}")
    DIAGRAMS_OK = False
    def get_chemistry_diagram(x): return None
    def calculate_chemistry(x): return None

def run(level):
    st.subheader(f"Chemistry - {level}")

    topics = {
        "S1": ["Select Chemistry Topic", "Bunsen Burner", "Beaker", "Water Molecule", "Filtration", "Evaporation", "Solubility"],
        "S2": ["Select Chemistry Topic", "Titration", "CO2", "Electrolysis", "pH Scale", "Acids and Bases"],
        "S3": ["Select Chemistry Topic", "Haber Process", "Voltaic Cell", "Chromatography", "Periodic Table"],
        "S4": ["Select Chemistry Topic", "Benzene", "Polymer", "Spectrometer", "Organic Reactions"]
    }

    topic = st.selectbox("Select Chemistry Topic", topics[level], key=f"chem_topic_{level}")

    if topic == "Select Chemistry Topic":
        st.info("Select a topic to see diagram and explanation")
        return

    col1, col2 = st.columns([2,1])

    with col1:
        if DIAGRAMS_OK:
            svg = get_chemistry_diagram(topic)
            if svg:
                st.markdown("### DIAGRAM")
                components.html(svg, height=450, scrolling=True)
                st.markdown("---")

            calc_result = calculate_chemistry(topic)
            if calc_result:
                st.markdown("### CALCULATOR")
                st.markdown(calc_result)
                st.markdown("---")

        try:
            with st.spinner("Generating UNEB lesson..."):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                SYSTEM_PROMPT = f"You are a UNEB {level} Chemistry tutor for Uganda. Use NCDC 2026 syllabus. Explain clearly with formula, reaction, and 1 practice question. End with TEACHER GROUND NOTES and AI DISCLAIMER."
                res = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": f"Explain {topic} for {level}"}],
                    max_tokens=1200,
                    temperature=0.3
                )
                st.markdown(res.choices[0].message.content)
        except Exception as e:
            st.error(f"AI Error: {e}")

    with col2:
        st.markdown("### Quick Tools")
        user_q = st.text_input("Ask Chemistry Qn", placeholder="balance H2 + O2", key=f"chem_q_{level}")
        if st.button("Ask", key=f"chem_btn_{level}") and user_q:
            if DIAGRAMS_OK:
                calc = calculate_chemistry(user_q)
                st.success(calc if calc else "Try: 'molar mass H2O'")
