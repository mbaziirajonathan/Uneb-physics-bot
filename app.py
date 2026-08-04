import streamlit as st
import os, io, json, re, time, ast
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from groq import Groq, RateLimitError
import pandas as pd
import matplotlib
matplotlib.use('Agg') # Fixes Streamlit Cloud backend crash
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Rectangle, Ellipse, FancyArrow

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
QBANK_FILE = "qbank.json"
AI_QBANK_FILE = "ai_qbank.json"
STUDENTS_FILE = "students.json"
CONTACT = "256751040731"

### DUAL ENGINE V3.9.9 - 3B REPLACED WITH 8B ###
AI_MODEL_SMART = "llama-3.3-70b-versatile" # Quality Engine
AI_MODEL_INSTANT = "llama-3.1-8b-instant" # Speed Engine. Replaces dead 3B
st.sidebar.warning(f"⚠️ LEGAL NOTICE: DIGITAL UNEB TUTOR 2026 PRO V3.9.9\nNCDC + UNEB EXAMINER MODE + DUAL ENGINE 70B + 8B\n📞 {CONTACT}")

### 3-SHOT ANTI-HALLUCINATION EXAMPLES FOR 70B ###
SHOT_1_CELL = '''fig, ax = plt.subplots(figsize=(9,9)); ax.set_xlim(0,1); ax.set_ylim(0,1)
ax.add_patch(Rectangle((0.05,0.05), 0.9, 0.9, fill=False, linewidth=3))
ax.add_patch(Circle((0.5,0.5), 0.12, color='#ffcdd2')); ax.add_patch(Ellipse((0.3,0.7), 0.1, 0.05, color='#81c784'))
ax.add_patch(Rectangle((0.6,0.2), 0.15, 0.1, color='#90caf9'))
ax.text(0.5,0.5,'1. Nucleus', ha='center', bbox=dict(boxstyle='round', facecolor='yellow'))
ax.annotate('2. Chloroplast', xy=(0.3,0.7), xytext=(0.1,0.8), arrowprops=dict(arrowstyle='->', color='black'))
ax.set_title('Plant Cell - S1 Biology', fontsize=16, fontweight='bold'); ax.axis('off')
plt.savefig('diagram.png', dpi=300, bbox_inches='tight'); plt.close()'''

SHOT_2_CIRCUIT = '''fig, ax = plt.subplots(figsize=(9,9)); ax.set_xlim(0,1); ax.set_ylim(0,1)
ax.plot([0.1,0.3],[0.5,0.5], 'k-', linewidth=4); ax.add_patch(Rectangle((0.3,0.45), 0.1, 0.1, fill=False, linewidth=4))
ax.add_patch(Circle((0.55,0.5), 0.08, fill=False, linewidth=4))
ax.plot([0.63,0.63],[0.5,0.7], 'k-', linewidth=4); ax.plot([0.63,0.1],[0.7,0.7], 'k-', linewidth=4)
ax.text(0.35,0.48,'1. Resistor', bbox=dict(boxstyle='round', facecolor='yellow'))
ax.annotate('2. Bulb', xy=(0.55,0.5), xytext=(0.7,0.6), arrowprops=dict(arrowstyle='->'))
ax.set_title('Simple Circuit - S2 Physics', fontsize=16, fontweight='bold'); ax.axis('off')
plt.savefig('diagram.png', dpi=300, bbox_inches='tight'); plt.close()'''

SHOT_3_HEART = '''fig, ax = plt.subplots(figsize=(9,9)); ax.set_xlim(0,1); ax.set_ylim(0,1)
ax.add_patch(Ellipse((0.5,0.5), 0.4, 0.5, color='#ef9a9a'))
ax.add_patch(Circle((0.35,0.4), 0.08, color='#d32f2f')); ax.add_patch(Circle((0.65,0.4), 0.08, color='#d32f2f'))
ax.text(0.35,0.4,'1. LA', ha='center', color='white', fontweight='bold')
ax.annotate('2. Aorta', xy=(0.5,0.75), xytext=(0.6,0.85), arrowprops=dict(arrowstyle='->'))
ax.set_title('Human Heart - S4 Biology', fontsize=16, fontweight='bold'); ax.axis('off')
plt.savefig('diagram.png', dpi=300, bbox_inches='tight'); plt.close()'''

