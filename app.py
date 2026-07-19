import streamlit as st
import os, io, pytz, random, json, sympy as sp
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
# ANTI-HALLUCINATION LOCK SYSTEM
# ==========================================
class CurriculumStep(BaseModel):
    step_number: int = Field(description="Sequential step index starting at 1.")
    curriculum_level: str = Field(description="Target S1-S6 level mapping e.g. 'S4 Physics'.")
    core_concept: str = Field(description="The scientific theory or mathematical axiom being applied.")
    explanation: str = Field(description="Pedagogical step-by-step reasoning using NCDC 2026 approved terms.")
    python_calculation_code: str = Field(description="EXCLUSIVE calculation code. Use sympy or math. Must set variable 'result'.")

class LockedCurriculumResponse(BaseModel):
    detected_topic: str = Field(description="Standardized curriculum topic string.")
    is_within_syllabus: bool = Field(description="True if topic is within S1-S6 NCDC 2026, False otherwise.")
    pedagogical_steps: list[CurriculumStep] = Field(description="Chronological step-by-step breakdown with theory.")
    final_answer_formula: str = Field(description="The final raw LaTeX formula or scientific outcome.")

SYSTEM_PROMPT = """
You are UCE/UACE DIGITAL TUTOR 2026: A deterministic NCDC 2026 Secondary School S1-S6 Curriculum Engine.
CRITICAL LAWS:
1. Grounding: Answer ONLY using NCDC 2026 Uganda syllabus for S1-S6 Physics, Chemistry, Biology, Mathematics.
2. Anti-Hallucination: Do NOT compute numbers in text. For ANY number or formula, you MUST put exact sympy/python code in `python_calculation_code` and set variable `result`.
3. Full Explanation: In `explanation` field, give full theory, definitions, procedure in clear English. Do NOT leave it empty.
4. Program of Thought: Each step must have valid python code.
5. Boundaries: If query is outside S1-S6 NCDC 2026, set `is_within_syllabus` = false and halt.
OUTPUT ONLY raw JSON matching schema. No markdown.
"""

def execute_deterministic_math(code_string: str) -> str:
    local_env = {"sp": sp, "symbols": sp.symbols, "math": __import__('math')}
    try:
        if "__import__" in code_string or "os." in code_string or "sys." in code_string or "open(" in code_string:
            return "Execution Blocked: Insecure code detected."
        exec(f"{code_string}", {}, local_env)
        result = local_env.get("result", "No 'result' variable set")
        return str(sp.simplify(result)) if hasattr(result, 'free_symbols') else str(result)
    except Exception as e:
        return f"Execution Error: {str(e)}"

def get_locked_ai_response(client, user_query, subject, class_level):
    full_prompt = f"Subject: {subject}. Class: {class_level}. NCDC 2026 Syllabus. Query: {user_query}"
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": full_prompt}],
        response_format={"type": "json_object"},
        temperature=0.0,
        max_tokens=2048
    )
    raw = resp.choices[0].message.content
    try:
        return LockedCurriculumResponse.model_validate_json(raw)
    except Exception as e:
        st.error(f"JSON Parse Error: {e}")
        return None

@st.cache_data
def create_pdf(content, filename):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 10)
    y = height - 50
    title = filename.replace(".pdf","")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"UCE/UACE DIGITAL TUTOR 2026 - {title}")
    y -= 30
    c.setFont("Helvetica", 10)
    for line in content.split('\n'):
        for chunk in [line[i:i+95] for i in range(0, len(line), 95)]:
            c.drawString(50, y, chunk)
            y -= 15
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 50
    c.save()
    buffer.seek(0)
    return buffer

def build_text_from_locked(locked):
    """Convert locked JSON to plain text for PDF download"""
    text = f"Topic: {locked.detected_topic}\n\n"
    for step in locked.pedagogical_steps:
        text += f"Step {step.step_number}: {step.curriculum_level}\n"
        text += f"Concept: {step.core_concept}\n"
        text += f"Explanation: {step.explanation}\n"
        if step.python_calculation_code:
            text += f"Code: {step.python_calculation_code}\n"
            text += f"Result: {execute_deterministic_math(step.python_calculation_code)}\n"
        text += "\n"
    text += f"Final Answer: {locked.final_answer_formula}"
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

def find_diagram(topic):
    if not DIAGRAMS_DIR.exists(): return None
    all_pngs = list(DIAGRAMS_DIR.glob("*.png"))
    if not all_pngs: return None
    topic_clean = topic.lower().replace(" ", "_").replace("/", "_")
    for png_path in all_pngs:
        if topic_clean == png_path.stem.lower(): return str(png_path)
    for png_path in all_pngs:
        if topic_clean in png_path.name.lower(): return str(png_path)
    topic_words = topic_clean.split("_")
    for png_path in all_pngs:
        png_name = png_path.name.lower()
        if all(word in png_name for word in topic_words if len(word) > 2): return str(png_path)
    return None

