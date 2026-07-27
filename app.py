import streamlit as st
import os, io, json, re, ast, difflib, time, math
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import base64
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
from docx import Document

# LAZY IMPORTS - Load only after login
np = pd = px = go = sp = plt = Axes3D = patches = Arc = Polygon = Circle = Rectangle = FancyArrow = Image = Groq = RateLimitError = None

LOG_FILE = "usage_log.json"
CONTACT = "256751040731"
AI_MODEL_LONG = "llama-3.3-70b-versatile"
AI_MODEL_FAST = "llama-3.1-8b-instant"
FIG_COUNTER = {"count": 0}

def load_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                logs = json.load(f)
                return logs[-500:]
            except: return []
    return []

def save_log(entry):
    logs = load_logs()
    logs.append(entry)
    with open(LOG_FILE, "w") as f: json.dump(logs, f, indent=2)

def log_activity(user_type, action, details):
    entry = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user_type, "action": action, "details": details}
    save_log(entry)

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
    global np, pd, px, go, sp, plt, Axes3D, patches, Arc, Polygon, Circle, Rectangle, FancyArrow, Image, Groq, RateLimitError
    import numpy as np
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    import sympy as sp
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.patches as patches
    from matplotlib.patches import Arc, Polygon, Circle, Rectangle, FancyArrow
    from PIL import Image
    from groq import Groq, RateLimitError

@st.cache_resource
def get_client():
    load_heavy_libs()
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

# ============ NCDC DIAGRAM ENGINE ============
def get_fig_label():
    FIG_COUNTER["count"] += 1
    return f"Fig. 1({chr(96+FIG_COUNTER['count'])})"

def draw_2d_shape(shape_type, params={}):
    load_heavy_libs()
    fig, ax = plt.subplots(figsize=(4,4)); ax.set_aspect('equal'); ax.axis('off')
    if shape_type == "triangle":
        pts = [[0,0], [4,0], [2,3]]; poly = Polygon(pts, closed=True, edgecolor='black', facecolor='none', linewidth=2); ax.add_patch(poly)
        for i, label in enumerate(["A","B","C"]): ax.text(pts[i][0]-0.2, pts[i][1]-0.2, label, fontsize=12)
    elif shape_type == "rectangle": w, h = params.get("w",6), params.get("h",4); rect = Rectangle((0,0), w, h, edgecolor='black', facecolor='none', linewidth=2); ax.add_patch(rect)
    elif shape_type == "circle": r = params.get("r",2); circ = Circle((2,2), r, edgecolor='black', facecolor='none', linewidth=2); ax.add_patch(circ)
    elif shape_type == "angle":
        deg = params.get("deg",60); ax.plot([0,4],[0,0],'k-', lw=2); ax.plot([0,4*math.cos(math.radians(deg))],[0,4*math.sin(math.radians(deg))],'k-', lw=2)
        arc = Arc((0,0), 1.5, 1.5, theta1=0, theta2=deg, color='black', linewidth=1.5); ax.add_patch(arc); ax.text(0.8,0.2,f"{deg}°")
    ax.set_xlim(-1,6); ax.set_ylim(-1,5)
    path = f"/tmp/{shape_type}_{int(time.time())}.png"; plt.savefig(path, dpi=150, bbox_inches='tight', pad_inches=0.1); plt.close(); return path

def detect_and_draw_diagram(text, subject, level):
    if subject!= "Mathematics": return []
    load_heavy_libs(); text = text.lower(); diagrams = []
    if "triangle" in text: diagrams.append(("triangle", draw_2d_shape("triangle")))
    elif "rectangle" in text: diagrams.append(("rectangle", draw_2d_shape("rectangle")))
    elif "circle" in text: diagrams.append(("circle", draw_2d_shape("circle")))
    elif "angle" in text: diagrams.append(("angle", draw_2d_shape("angle", {"deg":60})))
    return diagrams

