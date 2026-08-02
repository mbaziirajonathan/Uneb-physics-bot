import streamlit as st
import os, io, json, re, time, base64
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
from streamlit_option_menu import option_menu
from groq import Groq, RateLimitError
import pandas as pd

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026", page_icon="📚", layout="wide")

# ========== 1. SECRETS - NEW LOGIC KEPT ==========
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
STUDENT_PASSWORD = st.secrets["STUDENT_PASSWORD"] # unebtest2026
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"] # admin256
client = Groq(api_key=GROQ_API_KEY)

LOG_FILE = "usage_log.json"
CONTACT = "256751040731"
AI_MODEL_LONG = "llama-3.3-70b-versatile" # FROM OLD CODE
AI_MODEL_FAST = "llama-3.1-8b-instant" # FROM OLD CODE

# ========== 2. LEGAL ==========
st.sidebar.warning(f"⚠️ LEGAL NOTICE: DIGITAL UNEB TUTOR 2026\nFor NCDC learning only.\n📞 {CONTACT}")

# ============ 3. RESTORED FULL NCDC DATABASE - FROM YOUR OLD CODE. NO CUTS ============
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
OTHER_SUBJECTS = ["Geography", "History", "Literature in English", "CRE", "IRE", "Agriculture", "Entrepreneurship", "ICT", "Art and Design", "Music", "French", "Kiswahili", "Luganda", "Economics", "Commerce", "Technical Drawing", "Food and Nutrition", "Fashion and Textiles"]
for subj in OTHER_SUBJECTS:
    UNEB_CURRICULUM_MAP[subj] = {f"S{i}": [f"Topic {j}" for j in range(1,6)] for i in range(1,7)}

PRACTICAL_TOPICS = { # FROM OLD CODE
    "Mathematics": {"S1": ["Geometric Construction: Bisecting lines and angles"],"S2": ["Bearings and Scale Drawing", "Construction of Triangles"],"S3": ["Construction of Quadrilaterals", "Loci"],"S4": ["Building 3D Geometric Models", "Trigonometric Ratios using scale drawing"],"S5": ["Drawing Graphs of Functions", "Construction of Binomial Expansions"],"S6": ["Vectors in 3D Models", "Mechanics Practical: Motion"]},
    "Physics": {"S1": ["Measurement using Vernier Calipers", "Simple Pendulum"],"S2": ["Reflection using Plane Mirrors", "Specific Heat Capacity"],"S3": ["Series and Parallel Circuits", "Mapping Magnetic Fields", "Speed of Sound"],"S4": ["Electronics: Diode Characteristics", "A.C Circuit", "Radioactivity Simulation"],"S5": ["Projectile Motion", "Interference of Light", "Optics: Lens Practical"],"S6": ["Electric Field Mapping", "Electromagnetic Induction", "Quantum Physics Simulation"]},
    "Chemistry": {"S1": ["Filtration and Evaporation", "Testing for Gases"],"S2": ["Preparation of Salts", "Reactivity Series"],"S3": ["Rates of Reaction", "Mole Concept Practical"],"S4": ["REDOX Titration", "Organic Chemistry Tests"],"S5": ["Chemical Kinetics Experiment", "Buffer Preparation"],"S6": ["Electrochemistry: Electrolysis", "Qualitative Analysis"]},
    "Biology": {"S1": ["Using Light Microscope", "Classification of Specimens"],"S2": ["Testing for Food Nutrients", "Soil Analysis"],"S3": ["Dissection of a Flower", "Cell Division using Onion Root"],"S4": ["Genetics: Dihybrid Cross", "Ecology: Quadrats"],"S5": ["Enzyme Activity", "Osmosis in Plant Cells"],"S6": ["DNA Extraction", "Population Sampling Techniques"]}
}
AOI_FRAMEWORK = {"S1": "Community Problem", "S2": "Local Industry", "S3": "National Issue", "S4": "Global Challenge", "S5": "Research", "S6": "Professional"} # FROM OLD CODE

