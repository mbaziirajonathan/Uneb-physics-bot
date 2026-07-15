import streamlit as st
import os
import pytz
from datetime import datetime
from groq import Groq, GroqError
from typing import Dict, Any

UNEB_CURRICULUM_MAP = {
    "Physics": {
        "S1": {"Introduction to Physics": {}, "Measurement": {}, "Force": {}, "Work Energy Power": {}, "Pressure": {}},
        "S2": {"Electroscope": {}, "Current Electricity": {}, "Refraction": {}, "Heat": {}, "Waves": {}},
        "S3": {"Hookes Law": {}, "Specific Heat Capacity": {}, "Magnetism": {}, "Wave Motion": {}, "Radioactivity": {}},
        "S4": {"Transformers": {}, "X-Ray Production": {}, "Electronics": {}, "Nuclear Physics": {}, "Astrophysics": {}}
    },
    "Chemistry": {
        "S1": {"Structure of an Atom": {}, "Periodic Table": {}, "Chemical Bonding": {}, "Acids Bases Salts": {}, "Air and Combustion": {}},
        "S2": {"Water and Hydrogen": {}, "Oxygen": {}, "Carbon and its Compounds": {}, "Fertilizers": {}, "Metals": {}},
        "S3": {"Rates of Reaction": {}, "Energy Changes": {}, "Chemical Equilibrium": {}, "Acids and Bases": {}, "Organic Chemistry": {}},
        "S4": {"Electrochemistry": {}, "Nitrogen and Compounds": {}, "Sulphur and Compounds": {}, "Industrial Chemistry": {}, "Polymers": {}}
    },
    "Biology": {
        "S1": {"Plant Cell": {}, "Ecosystem": {}, "Classification": {}, "Nutrition in Plants": {}, "Nutrition in Animals": {}},
        "S2": {"Circulatory System": {}, "Photosynthesis": {}, "Respiration": {}, "Excretion": {}, "Reproduction in Plants": {}},
        "S3": {"DNA": {}, "Cell Division": {}, "Genetics": {}, "Evolution": {}, "Ecology": {}},
        "S4": {"Human Reproduction": {}, "Nervous System": {}, "Homeostasis": {}, "Immunity": {}, "Biotechnology": {}}
    }
}

# ALL DIAGRAMS MAPPED - PREVIOUS + NEW FROM YOUR SCREENSHOT
DIAGRAM_FILES = {
    # PHYSICS - 10 DIAGRAMS
    ("Physics", "S1", "Measurement"): "assets/vernier.png",
    ("Physics", "S1", "Force"): "assets/spring_balance.png",
    ("Physics", "S2", "Current Electricity"): "assets/simple_circuit.png",
    ("Physics", "S2", "Electroscope"): "assets/electroscope.png", 
    ("Physics", "S2", "Refraction"): "assets/refraction.png", 
    ("Physics", "S2", "Waves"): "assets/cro.png",
    ("Physics", "S3", "Hookes Law"): "assets/hookes_law.png", 
    ("Physics", "S3", "Specific Heat Capacity"): "assets/colorimeter.png",
    ("Physics", "S4", "Transformers"): "assets/ac_transformer.png", 
    ("Physics", "S4", "X-Ray Production"): "assets/xray_tube.png",

    # CHEMISTRY - 4 DIAGRAMS
    ("Chemistry", "S1", "Structure of an Atom"): "assets/atom.png",
    ("Chemistry", "S1", "Chemical Bonding"): "assets/covalent_water.png",
    ("Chemistry", "S2", "Water and Hydrogen"): "assets/filtration.png",
    ("Chemistry", "S2", "Metals"): "assets/fractional_distillation.png",

    # BIOLOGY - 7 DIAGRAMS
    ("Biology", "S1", "Plant Cell"): "assets/plant_cell.png", 
    ("Biology", "S1", "Ecosystem"): "assets/leaf.png",
    ("Biology", "S2", "Circulatory System"): "assets/heart.png", 
    ("Biology", "S2", "Photosynthesis"): "assets/photosynthesis.png",
    ("Biology", "S2", "Excretion"): "assets/nephron.png",
    ("Biology", "S3", "DNA"): "assets/dna.png",
    ("Biology", "S4", "Nervous System"): "assets/neurone.png",
}

