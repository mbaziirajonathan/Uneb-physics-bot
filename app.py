import streamlit as st
import os, io, pytz, random, json, sympy as sp, re, difflib, base64, tempfile
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field
from subjects import CURRICULUM, get_topics, get_practicals

@st.cache_resource
def get_client():
    from groq import Groq
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

# ==========================================
# STRICT SUBJECT-LOCKED CONCEPT MAP
# ==========================================
CONCEPT_MAP = {
    "Physics": {
        "measurement": ["spring_balance.png", "pendulum.png"],
        "force": ["spring_balance.png"],
        "motion": ["linear_motion.png", "pendulum.png"],
        "wave": ["transverse_wave.png", "longitudinal_wave.png"],
        "light": ["convex_concave_lens.png", "light_reflection.png"],
        "lens": ["convex_concave_lens.png"],
        "reflection": ["light_reflection.png"],
        "refraction": ["convex_concave_lens.png"],
        "electricity": ["simple_circuit.png", "ac_dc_electricity.png"],
        "circuit": ["simple_circuit.png"],
        "magnet": ["bar_magnet.png"],
        "transformer": ["transformer.png"],
        "generator": ["ac_generator.png"],
        "cro": ["cro.png"],
        "radioactivity": ["radioactivity.png"],
        "heat": ["heat_capacity.png"]
    },
    "Chemistry": {
        "atom": ["atom.png"],
        "bonding": ["chemical_bonding.png", "covalent_water.png"],
        "reaction": ["chemical_reaction.png"],
        "kinetics": ["chemical_kinetics.png"],
        "hydrocarbon": ["hydrocarbon.png"],
        "chromatography": ["chromatography.png"],
        "distillation": ["fractional_distillation.png"],
        "filtration": ["filtration.png"],
        "colorimeter": ["colorimeter.png"],
        "periodic": ["periodic_table.png"],
        "chemical cell": ["chemical_cell.png"]
    },
    "Biology": {
        "cell": ["animal_cell.png", "plant_cell.png", "prokaryotic_eukaryotic.png"],
        "animal cell": ["animal_cell.png"],
        "plant cell": ["plant_cell.png"],
        "dna": ["dna.png"],
        "neurone": ["neurone.png"],
        "nephron": ["nephron.png"],
        "alveolus": ["alveolus.png"],
        "heart": ["heart.png"],
        "brain": ["human_brain.png"],
        "eye": ["human_eye.png"],
        "ear": ["human_ear.png"],
        "leaf": ["leaf.png"],
        "respiratory": ["respiratory_system.png"],
        "ecology": ["ecology.png"],
        "body system": ["body_systems.png"],
        "growth": ["human_growth_cycle.png"],
        "transport": ["transport_in_plants.png"]
    },
    "Mathematics": {}
}

class CurriculumStep(BaseModel):
    step_number: int
    curriculum_level: str
    core_concept: str
    explanation: str
    python_calculation_code: str

class LockedCurriculumResponse(BaseModel):
    detected_topic: str
    is_within_syllabus: bool
    pedagogical_steps: list[CurriculumStep]
    final_answer_formula: str

SYSTEM_PROMPT = """
You are UCE/UACE DIGITAL TUTOR 2026: Expert NCDC 2026 Uganda Teacher for S1-S6.
RULES:
1. Teach like a human teacher. Use headings, bullets, examples, and clear English.
2. For calculations: provide python code that sets variable `result`. First line must define symbols.
3. Ground only in S1-S6 NCDC 2026 syllabus. If outside, set is_within_syllabus=false.
4. OUTPUT: Return ONLY a valid JSON object with keys: detected_topic, is_within_syllabus, pedagogical_steps[], final_answer_formula.
"""

def execute_deterministic_math(code_string: str) -> str:
    local_env = {"sp": sp, "symbols": sp.symbols, "math": __import__('math'), "sqrt": sp.sqrt, "pi": sp.pi, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "log": sp.log, "exp": sp.exp}
    try:
        if "__import__" in code_string or "os." in code_string: return "Blocked"
        common_symbols = "g, m, v, u, a, t, s, F, W, P, E, k, n, i, r, R, V, I, Q, T, L, f, lambda, theta, rho"
        exec(f"{common_symbols} = sp.symbols('{common_symbols}')", {}, local_env)
        exec(f"{code_string}", {}, local_env)
        result = local_env.get("result", "No result")
        if hasattr(result, 'free_symbols'): return str(sp.simplify(result).evalf(4))
        return str(result)
    except Exception as e: return f"Error: {str(e)}"

