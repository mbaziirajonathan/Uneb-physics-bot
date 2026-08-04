import streamlit as st
import os, io, json, re, time
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from groq import Groq, RateLimitError
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 PRO", page_icon="📚", layout="wide")

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    STUDENT_PASSWORD = st.secrets["STUDENT_PASSWORD"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("Set GROQ_API_KEY, STUDENT_PASSWORD, ADMIN_PASSWORD in Streamlit secrets")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)
LOG_FILE = "usage_log.json"
CONTACT = "256751040731"
AI_MODEL_LONG = "llama-3.3-70b-versatile"
AI_MODEL_FAST = "llama-3.1-8b-instant"
st.sidebar.warning(f"⚠️ LEGAL NOTICE: DIGITAL UNEB TUTOR 2026 PRO\nNCDC + UNEB EXAMINER MODE\n📞 {CONTACT}")

### CRITICAL SYSTEM PROMPT - NCDC LOCKED ###
MASTER_SYSTEM_PROMPT = """You are DIGITAL UNEB TUTOR 2026 PRO - NCDC UGANDA EXAMINER.
Role: Senior NCDC Curriculum Specialist + UNEB Chief Examiner for Uganda S1-S6.
CRITICAL RULES: 1. Use ONLY NCDC 2026 + Ugandan examples. 2. UNEB ITEM/TASK/SCENARIO format. 3. Diagrams: Title, Numbered labels 1.2.3., Arrows, DPI 300. Save to 'auto_diagram.png'. 4. NO HALLUCINATION."""

### 14 NCDC SUBJECTS RESTORED ###
UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Number Bases", "Integers", "Fractions", "Cartesian Coordinates", "Percentages", "Algebra I"], "S2": ["Patterns", "Bearings", "Angles", "Algebra II", "Sets", "Rates"], "S3": ["Quadratics", "Matrices", "Probability", "Vectors", "Similarity", "Trigonometry I"], "S4": ["Functions", "3D Geometry", "Statistics", "Circle Geometry", "Binomials"], "S5": ["Differentiation", "Integration", "Permutations", "Complex Numbers"], "S6": ["Differential Equations", "Mechanics", "Statistics II", "Linear Programming"]},
    "Physics": {"S1": ["Measurement", "Forces", "Work Energy Power", "Density", "Pressure"], "S2": ["Light", "Thermal Physics", "Electricity I", "Waves I", "Sound"], "S3": ["Electricity II", "Magnetism", "Waves II", "Atomic Physics"], "S4": ["Electromagnetism", "Electronics", "Radioactivity", "Astrophysics"], "S5": ["Gravitation", "Optics", "Fluid Mechanics", "Thermal Physics II"], "S6": ["Electric Fields", "Magnetic Fields", "Nuclear Physics", "Quantum Physics"]},
    "Chemistry": {"S1": ["States of Matter", "Mixtures", "Atoms", "Compounds"], "S2": ["Acids Alkalis", "Salts", "Air", "Water"], "S3": ["Bonding", "Stoichiometry", "Electrolysis", "Energy Changes"], "S4": ["REDOX", "Organic II", "Rate of Reaction", "Equilibrium I"], "S5": ["Energetics", "Kinetics", "Equilibrium II", "Acids and Bases"], "S6": ["Electrochemistry", "Organic III", "Industrial Chemistry"]},
    "Biology": {"S1": ["Cells", "Classification", "Nutrition in Plants", "Diversity"], "S2": ["Soil", "Nutrition in Animals", "Respiration", "Excretion"], "S3": ["Respiration", "Genetics I", "Reproduction", "Growth"], "S4": ["Coordination", "Ecology", "Photosynthesis", "Transport"], "S5": ["Cell Biology", "Enzymes", "Genetics II", "Microbiology"], "S6": ["Hormones", "Biotechnology", "Evolution", "Ecosystems"]},
    "Geography": {"S1": ["Map Reading", "Weather", "Vegetation", "Population"], "S2": ["Rocks", "Drainage", "Climate of Uganda", "Soils"], "S3": ["Industry", "Trade", "Transport", "Tourism"], "S4": ["Agriculture", "Mining", "Energy", "Settlement"], "S5": ["Geomorphology", "Climatology", "Biogeography"], "S6": ["Regional Geography", "GIS", "Field Work"]},
    "History": {"S1": ["Early Man", "Ancient Civilizations", "Iron Age in Africa"], "S2": ["Kingdoms of Uganda", "Long Distance Trade"], "S3": ["Scramble for Africa", "Colonialism in Uganda"], "S4": ["Decolonization", "WWI, WWII"], "S5": ["Political Developments 1962-1986"], "S6": ["Governance", "Regional Integration"]},
    "Agriculture": {"S1": ["Introduction to Agriculture", "Soil", "Crops"], "S2": ["Livestock", "Farm Tools"], "S3": ["Crop Production", "Animal Production"], "S4": ["Farm Management", "Agricultural Economics"], "S5": ["Crop Science", "Animal Science"], "S6": ["Agricultural Research", "Agribusiness"]},
    "CRE": {"S1": ["God's Creation", "Abraham"], "S2": ["Moses", "Prophets"], "S3": ["Jesus Ministry", "Parables"], "S4": ["Church", "Christian Living"], "S5": ["Ethics", "Comparative Religion"], "S6": ["Philosophy of Religion"]},
    "IRE": {"S1": ["Tawheed", "Prophets"], "S2": ["Quran", "Hadith"], "S3": ["Pillars of Islam", "Shariah"], "S4": ["Islamic History", "Jihad"], "S5": ["Fiqh", "Comparative Religion"], "S6": ["Islamic Economics"]},
    "Commerce": {"S1": ["Introduction to Business", "Goods and Services"], "S2": ["Money and Banking", "Trade"], "S3": ["Business Organizations", "Communication"], "S4": ["Insurance", "Marketing"], "S5": ["Public Finance", "Consumer Protection"], "S6": ["International Trade", "Entrepreneurship"]},
    "Economics": {"S1": ["Basic Concepts", "Wants and Needs"], "S2": ["Demand and Supply", "Money"], "S3": ["Production", "Market Structures"], "S4": ["National Income", "Inflation"], "S5": ["Public Finance", "Economic Growth"], "S6": ["International Economics", "Development"]},
    "Literature": {"S1": ["Poetry", "Prose"], "S2": ["Drama", "Novel"], "S3": ["Shakespeare", "African Literature"], "S4": ["Themes", "Literary Devices"], "S5": ["Critical Analysis", "Ugandan Authors"], "S6": ["Comparative Literature"]},
    "ICT": {"S1": ["Computer Basics", "Word Processing"], "S2": ["Spreadsheet", "Internet"], "S3": ["Programming Basics", "Database"], "S4": ["Web Design", "Graphics"], "S5": ["Python", "Networks"], "S6": ["AI", "Cybersecurity"]},
    "Fine Art": {"S1": ["Drawing", "Color"], "S2": ["Painting", "Sculpture"], "S3": ["Craft", "Design"], "S4": ["Art History", "Printmaking"], "S5": ["Advanced Painting", "Textiles"], "S6": ["Exhibition", "Career in Art"]}
}

