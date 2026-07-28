import streamlit as st
import os, io, json, re, time, math
from datetime import datetime
import pytz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS

# LAZY IMPORTS
np = pd = px = go = sp = plt = Axes3D = patches = Polygon = Circle = Rectangle = Image = Groq = RateLimitError = None

LOG_FILE = "usage_log.json"
CONTACT = "256751040731"
AI_MODEL_LONG = "llama-3.3-70b-versatile"
AI_MODEL_FAST = "llama-3.1-8b-instant"
FIG_COUNTER = {"count": 0}
UG_TZ = pytz.timezone("Africa/Kampala")

def load_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try: return json.load(f)[-500:]
            except: return []
    return []

def save_log(entry):
    logs = load_logs(); logs.append(entry)
    with open(LOG_FILE, "w") as f: json.dump(logs, f, indent=2)

def check_password():
    APP_PW = st.secrets.get("APP_PASSWORD", "UNEB2026")
    ADMIN_PW = st.secrets.get("ADMIN_PASSWORD", "ADMIN256")
    def password_entered():
        pw = st.session_state["password"]
        if pw == APP_PW: st.session_state["user_type"] = "Student"; st.session_state["password_correct"] = True
        elif pw == ADMIN_PW: st.session_state["user_type"] = "Admin"; st.session_state["password_correct"] = True
        else: st.session_state["password_correct"] = False
        if "password" in st.session_state: del st.session_state["password"]
    if "password_correct" not in st.session_state:
        st.title("🔒 DIGITAL UNEB TUTOR 2026 - Login")
        st.text_input("Enter Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔒 DIGITAL UNEB TUTOR 2026 - Login")
        st.text_input("Enter Password", type="password", on_change=password_entered, key="password")
        st.error("😞 Password incorrect")
        return False
    else: return True

def load_heavy_libs():
    global np, pd, px, go, sp, plt, Axes3D, patches, Polygon, Circle, Rectangle, Image, Groq, RateLimitError
    import numpy as np; import pandas as pd; import plotly.express as px; import plotly.graph_objects as go
    import sympy as sp; import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D; import matplotlib.patches as patches
    from matplotlib.patches import Polygon, Circle, Rectangle
    from PIL import Image
    from groq import Groq, RateLimitError

@st.cache_resource
def get_client():
    load_heavy_libs()
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

# ============ DIAGRAM ENGINE ============
def get_fig_label(): FIG_COUNTER["count"] += 1; return f"Fig. 1({chr(96+FIG_COUNTER['count'])})"
def draw_2d_shape(shape_type):
    load_heavy_libs(); fig, ax = plt.subplots(figsize=(4,4)); ax.set_aspect('equal'); ax.axis('off')
    if shape_type == "triangle":
        pts = [[0,0], [4,0], [2,3]]; poly = Polygon(pts, closed=True, edgecolor='black', facecolor='none', linewidth=2); ax.add_patch(poly)
        for i, label in enumerate(["A","B","C"]): ax.text(pts[i][0]-0.2, pts[i][1]-0.2, label, fontsize=12)
    path = f"/tmp/{shape_type}_{int(time.time())}.png"; plt.savefig(path, dpi=150, bbox_inches='tight'); plt.close(); return path
def detect_and_draw_diagram(text, subject):
    if subject!= "Mathematics": return []; load_heavy_libs(); text = text.lower(); diagrams = []
    if "triangle" in text: diagrams.append(("triangle", draw_2d_shape("triangle"))); return diagrams

# ============ HARD LOCKED SYSTEM PROMPTS ============
SMART_SYSTEM = """You are DIGITAL UNEB TUTOR 2026. You are a SMART AI like ChatGPT and Meta AI.

FORBIDDEN: You are NOT allowed to generate "ITEM 1. TASK: " format.
FORBIDDEN: You are NOT allowed to make up questions.

YOUR JOB: Answer the question directly. Explain, Define, Solve, Compare.
Use examples. Use Ugandan context. Use chain of thought. Be conversational.
Example Q: "What are functions in math"
Example A: "A function is a relationship where each input has exactly one output. Think of a boda fare: Distance -> Price. For every 1km input, you get 1 price output. Formula: f(x) = 2x + 1000"
"""

EXAMINER_SYSTEM = """You are DIGITAL UNEB EXAMINER 2026.

YOUR ONLY JOB: Generate UNEB ITEM/TASK/SCENARIO questions when explicitly asked.
MUST USE THIS FORMAT:
ITEM 1.
[Ugandan Scenario 2 paragraphs]

TASK:
As a [Subject] learner;
i)... (X marks)
ii)... (X marks)
iii)... (X marks)

SOLUTION:
**ITEM 1(i) Solution**
Step 1:...
Step 2: FORMULA → SUBSTITUTION → ANSWER
Step 3: Conclusion
"""

UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Number Bases", "Integers"], "S2": ["Algebra I", "Bearings"], "S3": ["Quadratic Equations", "Vectors"], "S4": ["Functions", "Statistics"], "S5": ["Calculus", "Complex Numbers"], "S6": ["Differential Equations", "Mechanics"]},
    "Physics": {"S1": ["Measurement", "Forces"], "S2": ["Light", "Electricity"], "S3": ["Magnetism", "Waves"], "S4": ["Electronics", "Modern Physics"], "S5": ["Mechanics", "Optics"], "S6": ["Electric Fields", "Quantum Physics"]},
    "Chemistry": {"S1": ["States of Matter", "Air"], "S2": ["Acids", "Periodic Table"], "S3": ["Bonding", "Mole Concept"], "S4": ["REDOX", "Organic"], "S5": ["Kinetics", "Equilibrium"], "S6": ["Electrochemistry", "Polymers"]},
    "Biology": {"S1": ["Cells", "Ecosystems"], "S2": ["Nutrition", "Transport"], "S3": ["Respiration", "Genetics"], "S4": ["Ecology", "Evolution"], "S5": ["Enzymes", "Cell Biology"], "S6": ["Biotechnology", "Immunity"]}
}
OTHER_SUBJECTS = ["Geography", "History", "Literature in English", "CRE", "IRE", "Agriculture", "Entrepreneurship", "ICT", "Economics", "Commerce"]
for subj in OTHER_SUBJECTS: UNEB_CURRICULUM_MAP[subj] = {f"S{i}": [f"Topic {j}" for j in range(1,6)] for i in range(1,7)}

PRACTICAL_TOPICS = {
    "Mathematics": {"S4": ["Building 3D Geometric Models"]},
    "Physics": {"S3": ["Series and Parallel Circuits"]},
    "Chemistry": {"S3": ["Rates of Reaction"]},
    "Biology": {"S3": ["Dissection of a Flower"]}
}
AOI_FRAMEWORK = {"S1": "Community Problem", "S2": "Local Industry", "S3": "National Issue", "S4": "Global Challenge", "S5": "Research", "S6": "Professional"}

def add_to_memory(role, content):
    if "chat_memory" not in st.session_state: st.session_state.chat_memory = []
    st.session_state.chat_memory.append({"role": role, "content": content})

def create_pdf(content, title):
    load_heavy_libs(); buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("Helvetica-Bold", 14); p.drawString(50,800,title); y=770; p.setFont("Helvetica", 10)
    for line in content.split('\n')[:80]: p.drawString(50,y,line[:95]); y-=14;
    p.save(); buffer.seek(0); return buffer

def read_uploaded_file(uploaded_file):
    if uploaded_file is None: return ""
    if uploaded_file.type == "text/plain": return uploaded_file.getvalue().decode("utf-8", errors='ignore')
    return ""

def display_with_pdf(content, name, subject):
    FIG_COUNTER["count"] = 0; st.markdown(content)
    formulas = re.findall(r'\$(.*?)\$', content)
    if formulas: st.markdown("### 🔑 Key Formula"); [st.latex(f) for f in formulas]
    diagrams = detect_and_draw_diagram(content, subject)
    for shape_name, diagram_path in diagrams: st.image(diagram_path, caption=f"{get_fig_label()}: {shape_name.title()}")
    pdf = create_pdf(content, name); st.download_button("📥 Download PDF", pdf, f"{name}.pdf", key=f"dl_{name}_{time.time()}")

def call_groq(client, system_prompt, user_prompt, model):
    try:
        res = client.chat.completions.create(model=model, messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}], max_tokens=4000, temperature=0.7);
        return res.choices[0].message.content
    except RateLimitError:
        res = client.chat.completions.create(model=AI_MODEL_FAST, messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}], max_tokens=2000);
        return res.choices[0].message.content
    except Exception as e: return f"AI Error: {e}"

# ============ 2 SEPARATE FUNCTIONS ============
def ask_smart_brain(client, user_query, subject, level, context=""):
    model = AI_MODEL_LONG
    prompt = f"Context: {context}\nLevel: {level}\nSubject: {subject}\nUser Question: {user_query}\n\nAnswer directly now."
    answer = call_groq(client, SMART_SYSTEM, prompt, model)
    add_to_memory("User", user_query); add_to_memory("AI", answer)
    return answer