# ============ RESTORED UNEB ITEM SYSTEM PROMPT ============
SYSTEM_PROMPT = """
You are DIGITAL UNEB EXAMINER 2026, the #1 Senior NCDC Uganda Examiner + Smart AI Tutor for ALL NCDC subjects S1-S6.

### RULE 1: SMART TUTOR MODE - DEFAULT
If the user asks: "define, explain, solve, summarize, what is, how does"
-> Answer directly with chain of thought, examples, and Ugandan context. DO NOT generate questions.

### RULE 2: UNEB EXAMINER MODE - ONLY WHEN REQUESTED
If the user says: "set questions, generate test, 10 items, exam, quiz"
-> YOU MUST SWITCH TO STRICT UNEB ITEM FORMAT BELOW:

### ABSOLUTE UNEB ITEM LOCKS
1. CURRICULUM LOCK: ONLY NCDC 2026 S1-S6. Use Ugandan contexts: districts, rivers, markets, farms.
2. OUTPUT FORMAT LOCK: PLAIN MARKDOWN TEXT. BAN JSON, { } [ ]
3. ITEM FORMAT LOCK: MUST use this exact structure:
ITEM 1.
[SCENARIO PARAGRAPH 1: 3-5 sentences. Realistic Ugandan problem. Name people, places, data]
[SCENARIO PARAGRAPH 2: Add more details]

TASK:
As a [Subject] learner;
i) [First competence task] (X scores)
ii) [Second competence task] (X scores)
iii)[Third competence task] (X scores)

### MANDATORY MARKING GUIDE - 3 STEPS FOR EVERY ITEM
**ITEM 1(i) Solution**
Step 1: Identification and Explanation of the Core Principle
Step 2: Practical Application and Evidence. For Math/Physics: Show FORMULA → SUBSTITUTION → ANSWER with SI units.
Step 3: Final Conclusion / Actionable Recommendation

4. QUANTITY RULE: When asked for questions, generate AT LEAST 10 ITEMS.
5. DIAGRAM LOCK: Draw diagrams ONLY for Mathematics. Describe for others.
6. LANGUAGE LOCK: Remind: Use SI units, Show working, Label diagrams, Answer scientifically.
"""

# ============ RESTORED FULL NCDC DATABASE ============
UNEB_CURRICULUM_MAP = {
    "Mathematics": {
        "S1": ["Number Bases", "Integers", "Fractions, Percentages and Decimals", "Cartesian Coordinates", "Geometric Construction", "Data Collection and Representation"],
        "S2": ["Patterns and Sequences", "Bearings", "Angle Properties", "Algebra I", "Business Arithmetic I", "Time and Time Tables", "Mapping and Relations"],
        "S3": ["Business Arithmetic II", "Quadratic Equations", "Matrices", "Probability", "Vectors", "Trigonometry I", "Mensuration"],
        "S4": ["Functions", "Three-Dimensional Geometry", "Statistics", "Linear Programming", "Trigonometry II", "Calculus Introduction"],
        "S5": ["Calculus: Differentiation", "Calculus: Integration", "Circular Measure", "Binomial Expansion", "Complex Numbers", "Sequences and Series"],
        "S6": ["Differential Equations", "Mechanics: Kinematics and Dynamics", "Probability Distributions", "Linear Programming Advanced", "Further Calculus", "Vectors in 3D"]
    },
    "Physics": {
        "S1": ["Introduction to Physics", "Measurement", "Forces and Their Effects", "Work, Energy and Power", "Pressure in Fluids", "Simple Machines"],
        "S2": ["Light: Reflection and Refraction", "Thermal Physics", "Static Electricity", "Current Electricity I", "Waves I"],
        "S3": ["Current Electricity II", "Magnetism", "Waves II: Sound", "Mechanics Continued", "Specific Heat Capacity"],
        "S4": ["Electromagnetism", "Electronics", "Modern Physics", "Nuclear Processes", "A.C Theory", "Astrophysics"],
        "S5": ["Mechanics: Motion and Dynamics", "Gravitation", "Thermal Physics Advanced", "Waves III: Interference and Diffraction", "Optics", "Fluid Mechanics"],
        "S6": ["Electric Fields", "Magnetic Fields", "Electromagnetic Induction", "Quantum Physics", "Radioactivity", "Solid State and Electronics"]
    },
    "Chemistry": {
        "S1": ["Chemistry and Society", "Experimental Chemistry", "States of Matter", "Temporary and Permanent Changes", "Mixtures, Elements and Compounds", "Air", "Water", "Rocks and Minerals"],
        "S2": ["Acids and Alkalis", "Salts", "The Periodic Table", "Carbon in the Environment", "Reactivity Series", "Metals and Non-Metals"],
        "S3": ["Structure and Bonding", "Stoichiometry and Mole Concept", "Fossil Fuels", "Properties and Structures of Substances", "Chemical Reactions", "Rates of Reaction"],
        "S4": ["REDOX Reactions", "Industrial Processes", "Trends in the Periodic Table", "Thermochemistry", "Consumable Chemicals", "Organic Chemistry II", "Nuclear Processes"],
        "S5": ["Atomic Structure Advanced", "Chemical Energetics", "Chemical Kinetics", "Equilibrium II", "Organic Chemistry III", "Acids, Bases and Buffers"],
        "S6": ["Electrochemistry Advanced", "Transition Metals and Complexes", "Organic Synthesis", "Analytical Chemistry", "Environmental Chemistry", "Polymers"]
    },
    "Biology": {
        "S1": ["Introduction to Biology", "Cells and the Microscope", "Classification of Living Things", "Insects", "Flowering Plants", "Ecosystems"],
        "S2": ["Soil Composition and Properties", "Soil Erosion and Conservation", "Nitrogen Cycle", "Nutrition in Plants", "Nutrition in Animals", "Transport in Living Things"],
        "S3": ["Transport in Plants and Animals", "Respiration and Gas Exchange", "Excretion and Homeostasis", "Cell Division", "Reproduction in Plants", "DNA and Genetics I"],
        "S4": ["Coordination and Receptors", "Locomotion", "Growth and Development", "Genetics and Inheritance", "Ecology", "Evolution", "Environmental Conservation"],
        "S5": ["Cell Biology", "Enzymes", "Transport in Plants Advanced", "Gas Exchange Systems", "Nutrition in Humans Advanced", "Respiration Cellular"],
        "S6": ["Hormonal Control and Feedback", "Coordination: Nervous System Advanced", "Population Ecology", "Biotechnology", "Genetic Engineering", "Immunity and Disease"]
    }
}

