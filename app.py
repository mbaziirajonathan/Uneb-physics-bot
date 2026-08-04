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

### CRITICAL SYSTEM PROMPT - NCDC LOCKED + UGANDAN CONTEXT ###
MASTER_SYSTEM_PROMPT = """You are DIGITAL UNEB TUTOR 2026 PRO - NCDC UGANDA EXAMINER.
Role: Senior NCDC Curriculum Specialist + UNEB Chief Examiner for Uganda S1-S6.

CRITICAL RULES:
1. NCDC LOCK: Use ONLY NCDC 2026 curriculum. Use Ugandan examples only: Kampala, Nile, Lake Victoria, Matoke, Boda, UPE, etc. No foreign examples.
2. UNEB FORMAT: All questions must be ITEM, TASK, SCENARIO based. Real life Ugandan context.
3. CHAIN OF THOUGHT: For every problem: 1.Understand 2.Formula 3.Substitute 4.Answer.
4. DIAGRAM RULES: Generate matplotlib code. MUST have Title, Numbered labels 1.2.3., Arrows, Legend, DPI 300. Save to 'auto_diagram.png'. Use 3D when needed.
5. NO HALLUCINATION: If topic not in NCDC, say "Not in NCDC S1-S6 syllabus" then give closest.
6. TONE: Smart like ChatGPT but strict NCDC examiner.

Spatial Examples: Atom shells, Cone h/r/l, Circuit series, Cell parts, Heart chambers."""

### RESTORED ALL 14 NCDC SUBJECTS S1-S6 ###
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

