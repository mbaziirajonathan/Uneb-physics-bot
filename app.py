import streamlit as st
import os, io, json, re, time, ast, hashlib
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from groq import Groq
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Rectangle, Ellipse, FancyArrow, Arrow
from matplotlib.lines import Line2D # ADDED FOR ARROWS IF AI MESSES UP

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 PRO", page_icon="📚", layout="wide")

### LOAD 2 API KEYS ###
try:
    GROQ_API_KEY_1 = st.secrets["GROQ_API_KEY_1"]
    GROQ_API_KEY_2 = st.secrets["GROQ_API_KEY_2"]
    STUDENT_PASSWORD = st.secrets["STUDENT_PASSWORD"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("Set GROQ_API_KEY_1, GROQ_API_KEY_2, STUDENT_PASSWORD, ADMIN_PASSWORD in Streamlit secrets")
    st.stop()

if "current_key" not in st.session_state: st.session_state.current_key = 1
if "key1_tokens" not in st.session_state: st.session_state.key1_tokens = 0
if "key2_tokens" not in st.session_state: st.session_state.key2_tokens = 0

def get_client():
    key = GROQ_API_KEY_1 if st.session_state.current_key == 1 else GROQ_API_KEY_2
    return Groq(api_key=key)

client = get_client()
LOG_FILE = "usage_log.json"
QBANK_FILE = "qbank.json"
AI_QBANK_FILE = "ai_qbank.json"
STUDENTS_FILE = "students.json"
CONTACT = "256751040731"

### DUAL ENGINE V4.0.3 ###
AI_MODEL_SMART = "llama-3.3-70b-versatile"
AI_MODEL_INSTANT = "llama-3.1-8b-instant"
st.sidebar.success(f"⚠️ DIGITAL UNEB TUTOR 2026 PRO V4.0.3\nSAFE EXEC ENGINE\nKey Active: {st.session_state.current_key}\n📞 {CONTACT}")
st.sidebar.metric("Key 1 Est Tokens", st.session_state.key1_tokens)
st.sidebar.metric("Key 2 Est Tokens", st.session_state.key2_tokens)

WEIGHTS_SMART = {"labels": 8, "arrows": 6, "dpi": 300}
WEIGHTS_INSTANT = {"labels": 4, "arrows": 3, "dpi": 200}

SYSTEM_SMART = f"""You are DIGITAL UNEB TUTOR 2026 PRO. Senior NCDC Examiner.
CRITICAL: OUTPUT ONLY THE BODY OF THE CODE. DO NOT WRITE IMPORTS. DO NOT WRITE 'import'.
YOU WILL GET plt, np, Circle, Rectangle, Ellipse, FancyArrow ALREADY IMPORTED.
WEIGHTS: labels={WEIGHTS_SMART['labels']}, arrows={WEIGHTS_SMART['arrows']}, dpi={WEIGHTS_SMART['dpi']}
RULES:
1. Start with: fig, ax = plt.subplots(figsize=(9,9))
2. ax.set_xlim(0,1); ax.set_ylim(0,1)
3. Draw using Circle, Rectangle, Ellipse, FancyArrow
4. {WEIGHTS_SMART['labels']} labels with bbox=dict(boxstyle='round', facecolor='yellow')
5. End with: plt.savefig('diagram.png', dpi={WEIGHTS_SMART['dpi']}, bbox_inches='tight'); plt.close(); ax.axis('off')
"""

SYSTEM_INSTANT = f"""OUTPUT ONLY CODE BODY. NO IMPORTS. NO 'import' WORD.
YOU ALREADY HAVE: plt, np, Circle, Rectangle, Ellipse, FancyArrow
WEIGHTS: labels={WEIGHTS_INSTANT['labels']}, arrows={WEIGHTS_INSTANT['arrows']}, dpi={WEIGHTS_INSTANT['dpi']}
End with plt.savefig and plt.close"""

### DATABASES ###
def load_db(file): return json.load(open(file,"r", encoding="utf-8")) if os.path.exists(file) else []
def save_db(file,data): json.dump(data,open(file,"w", encoding="utf-8"),indent=2)
if "students_db" not in st.session_state: st.session_state.students_db = load_db(STUDENTS_FILE)

UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Number Bases"], "S2": ["Angles"], "S3": ["Vectors"], "S4": ["Circle Geometry"], "S5": ["Differentiation"], "S6": ["Mechanics"]},
    "Physics": {"S1": ["Forces"], "S2": ["Electricity I"], "S3": ["Magnetism"], "S4": ["Electronics"], "S5": ["Optics"], "S6": ["Electric Fields"]},
    "Chemistry": {"S1": ["Atoms"], "S2": ["Acids Alkalis"], "S3": ["Bonding"], "S4": ["REDOX"], "S5": ["Kinetics"], "S6": ["Electrochemistry"]},
    "Biology": {"S1": ["Cells"], "S2": ["Respiration"], "S3": ["Genetics I"], "S4": ["Photosynthesis"], "S5": ["Cell Biology"], "S6": ["Hormones"]},
    "ICT": {"S1": ["Computer Basics"],"S2": ["Word Processing"],"S3": ["Spreadsheets"],"S4": ["Internet"],"S5": ["Programming Python"],"S6": ["Web Design"]},
    "Geography": {"S1": ["Map Reading"],"S2": ["Climate"],"S3": ["Rivers"],"S4": ["Population"],"S5": ["Industries"],"S6": ["GIS"]},
    "History": {"S1": ["Early Man"],"S2": ["Kingdoms"],"S3": ["Colonialism"],"S4": ["Independence"],"S5": ["World Wars"],"S6": ["Cold War"]},
    "CRE": {"S1": ["Creation"],"S2": ["Prophets"],"S3": ["Jesus"],"S4": ["Church"],"S5": ["Ethics"],"S6": ["Comparative"]},
    "IRE": {"S1": ["Tawheed"],"S2": ["Prophets"],"S3": ["Quran"],"S4": ["Hadith"],"S5": ["Fiqh"],"S6": ["History"]},
    "Literature": {"S1": ["Poetry"],"S2": ["Drama"],"S3": ["Novel"],"S4": ["Prose"],"S5": ["Shakespeare"],"S6": ["African Lit"]},
    "Commerce": {"S1": ["Business"],"S2": ["Trade"],"S3": ["Banking"],"S4": ["Insurance"],"S5": ["Marketing"],"S6": ["Entrepreneurship"]},
    "Economics": {"S1": ["Scarcity"],"S2": ["Demand"],"S3": ["Money"],"S4": ["Trade"],"S5": ["National Income"],"S6": ["Development"]},
    "Agriculture": {"S1": ["Soil"],"S2": ["Crops"],"S3": ["Livestock"],"S4": ["Tools"],"S5": ["Records"],"S6": ["Agribusiness"]},
    "Art": {"S1": ["Drawing"],"S2": ["Painting"],"S3": ["Sculpture"],"S4": ["Design"],"S5": ["Craft"],"S6": ["Art History"]}
}