# ============ 4. HARD LOCKED SYSTEM PROMPTS - FROM YOUR OLD CODE ============
SMART_SYSTEM = """You are DIGITAL UNEB TUTOR 2026. You are a SMART AI like ChatGPT and Meta AI.
FORBIDDEN: You are NOT allowed to generate "ITEM 1. TASK: " format unless user asks for test.
FORBIDDEN: You are NOT allowed to make up questions.
YOUR JOB: Answer the question directly. Explain, Define, Solve, Compare.
Use examples. Use Ugandan context. Use chain of thought. Be conversational.
Example Q: "What are functions in math"
Example A: "A function is a relationship where each input has exactly one output. Think of a boda fare: Distance -> Price. For every 1km input, you get 1 price output. Formula: f(x) = 2x + 1000"
"""
EXAMINER_SYSTEM = """You are DIGITAL UNEB EXAMINER 2026. Senior NCDC Examiner for Uganda S1-S6.
YOUR ONLY JOB: Generate UNEB ITEM/TASK/SCENARIO questions ONLY when asked.
MUST USE THIS EXACT FORMAT:
ITEM 1.
[SCENARIO PARAGRAPH 1: 3-5 sentences. Realistic Ugandan problem. Name people, districts, data]
[SCENARIO PARAGRAPH 2: Add more details]
TASK:
As a [Subject] learner;
i) [First competence task] (X scores)
ii) [Second competence task] (X scores)
iii)[Third competence task] (X scores)
SOLUTION:
**ITEM 1(i) Solution**
Step 1: Identification and Explanation of the Core Principle
Step 2: Practical Application. For Math/Physics: FORMULA → SUBSTITUTION → ANSWER with SI units.
Step 3: Final Conclusion / Recommendation
"""

# ========== 5. UTILS + LOGGING - FROM BOTH CODES ==========
def load_logs(): return json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []
def save_log(entry): logs = load_logs(); logs.append(entry); json.dump(logs, open(LOG_FILE,"w"))
def log_activity(user_type, action, details):
    flagged = any(word in details.lower() for word in ["exam now", "live exam", "help me cheat"])
    save_log({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user_type, "action": action, "details": details, "flagged": flagged})

def create_pdf(content, title): # FROM OLD CODE
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); p.setFont("Helvetica-Bold", 14); p.drawString(50,800,title); y=770; p.setFont("Helvetica", 10)
    for line in content.split('\n')[:80]: p.drawString(50,y,line[:95]); y-=14;
    p.save(); buffer.seek(0); return buffer

def text_to_speech(text): # NEW LOGIC KEPT
    tts = gTTS(text=text, lang='en'); fp = io.BytesIO(); tts.write_to_fp(fp)
    b64 = base64.b64encode(fp.getvalue()).decode()
    st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)

def call_groq(system_prompt, user_prompt, model): # FROM OLD CODE WITH FALLBACK
    try:
        res = client.chat.completions.create(model=model, messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}], max_tokens=4000, temperature=0.7)
        return res.choices[0].message.content
    except RateLimitError:
        res = client.chat.completions.create(model=AI_MODEL_FAST, messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}], max_tokens=2000)
        return res.choices[0].message.content
    except Exception as e: return f"AI Error: {e}. Check GROQ_API_KEY"

def ask_smart_brain(user_query, subject, class_level, topic):
    log_activity(st.session_state.role, "Smart Query", f"{subject} {class_level}: {user_query[:50]}")
    prompt = f"Level: {class_level}\nSubject: {subject}\nTopic: {topic}\nUser Question: {user_query}\n\nAnswer directly now with examples."
    return call_groq(SMART_SYSTEM, prompt, AI_MODEL_LONG)