def log_activity(activity, subject, class_level):
    if "activities_log" not in st.session_state: st.session_state.activities_log = []
    st.session_state.activities_log.append({"time": datetime.now(UGANDA_TZ).strftime("%Y-%m-%d %H:%M:%S"), "activity": activity, "subject": subject, "class": class_level, "license": st.session_state.license})

def show_gold_upgrade():
    st.warning("🔒 **UPGRADE TO GOLD PACKAGE**")
    st.info("Unlock S5 & S6 + All Subjects + Predict Papers + Bulk Generator")
    st.markdown(f"**WhatsApp/Call: {ADMIN_CONTACT}**")
    st.link_button(f"📱 WhatsApp {ADMIN_CONTACT}", f"https://wa.me/{ADMIN_CONTACT}")

def display_locked_response(locked, download_name="notes"):
    """Display + Download button"""
    if not locked: return
    st.success(f"✅ Topic Verified: {locked.detected_topic}")
    
    full_text = build_text_from_locked(locked)
    
    for step in locked.pedagogical_steps:
        with st.container(border=True):
            st.markdown(f"### Step {step.step_number}: {step.curriculum_level}")
            st.markdown(f"**Concept:** {step.core_concept}")
            st.markdown(f"**Explanation:** {step.explanation}")
            if step.python_calculation_code.strip():
                st.code(step.python_calculation_code, language="python")
                res = execute_deterministic_math(step.python_calculation_code)
                st.success(f"**Exact Calculation Result:** `{res}`")
    
    st.markdown("---")
    st.markdown("### Final Answer")
    st.latex(locked.final_answer_formula)
    
    # DOWNLOAD BUTTON ADDED TO ALL LOCKED RESPONSES
    pdf = create_pdf(full_text, f"{download_name}.pdf")
    st.download_button("📥 Download Notes as PDF", pdf, f"{download_name}.pdf", use_container_width=True)