class DiagramManager:
    @staticmethod
    def render(subject, level, topic):
        key = (subject, level, topic)
        if key in DIAGRAM_FILES:
            image_path = DIAGRAM_FILES[key]
            if os.path.exists(image_path):
                st.markdown('<div style="display:flex; justify-content:center; padding:10px; background:#f0f2f6; border-radius:10px;">', unsafe_allow_html=True)
                st.image(image_path, use_column_width=True, caption=f"{topic} Diagram")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error(f"Image not found: {image_path}")
        else:
            st.info("No diagram available for this topic yet")

try:
    import subjects.physics as physics
    import subjects.chemistry as chemistry
    import subjects.biology as biology
    SUBJECT_MODULES = {"Physics": physics, "Chemistry": chemistry, "Biology": biology}
except ImportError:
    SUBJECT_MODULES = {}
    st.warning("⚠️ Subject content modules not fully found. Defaulting to AI & Diagram generation only.")

st.set_page_config(page_title="UNEB AI Tutor 2026", page_icon="📚", layout="wide", initial_sidebar_state="expanded")

def init_session_state():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if "messages" not in st.session_state: st.session_state.messages = []
    if "current_topic" not in st.session_state: st.session_state.current_topic = None

def render_auth_gate():
    st.title("🛡️ UNEB AI Tutor - Secure Access")
    with st.form("login_form"):
        pwd = st.text_input("Enter Access Token", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if pwd == "UNEB_TEST_2026":
                st.session_state.logged_in = True; st.rerun()
            else: st.error("Invalid token. Access denied.")
    st.stop()

def get_groq_client() -> Groq:
    try:
        api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
        if not api_key: raise ValueError("API Key missing.")
        return Groq(api_key=api_key)
    except Exception as e:
        st.error("🚨 Integration Error: Groq API Key not configured properly in Streamlit secrets.")
        st.stop()

def generate_ai_response(client: Groq, subject: str, level: str, topic: str, user_prompt: str):
    system_prompt = f"You are an expert UNEB examiner and tutor for {subject} {level}. The current topic is: {topic}. Strictly align your answers with the Ugandan Lower Secondary Curriculum 2026. Use clear, direct language. Use bullet points for readability. Never use ASCII art. If a user asks for a diagram, tell them: 'Please refer to the diagram rendered in the interactive viewer above'."
    messages_payload = [{"role": "system", "content": system_prompt}] + st.session_state.messages
    try:
        response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages_payload, temperature=0.3, max_tokens=1024)
        return response.choices[0].message.content
    except GroqError as e:
        return f"⚠️ Connection Error to AI Engine: {str(e)}"

def main():
    init_session_state()
    if not st.session_state.logged_in: render_auth_gate()
    client = get_groq_client()
    st.sidebar.title("📚 UNEB Navigation")
    subject = st.sidebar.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
    level = st.sidebar.selectbox("Class Level", list(UNEB_CURRICULUM_MAP[subject].keys()))
    topics_list = list(UNEB_CURRICULUM_MAP[subject][level].keys())
    if not topics_list:
        st.sidebar.warning("No topics mapped for this level yet."); st.stop()
    topic = st.sidebar.selectbox("Topic", topics_list)
    if st.session_state.current_topic!= f"{subject}_{level}_{topic}":
        st.session_state.messages = []; st.session_state.current_topic = f"{subject}_{level}_{topic}"
    tz = pytz.timezone("Africa/Kampala")
    st.sidebar.divider()
    st.sidebar.caption(f"📍 Kampala Time: {datetime.now(tz).strftime('%A, %H:%M %p')}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False; st.rerun()
    st.title(f"{subject} {level}: {topic}")
    col_text, col_visual = st.columns([1.2, 1])
    with col_text:
        st.subheader("📖 Topic Overview")
        if subject in SUBJECT_MODULES:
            try:
                content = SUBJECT_MODULES[subject].get_content(level, topic)
                st.markdown(content.get("text", "No text overview provided in module."))
            except Exception:
                st.info("Ask the AI Tutor below for an overview of this topic.")
        else:
            st.info("Ask the AI Tutor below for a detailed explanation of this topic.")
    with col_visual:
        st.subheader("🔬 Interactive Diagram")
        DiagramManager.render(subject, level, topic) # NOW LOADS ALL 28 PNGs
    st.divider()
    st.subheader("🤖 Ask the UNEB AI Tutor")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    if prompt := st.chat_input("E.g., Explain how this diagram works..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Analyzing UNEB syllabus..."):
                answer = generate_ai_response(client, subject, level, topic, prompt)
                st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

if __name__ == "__main__":
    main()