PRACTICAL_DATABASE = {
    "Physics": {"S1-S4": {"Ohm's Law": {"objective": "Verify Ohm's Law", "apparatus": "Cell", "procedure": "Connect", "questions": ["State law"], "safety": "No short"}}},
    "Chemistry": {"S1-S4": {"Titration": {"objective": "Determine NaOH", "apparatus": "Burette", "procedure": "Titrate", "questions": ["Calculate"], "safety": "Acid"}}},
    "Biology": {"S1-S4": {"Microscope": {"objective": "Observe cells", "apparatus": "Microscope", "procedure": "Focus", "questions": ["Function"], "safety": "Clean"}}}
}

### CORE FUNCTIONS ###
def load_logs(): return json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []
def save_log(entry): logs = load_logs(); logs.append(entry); json.dump(logs, open(LOG_FILE,"w"))
def log_activity(user_type, action, details): save_log({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user_type, "action": action, "details": details})
def create_pdf(content, title):
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); p.setFont("Helvetica-Bold", 14); p.drawString(50,800,title); y=770; p.setFont("Helvetica", 10)
    for i,line in enumerate(content.split('\n')[:80]): p.drawString(50,y-(i*14),line[:95])
    p.save(); buffer.seek(0); return buffer

### KEY ROTATION + CACHE ###
@st.cache_data(ttl=3600, show_spinner=False)
def cached_groq_call(prompt_hash, user_prompt, mode, key_id):
    return call_groq_dual_raw(user_prompt, mode, key_id)

def switch_key():
    st.session_state.current_key = 2 if st.session_state.current_key == 1 else 1
    st.warning(f"🔄 Rate limit hit. Switched to API Key {st.session_state.current_key}")
    return get_client()

def estimate_tokens(text): return len(text) // 4

