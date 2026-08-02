import streamlit as st
import os, io, json, re, time
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
from streamlit_option_menu import option_menu
from groq import Groq, RateLimitError

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026", page_icon="📚", layout="wide")

# ========== SECRETS ==========
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
STUDENT_PASSWORD = st.secrets["STUDENT_PASSWORD"] # unebtest2026
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"] # admin256
client = Groq(api_key=GROQ_API_KEY)

LOG_FILE = "usage_log.json"
CONTACT = "256751040731"
AI_MODEL_LONG = "llama-3.3-70b-versatile"
AI_MODEL_FAST = "llama-3.1-8b-instant"
FIG_COUNTER = {"count": 0}

# ========== LEGAL ==========
st.sidebar.warning(f"""
⚠️ LEGAL NOTICE: DIGITAL UNEB TUTOR 2026
For learning support only as per NCDC.
NOT for use during UNEB exams.
📞 Support: {CONTACT}
""")

# ============ RESTORED FULL NCDC DATABASE - FROM YOUR CODE ============
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
OTHER_SUBJECTS = ["Geography", "History", "Literature in English", "CRE", "IRE", "Agriculture", "Entrepreneurship", "ICT", "Art and Design", "Music", "French", "Kiswahili", "Luganda", "Economics", "Commerce"]
for subj in OTHER_SUBJECTS:
    UNEB_CURRICULUM_MAP[subj] = {f"S{i}": [f"Topic {j}" for j in range(1,6)] for i in range(1,7)}

PRACTICAL_TOPICS = {
    "Mathematics": {"S1": ["Geometric Construction: Bisecting lines"],"S2": ["Bearings and Scale Drawing"],"S3": ["Construction of Quadrilaterals"],"S4": ["Building 3D Geometric Models"],"S5": ["Drawing Graphs of Functions"],"S6": ["Vectors in 3D Models"]},
    "Physics": {"S1": ["Measurement using Vernier Calipers"],"S2": ["Reflection using Plane Mirrors"],"S3": ["Series and Parallel Circuits"],"S4": ["Electronics: Diode Characteristics"],"S5": ["Projectile Motion"],"S6": ["Electric Field Mapping"]},
    "Chemistry": {"S1": ["Filtration and Evaporation"],"S2": ["Preparation of Salts"],"S3": ["Rates of Reaction"],"S4": ["REDOX Titration"],"S5": ["Chemical Kinetics Experiment"],"S6": ["Electrochemistry: Electrolysis"]},
    "Biology": {"S1": ["Using Light Microscope"],"S2": ["Testing for Food Nutrients"],"S3": ["Dissection of a Flower"],"S4": ["Genetics: Dihybrid Cross"],"S5": ["Enzyme Activity"],"S6": ["DNA Extraction"]}
}
AOI_FRAMEWORK = {"S1": "Community Problem", "S2": "Local Industry", "S3": "National Issue", "S4": "Global Challenge", "S5": "Research", "S6": "Professional"}

# ============ HARD LOCKED SYSTEM PROMPTS - FROM YOUR CODE ============
SMART_SYSTEM = """You are DIGITAL UNEB TUTOR 2026. You are a SMART AI like ChatGPT and Meta AI.
FORBIDDEN: You are NOT allowed to generate "ITEM 1. TASK: " format unless user asks for test.
FORBIDDEN: You are NOT allowed to make up questions.
YOUR JOB: Answer the question directly. Explain, Define, Solve, Compare.
Use examples. Use Ugandan context. Use chain of thought. Be conversational.
"""
EXAMINER_SYSTEM = """You are DIGITAL UNEB EXAMINER 2026. Senior NCDC Examiner for Uganda S1-S6.
YOUR ONLY JOB: Generate UNEB ITEM/TASK/SCENARIO questions ONLY when asked.
MUST USE THIS EXACT FORMAT:
ITEM 1.
[SCENARIO PARAGRAPH 1: 3-5 sentences. Realistic Ugandan problem. Name people, districts, data]
TASK:
As a [Subject] learner;
i) [First competence task] (X scores)
ii) [Second competence task] (X scores)
SOLUTION:
**ITEM 1(i) Solution** Step 1: Identification... Step 2: FORMULA → SUBSTITUTION → ANSWER
"""

# ========== UTILS + LOGGING ==========
def load_logs(): return json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []
def save_log(entry): logs = load_logs(); logs.append(entry); json.dump(logs, open(LOG_FILE,"w"))
def log_activity(user_type, action, details): save_log({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user_type, "action": action, "details": details})