OTHER_SUBJECTS = ["Geography", "History", "Literature in English", "CRE", "IRE", "Agriculture", "Entrepreneurship", "ICT", "Art and Design", "Music", "French", "Kiswahili", "Luganda", "Economics", "Commerce", "Technical Drawing", "Food and Nutrition"]
for subj in OTHER_SUBJECTS:
    UNEB_CURRICULUM_MAP[subj] = {f"S{i}": ["Topic 1", "Topic 2", "Topic 3", "Topic 4", "Topic 5"] for i in range(1,7)}

PRACTICAL_TOPICS = {
    "Mathematics": {"S1": ["Geometric Construction: Bisecting lines and angles"],"S2": ["Bearings and Scale Drawing", "Construction of Triangles"],"S3": ["Construction of Quadrilaterals", "Loci"],"S4": ["Building 3D Geometric Models", "Trigonometric Ratios using scale drawing"],"S5": ["Drawing Graphs of Functions", "Construction of Binomial Expansions"],"S6": ["Vectors in 3D Models", "Mechanics Practical: Motion"]},
    "Physics": {"S1": ["Measurement using Vernier Calipers", "Simple Pendulum"],"S2": ["Reflection using Plane Mirrors", "Specific Heat Capacity"],"S3": ["Series and Parallel Circuits", "Mapping Magnetic Fields", "Speed of Sound"],"S4": ["Electronics: Diode Characteristics", "A.C Circuit", "Radioactivity Simulation"],"S5": ["Projectile Motion", "Interference of Light", "Optics: Lens Practical"],"S6": ["Electric Field Mapping", "Electromagnetic Induction", "Quantum Physics Simulation"]},
    "Chemistry": {"S1": ["Filtration and Evaporation", "Testing for Gases"],"S2": ["Preparation of Salts", "Reactivity Series"],"S3": ["Rates of Reaction", "Mole Concept Practical"],"S4": ["REDOX Titration", "Organic Chemistry Tests"],"S5": ["Chemical Kinetics Experiment", "Buffer Preparation"],"S6": ["Electrochemistry: Electrolysis", "Qualitative Analysis"]},
    "Biology": {"S1": ["Using Light Microscope", "Classification of Specimens"],"S2": ["Testing for Food Nutrients", "Soil Analysis"],"S3": ["Dissection of a Flower", "Cell Division using Onion Root"],"S4": ["Genetics: Dihybrid Cross", "Ecology: Quadrats"],"S5": ["Enzyme Activity", "Osmosis in Plant Cells"],"S6": ["DNA Extraction", "Population Sampling Techniques"]}
}
AOI_FRAMEWORK = {"S1": "Community Problem", "S2": "Local Industry", "S3": "National Issue", "S4": "Global Challenge", "S5": "Research", "S6": "Professional"}

def add_to_memory(role, content):
    if "chat_memory" not in st.session_state: st.session_state.chat_memory = []
    st.session_state.chat_memory.append({"role": role, "content": content, "time": datetime.now().strftime("%H:%M")})