PRACTICAL_DATABASE = {
    "Physics": {"S1-S4": {"Ohm's Law": {"objective": "To verify Ohm's Law V=IR", "apparatus": "Cell, Ammeter, Voltmeter", "procedure": "Connect circuit", "observations": "I vs V", "questions": ["State Ohm's law"], "safety": "No short circuit"}, "Simple Pendulum": {"objective": "Find g", "apparatus": "Bob, String", "procedure": "Time 20 oscillations", "observations": "T vs L", "questions": ["Plot T^2"], "safety": "Safe"}, "Refraction": {"objective": "Find n", "apparatus": "Glass block", "procedure": "Trace rays", "observations": "i vs r", "questions": ["Snell"], "safety": "Care"}}, "S5-S6": {"RC Circuit": {"objective": "Find tau", "apparatus": "C,R", "procedure": "Charge", "observations": "V vs t", "questions": ["tau"], "safety": "Discharge"}, "Young's Modulus": {"objective": "Find Y", "apparatus": "Wire", "procedure": "Extend", "observations": "F vs e", "questions": ["Y"], "safety": "Goggles"}}},
    "Chemistry": {"S1-S4": {"Separation": {"objective": "Separate sand/salt", "apparatus": "Beaker", "procedure": "Dissolve", "observations": "Residue", "questions": ["Methods"], "safety": "Goggles"}, "Titration": {"objective": "Find conc", "apparatus": "Burette", "procedure": "Titrate", "observations": "Titre", "questions": ["Molarity"], "safety": "Acid"}, "Oxygen": {"objective": "Prep O2", "apparatus": "KClO3", "procedure": "Heat", "observations": "Splint", "questions": ["Eqn"], "safety": "Heat"}}, "S5-S6": {"Rate": {"objective": "Effect temp", "apparatus": "Mg", "procedure": "React", "observations": "Time", "questions": ["Rate"], "safety": "Fumes"}, "Electrolysis": {"objective": "CuSO4", "apparatus": "Electrodes", "procedure": "Current", "observations": "Deposit", "questions": ["Half"], "safety": "Low V"}}},
    "Biology": {"S1-S4": {"Microscope": {"objective": "Observe cells", "apparatus": "Microscope", "procedure": "Slide", "observations": "Draw", "questions": ["Nucleus"], "safety": "Clean"}, "Food Tests": {"objective": "Test food", "apparatus": "Iodine", "procedure": "Reagent", "observations": "Color", "questions": ["Protein"], "safety": "No taste"}, "Osmosis": {"objective": "Potato", "apparatus": "Potato", "procedure": "Soak", "observations": "Mass", "questions": ["Osmosis"], "safety": "Knife"}}, "S5-S6": {"Enzyme": {"objective": "pH effect", "apparatus": "Amylase", "procedure": "Test", "observations": "Time", "questions": ["pH"], "safety": "Sterile"}, "Transpiration": {"objective": "Rate", "apparatus": "Potometer", "procedure": "Bubble", "observations": "Distance", "questions": ["Factors"], "safety": "Water"}}}
}

