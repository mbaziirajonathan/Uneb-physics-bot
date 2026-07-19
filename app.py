import streamlit as st
import os, io, pytz, random, json, sympy as sp, re, difflib, base64, tempfile, time
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from subjects import CURRICULUM, get_topics, get_practicals

@st.cache_resource
def get_client():
    from groq import Groq
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

CONCEPT_MAP = {
    "Physics": {"measurement": ["spring_balance.png"], "force": ["spring_balance.png"], "motion": ["linear_motion.png"], "wave": ["transverse_wave.png"], "light": ["convex_concave_lens.png"], "electricity": ["simple_circuit.png"], "magnet": ["bar_magnet.png"], "heat": ["heat_capacity.png"], "pressure": ["spring_balance.png"], "atmospheric": ["spring_balance.png"], "fluid": ["spring_balance.png"]},
    "Chemistry": {"atom": ["atom.png"], "bonding": ["chemical_bonding.png"], "reaction": ["chemical_reaction.png"]},
    "Biology": {"cell": ["animal_cell.png"], "dna": ["dna.png"], "heart": ["heart.png"], "brain": ["human_brain.png"]},
    "Mathematics": {}
}

ADMIN_CONTACT = "256751040731"

def safe_execute_math(code_string: str) -> str:
    local_env = {"sp": sp, "sqrt": sp.sqrt, "pi": sp.pi, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "log": sp.log, "exp": sp.exp}
    try:
        if not code_string or "result" not in code_string: return None
        if "__import__" in code_string or "os." in code_string: return None
        exec(f"g, m, v, u, a, t, s, F, W, P, E, c, delta_T, Q, n, k, rho, h, A = sp.symbols('g m v u a t s F W P E c delta_T Q n k rho h A')", {}, local_env)
        exec(f"{code_string}", {}, local_env)
        result = local_env.get("result", None)
        if result is None: return None
        if hasattr(result, 'free_symbols'): return str(sp.simplify(result).evalf(4))
        return str(result)
    except:
        return None

def get_human_ai_response(client, user_query, subject, class_level, topic=""):
    """SYSTEM PROMPT LOCK ONLY. No code lock. Chain of thought + Uganda examples + Anti-hallucination"""
    system_prompt = f"""
You are an expert secondary school teacher for {class_level} {subject} in Uganda following the NCDC 2026 curriculum.

CORE RULES:
1. Teach the topic clearly with step-by-step reasoning. Show your thinking: First define, then explain, then give Uganda example, then formula if any.
2. Use Ugandan examples always. E.g: boda boda, matatu, Nile River, coffee farming, hydroelectric dams, local markets.
3. Stay within S1-S6 NCDC 2026 {subject} syllabus. If topic is outside, say "This topic is not in NCDC 2026 {class_level} {subject} syllabus" and do not hallucinate.
4. For calculations: State formula in $LaTeX$, show 1-2 steps, then give final answer with units.
5. Language: Simple, clear, like a classroom teacher. Use headings and bullet points.
6. Do NOT return JSON. Do NOT return code to student. Do NOT make up facts.

Topic to teach: {topic}
Class: {class_level} | Subject: {subject}
"""
    full_prompt = f"Explain: {topic}\n\nStudent question/context: {user_query}"

    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": full_prompt}],
                temperature=0.5, 
                max_tokens=3500,
                stream=False
            )
            raw = response.choices[0].message.content
            if raw and len(raw) > 150:
                return raw
            time.sleep(0.5)
        except:
            time.sleep(0.5)
            continue
    
    return f"### {topic}\n\nI could not generate a full explanation for this topic right now. Please try rephrasing or ask a follow-up. For help WhatsApp {ADMIN_CONTACT}"