### RESTORED FULL PRACTICALS DATABASE - 3 SCIENCES ###
PRACTICAL_DATABASE = {
    "Physics": {"S1-S4": {"Ohm's Law": {"objective": "To verify Ohm's Law V=IR", "apparatus": "Cell, Ammeter, Voltmeter, Rheostat", "procedure": "1. Connect circuit. 2. Vary rheostat. 3. Record V and I.", "observations": "I vs V Table", "questions": ["State Ohm's law"], "safety": "No short circuit"}, "Simple Pendulum": {"objective": "Find g", "apparatus": "Bob, String, Stopwatch", "procedure": "Time 20 oscillations", "observations": "T vs L", "questions": ["Plot T^2 vs L"], "safety": "Safe height"}, "Refraction": {"objective": "Find refractive index", "apparatus": "Glass block, Pins", "procedure": "Trace rays", "observations": "i vs r", "questions": ["Snell's Law"], "safety": "Handle glass"}}, "S5-S6": {"RC Circuit": {"objective": "Find time constant", "apparatus": "Capacitor, Resistor", "procedure": "Charge and discharge", "observations": "V vs t", "questions": ["Define tau"], "safety": "Discharge"}, "Young's Modulus": {"objective": "Find Y", "apparatus": "Wire, Masses", "procedure": "Measure extension", "observations": "F vs e", "questions": ["Calculate Y"], "safety": "Goggles"}}},
    "Chemistry": {"S1-S4": {"Separation": {"objective": "Separate sand and salt", "apparatus": "Beaker, Filter", "procedure": "Dissolve, Filter, Evaporate", "observations": "Residue, Filtrate", "questions": ["Name methods"], "safety": "Goggles"}, "Titration": {"objective": "Find NaOH conc", "apparatus": "Burette, Pipette", "procedure": "Titrate", "observations": "Titre", "questions": ["Calculate molarity"], "safety": "Acid burns"}, "Oxygen Prep": {"objective": "Prepare O2", "apparatus": "KClO3, MnO2", "procedure": "Heat", "observations": "Relights splint", "questions": ["Equation"], "safety": "Heat"}}, "S5-S6": {"Rate of Reaction": {"objective": "Effect of temp", "apparatus": "Mg, HCl", "procedure": "React at different temps", "observations": "Time", "questions": ["Explain rate"], "safety": "Fumes"}, "Electrolysis": {"objective": "Electrolyse CuSO4", "apparatus": "Electrodes", "procedure": "Pass current", "observations": "Deposits", "questions": ["Half equations"], "safety": "Low voltage"}}},
    "Biology": {"S1-S4": {"Microscope": {"objective": "Observe cells", "apparatus": "Microscope, Onion", "procedure": "Prepare slide", "observations": "Draw cell", "questions": ["Function nucleus"], "safety": "Clean lens"}, "Food Tests": {"objective": "Test nutrients", "apparatus": "Iodine, Benedict", "procedure": "Add reagents", "observations": "Color change", "questions": ["Test protein"], "safety": "No tasting"}, "Osmosis": {"objective": "Potato osmosis", "apparatus": "Potato, Sucrose", "procedure": "Place in solutions", "observations": "Mass change", "questions": ["Define osmosis"], "safety": "Sharp knife"}}, "S5-S6": {"Enzyme Action": {"objective": "Effect of pH", "apparatus": "Amylase, Starch", "procedure": "Test at pH", "observations": "Time", "questions": ["Optimum pH"], "safety": "Sterile"}, "Transpiration": {"objective": "Measure rate", "apparatus": "Potometer", "procedure": "Record bubble", "observations": "Distance", "questions": ["Factors"], "safety": "Water"}}}
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

### CRITICAL AUTO-RENDER ENGINE ###
def auto_render_pixel_diagram(topic, subject, level):
    st.info("🤖 CRITICAL MODE: AI generating labeled 3D diagram...")
    prompt = f"Generate ONLY python matplotlib code to draw '{topic}' for {level} {subject}. CRITICAL: Title, numbered labels with ax.text/ax.annotate, arrows, legend. Use Ugandan context if relevant. Save: plt.savefig('auto_diagram.png', dpi=300, bbox_inches='tight'); plt.close()"
    code = call_groq(prompt).replace("```python","").replace("```","")
    try:
        exec_globals = {"plt": plt, "np": np}
        exec(code, exec_globals)
        return "auto_diagram.png" if os.path.exists("auto_diagram.png") else "ERROR: No savefig"
    except Exception as e: return f"ERROR: {e}"

def generate_practical(subject, level, prac_name):
    level_group = "S1-S4" if int(level[1]) <= 4 else "S5-S6"
    data = PRACTICAL_DATABASE.get(subject,{}).get(level_group,{}).get(prac_name,{})
    if not data: return "Practical not in NCDC database for this level"
    prompt = f"Expand this NCDC practical into full UNEB report format for {subject} {level}. Use Ugandan school lab context: {data}"
    return call_groq(prompt)

def generate_uneb_item_task(subject, level, topic):
    prompt = f"Generate 1 UNEB ITEM/TASK/SCENARIO question for {level} {subject} topic: {topic}. MUST use Ugandan context: market in Kampala, boda, school in Gulu, Lake Victoria. Provide scenario, task, and marking guide."
    return call_groq(prompt)

def display_with_pdf(content, name):
    st.markdown(content)
    for f in re.findall(r'\$(.*?)\$', content): st.latex(f)
    pdf = create_pdf(content, name); st.download_button("📥 Download PDF", pdf, f"{name}.pdf", key=f"dl_{name}_{time.time()}")

### PORTALS ###
def show_student_portal():
    st.header("📚 Student Portal - NCDC S1 to S6 - 14 SUBJECTS")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Smart Search", "📖 Learn Topic", "🎨 Diagram Generator", "📝 UNEB ITEM/TASK"])

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
            aoi = call_groq(f"Generate NCDC Activity of Integration for {level2} {subject2} topic: {topic2}. Use Ugandan scenario.")
            display_with_pdf(aoi, "AOI")
        elif mode == "🧪 Practicals Lab":
            if subject2 in PRACTICAL_DATABASE:
                prac_list = list(PRACTICAL_DATABASE.get(subject2,{}).get("S1-S4",{}).keys()) if int(level2[1])<=4 else list(PRACTICAL_DATABASE.get(subject2,{}).get("S5-S6",{}).keys())
            else: prac_list = ["No practicals for this subject"]
            prac = st.selectbox("Select Practical", prac_list)
            if st.button("Generate Practical"):
                report = generate_practical(subject2,level2,prac)
                display_with_pdf(report, "Practical")
        elif mode == "📚 Bulk Revision" and st.button("Generate Revision"):
            rev = call_groq(f"Generate full NCDC revision notes + 20 Ugandan scenario questions for {topic2} {level2} {subject2}")
            display_with_pdf(rev, "Revision")

    with tab3:
        st.header("🎨 Diagram Generator - CRITICAL AI RENDER")
        subject3 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="svg_subj")
        level3 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="svg_level")
        topic3 = st.text_input("Describe Diagram:", "Draw human heart with 4 chambers")
        if st.button("Generate Diagram", type="primary"):
            log_activity("Student", "Generate Diagram", topic3)
            img_path = auto_render_pixel_diagram(topic3, subject3, level3)
            if "ERROR" in str(img_path): st.error(f"Rendering failed: {img_path}")
            else:
                st.image(img_path, caption=f"HD: {topic3}", use_container_width=True)
                with open(img_path, "rb") as file: st.download_button("📥 Download HD PNG", file, f"{topic3}.png")

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

st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO - V3.7.8 NCDC FULL RESTORE")
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"])
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    if user_type == "Student" and password == STUDENT_PASSWORD: st.session_state["role"] = "Student"; st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD: st.session_state["role"] = "Admin"; st.rerun()
    elif password: st.sidebar.error("Wrong password")

if st.session_state.get("role") == "Admin": show_admin_portal()
elif st.session_state.get("role") == "Student": show_student_portal()
else: st.info("Please login to continue")