### CORE FUNCTIONS ###
def load_logs(): return json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []
def save_log(entry): logs = load_logs(); logs.append(entry); json.dump(logs, open(LOG_FILE,"w"))
def log_activity(user_type, action, details): save_log({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user_type, "action": action, "details": details})
def create_pdf(content, title):
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); p.setFont("Helvetica-Bold", 14); p.drawString(50,800,title); y=770; p.setFont("Helvetica", 10)
    for i,line in enumerate(content.split('\n')[:80]): p.drawString(50,y-(i*14),line[:95])
    p.save(); buffer.seek(0); return buffer
def call_groq(user_prompt):
    try: res = client.chat.completions.create(model=AI_MODEL_LONG, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}], max_tokens=4000, temperature=0.3); return res.choices[0].message.content
    except RateLimitError: res = client.chat.completions.create(model=AI_MODEL_FAST, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}], max_tokens=2000, temperature=0.3); return res.choices[0].message.content

### ADVANCED LOOP ENGINE - BATCH DIAGRAM GENERATOR ###
def auto_render_pixel_diagram(topic, subject, level):
    prompt = f"Generate ONLY python matplotlib code to draw '{topic}' for {level} {subject}. CRITICAL: Title, numbered labels 1.2.3., arrows, legend. Ugandan context if possible. Save: plt.savefig('auto_diagram_{topic}.png', dpi=300, bbox_inches='tight'); plt.close()"
    code = call_groq(prompt).replace("```python","").replace("```","")
    try:
        exec_globals = {"plt": plt, "np": np}
        exec(code, exec_globals)
        fname = f"auto_diagram_{topic}.png".replace(" ", "_")
        return fname if os.path.exists(fname) else "ERROR"
    except Exception as e: return f"ERROR: {e}"

def batch_generate_diagrams(subject, level, topic_list):
    results = []
    progress = st.progress(0)
    for i, topic in enumerate(topic_list):
        st.write(f"Rendering {i+1}/{len(topic_list)}: {topic}")
        img_path = auto_render_pixel_diagram(topic, subject, level)
        if "ERROR" not in img_path:
            results.append({"topic": topic, "path": img_path})
        progress.progress((i+1)/len(topic_list))
        time.sleep(0.5) # Rate limit
    return results

def generate_practical(subject, level, prac_name):
    level_group = "S1-S4" if int(level[1]) <= 4 else "S5-S6"
    data = PRACTICAL_DATABASE.get(subject,{}).get(level_group,{}).get(prac_name,{})
    if not data: return "Practical not in NCDC database"
    prompt = f"Expand this NCDC practical into full UNEB report for {subject} {level} Ugandan context: {data}"
    return call_groq(prompt)

def generate_uneb_item_task(subject, level, topic):
    prompt = f"Generate 1 UNEB ITEM/TASK/SCENARIO for {level} {subject} topic: {topic}. Use Ugandan context: Kampala market, boda, Lake Victoria. Provide scenario, task, marking guide."
    return call_groq(prompt)

def display_with_pdf(content, name):
    st.markdown(content)
    for f in re.findall(r'\$(.*?)\$', content): st.latex(f)
    pdf = create_pdf(content, name); st.download_button("📥 Download PDF", pdf, f"{name}.pdf", key=f"dl_{name}_{time.time()}")