def transcribe_audio_with_groq(client, audio_bytes):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp: tmp.write(audio_bytes); tmp_path = tmp.name
        with open(tmp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(file=audio_file, model="whisper-large-v3", response_format="text")
        os.remove(tmp_path); return transcription.strip()
    except: return "Could not transcribe audio"

@st.cache_data
def create_pdf(content, filename):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    buffer = io.BytesIO(); c = canvas.Canvas(buffer, pagesize=A4); width, height = A4
    c.setFont("Helvetica", 10); y = height - 50
    c.setFont("Helvetica-Bold", 14); c.drawString(50, y, f"UCE/UACE DIGITAL TUTOR 2026 - {filename}"); y -= 30
    c.setFont("Helvetica", 10)
    for line in content.split('\n'):
        if "```" not in line:
            for chunk in [line[i:i+95] for i in range(0, len(line), 95)]:
                c.drawString(50, y, chunk); y -= 15
                if y < 50: c.showPage(); c.setFont("Helvetica", 10); y = height - 50
    c.save(); buffer.seek(0); return buffer

@st.cache_data
def generate_graph(data, x_col, y_col, title):
    import plotly.express as px
    fig = px.line(data, x=x_col, y=y_col, title=title, markers=True)
    fig.update_layout(template="plotly_white", height=400)
    return fig

st.set_page_config(page_title="UCE/UACE DIGITAL TUTOR 2026 GOLD", page_icon="📚", layout="wide")
UGANDA_TZ = pytz.timezone("Africa/Kampala")
BASE_DIR = Path(__file__).parent.resolve()
DIAGRAMS_DIR = BASE_DIR / "assets"
DIAGRAMS_DIR.mkdir(exist_ok=True)

SUBJECTS = ["Physics", "Chemistry", "Biology", "Mathematics"]
CLASSES = ["S1", "S2", "S3", "S4", "S5", "S6"]
GOLD_LOCKED_CLASSES = ["S5", "S6"]
GOLD_LOCKED_SUBJECTS = ["Physics", "Chemistry", "Biology", "Mathematics"]
MODES = ["Smart Search", "Theory Mode", "Lesson Preparation", "Diagrams Library", "Practicals Lab", "Quiz Mode", "Graph Generator", "Explainer Mode", "Locked Calculation Mode", "Predict Papers", "Voice Chat", "Progress Tracker", "Admin Dashboard", "Practical Assessment Generator", "Bulk Revision Generator"]

@st.cache_data
def get_all_diagrams():
    if not DIAGRAMS_DIR.exists(): return []
    return [p.name for p in DIAGRAMS_DIR.glob("*.png")]

def find_diagram(topic, subject):
    all_pngs = get_all_diagrams()
    if not all_pngs: return None
    topic_lower = topic.lower()
    if subject in CONCEPT_MAP:
        for keyword, files in CONCEPT_MAP[subject].items():
            if keyword in topic_lower:
                for f in files:
                    if f in all_pngs: return str(DIAGRAMS_DIR / f)
    return None

def log_activity(activity, subject, class_level):
    if "activities_log" not in st.session_state: st.session_state.activities_log = []
    st.session_state.activities_log.append({"time": datetime.now(UGANDA_TZ).strftime("%Y-%m-%d %H:%M:%S"), "activity": activity, "subject": subject, "class": class_level, "license": st.session_state.license})

def show_gold_upgrade():
    st.warning("🔒 **UPGRADE TO GOLD PACKAGE**")
    st.info("Unlock S5 & S6 + All Subjects + Predict Papers + Bulk Generator")
    st.markdown(f"**WhatsApp/Support: {ADMIN_CONTACT}**")
    st.link_button(f"📱 WhatsApp {ADMIN_CONTACT}", f"https://wa.me/{ADMIN_CONTACT}")

def display_student_notes(raw_text, download_name="notes"):
    clean_text = re.sub(r'```python(.*?)```', '', raw_text, flags=re.DOTALL)
    clean_text = clean_text.replace("```", "")
    st.markdown(clean_text)
    formulas = re.findall(r'\$(.*?)\$', raw_text)
    if formulas:
        st.markdown("### 🔑 Key Formula")
        for f in formulas: st.latex(f)
    code_blocks = re.findall(r'```python(.*?)```', raw_text, re.DOTALL)
    for code in code_blocks:
        res = safe_execute_math(code)
        if res:
            st.success(f"**Final Answer: {res}**")
    pdf = create_pdf(clean_text, f"{download_name}.pdf")
    st.download_button("📥 Download Full Notes as PDF", pdf, f"{download_name}.pdf", use_container_width=True)

def ask_bar(client, subject, class_level, mode, topic=""):
    st.markdown("---")
    user_q = st.text_input(f"💬 Ask follow-up question", key=f"ask_{mode}_{subject}")
    if st.button("Ask AI", key=f"ask_btn_{mode}_{subject}") and user_q:
        with st.spinner("AI is answering..."):
            raw = get_human_ai_response(client, user_q, subject, class_level, topic)
            display_student_notes(raw, f"followup_{subject}")

def main():
    if "activities_log" not in st.session_state: st.session_state.activities_log = []
    if "license" not in st.session_state: st.session_state.license = "FREE"
    st.markdown(f"""<div style="background:linear-gradient(90deg, #FFD700 0%, #FFA500 100%); padding:15px;">
    <h1 style="color:black; text-align:center">📚 UCE/UACE DIGITAL TUTOR 2026 GOLD</h1></div>""", unsafe_allow_html=True)

    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("🔒 Enter Access Key")
        col1, col2 = st.columns(2)
        FREE_PASS = st.secrets.get("FREE_PASSWORD", "UNEB_TEST_2026").upper().strip()
        GOLD_PASS = st.secrets.get("GOLD_PASSWORD", "GOLD2026").upper().strip()
        with col1:
            with st.container(border=True):
                st.markdown("### 🟢 FREE PACKAGE\nAccess: S1 - S4")
                free_password = st.text_input("Enter FREE Key", type="password", key="free_login")
                if st.button("Login FREE", type="secondary", use_container_width=True):
                    if free_password.upper().strip() == FREE_PASS: st.session_state.authenticated = True; st.session_state.license = "FREE"; st.rerun()
                    else: st.error("Invalid FREE Key")
        with col2:
            with st.container(border=True):
                st.markdown("### ⭐ GOLD PACKAGE\nAccess: S1 - S6 + All Features")
                gold_password = st.text_input("Enter GOLD Key", type="password", key="gold_login")
                if st.button("Login GOLD", type="primary", use_container_width=True):
                    if gold_password.upper().strip() == GOLD_PASS: st.session_state.authenticated = True; st.session_state.license = "GOLD"; st.rerun()
                    else: st.error("Invalid GOLD Key")
                st.markdown(f"[📱 WhatsApp Support {ADMIN_CONTACT}](https://wa.me/{ADMIN_CONTACT})")
        st.stop()

    client = get_client()
    with st.sidebar:
        st.success(f"License: {st.session_state.license}")
        st.markdown(f"**Support: WhatsApp {ADMIN_CONTACT}**")
        if st.session_state.license == "FREE":
            with st.container(border=True):
                st.markdown("### ⭐ UPGRADE TO GOLD")
                st.link_button("Get Gold Key", f"https://wa.me/{ADMIN_CONTACT}")
        subject = st.selectbox("Subject", SUBJECTS)
        available_classes = ["S1", "S2", "S3", "S4"] if st.session_state.license == "FREE" else CLASSES
        class_level = st.selectbox("Class", available_classes)

        topics_list = get_topics(subject, class_level)
        if not topics_list:
            topics_list = ["General Revision"]

        with st.expander(f"📖 {subject} {class_level} Topics"):
            for topic in topics_list: st.write(f"• {topic}")
        mode = st.radio("Mode", MODES)
        st.markdown("---")
        st.info(f"Any problem? WhatsApp: {ADMIN_CONTACT}")

    if class_level in GOLD_LOCKED_CLASSES and subject in GOLD_LOCKED_SUBJECTS and st.session_state.license == "FREE":
        st.error(f"🔒 **GOLD PACKAGE REQUIRED FOR {class_level} {subject}**")
        show_gold_upgrade(); st.stop()

    # ========= ALL 15 MODULES =========
    if mode == "Theory Mode":
        st.header("📘 Theory Mode - Detailed Notes")
        topic = st.selectbox("Topic", topics_list)
        if st.button("Generate Notes", type="primary"):
            with st.spinner("Generating notes..."):
                raw = get_human_ai_response(client, "Explain this topic", subject, class_level, topic)
                display_student_notes(raw, f"theory_{topic}")
        ask_bar(client, subject, class_level, mode, topic)

    elif mode == "Locked Calculation Mode":
        st.header("🔐 Calculation Mode")
        query = st.text_area("Enter your question")
        if st.button("Solve", type="primary") and query:
            raw = get_human_ai_response(client, query, subject, class_level, query)
            display_student_notes(raw, "calc")
            log_activity(f"Calc: {query}", subject, class_level)

    elif mode == "Smart Search":
        st.header("🧠 Smart Search")
        query = st.text_input("Ask any question")
        if st.button("Search") and query: display_student_notes(get_human_ai_response(client, query, subject, class_level, query), "search")
        ask_bar(client, subject, class_level, mode)

    elif mode == "Lesson Preparation":
        st.header("👨‍🏫 Lesson Preparation")
        topic = st.selectbox("Topic", topics_list)
        if st.button("Generate Lesson Plan"): display_student_notes(get_human_ai_response(client, "Write a 40min lesson plan with objectives and activities", subject, class_level, topic), "lesson")
        ask_bar(client, subject, class_level, mode, topic)

    elif mode == "Diagrams Library":
        st.header("🖼️ Diagrams Library")
        topic = st.selectbox("Topic", topics_list)
        path = find_diagram(topic, subject)
        if path: st.image(path, use_container_width=True)
        else: st.warning("No diagram available")
        ask_bar(client, subject, class_level, mode, topic)

    elif mode == "Practicals Lab":
        st.header("🧪 Practicals Lab")
        practicals_list = get_practicals(subject, class_level)
        if practicals_list:
            practical = st.selectbox("Select", [p["name"] for p in practicals_list])
            if st.button("Show"):
                p = next(p for p in practicals_list if p["name"] == practical)
                st.markdown(f"### {p['name']}"); st.markdown(f"**Aim:** {p['aim']}"); st.markdown(f"**Materials:** {p['materials']}"); st.markdown(f"**Procedure:** {p['procedure']}")
                log_activity(f"Practical: {practical}", subject, class_level)

    elif mode == "Quiz Mode":
        st.header("📝 Quiz Mode")
        topic = st.selectbox("Topic", topics_list)
        if st.button("Generate Quiz"): display_student_notes(get_human_ai_response(client, "Generate 5 MCQs with answers", subject, class_level, topic), "quiz")
        ask_bar(client, subject, class_level, mode, topic)

    elif mode == "Graph Generator":
        st.header("📊 Graph Generator")
        topic = st.selectbox("Topic", topics_list)
        if st.button("Generate Graph"):
            df = pd.DataFrame({"X":np.linspace(0,10,20),"Y":np.random.randn(20)})
            st.plotly_chart(generate_graph(df, "X","Y", topic))

    elif mode == "Explainer Mode":
        st.header("🎓 Explainer Mode")
        topic = st.selectbox("Topic", topics_list)
        if st.button("Explain"): display_student_notes(get_human_ai_response(client, "Explain with examples", subject, class_level, topic), "explain")

    elif mode == "Bulk Revision Generator":
        st.header("📚 Bulk Revision Generator")
        topic = st.selectbox("Topic", topics_list)
        if st.button("Generate"): display_student_notes(get_human_ai_response(client, "Generate 20 revision questions", subject, class_level, topic), "bulk")

    elif mode == "Predict Papers":
        st.header("📄 Predict Papers")
        if st.button("Predict"): display_student_notes(get_human_ai_response(client, "Predict likely exam questions", subject, class_level, f"{class_level} {subject}"), "predict")

    elif mode == "Voice Chat":
        st.header("🎤 Voice Chat")
        try:
            from streamlit_mic_recorder import mic_recorder
            audio = mic_recorder(start_prompt="🎙️ Record", stop_prompt="⏹️ Stop")
            if audio and "bytes" in audio:
                transcript = transcribe_audio_with_groq(client, audio["bytes"])
                st.success(transcript); display_student_notes(get_human_ai_response(client, transcript, subject, class_level, transcript), "voice")
        except: st.info("pip install streamlit-mic-recorder")

    elif mode == "Progress Tracker":
        st.header("📊 Progress Tracker")
        if st.session_state.activities_log: st.dataframe(pd.DataFrame(st.session_state.activities_log))

    elif mode == "Admin Dashboard":
        st.header("📈 Admin Dashboard")
        if st.session_state.activities_log: st.dataframe(pd.DataFrame(st.session_state.activities_log))

    elif mode == "Practical Assessment Generator":
        st.header("🧪 Practical AoI Generator")
        topic = st.selectbox("Topic", topics_list)
        if st.button("Generate AoI"): display_student_notes(get_human_ai_response(client, "Generate an activity of integration", subject, class_level, topic), "aoi")

if __name__ == "__main__":
    main()