def get_memory_context():
    if "chat_memory" not in st.session_state: return ""
    last_5 = st.session_state.chat_memory[-5:]
    return "Previous conversation:\n" + "\n".join([f"{m['role']}: {m['content']}" for m in last_5]) + "\n\n"

def add_performance(subject, topic, score):
    today = datetime.now().strftime("%Y-%m-%d")
    if "performance" not in st.session_state: st.session_state.performance = {}
    if today not in st.session_state.performance: st.session_state.performance[today] = []
    st.session_state.performance[today].append({"subject":subject, "topic":topic, "score":score})

def create_pdf(content, title):
    load_heavy_libs()
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); p.setFont("Helvetica-Bold", 14); p.drawString(50,800,title); y=770; p.setFont("Helvetica", 10)
    for line in content.split('\n')[:80]: p.drawString(50,y,line[:95]); y-=14;
    p.save(); buffer.seek(0); return buffer

def read_uploaded_file(uploaded_file):
    if uploaded_file is None: return ""
    if uploaded_file.type == "application/pdf": return "PDF uploaded. Content noted."
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file); return "\n".join([para.text for para in doc.paragraphs])
    else: return uploaded_file.getvalue().decode("utf-8")

def display_with_pdf(content, name, subject, level):
    FIG_COUNTER["count"] = 0
    st.markdown(content)
    formulas = re.findall(r'\$(.*?)\$', content)
    if formulas: st.markdown("### 🔑 Key Formula"); [st.latex(f) for f in formulas]
    diagrams = detect_and_draw_diagram(content, subject, level)
    for shape_name, diagram_path in diagrams:
        fig_label = get_fig_label()
        st.image(diagram_path, caption=f"{fig_label}: {shape_name.title()} Diagram")
    pdf = create_pdf(content, name); st.download_button("📥 Download PDF", pdf, f"{name}.pdf", key=f"dl_{name}")

def call_groq_safe(client, messages, model, max_tokens=4000, temperature=0.7):
    for attempt in range(3):
        try: res = client.chat.completions.create(model=model, messages=messages, max_tokens=max_tokens, temperature=temperature); return res.choices[0].message.content
        except RateLimitError:
            if attempt < 2: time.sleep(2 ** attempt)
            else: res = client.chat.completions.create(model=AI_MODEL_FAST, messages=messages, max_tokens=2000); return res.choices[0].message.content
        except Exception as e: return f"AI Error: {e}"

def get_ai_response(client, user_query, subject, class_level, topic, mode, lab_mode, context=""):
    memory = get_memory_context(); model = AI_MODEL_LONG if not lab_mode else AI_MODEL_FAST
    system = SYSTEM_PROMPT
    prompt = f"{memory}{context}\n\nLevel: {class_level}, Subject: {subject}, Topic: {topic}\nUser Request: {user_query}\n\nFollow RULE 1 or RULE 2 above depending on user intent. Use Ugandan context."
    answer = call_groq_safe(client, [{"role":"system","content":system},{"role":"user","content":prompt}], model, max_tokens=4000 if model==AI_MODEL_LONG else 2000, temperature=0.3)
    add_to_memory("User", user_query); add_to_memory("AI", answer); log_activity(st.session_state.user_type, "AI Query", f"{subject} {class_level} {topic}")
    return answer

def generate_lesson_plan(client, subject, level, topic, duration):
    prompt = f"Generate a detailed NCDC {duration} minute lesson plan for {level} {subject} on {topic}. Include: Title, Objective, Materials, Introduction, Presentation, Activities, Assessment, Homework. Use Ugandan context."
    return call_groq_safe(client, [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt}], AI_MODEL_LONG, max_tokens=3000)

def generate_report_card(client, student_data):
    prompt = f"Generate a professional NCDC Report Card for student: {student_data}. Include scores table, total, average, grade, remarks, teacher comment, principal comment."
    return call_groq_safe(client, [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt}], AI_MODEL_LONG, max_tokens=2000)

def generate_test(client, subject, level, topic, num_questions):
    prompt = f"Generate {num_questions} UNEB standard test questions for {level} {subject} on {topic}. MUST USE STRICT ITEM/TASK/SCENARIO FORMAT with 3-step marking guide and Uganda scenarios."
    return call_groq_safe(client, [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt}], AI_MODEL_LONG, max_tokens=4000)