def call_groq_dual_raw(user_prompt, mode="Smart", key_id=1):
    global client
    system = SYSTEM_SMART if mode=="Smart" else SYSTEM_INSTANT
    model = AI_MODEL_SMART if mode=="Smart" else AI_MODEL_INSTANT
    tokens = 3500 if mode=="Smart" else 1200
    try:
        res = client.chat.completions.create(model=model, messages=[{"role":"system","content":system},{"role":"user","content":user_prompt}], max_tokens=tokens, temperature=0.01)
        used = estimate_tokens(user_prompt + res.choices[0].message.content)
        if key_id == 1: st.session_state.key1_tokens += used
        else: st.session_state.key2_tokens += used
        return res.choices[0].message.content
    except Exception as e:
        if "rate_limit_exceeded" in str(e):
            client = switch_key()
            return call_groq_dual_raw(user_prompt, mode, st.session_state.current_key)
        return f"GROQ_ERROR: {e}"

def call_groq_dual(user_prompt, mode="Smart"):
    prompt_hash = hashlib.md5((user_prompt + mode).encode()).hexdigest()
    return cached_groq_call(prompt_hash, user_prompt, mode, st.session_state.current_key)

### FIX: STRIP ALL IMPORTS FROM AI ###
def sanitize_ai_code(raw):
    if not raw or "GROQ_ERROR" in raw: return raw, False
    code = re.sub(r'```python|```', '', raw).strip()
    # DELETE ANY LINE STARTING WITH IMPORT
    code = "\n".join([line for line in code.split('\n') if not line.strip().startswith('import')])
    # WRAP IN SAFE HEADER
    header = "fig, ax = plt.subplots(figsize=(9,9))\nax.set_xlim(0,1)\nax.set_ylim(0,1)\n"
    code = header + code
    try: ast.parse(code); return code, True
    except SyntaxError as e: return f"SyntaxError line {e.lineno}: {e.msg}", False

def auto_render_pixel_diagram(topic, subject, level, mode="Smart"):
    weights = WEIGHTS_SMART if mode=="Smart" else WEIGHTS_INSTANT
    st.info(f"🤖 Running {mode} Engine | Labels:{weights['labels']} DPI:{weights['dpi']} | Key:{st.session_state.current_key}")

    prompt = f"Task: Draw and label '{topic}' for {level} {subject}. Use Circle Rectangle Ellipse FancyArrow. {weights['labels']} labels."
    raw_code = call_groq_dual(prompt, mode)
    if "GROQ_ERROR" in raw_code: return raw_code

    code, is_valid = sanitize_ai_code(raw_code)
    if not is_valid: return f"ERROR: {code}"

    with st.expander(f"View {mode} AI Generated Code Body"):
        st.code(code, language="python")

    try:
        plt.close('all')
        # SAFE GLOBALS - ALL LIBS PRELOADED
        safe_globals = {
            "plt": plt, "np": np,
            "Circle": Circle, "Rectangle": Rectangle, "Ellipse": Ellipse,
            "FancyArrow": FancyArrow, "Arrow": Arrow, "Line2D": Line2D
        }
        exec(code, {"__builtins__": {}}, safe_globals) # NO IMPORTS ALLOWED
        return "diagram.png" if os.path.exists("diagram.png") else "ERROR: File not saved"
    except Exception as e:
        return f"ERROR: Runtime {type(e).__name__}: {e}"

def generate_practical(subject, level, prac_name):
    level_group = "S1-S4" if int(level[1]) <= 4 else "S5-S6"
    data = PRACTICAL_DATABASE.get(subject,{}).get(level_group,{}).get(prac_name,{})
    if not data: return "Practical not found"
    return call_groq_dual(f"Expand to UNEB report: {data} for {subject} {level}", "Smart")

def display_with_pdf(content, name):
    st.markdown(content)
    for f in re.findall(r'\$(.*?)\$', content): st.latex(f)
    pdf = create_pdf(content, name); st.download_button("📥 Download PDF", pdf, f"{name}.pdf", key=f"dl_{name}_{time.time()}")

