import streamlit as st
from groq import Groq
from streamlit_mermaid import st_mermaid
import re

def extract_mermaid(text):
    match = re.search(r"```mermaid(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else None

def run(level):
    st.subheader(f"Biology - {level}")

    topics = {
        "S1": [
            "Select Topic", "Animal Cell", "Plant Cell", "Differences: Plant vs Animal Cell", 
            "Leaf Structure", "Hand Lens", "Light Microscope", "Photosynthesis", 
            "Characteristics of Living Things", "Classification of Organisms"
        ],
        "S2": [
            "Select Topic", "Heart Structure", "Blood Circulation", "Respiratory System", 
            "Digestive System", "Human Skeleton", "Teeth", "Nutrition", "Transport in Plants"
        ],
        "S3": [
            "Select Topic", "Neuron", "Reflex Arc", "Kidney Structure", "Nephron", 
            "Photosynthesis Light/Dark Stage", "DNA Structure", "Cell Division: Mitosis", 
            "Cell Division: Meiosis", "Enzymes", "Diffusion and Osmosis"
        ],
        "S4": [
            "Select Topic", "Brain Structure", "Human Eye", "Ear Structure", "DNA Replication", 
            "Genetics: Monohybrid Cross", "Evolution", "Ecology: Food Web", 
            "Ecosystem", "Pollution", "Reproduction in Humans"
        ]
    }

    topic = st.selectbox("Select Biology Topic", topics[level], key=f"biology_{level}")

    if topic == "Select Topic":
        st.info("Select a topic to generate AI lesson + diagram")
        return

    col1, col2 = st.columns([3, 1])

    with col1:
        if st.button("Generate Lesson", type="primary", key=f"btn_bio_{level}"):
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                
                SYSTEM_PROMPT = f"""You are a UNEB {level} Biology tutor for Uganda. Use NCDC 2026 syllabus.
                RULE 1: Explain with definition, structure/function, 1 worked example, 1 practice question [4 marks].
                RULE 2: For anatomy, processes, cycles, you MUST output a Mermaid diagram in a ```mermaid``` code block.
                RULE 3: Use graph TD for cycles like photosynthesis. Use graph LR for anatomy labeling.
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
        user_q = st.text_input("Ask Biology Qn", placeholder="function of mitochondria", key=f"calc_bio_{level}")
        if st.button("Ask", key=f"ask_bio_{level}") and user_q:
            st.info("Ask me any UNEB Biology question")