def create_pdf(content, title):
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); p.setFont("Helvetica-Bold", 14); p.drawString(50,800,title); y=770; p.setFont("Helvetica", 10)
    for line in content.split('\n')[:80]: p.drawString(50,y,line[:95]); y-=14;
    p.save(); buffer.seek(0); return buffer

def text_to_speech(text):
    tts = gTTS(text=text, lang='en'); fp = io.BytesIO(); tts.write_to_fp(fp)
    b64 = base64.b64encode(fp.getvalue()).decode()
    st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)

def call_groq(system_prompt, user_prompt, model):
    try:
        res = client.chat.completions.create(model=model, messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}], max_tokens=4000, temperature=0.7)
        return res.choices[0].message.content
    except RateLimitError:
        res = client.chat.completions.create(model=AI_MODEL_FAST, messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}], max_tokens=2000)
        return res.choices[0].message.content
    except Exception as e: return f"AI Error: {e}"

def ask_smart_brain(user_query, subject, class_level, topic):
    log_activity(st.session_state.role, "Smart Query", f"{subject} {class_level}")
    prompt = f"Level: {class_level}\nSubject: {subject}\nTopic: {topic}\nUser Question: {user_query}\n\nAnswer directly now with examples."
    return call_groq(SMART_SYSTEM, prompt, AI_MODEL_LONG)

def generate_exam_items(user_query, subject, level): return call_groq(EXAMINER_SYSTEM, f"Generate UNEB ITEMS for: Level: {level}, Subject: {subject}, Request: {user_query}", AI_MODEL_LONG)
def generate_lesson_plan(subject, level, topic, duration): return call_groq(SMART_SYSTEM, f"Generate NCDC {duration} min lesson plan for {level} {subject} on {topic}", AI_MODEL_LONG)
def generate_report_card(student_data): return call_groq(SMART_SYSTEM, f"Generate NCDC Report Card for student: {student_data}", AI_MODEL_LONG)
def generate_practical(subject, level, topic): return call_groq(EXAMINER_SYSTEM, f"Generate FULL NCDC {level} {subject} practical for: {topic}", AI_MODEL_LONG)
def generate_bulk_revision(subject, level):
    topics = ', '.join(UNEB_CURRICULUM_MAP[subject][level])
    return call_groq(EXAMINER_SYSTEM, f"Generate 20 ITEMS in STRICT UNEB FORMAT for {level} {subject}: {topics}", AI_MODEL_LONG)

def display_with_pdf(content, name):
    st.markdown(content)
    pdf = create_pdf(content, name); st.download_button("📥 Download PDF", pdf, f"{name}.pdf")

# ========== STUDENT PORTAL ==========
def show_student_portal():
    st.header("📚 Student Portal - S1 to S6")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tab1, tab2 = st.tabs(["🔍 Smart Learn", "📖 Learn Topic + Practicals"])

    with tab1:
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="search_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="search_level")
        ask_q = st.text_area("Ask: 'define osmosis' OR 'solve 2x+3=7'")
        mic_recorder(key="voice")
        if st.button("Ask AI Brain", type="primary"):
            ans = ask_smart_brain(ask_q, subject, level, "General")
            display_with_pdf(ans, f"Answer_{subject}")
            if st.checkbox("Listen"): text_to_speech(ans[:500])

    with tab2:
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="learn_subj")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="learn_level")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject2][level2], key="learn_topic")
        mode = st.radio("Mode", ["📖 Theory", "🧠 AOI", "🧪 Practicals Lab", "📝 Quiz", "📚 Bulk Revision"])

        if mode == "📖 Theory" and st.button("Teach Me"):
            raw = ask_smart_brain(f"Teach {topic2} in detail with examples", subject2, level2, topic2); display_with_pdf(raw, f"Theory_{topic2}")
        elif mode == "🧠 AOI":
            st.info(f"AOI Focus: {AOI_FRAMEWORK[level2]}")
            if st.button("Generate AOI"): raw = ask_smart_brain(f"Design AOI project for {level2} {subject2} on {topic2}", subject2, level2, topic2); display_with_pdf(raw, f"AOI_{topic2}")
        elif mode == "🧪 Practicals Lab":
            prac = st.selectbox("Select NCDC Practical", PRACTICAL_TOPICS.get(subject2,{}).get(level2,["No practicals"]))
            if st.button("Generate Practical"): report = generate_practical(subject2,level2,prac); display_with_pdf(report, f"Practical_{prac}")
        elif mode == "📝 Quiz" and st.button("Generate 10 ITEMS"):
            quiz = generate_exam_items(f"Generate 10 questions on {topic2}", subject2, level2); display_with_pdf(quiz, f"Quiz_{topic2}")
        elif mode == "📚 Bulk Revision" and st.button("Generate 20 ITEMS", type="primary"):
            bulk = generate_bulk_revision(subject2, level2); display_with_pdf(bulk, f"Bulk_{subject2}_{level2}")