SYSTEM_SMART = f"""You are DIGITAL UNEB TUTOR 2026 PRO. Senior NCDC Curriculum Specialist + UNEB Chief Examiner for Uganda S1-S6.
OUTPUT ONLY PYTHON CODE. NO EXPLANATIONS. NO MARKDOWN.
COPY THIS STYLE EXACTLY FOR DIAGRAMS: {SHOT_1_CELL} --- {SHOT_2_CIRCUIT} --- {SHOT_3_HEART}
STRICT RULES FOR DIAGRAMS:
1. MUST have: plt.subplots, ax.set_xlim(0,1), ax.set_ylim(0,1), Title, 5-8 numbered labels in yellow boxes, black arrows pointing to parts
2. Use ONLY: Circle, Rectangle, Ellipse, FancyArrow from matplotlib.patches
3. Save: plt.savefig('diagram.png', dpi=300, bbox_inches='tight'); plt.close()
4. NCDC Uganda S1-S6. Label all parts accurately. ax.axis('off')"""

SYSTEM_INSTANT = """You are FAST DIAGRAM BOT.
OUTPUT ONLY PYTHON CODE. NO TEXT. NO EXPLANATIONS.
RULES:
1. Use Circle, Rectangle, Ellipse only.
2. Add Title. Add 3-4 labels with numbers and bbox.
3. Save: plt.savefig('diagram.png', dpi=200, bbox_inches='tight'); plt.close()
4. ax.axis('off')"""

### DATABASES - YOUR CORE + RESTORED ALL 14 SUBJECTS ###
def load_db(file): return json.load(open(file,"r", encoding="utf-8")) if os.path.exists(file) else []
def save_db(file,data): json.dump(data,open(file,"w", encoding="utf-8"),indent=2)

if "students_db" not in st.session_state: st.session_state.students_db = load_db(STUDENTS_FILE)

UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Number Bases", "Integers", "Fractions", "Cartesian Coordinates", "Percentages", "Algebra I"], "S2": ["Patterns", "Bearings", "Angles", "Algebra II", "Sets", "Rates"], "S3": ["Quadratics", "Matrices", "Probability", "Vectors", "Similarity", "Trigonometry I"], "S4": ["Functions", "3D Geometry", "Statistics", "Circle Geometry", "Binomials"], "S5": ["Differentiation", "Integration", "Permutations", "Complex Numbers"], "S6": ["Differential Equations", "Mechanics", "Statistics II", "Linear Programming"]},
    "Physics": {"S1": ["Measurement", "Forces", "Work Energy Power", "Density", "Pressure"], "S2": ["Light", "Thermal Physics", "Electricity I", "Waves I", "Sound"], "S3": ["Electricity II", "Magnetism", "Waves II", "Atomic Physics"], "S4": ["Electromagnetism", "Electronics", "Radioactivity", "Astrophysics"], "S5": ["Gravitation", "Optics", "Fluid Mechanics", "Thermal Physics II"], "S6": ["Electric Fields", "Magnetic Fields", "Nuclear Physics", "Quantum Physics"]},
    "Chemistry": {"S1": ["States of Matter", "Mixtures", "Atoms", "Compounds"], "S2": ["Acids Alkalis", "Salts", "Air", "Water"], "S3": ["Bonding", "Stoichiometry", "Electrolysis", "Energy Changes"], "S4": ["REDOX", "Organic II", "Rate of Reaction", "Equilibrium I"], "S5": ["Energetics", "Kinetics", "Equilibrium II", "Acids and Bases"], "S6": ["Electrochemistry", "Organic III", "Industrial Chemistry"]},
    "Biology": {"S1": ["Cells", "Classification", "Nutrition in Plants", "Diversity"], "S2": ["Soil", "Nutrition in Animals", "Respiration", "Excretion"], "S3": ["Respiration", "Genetics I", "Reproduction", "Growth"], "S4": ["Coordination", "Ecology", "Photosynthesis", "Transport"], "S5": ["Cell Biology", "Enzymes", "Genetics II", "Microbiology"], "S6": ["Hormones", "Biotechnology", "Evolution", "Ecosystems"]},
    "ICT": {"S1": ["Computer Basics","Hardware"],"S2": ["Word Processing"],"S3": ["Spreadsheets","Databases"],"S4": ["Internet","Networking"],"S5": ["Programming Python"],"S6": ["Web Design","Data Analysis"]},
    "Geography": {"S1": ["Map Reading"],"S2": ["Climate","Vegetation"],"S3": ["Rivers","Lakes"],"S4": ["Population","Settlement"],"S5": ["Industries","Trade"],"S6": ["GIS","Environmental Issues"]},
    "History": {"S1": ["Early Man"],"S2": ["Kingdoms of Uganda"],"S3": ["Colonialism"],"S4": ["Independence"],"S5": ["World Wars"],"S6": ["Cold War"]},
    "CRE": {"S1": ["Creation"],"S2": ["Prophets"],"S3": ["Jesus Ministry"],"S4": ["Church"],"S5": ["Ethics"],"S6": ["Comparative Religion"]},
    "IRE": {"S1": ["Tawheed"],"S2": ["Prophets"],"S3": ["Quran"],"S4": ["Hadith"],"S5": ["Fiqh"],"S6": ["Islamic History"]},
    "Literature": {"S1": ["Poetry"],"S2": ["Drama"],"S3": ["Novel"],"S4": ["Prose"],"S5": ["Shakespeare"],"S6": ["African Literature"]},
    "Commerce": {"S1": ["Business Basics"],"S2": ["Trade"],"S3": ["Banking"],"S4": ["Insurance"],"S5": ["Marketing"],"S6": ["Entrepreneurship"]},
    "Economics": {"S1": ["Scarcity"],"S2": ["Demand Supply"],"S3": ["Money"],"S4": ["Trade"],"S5": ["National Income"],"S6": ["Development"]},
    "Agriculture": {"S1": ["Soil"],"S2": ["Crops"],"S3": ["Livestock"],"S4": ["Farm Tools"],"S5": ["Farm Records"],"S6": ["Agribusiness"]},
    "Art": {"S1": ["Drawing"],"S2": ["Painting"],"S3": ["Sculpture"],"S4": ["Design"],"S5": ["Craft"],"S6": ["Art History"]}
}

PRACTICAL_DATABASE = {
    "Physics": {"S1-S4": {"Ohm's Law": {"objective": "To verify Ohm's Law V=IR", "apparatus": "Cell, Ammeter, Voltmeter, Rheostat, Connecting wires", "procedure": "1. Connect circuit in series. 2. Vary rheostat. 3. Record V and I.", "observations": "Table: Current I(A) | Voltage V(V)", "questions": ["State Ohm's law", "Plot V vs I graph", "Find slope"], "safety": "Do not short circuit the cell"}, "Simple Pendulum": {"objective": "To determine acceleration due to gravity g", "apparatus": "Bob, String, Meter rule, Stopwatch, Stand", "procedure": "1. Set up pendulum. 2. Time 20 oscillations. 3. Repeat for different lengths.", "observations": "Table: Length L(m) | Time t(s) | Period T(s)", "questions": ["What affects period?", "Plot T^2 vs L"], "safety": "Ensure bob does not hit anyone"}}, "S5-S6": {"RC Circuit": {"objective": "To determine time constant of RC circuit", "apparatus": "Capacitor, Resistor, Voltmeter, Stopwatch", "procedure": "1. Charge capacitor. 2. Discharge through resistor. 3. Record V vs t.", "observations": "Graph: Voltage vs Time", "questions": ["Define time constant tau", "Calculate tau"], "safety": "Discharge capacitor before handling"}}},
    "Chemistry": {"S1-S4": {"Separation of Mixtures": {"objective": "To separate sand and salt mixture", "apparatus": "Beaker, Filter paper, Funnel, Bunsen burner, Evaporating dish", "procedure": "1. Add water. 2. Filter. 3. Evaporate filtrate.", "observations": "Residue: Sand. Filtrate: Salt solution", "questions": ["Name methods used"], "safety": "Wear goggles"}}, "S5-S6": {"Rate of Reaction": {"objective": "To investigate effect of temperature on rate", "apparatus": "Conical flask, Mg ribbon, HCl, Stopwatch", "procedure": "1. React Mg with HCl at different temps.", "observations": "Table: Temp | Time", "questions": ["Plot graph"], "safety": "HCl fumes are dangerous"}}},
    "Biology": {"S1-S4": {"Use of Microscope": {"objective": "To observe plant and animal cells", "apparatus": "Microscope, Onion epidermis", "procedure": "1. Place specimen. 2. Focus. 3. Draw.", "observations": "Draw and label cell parts", "questions": ["Function of nucleus"], "safety": "Clean lens"}}, "S5-S6": {"Enzyme Action": {"objective": "To investigate effect of pH on amylase", "apparatus": "Amylase, Starch, Buffer solutions", "procedure": "1. Mix at different pH.", "observations": "Table: pH | Time", "questions": ["Optimum pH"], "safety": "Sterile conditions"}}}
}