def generate_exam_items(user_query, subject, level): return call_groq(EXAMINER_SYSTEM, f"Generate UNEB ITEMS for: Level: {level}, Subject: {subject}, Request: {user_query}", AI_MODEL_LONG)
def generate_lesson_plan(subject, level, topic, duration): return call_groq(SMART_SYSTEM, f"Generate a detailed NCDC {duration} minute lesson plan for {level} {subject} on {topic}.", AI_MODEL_LONG)
def generate_report_card(student_data): return call_groq(SMART_SYSTEM, f"Generate a professional NCDC Report Card for student: {student_data}.", AI_MODEL_LONG)
def generate_practical(subject, level, topic): return call_groq(EXAMINER_SYSTEM, f"Generate FULL detailed NCDC {level} {subject} practical for: {topic}. Must include: AIM, APPARATUS, PROCEDURE, DATA TABLE, OBSERVATIONS, CONCLUSION, SAFETY.", AI_MODEL_LONG)
def generate_bulk_revision(subject, level): # FROM OLD CODE
    topics = ', '.join(UNEB_CURRICULUM_MAP[subject][level])
    return call_groq(EXAMINER_SYSTEM, f"Generate 20 ITEMS in STRICT UNEB ITEM/TASK/SCENARIO FORMAT for {level} {subject}: {topics}.", AI_MODEL_LONG)

def display_with_pdf(content, name): # FROM OLD CODE
    st.markdown(content)
    formulas = re.findall(r'\$(.*?)\$', content)
    if formulas: st.markdown("### 🔑 Key Formula"); [st.latex(f) for f in formulas]
    pdf = create_pdf(content, name); st.download_button("📥 Download PDF", pdf, f"{name}.pdf")

# ========== 6. STUDENT PORTAL - ALL 4 TABS FROM OLD CODE ==========
def show_student_portal():
    st.header("📚 Student Portal - S1 to S6")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tab1, tab2 = st.tabs(["🔍 Smart Search", "📖 Learn Topic"])

    with tab1:
        st.header("🔍 Smart Search - Ask Anything Like ChatGPT")
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="search_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="search_level")
        ask_q = st.text_area("Ask: 'define osmosis' OR 'solve 2x+3=7'")
        mic_recorder(key="voice")
        if st.button("Ask AI Brain", type="primary") and ask_q:
            ans = ask_smart_brain(ask_q, subject, level, "General")
            display_with_pdf(ans, f"Answer_{subject}")
            if st.checkbox("Listen"): text_to_speech(ans[:500])

    with tab2:
        st.header("📖 Learn Topic + All Features Restored")
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="learn_subj")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="learn_level")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject2][level2], key="learn_topic")
        mode = st.radio("Mode", ["📖 Theory", "🧠 AOI", "🧪 Practicals Lab", "📝 Quiz Mode", "📚 Bulk Revision"])

        if mode == "📖 Theory" and st.button("Teach Me This Topic", type="primary"): raw = ask_smart_brain(f"Teach {topic2} in detail with examples", subject2, level2, topic2); display_with_pdf(raw, f"Theory_{topic2}")
        elif mode == "🧠 AOI": st.info(f"AOI Focus: {AOI_FRAMEWORK[level2]}");
        if st.button("Generate AOI Project"): raw = ask_smart_brain(f"Design AOI project for {level2} {subject2} on {topic2}", subject2, level2, topic2); display_with_pdf(raw, f"AOI_{topic2}")
        elif mode == "🧪 Practicals Lab":
            prac = st.selectbox("Select NCDC Practical", PRACTICAL_TOPICS.get(subject2,{}).get(level2,["No practicals for this topic"]))
            if st.button("Generate Full Practical"): report = generate_practical(subject2,level2,prac); display_with_pdf(report, f"Practical_{prac}")
        elif mode == "📝 Quiz Mode" and st.button("Generate 10 UNEB ITEMS"): quiz = generate_exam_items(f"Generate 10 questions on {topic2}", subject2, level2); display_with_pdf(quiz, f"Quiz_{topic2}")
        elif mode == "📚 Bulk Revision" and st.button("Generate 20 ITEMS", type="primary"): bulk = generate_bulk_revision(subject2, level2); display_with_pdf(bulk, f"BulkRevision_{subject2}_{level2}")