def ask_bar(client, subject, class_level, mode, default_label="Ask a follow-up question"):
    st.markdown("---")
    user_q = st.text_input(f"💬 {default_label}", key=f"ask_{mode}_{subject}")
    if st.button("Ask AI", key=f"ask_btn_{mode}_{subject}") and user_q:
        with st.spinner("AI is answering..."):
            locked = get_locked_ai_response(client, user_q, subject, class_level)
            if locked and locked.is_within_syllabus:
                display_locked_response(locked, f"followup_{subject}")
            else:
                st.error("Query outside S1-S6 NCDC 2026")

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
                st.markdown("### 🟢 FREE PACKAGE")
                st.write("Access: S1 - S4")
                free_password = st.text_input("Enter FREE Key", type="password", key="free_login")
                if st.button("Login FREE", type="secondary", use_container_width=True):
                    if free_password.upper().strip() == FREE_PASS:
                        st.session_state.authenticated = True; st.session_state.license = "FREE"; st.rerun()
                    else: st.error("Invalid FREE Key")
        with col2:
            with st.container(border=True):
                st.markdown("### ⭐ GOLD PACKAGE")
                st.write("Access: S1 - S6 + All Features")
                gold_password = st.text_input("Enter GOLD Key", type="password", key="gold_login")
                if st.button("Login GOLD", type="primary", use_container_width=True):
                    if gold_password.upper().strip() == GOLD_PASS:
                        st.session_state.authenticated = True; st.session_state.license = "GOLD"; st.rerun()
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
        show_gold_upgrade()
        st.stop()

    # ALL 15 MODES WITH DOWNLOAD
    if mode == "Locked Calculation Mode":
        st.header("🔐 Locked Calculation Mode - No Hallucinations")
        query = st.text_area("Enter your Physics/Chem/Math question")
        if st.button("Solve with Python Lock", type="primary") and query:
            with st.spinner("Running Anti-Hallucination Engine..."):
                locked = get_locked_ai_response(client, query, subject, class_level)
            if not locked or not locked.is_within_syllabus:
                st.error("❌ Blocked: Query outside S1-S6 NCDC 2026 curriculum")
            else:
                display_locked_response(locked, f"calc_{subject}_{class_level}")
                log_activity(f"LockedCalc: {query}", subject, class_level)

    elif mode == "Smart Search":
        st.header("🧠 Smart Search")
        query = st.text_input("Ask any question")
        if st.button("Search") and query:
            locked = get_locked_ai_response(client, f"Explain {query} with theory and examples", subject, class_level)
            if locked: display_locked_response(locked, f"search_{subject}")
        ask_bar(client, subject, class_level, mode)

    elif mode == "Theory Mode":
        st.header("📘 Theory Mode")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Generate Notes"):
            with st.spinner("Generating notes..."):
                locked = get_locked_ai_response(client, f"Detailed NCDC 2026 notes on {topic} with definitions and examples", subject, class_level)
                if locked: display_locked_response(locked, f"theory_{topic}")
        ask_bar(client, subject, class_level, mode)

    elif mode == "Lesson Preparation":
        st.header("👨‍🏫 Lesson Preparation")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Generate Lesson Plan + AoI"):
            locked = get_locked_ai_response(client, f"40min competency-based lesson plan with AoI for {topic} in Ugandan context", subject, class_level)
            if locked:
                display_locked_response(locked, f"lesson_{topic}")
        ask_bar(client, subject, class_level, mode)

    elif mode == "Diagrams Library":
        st.header("🖼️ Diagrams Library")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        path = find_diagram(topic)
        st.info(f"Found {len(list(DIAGRAMS_DIR.glob('*.png')))} images in assets folder")
        if path: 
            st.image(path, caption=topic, use_container_width=True); st.success(f"✅ Match: {Path(path).name}")
            # DOWNLOAD IMAGE OPTION
            with open(path, "rb") as f:
                st.download_button("📥 Download Diagram", f, Path(path).name, use_container_width=True)
        else: st.warning(f"No diagram found for '{topic}'")
        ask_bar(client, subject, class_level, mode)

    elif mode == "Practicals Lab":
        st.header("🧪 Practicals Lab")
        practicals_list = get_practicals(subject, class_level)
        if practicals_list:
            practical = st.selectbox("Select Practical", [p["name"] for p in practicals_list])
            if st.button("Show Practical"):
                p = next(p for p in practicals_list if p["name"] == practical)
                text = f"Practical: {p['name']}\nAim: {p['aim']}\nMaterials: {p['materials']}\nProcedure: {p['procedure']}"
                with st.container(border=True):
                    st.subheader(p["name"])
                    st.markdown(f"**Aim:** {p['aim']}")
                    st.markdown(f"**Materials/Apparatus:** {p['materials']}")
                    st.markdown(f"**Procedure:** {p['procedure']}")
                    st.info("Follow NCDC 2026 safety guidelines")
                # DOWNLOAD PRACTICAL PDF
                pdf = create_pdf(text, f"practical_{p['name']}.pdf")
                st.download_button("📥 Download Practical as PDF", pdf, f"practical_{p['name']}.pdf", use_container_width=True)
                if p["graph"]:
                    if st.button("Generate Sample Graph"):
                        x = np.linspace(0,10,20); y = x * random.uniform(0.5,2) + np.random.randn(20)*2
                        fig = generate_graph(pd.DataFrame({"X":x,"Y":y}), "X","Y", p["graph"])
                        st.plotly_chart(fig, use_container_width=True)
                log_activity(f"Practical: {practical}", subject, class_level)
        else:
            st.info(f"No practicals defined for {subject} {class_level}")
        ask_bar(client, subject, class_level, mode)

    elif mode == "Quiz Mode":
        st.header("📝 Quiz Mode")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Generate 5 MCQs"):
            locked = get_locked_ai_response(client, f"Generate 5 competency-based MCQs with answers and explanations on {topic}", subject, class_level)
            if locked: display_locked_response(locked, f"quiz_{topic}")
        ask_bar(client, subject, class_level, mode)

    elif mode == "Graph Generator":
        st.header("📊 Graph Generator")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Generate Sample Data Graph"):
            x = np.linspace(0,10,20); y = x**2 * 0.5 + np.random.randn(20)*5
            df = pd.DataFrame({"X":x,"Y":y})
            fig = generate_graph(df, "X","Y", topic)
            st.plotly_chart(fig, use_container_width=True)
            st.download_button("📥 Download Graph Data CSV", df.to_csv(index=False).encode(), "graph_data.csv")

    elif mode == "Explainer Mode":
        st.header("🎓 Explainer Mode")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Explain Topic"):
            locked = get_locked_ai_response(client, f"Explain {topic} with 3 worked examples and common mistakes", subject, class_level)
            if locked: display_locked_response(locked, f"explainer_{topic}")

    elif mode == "Bulk Revision Generator":
        st.header("📚 Bulk Revision Generator")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Generate"):
            locked = get_locked_ai_response(client, f"Generate 20 revision questions with answers on {topic}", subject, class_level)
            if locked: display_locked_response(locked, f"revision_{topic}")

    elif mode == "Predict Papers":
        st.header("📄 Predict Papers")
        if st.button("Predict Full Subject"):
            locked = get_locked_ai_response(client, f"Predict UCE/UACE competency-based questions for {class_level} {subject}", subject, class_level)
            if locked: display_locked_response(locked, f"predict_{subject}_{class_level}")

    elif mode == "Voice Chat":
        st.header("🎤 Voice Chat")
        query = st.text_input("Type your question")
        if st.button("Send") and query: ask_bar(client, subject, class_level, mode)

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
        if st.button("Generate AoI"):
            locked = get_locked_ai_response(client, f"Generate Competency-based Activity of Integration for {topic} with Ugandan scenario", subject, class_level)
            if locked: display_locked_response(locked, f"aoi_{topic}")

if __name__ == "__main__":
    main()