def generate_practical(client, subject, level, topic, lab_mode):
    model = AI_MODEL_LONG if not lab_mode else AI_MODEL_FAST
    prompt = f"Generate FULL detailed NCDC {level} {subject} practical for: {topic} in UNEB ITEM FORMAT. Must include: AIM, APPARATUS, PROCEDURE, DATA TABLE, OBSERVATIONS, CONCLUSION, SAFETY."
    return call_groq_safe(client, [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt}], model, max_tokens=3000, temperature=0.5)

def generate_bulk_revision(client, subject, level, lab_mode):
    model = AI_MODEL_LONG if not lab_mode else AI_MODEL_FAST
    topics = ', '.join(UNEB_CURRICULUM_MAP[subject][level])
    prompt = f"Generate 20 ITEMS in STRICT UNEB ITEM/TASK/SCENARIO FORMAT for {level} {subject}: {topics}. Each ITEM must have Uganda scenario and 3-step answer."
    return call_groq_safe(client, [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt}], model, max_tokens=4000)

def generate_mock_paper(client, subject, level, paper, lab_mode):
    model = AI_MODEL_LONG if not lab_mode else AI_MODEL_FAST
    prompts = {"P1":f"Generate 40 ITEMS in STRICT UNEB ITEM/TASK/SCENARIO FORMAT for {subject} {level}.","P2":f"Generate 10 ITEMS Theory for {subject} {level} in STRICT ITEM FORMAT.","P3":f"Generate 5 ITEMS Practical for {subject} {level} in STRICT ITEM FORMAT."}
    return call_groq_safe(client, [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompts[paper]}], model, max_tokens=4000, temperature=0.3)

def admin_dashboard():
    load_heavy_libs()
    st.title("👨‍💼 ADMIN DASHBOARD"); logs = load_logs()
    if not logs: st.warning("No activity yet"); return
    df = pd.DataFrame(logs); col1,col2,col3 = st.columns(3)
    col1.metric("Total Activities", len(df)); col2.metric("Today", len(df[df['timestamp'].str.startswith(datetime.now().strftime("%Y-%m-%d"))])); col3.metric("Users", df['user'].nunique())
    st.subheader("Live Activity Feed"); st.dataframe(df.tail(50), use_container_width=True)