# ========== ADMIN PORTAL - 14 TABS RESTORED ==========
def show_admin_portal():
    st.header("🏫 Admin/Teacher Portal")
    if st.button("Logout"): st.session_state.clear(); st.rerun()

    TAB_NAMES = [
        "Admin Dashboard",
        "Test Paper Generator",
        "Lesson Plan + SOW",
        "Single Report Card",
        "BULK EXAMS GENERATOR",
        "Performance Analytics",
        "Student Management",
        "Question Bank Manager",
        "Curriculum Planner",
        "Attendance Tracker",
        "Fee Management",
        "Communication Hub",
        "Resource Library",
        "Settings & Compliance"
    ]
    selected = option_menu(None, TAB_NAMES, orientation="horizontal", styles={"nav-link": {"font-size": "12px"}})

    if selected == "Admin Dashboard":
        logs = load_logs()
        col1,col2,col3 = st.columns(3)
        col1.metric("Total Activities", len(logs))
        col2.metric("Flagged", len([l for l in logs if l.get('flagged')]))
        col3.metric("Users", len(set([l['user'] for l in logs])))
        st.subheader("Live Activity Feed"); st.dataframe(logs[-50:], use_container_width=True)

    elif selected == "Test Paper Generator":
        s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="test_subj")
        l = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="test_level")
        t = st.text_input("Topic or 'All Topics'")
        n = st.slider("Number of Questions",5,50,20)
        if st.button("Generate Test Paper", type="primary"):
            display_with_pdf(generate_exam_items(f"Generate {n} UNEB ITEMS on {t}", s, l), f"Test_{s}_{l}")

    elif selected == "Lesson Plan + SOW":
        s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="lp_subj")
        l = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="lp_level")
        t = st.text_input("Topic")
        d = st.number_input("Duration minutes",40,120,80)
        scheme = st.checkbox("Generate Scheme of Work too")
        if st.button("Generate Lesson Plan"):
            lp = generate_lesson_plan(s,l,t,d)
            if scheme: lp += "\n\n### SCHEME OF WORK\nWeek 1-8 breakdown based on NCDC"
            display_with_pdf(lp, f"LessonPlan_{t}")

    elif selected == "Single Report Card":
        name = st.text_input("Student Name")
        term = st.selectbox("Term", ["Term 1", "Term 2", "Term 3"])
        scores = {}
        for sub in ["Mathematics","English","Physics","Chemistry","Biology"]:
            scores[sub] = st.number_input(sub,0,100)
        if st.button("Generate Report Card"):
            data = f"Name: {name}\nTerm: {term}\n" + "\n".join([f"{k}: {v}" for k,v in scores.items()])
            rc = generate_report_card(data)
            display_with_pdf(rc, f"Report_{name}")

    elif selected == "BULK EXAMS GENERATOR":
        s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="bulk_subj")
        l = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="bulk_level")
        paper_type = st.radio("Paper Type", ["Midterm", "End of Term", "Mock UNEB"])
        if st.button("Generate 20 ITEMS Bulk", type="primary"):
            bulk = generate_bulk_revision(s,l)
            display_with_pdf(bulk, f"Bulk_{paper_type}_{s}_{l}")

    elif selected == "Performance Analytics":
        st.info("📊 Coming: Class average, Top 10 students, Weak topics analysis from usage_log.json")
        logs = load_logs()
        if logs: st.bar_chart([len(logs)])

    elif selected == "Student Management":
        st.info("👨‍🎓 Coming: Add/Remove students, Assign classes, View progress")

    elif selected == "Question Bank Manager":
        st.info("📚 Coming: Save generated tests to bank, Tag by topic, Reuse")

    elif selected == "Curriculum Planner":
        st.info("🗓️ Coming: Auto-generate Scheme of Work for whole term based on NCDC")

    elif selected == "Attendance Tracker":
        st.info("✅ Coming: Daily attendance, Export to Excel")

    elif selected == "Fee Management":
        st.info("💰 Coming: Track fees, Generate receipts")

    elif selected == "Communication Hub":
        st.info("📢 Coming: Send SMS/WhatsApp to parents")

    elif selected == "Resource Library":
        st.info("📁 Coming: Upload past papers, Marking guides")

    elif selected == "Settings & Compliance":
        st.info(f"⚙️ Support: {CONTACT}\nLegal: For NCDC use only")

# ========== MAIN ROUTER ==========
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
