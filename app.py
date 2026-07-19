import streamlit as st
import os, io, pytz, random, json, sympy as sp, re, difflib
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
# ANTI-HALLUCINATION LOCK SYSTEM - DEBUGGED
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
3. Variable Declaration: In python_calculation_code, FIRST line MUST be `var1, var2 = sp.symbols('var1 var2')`. Never use undefined variables like W, F, v.
4. Full Explanation: In `explanation` field, give full theory, definitions, procedure in clear English. Do NOT leave it empty.
5. Program of Thought: Each step must have valid python code.
6. Boundaries: If query is outside S1-S6 NCDC 2026, set `is_within_syllabus` = false and halt.
7. OUTPUT FORMAT: You MUST output ONLY valid JSON. No text before or after. No markdown. All 4 fields required.
"""

def execute_deterministic_math(code_string: str) -> str:
    local_env = {"sp": sp, "symbols": sp.symbols, "math": __import__('math'), "sqrt": sp.sqrt, "pi": sp.pi, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "log": sp.log, "exp": sp.exp}
    try:
        if "__import__" in code_string or "os." in code_string or "sys." in code_string or "open(" in code_string:
            return "Execution Blocked: Insecure code detected."
        common_symbols = "g, m, v, u, a, t, s, F, W, P, E, k, n, i, r, R, V, I, Q, T, L, f, lambda, theta, rho"
        exec(f"{common_symbols} = sp.symbols('{common_symbols}')", {}, local_env)
        exec(f"{code_string}", {}, local_env)
        result = local_env.get("result", "No 'result' variable set")
        if hasattr(result, 'free_symbols'):
            return str(sp.simplify(result).evalf(4))
        return str(result)
    except Exception as e:
        return f"Execution Error: {str(e)}. Hint: Check variable definitions."

def clean_json(raw):
    raw = raw.strip()
    raw = re.sub(r"```json", "", raw)
    raw = re.sub(r"```", "", raw)
    return raw.strip()

def get_locked_ai_response(client, user_query, subject, class_level):
    full_prompt = f"Subject: {subject}. Class: {class_level}. NCDC 2026 Syllabus. Query: {user_query}. Remember to define all variables in python_calculation_code."
    for attempt in range(2):
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": full_prompt}],
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=2048
        )
        raw = resp.choices[0].message.content
        raw = clean_json(raw)
        try:
            return LockedCurriculumResponse.model_validate_json(raw)
        except Exception as e:
            if attempt == 0:
                full_prompt = f"ERROR: Previous response was invalid JSON or missing fields. MUST include detected_topic, is_within_syllabus, pedagogical_steps, final_answer_formula. Subject: {subject}. Class: {class_level}. Query: {user_query}"
                continue
            else:
                return LockedCurriculumResponse(
                    detected_topic=f"{subject} - {user_query[:50]}",
                    is_within_syllabus=True,
                    pedagogical_steps=[CurriculumStep(
                        step_number=1,
                        curriculum_level=f"{class_level} {subject}",
                        core_concept="System Notice",
                        explanation=f"AI response parsing failed. Please rephrase. Error details: {str(e)}",
                        python_calculation_code=""
                    )],
                    final_answer_formula="N/A"
                )

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

@st.cache_data
def get_all_diagrams():
    if not DIAGRAMS_DIR.exists(): return []
    return [p for p in DIAGRAMS_DIR.glob("*.png")]

def find_diagram(topic):
    """FUZZY MATCH: Finds best image for topic even if names don't match exactly"""
    all_pngs = get_all_diagrams()
    if not all_pngs: return None

    topic_clean = topic.lower().replace(" ", "_").replace("/", "_").replace(":", "").replace("-", "_")
    topic_words = [w for w in topic_clean.split("_") if len(w) > 2]

    # 1. Exact match
    for png_path in all_pngs:
        if topic_clean == png_path.stem.lower():
            return str(png_path)

    # 2. Substring match
    for png_path in all_pngs:
        if topic_clean in png_path.name.lower():
            return str(png_path)

    # 3. FUZZY WORD MATCH: Score by how many topic words are in filename
    best_score = 0
    best_match = None
    for png_path in all_pngs:
        png_name = png_path.name.lower()
        score = sum(1 for word in topic_words if word in png_name)
        if score > best_score:
            best_score = score
            best_match = png_path

    # 4. difflib fallback for close names like "mechanics" vs "mechanical_properties"
    if best_score == 0:
        png_names = [p.stem.lower() for p in all_pngs]
        close = difflib.get_close_matches(topic_clean, png_names, n=1, cutoff=0.6)
        if close:
            idx = png_names.index(close[0])
            best_match = all_pngs[idx]

    return str(best_match) if best_match else None

def log_activity(activity, subject, class_level):
    if "activities_log" not in st.session_state: st.session_state.activities_log = []
    st.session_state.activities_log.append({"time": datetime.now(UGANDA_TZ).strftime("%Y-%m-%d %H:%M:%S"), "activity": activity, "subject": subject, "class": class_level, "license": st.session_state.license})

def show_gold_upgrade():
    st.warning("🔒 **UPGRADE TO GOLD PACKAGE**")
    st.info("Unlock S5 & S6 + All Subjects + Predict Papers + Bulk Generator")
    st.markdown(f"**WhatsApp/Call: {ADMIN_CONTACT}**")
    st.link_button(f"📱 WhatsApp {ADMIN_CONTACT}", f"https://wa.me/{ADMIN_CONTACT}")

def display_locked_response(locked, download_name="notes"):
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
        path = find_diagram(topic) # NOW FUZZY
        st.info(f"Found {len(get_all_diagrams())} images in assets folder")
        if path:
            try: # SAFE LOAD TO PREVENT CRASH
                st.image(path, caption=topic, use_container_width=True)
                st.success(f"✅ Best Match: {Path(path).name}")
                with open(path, "rb") as f:
                    st.download_button("📥 Download Diagram", f, Path(path).name, use_container_width=True)
            except Exception as e:
                st.error(f"Could not load image: {e}")
        else:
            st.warning(f"No diagram found for '{topic}'. Try keywords like 'lens', 'circuit', 'cell'")
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