def extract_json_from_text(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    return match.group(0) if match else text

def get_locked_ai_response(client, user_query, subject, class_level):
    full_prompt = f"Subject: {subject}. Class: {class_level}. NCDC 2026. Query: {user_query}"
    for attempt in range(2):
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": full_prompt}],
            temperature=0.1,
            max_tokens=8192
        )
        raw = extract_json_from_text(resp.choices[0].message.content)
        try:
            return LockedCurriculumResponse.model_validate_json(raw)
        except:
            if attempt == 0: full_prompt = f"Return ONLY valid JSON. {full_prompt}"
    return LockedCurriculumResponse(
        detected_topic=f"{subject}: {user_query[:80]}",
        is_within_syllabus=True,
        pedagogical_steps=[CurriculumStep(
            step_number=1, curriculum_level=f"{class_level} {subject}",
            core_concept="Explanation", explanation=raw[:3000], python_calculation_code=""
        )],
        final_answer_formula="N/A"
    )

def transcribe_audio_with_groq(client, audio_bytes):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes); tmp_path = tmp.name
        with open(tmp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(file=audio_file, model="whisper-large-v3", response_format="text")
        os.remove(tmp_path)
        return transcription.strip()
    except Exception as e: return f"Transcription Error: {str(e)}"

@st.cache_data
def create_pdf(content, filename):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    buffer = io.BytesIO(); c = canvas.Canvas(buffer, pagesize=A4); width, height = A4
    c.setFont("Helvetica", 10); y = height - 50
    c.setFont("Helvetica-Bold", 14); c.drawString(50, y, f"UCE/UACE DIGITAL TUTOR 2026"); y -= 30
    c.setFont("Helvetica", 10)
    for line in content.split('\n'):
        for chunk in [line[i:i+95] for i in range(0, len(line), 95)]:
            c.drawString(50, y, chunk); y -= 15
            if y < 50: c.showPage(); c.setFont("Helvetica", 10); y = height - 50
    c.save(); buffer.seek(0); return buffer

def build_text_from_locked(locked):
    text = f"Topic: {locked.detected_topic}\n\n"
    for step in locked.pedagogical_steps:
        text += f"{step.core_concept}\n{step.explanation}\n"
        if step.python_calculation_code:
            text += f"Code: {step.python_calculation_code}\nResult: {execute_deterministic_math(step.python_calculation_code)}\n"
    text += f"\nFinal Formula: {locked.final_answer_formula}"
    return text

@st.cache_data
def generate_graph(data, x_col, y_col, title):
    import plotly.express as px
    fig = px.line(data, x=x_col, y=y_col, title=title, markers=True)
    fig.update_layout(template="plotly_white", height=400)
    return fig

st.set_page_config(page_title="UCE/UACE DIGITAL TUTOR 2026 GOLD", page_icon="📚", layout="wide")
ADMIN_CONTACT = "256751040731"
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
                    if f in all_pngs:
                        return str(DIAGRAMS_DIR / f)
    return None

def log_activity(activity, subject, class_level):
    if "activities_log" not in st.session_state: st.session_state.activities_log = []
    st.session_state.activities_log.append({"time": datetime.now(UGANDA_TZ).strftime("%Y-%m-%d %H:%M:%S"), "activity": activity, "subject": subject, "class": class_level, "license": st.session_state.license})

def show_gold_upgrade():
    st.warning("🔒 **UPGRADE TO GOLD PACKAGE**")
    st.info("Unlock S5 & S6 + All Subjects + Predict Papers + Bulk Generator")
    st.markdown(f"**WhatsApp/Call: {ADMIN_CONTACT}**")
    st.link_button(f"📱 WhatsApp {ADMIN_CONTACT}", f"https://wa.me/{ADMIN_CONTACT}")

def display_human_notes(locked, download_name="notes"):
    if not locked: return
    st.markdown(f"## 📖 {locked.detected_topic}")
    if not locked.is_within_syllabus:
        st.error("This topic is outside S1-S6 NCDC 2026 syllabus")
        return
    full_text = build_text_from_locked(locked)
    for step in locked.pedagogical_steps:
        with st.container(border=True):
            st.markdown(f"### {step.core_concept}")
            st.markdown(step.explanation.replace('\\n', '\n'))
            if step.python_calculation_code.strip():
                st.markdown("**Worked Example:**")
                st.code(step.python_calculation_code, language="python")
                res = execute_deterministic_math(step.python_calculation_code)
                st.success(f"**Answer:** `{res}`")
    if locked.final_answer_formula and locked.final_answer_formula!= "N/A":
        st.markdown("### 🔑 Key Formula")
        st.latex(locked.final_answer_formula)
    pdf = create_pdf(full_text, f"{download_name}.pdf")
    st.download_button("📥 Download Full Notes as PDF", pdf, f"{download_name}.pdf", use_container_width=True)

def ask_bar(client, subject, class_level, mode):
    st.markdown("---")
    user_q = st.text_input(f"💬 Ask follow-up", key=f"ask_{mode}_{subject}")
    if st.button("Ask AI", key=f"ask_btn_{mode}_{subject}") and user_q:
        locked = get_locked_ai_response(client, user_q, subject, class_level)
        display_human_notes(locked, f"followup_{subject}")

def main():
    if "activities_log" not in st.session_state: st.session_state.activities_log = []
    if "license" not in st.session_state: st.session_state.license = "FREE"
    st.markdown("""<div style="background:linear-gradient(90deg, #FFD700 0%, #FFA500 100%); padding:15px;"><h1 style="color:black; text-align:center">📚 UCE/UACE DIGITAL TUTOR 2026 GOLD - NCDC LOCKED</h1></div>""", unsafe_allow_html=True)

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
                st.markdown(f"[📱 WhatsApp {ADMIN_CONTACT}](https://wa.me/{ADMIN_CONTACT})")
        st.stop()

    client = get_client()
    with st.sidebar:
        st.success(f"License: {st.session_state.license}")
        if st.session_state.license == "FREE":
            with st.container(border=True):
                st.markdown("### ⭐ UPGRADE TO GOLD")
                st.link_button("Get Gold Key", f"https://wa.me/{ADMIN_CONTACT}")
        subject = st.selectbox("Subject", SUBJECTS)
        available_classes = ["S1", "S2", "S3", "S4"] if st.session_state.license == "FREE" else CLASSES
        class_level = st.selectbox("Class", available_classes)
        with st.expander(f"📖 {subject} {class_level} Topics"):
            for topic in get_topics(subject, class_level): st.write(f"• {topic}")
        mode = st.radio("Mode", MODES)

    if class_level in GOLD_LOCKED_CLASSES and subject in GOLD_LOCKED_SUBJECTS and st.session_state.license == "FREE":
        st.error(f"🔒 **GOLD PACKAGE REQUIRED FOR {class_level} {subject}**")
        show_gold_upgrade(); st.stop()

    # ALL 15 MODES RESTORED
    if mode == "Locked Calculation Mode":
        st.header("🔐 Locked Calculation Mode - No Hallucinations")
        query = st.text_area("Enter your Physics/Chem/Math question")
        if st.button("Solve with Python Lock", type="primary") and query:
            locked = get_locked_ai_response(client, query, subject, class_level)
            display_human_notes(locked, f"calc_{subject}_{class_level}")
            log_activity(f"LockedCalc: {query}", subject, class_level)

    elif mode == "Smart Search":
        st.header("🧠 Smart Search")
        query = st.text_input("Ask any question")
        if st.button("Search") and query: display_human_notes(get_locked_ai_response(client, f"Explain {query}", subject, class_level), f"search_{subject}")
        ask_bar(client, subject, class_level, mode)

    elif mode == "Theory Mode":
        st.header("📘 Theory Mode - Detailed Human Notes")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Generate Notes", type="primary"):
            locked = get_locked_ai_response(client, f"Write detailed NCDC 2026 notes on {topic} with definitions, examples, key formulas", subject, class_level)
            display_human_notes(locked, f"theory_{topic}")
        ask_bar(client, subject, class_level, mode)

    elif mode == "Lesson Preparation":
        st.header("👨‍🏫 Lesson Preparation")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Generate Lesson Plan + AoI"):
            locked = get_locked_ai_response(client, f"40min competency-based lesson plan with AoI for {topic} in Ugandan context", subject, class_level)
            display_human_notes(locked, f"lesson_{topic}")
        ask_bar(client, subject, class_level, mode)

    elif mode == "Diagrams Library":
        st.header("🖼️ Diagrams Library")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        path = find_diagram(topic, subject)
        st.info(f"Found {len(get_all_diagrams())} images")
        if path:
            try: st.image(path, caption=f"{subject}: {topic}", use_container_width=True)
            except: st.error("Image error")
        else: st.warning(f"❌ No diagram for '{topic}' in {subject}")
        ask_bar(client, subject, class_level, mode)

    elif mode == "Practicals Lab":
        st.header("🧪 Practicals Lab")
        practicals_list = get_practicals(subject, class_level)
        if practicals_list:
            practical = st.selectbox("Select Practical", [p["name"] for p in practicals_list])
            if st.button("Show Practical"):
                p = next(p for p in practicals_list if p["name"] == practical)
                with st.container(border=True):
                    st.subheader(p["name"]); st.markdown(f"**Aim:** {p['aim']}")
                    st.markdown(f"**Materials:** {p['materials']}"); st.markdown(f"**Procedure:** {p['procedure']}")
                pdf = create_pdf(f"Practical: {p['name']}\nAim: {p['aim']}\nMaterials: {p['materials']}\nProcedure: {p['procedure']}", f"practical_{p['name']}.pdf")
                st.download_button("📥 Download Practical PDF", pdf, f"practical_{p['name']}.pdf")
                if p["graph"]:
                    if st.button("Generate Sample Graph"):
                        x = np.linspace(0,10,20); y = x * random.uniform(0.5,2) + np.random.randn(20)*2
                        st.plotly_chart(generate_graph(pd.DataFrame({"X":x,"Y":y}), "X","Y", p["graph"]))
                log_activity(f"Practical: {practical}", subject, class_level)
        ask_bar(client, subject, class_level, mode)

    elif mode == "Quiz Mode":
        st.header("📝 Quiz Mode")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Generate 5 MCQs"): display_human_notes(get_locked_ai_response(client, f"Generate 5 MCQs with answers on {topic}", subject, class_level), f"quiz_{topic}")
        ask_bar(client, subject, class_level, mode)

    elif mode == "Graph Generator":
        st.header("📊 Graph Generator")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Generate Sample Data Graph"):
            x = np.linspace(0,10,20); y = x**2 * 0.5 + np.random.randn(20)*5
            df = pd.DataFrame({"X":x,"Y":y})
            st.plotly_chart(generate_graph(df, "X","Y", topic))
            st.download_button("📥 Download CSV", df.to_csv(index=False).encode(), "graph_data.csv")

    elif mode == "Explainer Mode":
        st.header("🎓 Explainer Mode")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Explain Topic"): display_human_notes(get_locked_ai_response(client, f"Explain {topic} with 3 examples and mistakes", subject, class_level), f"explainer_{topic}")

    elif mode == "Bulk Revision Generator":
        st.header("📚 Bulk Revision Generator")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Generate"): display_human_notes(get_locked_ai_response(client, f"Generate 20 revision questions with answers on {topic}", subject, class_level), f"revision_{topic}")

    elif mode == "Predict Papers":
        st.header("📄 Predict Papers")
        if st.button("Predict Full Subject"): display_human_notes(get_locked_ai_response(client, f"Predict UCE/UACE questions for {class_level} {subject}", subject, class_level), f"predict_{subject}_{class_level}")

    elif mode == "Voice Chat":
        st.header("🎤 Voice Chat")
        try:
            from streamlit_mic_recorder import mic_recorder
            audio = mic_recorder(start_prompt="🎙️ Record", stop_prompt="⏹️ Stop", key="voice_rec")
            if audio and "bytes" in audio:
                with st.spinner("Transcribing..."): transcript = transcribe_audio_with_groq(client, audio["bytes"])
                st.success(f"You said: {transcript}")
                display_human_notes(get_locked_ai_response(client, transcript, subject, class_level), "voice")
        except: st.info("Install streamlit-mic-recorder")

    elif mode == "Progress Tracker":
        st.header("📊 Progress Tracker")
        if st.session_state.activities_log:
            df = pd.DataFrame(st.session_state.activities_log)
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Download Progress CSV", df.to_csv(index=False).encode(), "progress.csv")

    elif mode == "Admin Dashboard":
        st.header("📈 Admin Dashboard")
        if st.session_state.activities_log:
            df = pd.DataFrame(st.session_state.activities_log)
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Download Admin Log CSV", df.to_csv(index=False).encode(), "admin_log.csv")

    elif mode == "Practical Assessment Generator":
        st.header("🧪 Practical AoI Generator")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Generate AoI"): display_human_notes(get_locked_ai_response(client, f"Generate Competency-based AoI for {topic} with Ugandan scenario", subject, class_level), f"aoi_{topic}")

if __name__ == "__main__":
    main()