### PORTALS ###
def show_student_portal():
    st.header("📚 Student Portal - S1 to S6 - NCDC PRO MODE")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tab1, tab2, tab3 = st.tabs(["🔍 Smart Search + Solver", "📖 Learn Topic", "🎨 AI Diagram Generator"])

    with tab1:
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="search_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="search_level")
        ask_q = st.text_area("Ask any question / Solve any problem")
        if st.button("Ask AI Brain", type="primary") and ask_q:
            log_activity("Student", "Ask Question", ask_q)
            ans = call_groq_dual(f"Use Chain of Thought: {ask_q} for {level} {subject}", "Smart")
            display_with_pdf(ans, "Answer")

    with tab2:
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="learn_subj")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="learn_level")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject2][level2], key="learn_topic")
        mode = st.radio("Mode", ["📖 Theory", "🧠 AOI", "🧪 Practicals Lab", "📝 UNEB Quiz Mode", "📚 Bulk Revision"])

        if mode == "📖 Theory" and st.button("Teach Me"):
            raw = call_groq_dual(f"Teach {topic2} step by step for {level2} {subject2}", "Smart")
            display_with_pdf(raw, "Theory")
        elif mode == "🧠 AOI" and st.button("Generate AOI"):
            aoi = call_groq_dual(f"Generate NCDC Activity of Integration for {level2} {subject2} topic: {topic2}", "Smart")
            display_with_pdf(aoi, "AOI")
        elif mode == "🧪 Practicals Lab":
            prac_list = list(PRACTICAL_DATABASE.get(subject2,{}).get("S1-S4",{}).keys())
            prac = st.selectbox("Select Practical", prac_list if prac_list else ["None"])
            if st.button("Generate Practical"):
                report = generate_practical(subject2,level2,prac)
                display_with_pdf(report, "Practical")
        elif mode == "📝 UNEB Quiz Mode" and st.button("Generate Quiz"):
            quiz = call_groq_dual(f"Generate 10 UNEB questions on {topic2} for {level2} {subject2}", "Smart")
            display_with_pdf(quiz, "Quiz")
        elif mode == "📚 Bulk Revision" and st.button("Generate Revision"):
            rev = call_groq_dual(f"Generate full revision + 20 questions for {topic2} {level2} {subject2}", "Smart")
            display_with_pdf(rev, "Revision")

    with tab3:
        st.header("🎨 AI Diagram Generator - V4.0.3 SAFE EXEC")
        subject3 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="svg_subj")
        level3 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="svg_level")
        topic3 = st.text_input("Describe Diagram:", "Draw and label Human Heart S4 Biology")
        diagram_mode = st.radio("Choose Engine", ["HD Pixel [AI Smart 70B - 8 Labels]", "HD Pixel [AI Instant 8B - 4 Labels]"])

        if st.button("Generate Diagram", type="primary"):
            log_activity("Student", "Generate Diagram", topic3)
            m = "Smart" if "Smart" in diagram_mode else "Instant"
            img_path = auto_render_pixel_diagram(topic3, subject3, level3, m)
            if "ERROR" in str(img_path): st.error(f"Rendering failed: {img_path}")
            else:
                st.success(f"✅ Rendered with: {AI_MODEL_SMART if m=='Smart' else AI_MODEL_INSTANT} on Key {st.session_state.current_key}")
                st.image(img_path, caption=f"HD: {topic3}", use_container_width=True)
                with open(img_path, "rb") as file: st.download_button("📥 Download HD PNG", file, f"{topic3}.png")

def show_admin_portal():
    st.header("🏫 Admin Portal - V4.0.3")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tab1, tab2, tab3 = st.tabs(["📊 Analytics", "📖 Curriculum Manager", "🤖 AI QBank Generator"])
    with tab1:
        logs = load_logs()
        st.metric("Total Logs", len(logs))
        if logs: st.dataframe(pd.DataFrame(logs))
    with tab2:
        st.subheader("NCDC Curriculum")
        subj = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)])
        st.write(UNEB_CURRICULUM_MAP[subj][level])
    with tab3:
        st.subheader("AI Generate QBank")
        subj = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="qgen_subj")
        lvl = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="qgen_lvl")
        if st.button("Generate 20 Questions"):
            res = call_groq_dual(f"Generate 20 UNEB MCQ for {lvl} {subj}. Return JSON", "Smart")
            try: save_db(AI_QBANK_FILE, json.loads(res)); st.success("Saved")
            except: st.error("Bad JSON"); st.code(res)

st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO - V4.0.3 SAFE EXEC")
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"])
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    if user_type == "Student" and password == STUDENT_PASSWORD: st.session_state["role"] = "Student"; st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD: st.session_state["role"] = "Admin"; st.rerun()
    elif password: st.sidebar.error("Wrong password")

if st.session_state.get("role") == "Admin": show_admin_portal()
elif st.session_state.get("role") == "Student": show_student_portal()
else: st.info("Please login to continue")
