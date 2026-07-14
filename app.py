import streamlit as st
import os
import pytz
from datetime import datetime
from groq import Groq, GroqError
from typing import Dict, Any

SVG_SPRITES = """
<svg style="display:none;">
  <symbol id="atom" viewBox="0 0 100 100"><circle cx="50" cy="50" r="10" fill="#FF6B6B"/><ellipse cx="50" cy="50" rx="40" ry="10" stroke="#4ECDC4" stroke-width="2" fill="none" transform="rotate(0 50 50)"/><ellipse cx="50" cy="50" rx="40" ry="10" stroke="#4ECDC4" stroke-width="2" fill="none" transform="rotate(60 50 50)"/><ellipse cx="50" cy="50" rx="40" ry="10" stroke="#4ECDC4" stroke-width="2" fill="none" transform="rotate(120 50 50)"/></symbol>
  <symbol id="transformer" viewBox="0 0 120 100"><rect x="10" y="20" width="30" height="60" fill="#95E1D3"/><rect x="80" y="20" width="30" height="60" fill="#95E1D3"/><path d="M40 50 Q60 30 80 50 Q60 70 40 50" stroke="#F38181" stroke-width="3" fill="none"/></symbol>
  <symbol id="plant_cell" viewBox="0 0 100 100"><rect x="10" y="10" width="80" height="80" fill="none" stroke="#2D5016" stroke-width="2"/><circle cx="50" cy="50" r="15" fill="#A8E6CF"/></symbol>
  <symbol id="hookes_law" viewBox="0 0 100 100"><path d="M45 30 L55 35 L45 40 L55 45 L45 50 L55 55 L45 60 L55 65 L45 70" stroke="#000" fill="none"/><rect x="40" y="70" width="20" height="15" fill="#FFD93D"/></symbol>
  <symbol id="xray_tube" viewBox="0 0 120 80"><rect x="10" y="20" width="100" height="40" fill="#C7CEEA" stroke="#000"/><circle cx="30" cy="40" r="5" fill="#FFD93D"/><polygon points="90,25 110,40 90,55" fill="#FF6B6B"/></symbol>
  <symbol id="dna" viewBox="0 0 100 100"><path d="M30 10 Q50 30 30 50 Q50 70 30 90" stroke="#4ECDC4" stroke-width="3" fill="none"/><path d="M70 10 Q50 30 70 50 Q50 70 70 90" stroke="#FF6B6B" stroke-width="3" fill="none"/></symbol>
  <symbol id="ecosystem" viewBox="0 0 100 100"><rect x="0" y="70" width="100" height="30" fill="#8B4513"/><circle cx="20" cy="50" r="15" fill="#2D5016"/><circle cx="50" cy="20" r="15" fill="#FFD93D"/></symbol>
  <symbol id="circulatory" viewBox="0 0 100 100"><path d="M50 20 C30 20 20 40 20 50 C20 70 50 90 50 90 C50 90 80 70 80 50 C80 40 70 20 50 20" fill="none" stroke="#FF6B6B" stroke-width="3"/><circle cx="50" cy="45" r="8" fill="#FF6B6B"/></symbol>
  <symbol id="photosynthesis" viewBox="0 0 100 100"><rect x="10" y="60" width="80" height="10" fill="#8B4513"/><rect x="40" y="30" width="20" height="30" fill="#2D5016"/><circle cx="20" cy="20" r="10" fill="#FFD93D"/></symbol>
  <symbol id="electroscope" viewBox="0 0 100 100"><rect x="40" y="10" width="20" height="40" fill="#C7CEEA"/><circle cx="50" cy="60" r="20" fill="none" stroke="#000"/></symbol>
  <symbol id="refraction" viewBox="0 0 100 100"><line x1="0" y1="50" x2="100" y2="50" stroke="#999"/><line x1="10" y1="20" x2="50" y2="50" stroke="#FF6B6B" stroke-width="2"/><line x1="50" y1="50" x2="90" y2="70" stroke="#FF6B6B" stroke-width="2"/></symbol>
  <symbol id="specific_heat" viewBox="0 0 100 100"><rect x="20" y="40" width="60" height="40" fill="#C7CEEA"/><path d="M50 20 Q60 30 50 40" fill="#FF6B6B"/></symbol>
  <symbol id="wave" viewBox="0 0 100 100"><path d="M0 50 Q25 20 50 50 T100 50" stroke="#4ECDC4" stroke-width="2" fill="none"/></symbol>
  <symbol id="battery" viewBox="0 0 100 100"><rect x="30" y="30" width="40" height="40" fill="#FFD93D"/><line x1="30" y1="40" x2="20" y2="40" stroke="#000" stroke-width="3"/><line x1="70" y1="50" x2="80" y2="50" stroke="#000" stroke-width="3"/></symbol>
  <symbol id="microscope" viewBox="0 0 100 100"><rect x="40" y="10" width="20" height="60" fill="#C7CEEA"/><circle cx="50" cy="80" r="15" fill="#95E1D3"/></symbol>
</svg>
"""

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

DIAGRAM_LOOKUP = {
    ("Physics", "S2", "Electroscope"): "electroscope", ("Physics", "S2", "Refraction"): "refraction", ("Physics", "S2", "Waves"): "wave",
    ("Physics", "S3", "Hookes Law"): "hookes_law", ("Physics", "S3", "Specific Heat Capacity"): "specific_heat",
    ("Physics", "S4", "Transformers"): "transformer", ("Physics", "S4", "X-Ray Production"): "xray_tube",
    ("Chemistry", "S1", "Structure of an Atom"): "atom",
    ("Biology", "S1", "Plant Cell"): "plant_cell", ("Biology", "S1", "Ecosystem"): "ecosystem",
    ("Biology", "S2", "Circulatory System"): "circulatory", ("Biology", "S2", "Photosynthesis"): "photosynthesis",
    ("Biology", "S3", "DNA"): "dna"
}

class DiagramManager:
    @staticmethod
    def initialize_sprites():
        st.markdown(SVG_SPRITES, unsafe_allow_html=True)
    @staticmethod
    def get_symbol_by_curriculum(subject, level, topic):
        return DIAGRAM_LOOKUP.get((subject, level, topic), None)
    @staticmethod
    def render(symbol_id):
        if symbol_id:
            st.markdown(f'<div style="display:flex; justify-content:center; padding:20px; background:#f0f2f6; border-radius:10px;"><svg width="100%" height="350" style="max-width:500px;"><use href="#{symbol_id}"></use></svg></div>', unsafe_allow_html=True)
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
    DiagramManager.initialize_sprites()
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
        symbol_id = DiagramManager.get_symbol_by_curriculum(subject, level, topic)
        DiagramManager.render(symbol_id)
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