def generate_exam_items(client, user_query, subject, level):
    model = AI_MODEL_LONG
    prompt = f"Generate UNEB ITEMS for: Level: {level}, Subject: {subject}, Request: {user_query}"
    return call_groq(client, EXAMINER_SYSTEM, prompt, model)

def generate_lesson_plan(client, subject, level, topic, duration):
    prompt = f"Generate NCDC {duration} min lesson plan for {level} {subject} on {topic}."
    return call_groq(client, SMART_SYSTEM, prompt, AI_MODEL_LONG)

def admin_dashboard():
    load_heavy_libs(); st.title("👨‍💼 ADMIN DASHBOARD"); logs = load_logs()
    if not logs: st.warning("No activity yet"); return
    df = pd.DataFrame(logs); st.dataframe(df.tail(50))

def main():
    if not check_password(): st.stop()
    st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026", layout="wide")
    client = get_client()
    if "chat_memory" not in st.session_state: st.session_state.chat_memory = []

    st.markdown("<h1 style='text-align:center; background:gold; color:black; padding:10px'>📚 DIGITAL UNEB TUTOR 2026</h1>", unsafe_allow_html=True)

    # ============ FIXED: 4 TABS INCLUDING TEACHER TOOLS ============
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Smart Search", "📖 Learn Topic", "🧪 Teacher Tools", "👨‍💼 Admin"])

    with st.sidebar:
        st.success(f"Logged in as: {st.session_state.user_type}")
        lab_mode = st.toggle("🚀 FAST MODE", value=False)
        if st.button("Logout"): st.session_state.clear(); st.rerun()
        if st.button("🗑️ Clear Memory"): st.session_state.chat_memory = []; st.rerun()

    with tab1:
        st.header("🔍 Smart Search - Ask Anything Like ChatGPT")
        uploaded_file = st.file_uploader("📎 Upload.txt file", type=["txt"], key="search_upload")
        file_context = read_uploaded_file(uploaded_file)
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)])
        ask_q = st.text_area("Ask: define, explain, solve, compare...")
        if st.button("Ask AI Brain", type="primary"):
            ans = ask_smart_brain(client, ask_q, subject, level, file_context)
            display_with_pdf(ans, f"Answer", subject)

    with tab2:
        st.header("📖 Learn Topic")
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="s2")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="l2")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject2][level2])
        mode = st.radio("Mode", ["📖 Theory", "🧠 AOI", "🧪 Practicals Lab", "📝 Generate Test"])

        if mode == "📖 Theory":
            if st.button("Teach Me This Topic", type="primary"):
                ans = ask_smart_brain(client, f"Teach me {topic2} in detail with examples", subject2, level2)
                display_with_pdf(ans, f"Theory", subject2)
        elif mode == "📝 Generate Test":
            if st.button("Generate 10 UNEB ITEMS"):
                test = generate_exam_items(client, f"Generate 10 questions on {topic2}", subject2, level2)
                display_with_pdf(test, "Test", subject2)

    with tab3: # ============ TEACHER TOOLS TAB RESTORED ============
        st.header("🧪 Teacher Tools")
        tool = st.radio("Select Tool", ["Lesson Plan Generator", "Report Card Generator", "Test Generator"])
        if tool == "Lesson Plan Generator":
            s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="s3")
            l = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="l3")
            t = st.text_input("Topic"); d = st.number_input("Minutes", 40, 120, 40)
            if st.button("Generate Lesson Plan"):
                lp = generate_lesson_plan(client, s, l, t, d); display_with_pdf(lp, "LessonPlan", s)
        elif tool == "Report Card Generator":
            data = st.text_area("Paste: Name, Math 80, Eng 70...")
            if st.button("Generate Report Card"):
                rc = call_groq(client, SMART_SYSTEM, f"Generate NCDC Report Card for: {data}", AI_MODEL_LONG); display_with_pdf(rc, "ReportCard", "General")
        elif tool == "Test Generator":
            s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="s4")
            l = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="l4")
            t = st.text_input("Topic"); n = st.slider("Questions", 5, 20, 10)
            if st.button("Generate Test"):
                test = generate_exam_items(client, f"Generate {n} questions on {t}", s, l); display_with_pdf(test, "Test", s)

    with tab4:
        if st.session_state.user_type == "Admin": admin_dashboard()
        else: st.warning("Admin access only")

if __name__ == "__main__": main()