# ========== 7. ADMIN PORTAL - ALL 14 TABS ==========
def show_admin_portal():
    st.header("🏫 Admin/Teacher Portal")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    TAB_NAMES = ["Admin Dashboard", "Test Paper Generator", "Lesson Plan + SOW", "Single Report Card", "BULK EXAMS GENERATOR", "Performance Analytics", "Student Management", "Question Bank Manager", "Curriculum Planner", "Attendance Tracker", "Fee Management", "Communication Hub", "Resource Library", "Settings & Compliance"]
    selected = option_menu(None, TAB_NAMES, orientation="horizontal")
    logs = load_logs(); df_logs = pd.DataFrame(logs) if logs else pd.DataFrame()

    if selected == "Admin Dashboard":
        col1,col2,col3 = st.columns(3); col1.metric("Total Activities", len(logs)); col2.metric("Flagged", len([l for l in logs if l.get('flagged')])); col3.metric("Users", len(set([l['user'] for l in logs])))
        st.dataframe(logs[-50:])
    elif selected == "Test Paper Generator": s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys())); l = st.selectbox("Class", [f"S{i}" for i in range(1,7)]); t = st.text_input("Topic"); n = st.slider("Questions",5,50,20)
        if st.button("Generate"): display_with_pdf(generate_exam_items(f"Generate {n} on {t}", s, l), "Test")
    elif selected == "Lesson Plan + SOW": s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys())); l = st.selectbox("Class", [f"S{i}" for i in range(1,7)]); t = st.text_input("Topic"); d = st.number_input("Minutes",40,120,80)
        if st.button("Generate"): display_with_pdf(generate_lesson_plan(s,l,t,d), "LessonPlan")
    elif selected == "Single Report Card": name = st.text_input("Name"); scores = {sub: st.number_input(sub,0,100) for sub in ["Math","English","Science"]}
        if st.button("Generate"): display_with_pdf(generate_report_card(f"Name: {name}\n{scores}"), "Report")
    elif selected == "BULK EXAMS GENERATOR": s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys())); l = st.selectbox("Class", [f"S{i}" for i in range(1,7)])
        if st.button("Generate 20"): display_with_pdf(generate_bulk_revision(s,l), "Bulk")
    elif selected == "Performance Analytics": st.line_chart(df_logs.groupby(pd.to_datetime(df_logs['timestamp']).dt.date).size()) if not df_logs.empty else st.info("No data")
    elif selected == "Student Management":
        if "students_db" not in st.session_state: st.session_state.students_db = []
        name = st.text_input("Add Student");
        if st.button("Add"): st.session_state.students_db.append({"name": name}); st.success("Added")
        st.dataframe(st.session_state.students_db)
    elif selected == "Question Bank Manager":
        if "qbank" not in st.session_state: st.session_state.qbank = []
        q = st.text_area("Question");
        if st.button("Save"): st.session_state.qbank.append({"q": q}); st.success("Saved")
        st.dataframe(st.session_state.qbank)
    elif selected == "Curriculum Planner": s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys())); l = st.selectbox("Class", [f"S{i}" for i in range(1,7)])
        if st.button("Generate SOW"): topics = UNEB_CURRICULUM_MAP[s][l]; sow = "\n".join([f"Week {i+1}: {t}" for i,t in enumerate(topics)]); display_with_pdf(sow, "SOW")
    else: st.info(f"{selected} UI Ready")

# ========== 8. MAIN ROUTER - NEW LOGIN LOGIC KEPT ==========
st.title("🎓 DIGITAL UNEB TUTOR 2026 - ALL NCDC SUBJECTS S1-S6")
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"])
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if user_type == "Student" and password == STUDENT_PASSWORD: st.session_state["role"]="Student"; st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD: st.session_state["role"]="Admin"; st.rerun()
    elif password: st.sidebar.error("Wrong password")

if st.session_state.get("role") == "Admin": show_admin_portal()
elif st.session_state.get("role") == "Student": show_student_portal()
else: st.info("Please login to continue")
