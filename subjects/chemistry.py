import streamlit as st
from groq import Groq
from streamlit_mermaid import st_mermaid
import re

def extract_mermaid(text):
    match = re.search(r"```mermaid(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else None

def run(level):
    st.subheader(f"Chemistry - {level}")

    topics = {
        "S1": [
            "Select Topic", "Bunsen Burner", "Beaker", "Test Tube", "Water Molecule", 
            "Filtration", "Evaporation", "Solubility", "States of Matter", "Mixtures vs Compounds"
        ],
        "S2": [
            "Select Topic", "Titration Setup", "Carbon Dioxide Gas Preparation", "Electrolysis of Water", 
            "pH Scale", "Acids and Bases", "Indicators", "Chemical Reactions", "Periodic Table"
        ],
        "S3": [
            "Select Topic", "Haber Process", "Voltaic Cell", "Electrolytic Cell", "Chromatography", 
            "Atomic Structure", "Chemical Bonding", "Mole Concept", "Rates of Reaction"
        ],
        "S4": [
            "Select Topic", "Benzene Structure", "Polymerization", "Spectrometer", "Organic Chemistry: Alkanes", 
            "Organic Chemistry: Alkenes", "Acid-Base Titration Curve", "Redox Reactions", "Qualitative Analysis"
        ]
    }

    topic = st.selectbox("Select Chemistry Topic", topics[level], key=f"chemistry_{level}")

    if topic == "Select Topic":
        st.info("Select a topic to generate AI lesson + diagram")
        return

    col1, col2 = st.columns([3, 1])

    with col1:
        if st.button("Generate Lesson", type="primary", key=f"btn_chem_{level}"):
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                
                SYSTEM_PROMPT = f"""You are a UNEB {level} Chemistry tutor for Uganda. Use NCDC 2026 syllabus.
                RULE 1: Explain with definition, formula, chemical equation, 1 worked example, 1 practice question [4 marks].
                RULE 2: For apparatus, processes, reactions, cycles, you MUST output a Mermaid diagram in a ```mermaid``` code block.
                RULE 3: Use flowchart TD for apparatus setup. Use graph TD for processes like Haber Process.
                RULE 4: End with 'TEACHER GROUND NOTES:' and 'AI DISCLAIMER: Verify with UNEB teacher'.
                """
                
                with st.spinner("AI is drawing the diagram..."):
                    res = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT}, 
                            {"role": "user", "content": f"Teach {topic} for {level}"}
                        ],
                        max_tokens=1500,
                        temperature=0.2
                    )
                    content = res.choices[0].message.content

                mermaid_code = extract_mermaid(content)
                if mermaid_code:
                    st.markdown("### DIAGRAM")
                    st_mermaid(mermaid_code)
                    content = content.replace(f"```mermaid\n{mermaid_code}\n```", "")
                    st.markdown("---")

                st.markdown("### EXPLANATION")
                st.markdown(content)

            except Exception as e:
                st.error(f"Groq Error: {e}")

    with col2:
        st.markdown("### Quick Tools")
        user_q = st.text_input("Ask or Balance", placeholder="balance H2 + O2 -> H2O", key=f"calc_chem_{level}")
        if st.button("Ask", key=f"ask_chem_{level}") and user_q:
            st.info("Ask me to balance equations or explain reactions")
