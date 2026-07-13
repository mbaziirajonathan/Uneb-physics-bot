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
        "S1": ["Select Topic", "Measurement", "Density", "Forces", "Pressure", "Energy", "Light", "Convex Lens", "Concave Lens", "Prism", "Total Internal Reflection", "Simple Microscope", "Human Eye"],
        "S2": ["Select Topic", "Waves", "Sound Wave", "Standing Wave", "Doppler Effect", "Echo", "Heat", "Gas Laws"],
        "S3": ["Select Topic", "Electric Field", "Magnetic Field", "Electromagnetic Waves", "Series Circuit", "Parallel Circuit", "Transformer", "Radioactivity"],
        "S4": ["Select Topic", "Nuclear Physics", "Photoelectric Effect", "Solar Eclipse", "Electronics"]
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
                RULE 2: If topic has a process, anatomy, ray diagram, or cycle, you MUST output a Mermaid diagram in a ```mermaid``` code block.
                RULE 3: Keep Mermaid simple. Max 8 nodes. Use graph TD for processes, graph LR for ray diagrams.
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

                # 1. CHECK FOR DIAGRAM FIRST
                mermaid_code = extract_mermaid(content)
                if mermaid_code:
                    st.markdown("### DIAGRAM")
                    st_mermaid(mermaid_code) # THIS RENDERS IT LIVE
                    content = content.replace(f"```mermaid\n{mermaid_code}\n```", "") # Remove from text
                    st.markdown("---")

                # 2. SHOW TEXT
                st.markdown("### EXPLANATION")
                st.markdown(content)

            except Exception as e:
                st.error(f"Groq Error: {e}")

    with col2:
        st.markdown("### Quick Tools")
        user_q = st.text_input("Ask or Calculate", placeholder="calculate speed 100 20", key=f"calc_{level}")
        if st.button("Ask", key=f"ask_{level}") and user_q:
            st.info("Calculator: try 'calculate speed 100 20' or 'calculate force 10 5'")