### SVG ENGINE - YOUR CORE UNCHANGED ###
def svg_header(title): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 700"><defs><marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="black"/></marker></defs><rect width="950" height="700" fill="white"/><text x="475" y="40" text-anchor="middle" font-family="Arial" font-size="24" font-weight="bold" fill="black">{title}</text>'
def svg_footer(): return '</svg>'
def render_universal_svg(raw_svg): return f'<div style="width:100%; max-width:1000px; margin:auto; background:white; padding:20px; border-radius:15px; border:4px solid #1a237e;">{raw_svg}</div>'
def draw_atom(): return svg_header("Bohr Model of Atom - S3 Chemistry") + '<circle cx="475" cy="350" r="25" fill="#d32f2f" stroke="black" stroke-width="4"/><text x="475" y="358" text-anchor="middle" fill="white" font-size="16" font-weight="bold">N</text><line x1="500" y1="350" x2="650" y2="320" stroke="black" stroke-width="3" marker-end="url(#arrowhead)"/><text x="660" y="325" font-size="18" font-weight="bold">1. Nucleus</text>' + svg_footer()
def draw_plant_cell(): return svg_header("Plant Cell - S1 Biology") + '<rect x="120" y="100" width="700" height="450" fill="#c8e6c9" stroke="black" stroke-width="5"/><circle cx="350" cy="325" r="70" fill="#ffcdd2" stroke="black" stroke-width="4"/>' + svg_footer()
def draw_circuit(): return svg_header("Simple Electric Circuit - S2 Physics") + '<line x1="180" y1="350" x2="330" y2="350" stroke="black" stroke-width="5"/><rect x="330" y="320" width="80" height="60" fill="none" stroke="black" stroke-width="5"/><circle cx="540" cy="350" r="50" fill="none" stroke="black" stroke-width="5"/>' + svg_footer()
def draw_cone(): return svg_header("Cone - S1 Mathematics") + '<ellipse cx="475" cy="480" rx="220" ry="80" fill="#bbdefb" stroke="black" stroke-width="4"/>' + svg_footer()
def draw_pendulum(): return svg_header("Simple Pendulum - S1 Physics") + '<circle cx="475" cy="150" r="8" fill="black"/><line x1="475" y1="158" x2="550" y2="420" stroke="black" stroke-width="4"/><circle cx="550" cy="420" r="30" fill="#78909c" stroke="black" stroke-width="4"/>' + svg_footer()
def draw_water_cycle(): return svg_header("Water Cycle - S1 Geography") + '<circle cx="750" cy="100" r="50" fill="yellow"/>' + svg_footer()
AUTO_DRAW_ENGINE = {"atom": draw_atom, "cell": draw_plant_cell, "circuit": draw_circuit, "cone": draw_cone, "pendulum": draw_pendulum, "water cycle": draw_water_cycle}