### PORTALS ###
def show_student_portal():
    st.header("📚 Student Portal - NCDC S1 to S6 - 14 SUBJECTS")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Smart Search", "📖 Learn Topic", "🎨 Batch Diagram Generator", "📝 UNEB ITEM/TASK"])

    with tab1:
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="search_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="search_level")
        ask_q = st.text_area("Ask any NCDC question")
        if st.button("Ask AI Brain", type="primary") and ask_q:
            log_activity("Student", "Ask Question", ask_q)
            ans = call_groq(f"Answer with Ugandan examples: {ask_q} for {level} {subject}")
            display_with_pdf(ans, "Answer")

    with tab2:
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="learn_subj")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="learn_level")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject2][level2], key="learn_topic")
        mode = st.radio("Mode", ["📖 Theory", "🧠 AOI", "🧪 Practicals Lab", "📚 Bulk Revision"])
        log_activity("Student", "Learn Mode", mode)

        if mode == "📖 Theory" and st.button("Teach Me"):
            raw = call_groq(f"Teach {topic2} with Ugandan examples for {level2} {subject2}")
            display_with_pdf(raw, "Theory")
        elif mode == "🧠 AOI" and st.button("Generate AOI"):
            aoi = call_groq(f"Generate NCDC Activity of Integration for {level2} {subject2} topic: {topic2}. Ugandan scenario.")
            display_with_pdf(aoi, "AOI")
        elif mode == "🧪 Practicals Lab":
            if subject2 in PRACTICAL_DATABASE:
                prac_list = list(PRACTICAL_DATABASE.get(subject2,{}).get("S1-S4",{}).keys()) if int(level2[1])<=4 else list(PRACTICAL_DATABASE.get(subject2,{}).get("S5-S6",{}).keys())
            else: prac_list = ["No practicals"]
            prac = st.selectbox("Select Practical", prac_list)
            if st.button("Generate Practical"):
                report = generate_practical(subject2,level2,prac)
                display_with_pdf(report, "Practical")
        elif mode == "📚 Bulk Revision" and st.button("Generate Revision"):
            rev = call_groq(f"Generate NCDC revision + 20 Ugandan questions for {topic2} {level2} {subject2}")
            display_with_pdf(rev, "Revision")

    with tab3:
        st.header("🎨 Batch Diagram Generator - LOOP ALL TOPICS")
        subject3 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="batch_subj")
        level3 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="batch_level")

        col1, col2 = st.columns(2)
        with col1:
            mode = st.radio("Batch Mode", ["1 Topic", "All Topics in Class", "Selected Topics"])
        with col2:
            if mode == "1 Topic":
                topic_single = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject3][level3])
                topic_list = [topic_single]
            elif mode == "All Topics in Class":
                topic_list = UNEB_CURRICULUM_MAP[subject3][level3]
                st.info(f"Will generate {len(topic_list)} diagrams")
            else:
                topic_list = st.multiselect("Select Topics", UNEB_CURRICULUM_MAP[subject3][level3])

        if st.button("Generate Batch Diagrams", type="primary"):
            log_activity("Student", "Batch Generate", f"{subject3} {level3}")
            results = batch_generate_diagrams(subject3, level3, topic_list)
            st.success(f"Generated {len(results)} diagrams")
            for r in results:
                st.image(r["path"], caption=f"{r['topic']}", use_container_width=True)
                with open(r["path"], "rb") as file: st.download_button("📥 Download", file, r["path"], key=r["path"])

    with tab4:
        st.header("📝 UNEB ITEM/TASK/SCENARIO GENERATOR")
        subject4 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="item_subj")
        level4 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="item_level")
        topic4 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject4][level4], key="item_topic")
        if st.button("Generate UNEB ITEM/TASK", type="primary"):
            item = generate_uneb_item_task(subject4, level4, topic4)
            display_with_pdf(item, "UNEB_ITEM")

def show_admin_portal():
    st.header("🏫 Admin Portal - NCDC MANAGER")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tab1, tab2 = st.tabs(["📊 Analytics", "📖 Curriculum Manager"])
    with tab1:
        logs = load_logs()
        st.metric("Total Logs", len(logs))
        if logs: st.dataframe(pd.DataFrame(logs))
    with tab2:
        st.subheader("14 NCDC Subjects")
        subj = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)])
        st.write(UNEB_CURRICULUM_MAP[subj][level])

st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO - V3.7.9 BATCH LOOP ENGINE")
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"])
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    if user_type == "Student" and password == STUDENT_PASSWORD: st.session_state["role"] = "Student"; st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD: st.session_state["role"] = "Admin"; st.rerun()
    elif password: st.sidebar.error("Wrong password")

if st.session_state.get("role") == "Admin": show_admin_portal()
elif st.session_state.get("role") == "Student": show_student_portal()
else: st.info("Please login to continue")