def main():
    if not check_password(): st.stop()
    st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026", page_icon="📚", layout="wide")
    client = get_client()

    if "chat_memory" not in st.session_state: st.session_state.chat_memory = []
    if "performance" not in st.session_state: st.session_state.performance = {}
    st.markdown("<h1 style='text-align:center; background:gold; color:black; padding:10px'>📚 DIGITAL UNEB TUTOR 2026 - ALL NCDC SUBJECTS S1-S6</h1>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Smart Search", "📖 Learn Topic", "🧪 Teacher Tools", "👨‍💼 Admin"])

    with st.sidebar:
        st.markdown(f"<div style='background:#2b2b2b; color:white; padding:12px; border-left:4px solid #ffc107; border-radius:5px; margin-bottom:15px'><b>⚠️ DISCLAIMER</b><br>For learning support only.<br><b>📞 Support:</b> {CONTACT}</div>", unsafe_allow_html=True)
        st.success(f"Logged in as: {st.session_state.user_type}")
        lab_mode = st.toggle("🚀 FAST MODE", value=True)
        if st.button("Logout"): st.session_state.clear(); st.rerun(); return
        if st.button("🗑️ Clear Memory"): st.session_state.chat_memory = []; st.rerun()

    with tab1:
        st.header("🔍 Smart Search - Ask Anything")
        uploaded_file = st.file_uploader("📎 Upload document to ask about", type=["pdf","docx","txt"], key="search_upload")
        file_context = read_uploaded_file(uploaded_file)
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="search_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="search_level")
        ask_q = st.text_area("Ask any question: define photosynthesis, solve 2x+3=7, set 10 questions on vectors...")
        if st.button("Ask AI Brain", type="primary"):
            with st.spinner("Thinking..."):
                ans = get_ai_response(client, ask_q, subject, level, "General", "Search", lab_mode, context=file_context)
                display_with_pdf(ans, f"Answer_{subject}", subject, level)

    with tab2:
        st.header("📖 Learn Topic + Old Features")
        uploaded_file2 = st.file_uploader("📎 Upload notes", type=["pdf","docx","txt"], key="learn_upload")
        file_context2 = read_uploaded_file(uploaded_file2)
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="learn_subj")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="learn_level")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject2][level2], key="learn_topic")
        mode = st.radio("Mode", ["📖 Theory", "🧠 AOI", "🧪 Practicals Lab", "📝 Quiz Mode", "📚 Bulk Revision", "📄 Mock Exams"])

        if mode == "📖 Theory":
            if st.button("Generate Notes + 10 ITEMS", type="primary"): raw = get_ai_response(client, f"Teach {topic2} in detail then generate 10 ITEMS in STRICT UNEB ITEM/TASK/SCENARIO FORMAT", subject2, level2, topic2, "Theory", lab_mode, context=file_context2); display_with_pdf(raw, f"Theory_{topic2}", subject2, level2); add_performance(subject2, topic2, 8)
        elif mode == "🧠 AOI":
            research_q = st.text_area("Describe a real-life problem")
            if st.button("Generate AOI Project"): raw = get_ai_response(client, f"Design AOI for {level2} {subject2} on {topic2} in ITEM FORMAT. Problem: {research_q}", subject2, level2, topic2, "AOI", lab_mode); display_with_pdf(raw, f"AOI_{topic2}", subject2, level2)
        elif mode == "🧪 Practicals Lab":
            prac = st.selectbox("Select NCDC Practical", PRACTICAL_TOPICS.get(subject2,{}).get(level2,["No practicals for this topic"]))
            if st.button("Generate Full Practical"): report = generate_practical(client,subject2,level2,prac, lab_mode); display_with_pdf(report, f"Practical_{prac}", subject2, level2); add_performance(subject2, prac, 9)
        elif mode == "📝 Quiz Mode":
            if st.button("Generate 10 ITEMS + Answers"): quiz = get_ai_response(client, f"Generate 10 ITEMS in STRICT UNEB ITEM/TASK/SCENARIO FORMAT for {topic2} with 3-step answers", subject2, level2, topic2, "Quiz", lab_mode); display_with_pdf(quiz, f"Quiz_{topic2}", subject2, level2); add_performance(subject2, topic2, 7)
        elif mode == "📚 Bulk Revision":
            if st.button("Generate 20 ITEMS", type="primary"): bulk = generate_bulk_revision(client, subject2, level2, lab_mode); display_with_pdf(bulk, f"BulkRevision_{subject2}_{level2}", subject2, level2)
        elif mode == "📄 Mock Exams":
            col1,col2,col3 = st.columns(3)
            with col1:
                if st.button("Generate P1"): mock = generate_mock_paper(client, subject2, level2, "P1", lab_mode); display_with_pdf(mock, "MockP1", subject2, level2)
            with col2:
                if st.button("Generate P2"): mock = generate_mock_paper(client, subject2, level2, "P2", lab_mode); display_with_pdf(mock, "MockP2", subject2, level2)
            with col3:
                if st.button("Generate P3"): mock = generate_mock_paper(client, subject2, level2, "P3", lab_mode); display_with_pdf(mock, "MockP3", subject2, level2)

    with tab3:
        st.header("🧪 Teacher Tools")
        uploaded_file3 = st.file_uploader("📎 Upload class list or syllabus", type=["pdf","docx","txt"], key="teacher_upload")
        file_context3 = read_uploaded_file(uploaded_file3)
        tool = st.radio("Select Tool", ["Lesson Plan Generator", "Report Card Generator", "Test + Marksheet Generator"])

        if tool == "Lesson Plan Generator":
            subject3 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="lp_subj")
            level3 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="lp_level")
            topic3 = st.text_input("Topic")
            duration = st.number_input("Duration minutes", 40, 120, 40)
            if st.button("Generate Lesson Plan"):
                lp = generate_lesson_plan(client, subject3, level3, topic3, duration)
                display_with_pdf(lp, f"LessonPlan_{topic3}", subject3, level3)

        elif tool == "Report Card Generator":
            student_data = st.text_area("Paste student data: Name, Scores: Math 80, Phy 75...")
            if st.button("Generate Report Card"):
                rc = generate_report_card(client, student_data + "\n" + file_context3)
                display_with_pdf(rc, "ReportCard", "General", "S1")

        elif tool == "Test + Marksheet Generator":
            subject4 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="test_subj")
            level4 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="test_level")
            topic4 = st.text_input("Topic for test")
            num_q = st.slider("Number of Questions", 5, 50, 10)
            if st.button("Generate Test"):
                test = generate_test(client, subject4, level4, topic4, num_q)
                display_with_pdf(test, f"Test_{topic4}", subject4, level4)

    with tab4:
        if st.session_state.user_type == "Admin": admin_dashboard()
        else: st.warning("Admin access only")

if __name__ == "__main__": main()