### CORE FUNCTIONS ###
def load_logs(): return json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []
def save_log(entry): logs = load_logs(); logs.append(entry); json.dump(logs, open(LOG_FILE,"w"))
def log_activity(user_type, action, details): save_log({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user_type, "action": action, "details": details})
def create_pdf(content, title):
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); p.setFont("Helvetica-Bold", 14); p.drawString(50,800,title); y=770; p.setFont("Helvetica", 10)
    for i,line in enumerate(content.split('\n')[:80]): p.drawString(50,y-(i*14),line[:95])
    p.save(); buffer.seek(0); return buffer

def call_groq_dual(user_prompt, mode="Smart"):
    system = SYSTEM_SMART if mode=="Smart" else SYSTEM_INSTANT
    model = AI_MODEL_SMART if mode=="Smart" else AI_MODEL_INSTANT
    tokens = 3500 if mode=="Smart" else 1200

    try:
        res = client.chat.completions.create(model=model, messages=[{"role":"system","content":system},{"role":"user","content":user_prompt}], max_tokens=tokens, temperature=0.1)
        return res.choices[0].message.content
    except Exception as e:
        return f"GROQ_ERROR: {e}"

def extract_code(raw):
    if not raw or "GROQ_ERROR" in raw: return raw
    code = re.sub(r'```python|```', '', raw).strip()
    match = re.search(r'(from matplotlib|import matplotlib|fig, ax = plt).*', code, re.DOTALL)
    return match.group(0) if match else code

def auto_render_pixel_diagram(topic, subject, level, mode="Smart"):
    st.info(f"🤖 Running {mode} Engine - Model: {AI_MODEL_SMART if mode=='Smart' else AI_MODEL_INSTANT}")
    prompt = f"Generate ONLY python matplotlib code to draw '{topic}' for {level} {subject}. MUST include: plt.savefig('diagram.png', dpi=300) and plt.close(). Use Circle Rectangle Ellipse FancyArrow. 5 numbered labels with arrows."

    raw_code = call_groq_dual(prompt, mode)
    if "GROQ_ERROR" in raw_code: return raw_code

    code = extract_code(raw_code)
    code = "from matplotlib.patches import Circle, Rectangle, Ellipse, FancyArrow\nimport matplotlib.pyplot as plt\nimport numpy as np\n" + code
    code = code.replace("/mnt/data/diagram.png", "diagram.png")

    with st.expander(f"View {mode} AI Generated Code"):
        st.code(code, language="python")

    try:
        plt.close('all')
        safe_globals = {"plt": plt, "np": np, "Circle": Circle, "Rectangle": Rectangle, "Ellipse": Ellipse, "FancyArrow": FancyArrow}
        exec(code, {"__builtins__": {}}, safe_globals)
        return "diagram.png" if os.path.exists("diagram.png") else "ERROR: No file created"
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {e}"

def generate_practical(subject, level, prac_name):
    level_group = "S1-S4" if int(level[1]) <= 4 else "S5-S6"
    data = PRACTICAL_DATABASE.get(subject,{}).get(level_group,{}).get(prac_name,{})
    if not data: return "Practical not found in database"
    prompt = f"Expand this NCDC practical into full UNEB report format: {data} for {subject} {level}"
    return call_groq_dual(prompt, "Smart")

def display_with_pdf(content, name):
    st.markdown(content)
    for f in re.findall(r'\$(.*?)\$', content): st.latex(f)
    pdf = create_pdf(content, name); st.download_button("📥 Download PDF", pdf, f"{name}.pdf", key=f"dl_{name}_{time.time()}")

### PORTALS - YOUR CORE ARCHITECTURE 100% ###
def show_student_portal():
    st.header("📚 Student Portal - S1 to S6 - NCDC PRO MODE")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tab1, tab2, tab3 = st.tabs(["🔍 Smart Search + Solver", "📖 Learn Topic", "🎨 Diagram Generator"])

    with tab1:
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="search_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="search_level")
        ask_q = st.text_area("Ask any question / Solve any problem")
        if st.button("Ask AI Brain", type="primary") and ask_q:
            log_activity("Student", "Ask Question", ask_q)
            ans = call_groq_dual(f"Use Chain of Thought. Answer step by step: {ask_q} for {level} {subject}", "Smart")
            display_with_pdf(ans, "Answer")

    with tab2:
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="learn_subj")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="learn_level")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject2][level2], key="learn_topic")
        mode = st.radio("Mode", ["📖 Theory", "🧠 AOI", "🧪 Practicals Lab", "📝 UNEB Quiz Mode", "📚 Bulk Revision"])
        log_activity("Student", "Learn Mode", mode)

        if mode == "📖 Theory" and st.button("Teach Me"):
            raw = call_groq_dual(f"Teach {topic2} step by step with examples for {level2} {subject2}", "Smart")
            display_with_pdf(raw, "Theory")
        elif mode == "🧠 AOI" and st.button("Generate Activity of Integration"):
            aoi = call_groq_dual(f"Generate NCDC Activity of Integration for {level2} {subject2} topic: {topic2}", "Smart")
            display_with_pdf(aoi, "AOI")
        elif mode == "🧪 Practicals Lab":
            prac_list = list(PRACTICAL_DATABASE.get(subject2,{}).get("S1-S4",{}).keys()) if int(level2[1])<=4 else list(PRACTICAL_DATABASE.get(subject2,{}).get("S5-S6",{}).keys())
            if not prac_list: prac_list = ["No practicals in DB"]
            prac = st.selectbox("Select Practical", prac_list)
            if st.button("Generate Practical"):
                report = generate_practical(subject2,level2,prac)
                display_with_pdf(report, "Practical")
        elif mode == "📝 UNEB Quiz Mode" and st.button("Generate Quiz"):
            quiz = call_groq_dual(f"Generate 10 UNEB ITEM/TASK/SCENARIO questions with answers on {topic2} for {level2} {subject2}", "Smart")
            display_with_pdf(quiz, "Quiz")
        elif mode == "📚 Bulk Revision" and st.button("Generate Revision"):
            rev = call_groq_dual(f"Generate full revision notes + 20 questions for {topic2} {level2} {subject2}", "Smart")
            display_with_pdf(rev, "Revision")

    with tab3:
        st.header("🎨 Diagram Generator - V3.9.9 DUAL ENGINE")
        subject3 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="svg_subj")
        level3 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="svg_level")
        topic3 = st.text_input("Describe Diagram:", "Draw atom")
        diagram_mode = st.radio("Choose Output Mode", ["1. Instant SVG [Auto Draw]", "2. HD Pixel Image [AI Smart 70B]", "3. HD Pixel Image [AI Instant 8B]"])

        if st.button("Generate Diagram", type="primary"):
            log_activity("Student", "Generate Diagram", topic3)
            if diagram_mode == "1. Instant SVG [Auto Draw]":
                topic_lower = topic3.lower()
                found = False
                for key, func in AUTO_DRAW_ENGINE.items():
                    if key in topic_lower:
                        st.markdown(render_universal_svg(func()), unsafe_allow_html=True)
                        st.success("✅ Instant SVG with labels")
                        found = True; break
                if not found: st.warning("Not in AutoDraw. Try: atom, cone, cell, circuit, pendulum, water cycle")
            else:
                m = "Smart" if "Smart" in diagram_mode else "Instant"
                img_path = auto_render_pixel_diagram(topic3, subject3, level3, m)
                if "ERROR" in str(img_path) or "GROQ_ERROR" in str(img_path): st.error(f"Rendering failed: {img_path}")
                else:
                    st.image(img_path, caption=f"HD: {topic3}", use_container_width=True)
                    with open(img_path, "rb") as file: st.download_button("📥 Download HD PNG", file, f"{topic3}.png")

def show_admin_portal():
    st.header("🏫 Admin Portal - V3.9.9")
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

st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO - V3.9.9 CORE RESTORED")
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"])
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    if user_type == "Student" and password == STUDENT_PASSWORD: st.session_state["role"] = "Student"; st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD: st.session_state["role"] = "Admin"; st.rerun()
    elif password: st.sidebar.error("Wrong password")

if st.session_state.get("role") == "Admin": show_admin_portal()
elif st.session_state.get("role") == "Student": show_student_portal()
else: st.info("Please login to continue")
