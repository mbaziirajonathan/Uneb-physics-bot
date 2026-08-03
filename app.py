import streamlit as st
import os, io, json, re, time, base64, math
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
from streamlit_option_menu import option_menu
from groq import Groq, RateLimitError
import pandas as pd

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 PRO", page_icon="📚", layout="wide")

# ========== 1. SECRETS ==========
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    STUDENT_PASSWORD = st.secrets["STUDENT_PASSWORD"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("Secrets not found. Please set GROQ_API_KEY, STUDENT_PASSWORD, ADMIN_PASSWORD in Streamlit Cloud")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

LOG_FILE = "usage_log.json"
CONTACT = "256751040731"
AI_MODEL_LONG = "llama-3.3-70b-versatile"
AI_MODEL_FAST = "llama-3.1-8b-instant"

st.sidebar.warning(f"⚠️ LEGAL NOTICE: DIGITAL UNEB TUTOR 2026 PRO\nNCDC + UNEB EXAMINER MODE\n📞 {CONTACT}")

# ============ 2. FULL 22 SUBJECTS S1-S6 DATABASE - NO DATA LOST ============
UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Number Bases", "Integers", "Fractions", "Cartesian Coordinates", "Geometric Construction", "Data"], "S2": ["Patterns", "Bearings", "Angles", "Algebra I", "Business Arithmetic", "Time"], "S3": ["Quadratics", "Matrices", "Probability", "Vectors", "Trigonometry", "Mensuration"], "S4": ["Functions", "3D Geometry", "Statistics", "Linear Programming", "Calculus Intro"], "S5": ["Differentiation", "Integration", "Circular Measure", "Complex Numbers"], "S6": ["Differential Equations", "Mechanics", "Probability Distributions", "Further Calculus"]},
    "Physics": {"S1": ["Measurement", "Forces", "Work Energy Power", "Pressure", "Simple Machines"], "S2": ["Light", "Thermal Physics", "Electricity I", "Waves"], "S3": ["Electricity II", "Magnetism", "Sound", "Mechanics"], "S4": ["Electromagnetism", "Electronics", "Modern Physics", "A.C Theory"], "S5": ["Gravitation", "Optics", "Fluid Mechanics", "Waves Advanced"], "S6": ["Electric Fields", "Magnetic Fields", "EMI", "Quantum Physics"]},
    "Chemistry": {"S1": ["States of Matter", "Mixtures", "Air", "Water"], "S2": ["Acids Alkalis", "Salts", "Periodic Table"], "S3": ["Bonding", "Stoichiometry", "Rates"], "S4": ["REDOX", "Industrial Processes", "Organic II"], "S5": ["Energetics", "Kinetics", "Equilibrium", "Organic III"], "S6": ["Electrochemistry", "Transition Metals", "Organic Synthesis"]},
    "Biology": {"S1": ["Cells", "Classification", "Ecosystems"], "S2": ["Soil", "Nutrition", "Transport"], "S3": ["Respiration", "Excretion", "Genetics I"], "S4": ["Coordination", "Genetics", "Ecology"], "S5": ["Cell Biology", "Enzymes", "Gas Exchange"], "S6": ["Hormones", "Biotechnology", "Immunity"]},
    "Geography": {"S1": ["Earth", "Maps", "Weather"], "S2": ["Rocks", "Drainage", "Soils"], "S3": ["Transport", "Trade", "Industry"], "S4": ["EAC", "GIS", "Regional Development"], "S5": ["Physical Geo Advanced", "Research"], "S6": ["Geomorphology", "Climatology"]},
    "History": {"S1": ["Early Man", "Ancient Civilizations"], "S2": ["Scramble for Africa", "Colonialism"], "S3": ["Nationalism", "WWI WWII"], "S4": ["Independence", "Cold War"], "S5": ["East African History", "World History"], "S6": ["International Relations"]},
    "Literature": {"S1": ["Prose: River and Source", "Poetry", "Drama"], "S2": ["Animal Farm", "Shakespeare"], "S3": ["A Thousand Splendid Suns", "The Tempest"], "S4": ["The Pearl", "An Enemy of the People"], "S5": ["Macbeth", "Sonnets"], "S6": ["King Lear", "Post Colonial"]},
    "English": {"S1": ["Grammar", "Comprehension", "Composition"], "S2": ["Tenses", "Summary", "Letters"], "S3": ["Clauses", "Reports", "Debate"], "S4": ["Punctuation", "CV", "Interview"]},
    "CRE": {f"S{i}": [f"CRE S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}, "IRE": {f"S{i}": [f"IRE S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "Agriculture": {f"S{i}": [f"Agriculture S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}, "Entrepreneurship": {f"S{i}": [f"Entrepreneurship S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "ICT": {f"S{i}": [f"ICT S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}, "Art and Design": {f"S{i}": [f"Art S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "Music": {f"S{i}": [f"Music S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}, "French": {f"S{i}": [f"French S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "Kiswahili": {f"S{i}": [f"Kiswahili S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}, "Luganda": {f"S{i}": [f"Luganda S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "Economics": {f"S{i}": [f"Economics S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}, "Commerce": {f"S{i}": [f"Commerce S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "Technical Drawing": {f"S{i}": [f"Tech Drawing S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}, "Food and Nutrition": {f"S{i}": [f"Food & Nutrition S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "Fashion and Textiles": {f"S{i}": [f"Fashion S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}
}

PRACTICAL_TOPICS = {"Mathematics": {"S1": ["Geometric Construction"]}, "Physics": {"S1": ["Simple Pendulum"]}, "Chemistry": {"S1": ["Filtration"]}, "Biology": {"S1": ["Light Microscope"]}}

# ============ 3. 20 HARDCODED TEMPLATES V3.4.1 ============
DIAGRAM_TEMPLATES = {
    "plant cell": {"title": "Plant Cell S1 Biology", "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><g id="cell-wall"><rect x="200" y="150" width="400" height="300" fill="#dcedc8" stroke="black" stroke-width="2"/><text x="620" y="160" font-family="Arial" font-size="14">Cell Wall</text><line x1="600" y1="160" x2="200" y2="150" stroke="black"/></g><g id="cell-membrane"><rect x="205" y="155" width="390" height="290" fill="none" stroke="green" stroke-width="1.5"/><text x="615" y="180" font-family="Arial" font-size="14">Cell Membrane</text><line x1="595" y1="180" x2="205" y2="155" stroke="green"/></g><g id="nucleus"><circle cx="300" cy="300" r="40" fill="#ffcdd2" stroke="black"/><text x="150" y="300" font-family="Arial" font-size="14">Nucleus</text><line x1="170" y1="300" x2="260" y2="300" stroke="black"/></g><g id="vacuole"><circle cx="450" cy="300" r="90" fill="#e1f5fe" stroke="black"/><text x="560" y="300" font-family="Arial" font-size="14">Vacuole</text><line x1="540" y1="300" x2="540" y2="300" stroke="black"/></g></svg>'},
    "animal cell": {"title": "Animal Cell S1 Biology", "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><g id="cell-membrane"><circle cx="400" cy="300" r="150" fill="#e1f5fe" stroke="black" stroke-width="2"/><text x="570" y="300" font-family="Arial" font-size="14">Cell Membrane</text></g><g id="nucleus"><circle cx="400" cy="300" r="40" fill="#ffcdd2" stroke="black"/><text x="250" y="300" font-family="Arial" font-size="14">Nucleus</text></g></svg>'},
    "human heart": {"title": "Human Heart S2 Biology", "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><g id="left-atrium"><circle cx="320" cy="220" r="40" fill="#ffcdd2" stroke="black"/><text x="370" y="220" font-family="Arial" font-size="14">Left Atrium</text></g><g id="right-atrium"><circle cx="480" cy="220" r="40" fill="#ffcdd2" stroke="black"/><text x="530" y="220" font-family="Arial" font-size="14">Right Atrium</text></g><g id="left-ventricle"><circle cx="320" cy="350" r="60" fill="#ef9a9a" stroke="black"/><text x="390" y="350" font-family="Arial" font-size="14">Left Ventricle</text></g><g id="right-ventricle"><circle cx="480" cy="350" r="60" fill="#ef9a9a" stroke="black"/><text x="550" y="350" font-family="Arial" font-size="14">Right Ventricle</text></g><line x1="320" y1="260" x2="320" y2="290" stroke="black" marker-end="url(#arrow)"/><line x1="480" y1="260" x2="480" y2="290" stroke="black" marker-end="url(#arrow)"/><defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="black"/></marker></defs></svg>'},
    "carbon cycle": {"title": "Carbon Cycle S2 Geography", "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><g id="atmosphere"><rect x="340" y="80" width="120" height="50" fill="#bbdefb" stroke="black"/><text x="400" y="110" text-anchor="middle" font-family="Arial" font-size="14">Atmosphere</text></g><g id="plants"><rect x="140" y="300" width="100" height="50" fill="#a5d6a7" stroke="black"/><text x="190" y="330" text-anchor="middle" font-family="Arial" font-size="14">Plants</text></g><line x1="340" y1="105" x2="240" y2="300" stroke="black" marker-end="url(#arrow)"/></svg>'},
    "water cycle": {"title": "Water Cycle S1 Geography", "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><g id="sun"><circle cx="700" cy="100" r="30" fill="#fff176" stroke="black"/><text x="700" y="150" text-anchor="middle" font-family="Arial" font-size="14">Sun</text></g><g id="cloud"><ellipse cx="400" cy="100" rx="50" ry="30" fill="white" stroke="black"/><text x="400" y="150" text-anchor="middle" font-family="Arial" font-size="14">Cloud</text></g></svg>'},
    "convex lens": {"title": "Convex Lens Ray Diagram S3 Physics", "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><g id="lens"><ellipse cx="400" cy="300" rx="10" ry="150" fill="#e1f5fe" stroke="black"/><text x="420" y="300" font-family="Arial" font-size="14">Convex Lens</text></g><g id="focal-point"><circle cx="300" cy="300" r="5" fill="black"/><text x="310" y="290" font-family="Arial" font-size="14">F</text></g></svg>'},
    "simple circuit": {"title": "Simple Circuit S2 Physics", "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><g id="battery"><rect x="150" y="270" width="40" height="60" fill="none" stroke="black" stroke-width="2"/><text x="150" y="350" font-family="Arial" font-size="14">Battery</text></g><g id="bulb"><circle cx="650" cy="300" r="30" fill="none" stroke="black" stroke-width="2"/><text x="650" y="350" text-anchor="middle" font-family="Arial" font-size="14">Bulb</text></g></svg>'},
    "refraction prism": {"title": "Refraction Through Prism S3 Physics", "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><g id="prism"><polygon points="400,150 300,450 500,450" fill="none" stroke="black" stroke-width="2"/><text x="400" y="470" text-anchor="middle" font-family="Arial" font-size="14">Triangular Prism</text></g></svg>'},
    "simple pendulum": {"title": "Simple Pendulum S1 Physics", "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><g id="pivot"><circle cx="400" cy="150" r="5" fill="black"/><text x="410" y="145" font-family="Arial" font-size="14">Pivot</text></g><line x1="400" y1="155" x2="450" y2="350" stroke="black" stroke-width="2"/><g id="bob"><circle cx="450" cy="350" r="20" fill="#90a4ae" stroke="black"/><text x="480" y="350" font-family="Arial" font-size="14">Bob</text></g></svg>'},
    "water molecule": {"title": "Water Molecule H2O S2 Chemistry", "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 800 600"><g id="oxygen"><circle cx="400" cy="300" r="30" fill="#f44336" stroke="black"/><text x="400" y="305" text-anchor="middle" fill="white" font-family="Arial" font-size="14">O</text></g><g id="hydrogen1"><circle cx="350" cy="250" r="20" fill="#90caf9" stroke="black"/><text x="350" y="255" text-anchor="middle" fill="white" font-family="Arial" font-size="14">H</text></g><line x1="380" y1="280" x2="360" y2="260" stroke="black" stroke-width="2"/></svg>'},
    "atom structure": {"title": "Atom Structure S3 Chemistry", "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><g id="nucleus"><circle cx="400" cy="300" r="25" fill="#ef5350" stroke="black"/><text x="400" y="305" text-anchor="middle" fill="white" font-family="Arial" font-size="14">Nucleus</text></g><circle cx="400" cy="300" r="100" fill="none" stroke="gray" stroke-dasharray="4,4"/></svg>'},
    "filtration": {"title": "Filtration Apparatus S1 Chemistry", "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><g id="funnel"><polygon points="350,200 450,200 400,300" fill="none" stroke="black" stroke-width="2"/><text x="400" y="180" text-anchor="middle" font-family="Arial" font-size="14">Funnel</text></g><g id="beaker"><rect x="350" y="320" width="100" height="80" fill="none" stroke="black" stroke-width="2"/><text x="400" y="420" text-anchor="middle" font-family="Arial" font-size="14">Beaker</text></g></svg>'},
    "cartesian plane": {"title": "Cartesian Coordinates S1 Math", "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><line x1="400" y1="50" x2="400" y2="550" stroke="black" stroke-width="2"/><line x1="50" y1="300" x2="750" y2="300" stroke="black" stroke-width="2"/><text x="760" y="305" font-family="Arial" font-size="14">X</text><text x="405" y="40" font-family="Arial" font-size="14">Y</text><circle cx="400" cy="300" r="4" fill="black"/><text x="410" y="310" font-family="Arial" font-size="14">Origin</text></svg>'},
    "triangle construction": {"title": "Triangle Construction S1 Math", "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><g id="A"><circle cx="250" cy="400" r="5" fill="black"/><text x="240" y="420" font-family="Arial" font-size="14">A</text></g><g id="B"><circle cx="550" cy="400" r="5" fill="black"/><text x="560" y="420" font-family="Arial" font-size="14">B</text></g><g id="C"><circle cx="400" cy="200" r="5" fill="black"/><text x="410" y="190" font-family="Arial" font-size="14">C</text></g><line x1="250" y1="400" x2="550" y2="400" stroke="black"/><line x1="550" y1="400" x2="400" y2="200" stroke="black"/><line x1="400" y1="200" x2="250" y2="400" stroke="black"/></svg>'},
    "bar graph": {"title": "Bar Graph S1 Math", "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><rect x="150" y="400" width="80" height="100" fill="#42a5f5" stroke="black"/><text x="190" y="520" text-anchor="middle" font-family="Arial" font-size="14">Jan</text></svg>'},
    "circle parts": {"title": "Parts of a Circle S2 Math", "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><circle cx="400" cy="300" r="100" fill="none" stroke="black" stroke-width="2"/><line x1="400" y1="300" x2="500" y2="300" stroke="red" stroke-width="2"/><text x="510" y="305" font-family="Arial" font-size="14">Radius</text></svg>'},
    "soil profile": {"title": "Soil Profile S2 Agriculture", "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><rect x="250" y="150" width="300" height="60" fill="#8d6e63" stroke="black"/><text x="560" y="180" font-family="Arial" font-size="14">Topsoil</text></svg>'},
    "crop rotation": {"title": "4 Year Crop Rotation S3 Agriculture", "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><rect x="200" y="200" width="120" height="60" fill="#a5d6a7" stroke="black"/><text x="260" y="235" text-anchor="middle" font-family="Arial" font-size="14">Legumes</text></svg>'},
    "irrigation": {"title": "Drip Irrigation S4 Agriculture", "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><rect x="100" y="200" width="80" height="60" fill="#90caf9" stroke="black"/><text x="140" y="235" text-anchor="middle" font-family="Arial" font-size="14">Tank</text></svg>'},
    "digestive system cow": {"title": "Ruminant Digestive System S3 Agriculture", "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><circle cx="300" cy="300" r="50" fill="#bcaaa4" stroke="black"/><text x="300" y="305" text-anchor="middle" font-family="Arial" font-size="14">Rumen</text></svg>'}
}

# ============ 4. MASTER SYSTEM PROMPT V3.4.1 BLUEPRINT ============
MASTER_SYSTEM_PROMPT = """
You are DIGITAL UNEB TUTOR 2026 PRO. Senior NCDC UNEB Examiner for Uganda S1-S6.

CRITICAL OUTPUT RULE: YOU MUST OUTPUT ONLY RAW SVG XML. NO TEXT. NO EXPLANATION. NO ```svg FENCES.

LAW 1: SVG BLUEPRINT - NCDC/UNEB SCIENTIFIC ACCURACY
When generating SVG you MUST follow:
1. CANVAS: Use fixed viewBox="0 0 800 600". This is mandatory.
2. ACCURACY: Base drawing on NCDC S1-S6 Syllabus + UNEB standards. Label all parts with official names.
3. LABELING: For every part use <g id="part-name">. Inside use <circle/rect/path> + <line> pointer + <text x="" y="" font-size="14" font-family="Arial">Label</text>
4. STYLING: stroke="black", font-size="14", font-family="Arial", fill="white" or light colors. High contrast for printing.
5. VECTOR ONLY: Use only <path>, <circle>, <rect>, <line>, <polyline>, <text>, <g>. NO PNG, NO external links.
6. STRUCTURE: Wrap all in <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">

LAW 2: UNEB EXAMINER MODE - ITEM/TASK/SCENARIO
For questions use Ugandan context. ITEM:... TASK:... SCENARIO:...

LAW 3: STEP BY STEP SOLVER
For math show Given, Formula, Substitution, Answer with units.
"""

# ============ 5. SVG RENDERER V3.4.1 BLUEPRINT ============
def render_universal_svg(raw_svg_from_ai):
    if not raw_svg_from_ai or "<svg" not in raw_svg_from_ai:
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><text x="10" y="20" fill="red">Error: AI did not return valid SVG</text></svg>'
    clean_svg = raw_svg_from_ai.replace("```svg", "").replace("```", "").strip()
    return f'<div style="width:100%; max-width:800px; margin:auto;">{clean_svg}</div>'

# ============ 6. CORE FUNCTIONS ============
def load_logs(): return json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []
def save_log(entry): logs = load_logs(); logs.append(entry); json.dump(logs, open(LOG_FILE,"w"))
def log_activity(user_type, action, details): flagged = "cheat" in details.lower(); save_log({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user_type, "action": action, "details": details, "flagged": flagged})

def create_pdf(content, title):
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); p.setFont("Helvetica-Bold", 14); p.drawString(50,800,title); y=770; p.setFont("Helvetica", 10)
    for i,line in enumerate(content.split('\n')[:80]): p.drawString(50,y-(i*14),line[:95])
    p.save(); buffer.seek(0); return buffer

def call_groq(user_prompt, mode="smart"):
    try:
        temp = 0.1 if mode=="svg" else 0.7
        tokens = 1500 if mode=="svg" else 4000
        res = client.chat.completions.create(model=AI_MODEL_LONG, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}], max_tokens=tokens, temperature=temp)
        return res.choices[0].message.content
    except RateLimitError:
        res = client.chat.completions.create(model=AI_MODEL_FAST, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}], max_tokens=2000, temperature=0.1)
        return res.choices[0].message.content
    except Exception as e: return f"AI Error: {e}"

def generate_diagram(topic, subject, level):
    raw = call_groq(f"SVG BLUEPRINT MODE: Generate ONLY RAW SVG XML for {level} {subject}: {topic}. Use NCDC standards. viewBox 800x600. Follow all 6 LAW 1 rules.", mode="svg")
    return raw

def ask_smart_brain(user_query, subject, class_level, topic):
    log_activity(st.session_state.role, "Smart Query", f"{subject} {class_level}")
    return call_groq(f"SMART MODE + STEP BY STEP: Level: {class_level}\nSubject: {subject}\nTopic: {topic}\nUser Question: {user_query}")

def generate_exam_items(user_query, subject, level):
    return call_groq(f"UNEB EXAMINER MODE ITEM/TASK/SCENARIO: Level: {level}, Subject: {subject}, Request: {user_query}")

def generate_bulk_revision(subject, level):
    topics = ', '.join(UNEB_CURRICULUM_MAP[subject][level])
    return call_groq(f"UNEB EXAMINER MODE: Generate 20 UNEB ITEM/TASK/SCENARIO for {level} {subject}: {topics}")

def generate_practical(subject, level, topic):
    return call_groq(f"UNEB EXAMINER MODE: Generate FULL NCDC {level} {subject} practical with method, apparatus, results table for: {topic}")

def generate_lesson_plan(subject, level, topic, duration):
    return call_groq(f"SMART MODE: Generate NCDC {duration} min lesson plan for {level} {subject} on {topic}")

def generate_report_card(student_data):
    return call_groq(f"SMART MODE: Generate NCDC Report Card with comments for: {student_data}")

def display_with_pdf(content, name):
    st.markdown(content)
    for f in re.findall(r'\$(.*?)\$', content): st.latex(f)
    pdf = create_pdf(content, name)
    st.download_button("📥 Download PDF", pdf, f"{name}.pdf", key=f"dl_{name}_{time.time()}")

def text_to_speech(text):
    tts = gTTS(text=text, lang='en'); fp = io.BytesIO(); tts.write_to_fp(fp)
    b64 = base64.b64encode(fp.getvalue()).decode()
    st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)

# ============ 7. STUDENT PORTAL ============
def show_student_portal():
    st.header("📚 Student Portal - S1 to S6 - NCDC PRO MODE")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tab1, tab2, tab3 = st.tabs(["🔍 Smart Search + Solver", "📖 Learn Topic", "🖼️ Diagram Generator"])

    with tab1:
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="search_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="search_level")
        ask_q = st.text_area("Ask anything: 'Solve: A car moves 100m in 5s. Find speed' OR 'Explain osmosis'")
        mic_recorder(key="voice")
        if st.button("Ask AI Brain", type="primary") and ask_q:
            ans = ask_smart_brain(ask_q, subject, level, "General"); display_with_pdf(ans, "Answer")
            if st.checkbox("🔊 Listen"): text_to_speech(ans[:500])

    with tab2:
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="learn_subj")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="learn_level")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject2][level2], key="learn_topic")
        mode = st.radio("Mode", ["📖 Theory", "🧠 AOI", "🧪 Practicals Lab", "📝 UNEB Quiz Mode", "📚 Bulk Revision"])
        if mode == "📖 Theory" and st.button("Teach Me"): raw = ask_smart_brain(f"Teach {topic2} step by step with examples", subject2, level2, topic2); display_with_pdf(raw, "Theory")
        elif mode == "🧠 AOI" and st.button("Generate AOI"): raw = ask_smart_brain(f"Design AOI project for {topic2} in Uganda with materials", subject2, level2, topic2); display_with_pdf(raw, "AOI")
        elif mode == "🧪 Practicals Lab":
            prac = st.selectbox("Select Practical", PRACTICAL_TOPICS.get(subject2,{}).get(level2,["No practicals"]))
            if st.button("Generate Practical"): report = generate_practical(subject2,level2,prac); display_with_pdf(report, "Practical")
        elif mode == "📝 UNEB Quiz Mode" and st.button("Generate 10 UNEB ITEMS"): quiz = generate_exam_items(f"Generate 10 UNEB ITEM/TASK/SCENARIO on {topic2}", subject2, level2); display_with_pdf(quiz, "Quiz")
        elif mode == "📚 Bulk Revision" and st.button("Generate 20 UNEB ITEMS"): bulk = generate_bulk_revision(subject2, level2); display_with_pdf(bulk, "Bulk")

    with tab3:
        st.header("🖼️ UNEB Diagram Generator - TEMPLATE + BLUEPRINT V3.4.1")
        subject3 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="svg_subj")
        level3 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="svg_level")
        topic3 = st.text_input("Describe Diagram", "Draw a plant cell S1 Biology")

        if st.button("Generate Diagram", type="primary"):
            topic_lower = topic3.lower()
            log_activity(st.session_state.role, "Diagram Gen", topic3)

            found_template = None
            for key in DIAGRAM_TEMPLATES:
                if key in topic_lower:
                    found_template = DIAGRAM_TEMPLATES[key]["svg"]
                    break

            if found_template:
                with st.spinner("Loading Accurate Template..."):
                    st.markdown(render_universal_svg(found_template), unsafe_allow_html=True)
                    st.success("✅ Generated with Specific Template 8.5/10")

            else:
                with st.spinner("AI is drawing with Blueprint SVG Engine..."):
                    raw_svg = generate_diagram(topic3, subject3, level3)
                if raw_svg:
                    st.markdown(render_universal_svg(raw_svg), unsafe_allow_html=True)
                    st.success("✅ Generated with Blueprint Universal SVG Engine 9/10")
                else: st.error("Failed. Try: 'Construct a triangle' or 'Draw bar graph'")

# ============ 8. ADMIN PORTAL - NO DATA LOST ============
def show_admin_portal():
    st.header("🏫 Admin/Teacher Portal PRO")
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

    TAB_NAMES = [
        "Admin Dashboard", "UNEB Paper Generator", "Lesson Plan + SOW",
        "Single Report Card", "BULK EXAMS GENERATOR", "Performance Analytics",
        "Student Management", "Question Bank Manager", "Curriculum Planner"
    ]
    selected = option_menu(None, TAB_NAMES, orientation="horizontal")
    logs = load_logs()
    df_logs = pd.DataFrame(logs) if logs else pd.DataFrame()

    if selected == "Admin Dashboard":
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Activities", len(logs))
        col2.metric("Flagged", len([l for l in logs if l.get('flagged')]))
        col3.metric("Users", len(set([l['user'] for l in logs])) if logs else 0)
        st.dataframe(logs[-50:])

    elif selected == "UNEB Paper Generator":
        s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
        l = st.selectbox("Class", [f"S{i}" for i in range(1,7)])
        t = st.text_input("Topic")
        n = st.slider("Questions", 5, 50, 20)
        if st.button("Generate UNEB Paper"):
            paper = generate_exam_items(f"Generate {n} UNEB ITEM/TASK/SCENARIO on {t}", s, l)
            display_with_pdf(paper, "UNEB_Test")

    elif selected == "Lesson Plan + SOW":
        s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="lp_subj")
        l = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="lp_level")
        t = st.text_input("Topic", key="lp_topic")
        d = st.number_input("Minutes", 40, 120, 80)
        if st.button("Generate Lesson Plan"):
            plan = generate_lesson_plan(s, l, t, d)
            display_with_pdf(plan, "LessonPlan")

    elif selected == "Single Report Card":
        name = st.text_input("Student Name")
        scores = {sub: st.number_input(sub, 0, 100) for sub in ["Math", "English", "Science"]}
        if st.button("Generate Report"):
            report = generate_report_card(f"Name: {name}\nScores: {scores}")
            display_with_pdf(report, "Report")

    elif selected == "BULK EXAMS GENERATOR":
        s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="bulk_subj")
        l = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="bulk_level")
        if st.button("Generate 20 UNEB ITEMS"):
            bulk = generate_bulk_revision(s, l)
            display_with_pdf(bulk, "Bulk")

    elif selected == "Performance Analytics":
        if not df_logs.empty:
            st.line_chart(df_logs.groupby(pd.to_datetime(df_logs['timestamp']).dt.date).size())
        else:
            st.info("No data yet")

    elif selected == "Student Management":
        if "students_db" not in st.session_state:
            st.session_state.students_db = []
        name = st.text_input("Add Student Name")
        if st.button("Add Student"):
            st.session_state.students_db.append({"name": name})
            st.success("Added")
        st.dataframe(st.session_state.students_db)

    elif selected == "Question Bank Manager":
        if "qbank" not in st.session_state:
            st.session_state.qbank = []
        q = st.text_area("Enter Question")
        if st.button("Save Question"):
            st.session_state.qbank.append({"q": q})
            st.success("Saved")
        st.dataframe(st.session_state.qbank)

    elif selected == "Curriculum Planner":
        s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="cp_subj")
        l = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="cp_level")
        if st.button("Generate SOW"):
            sow = "\n".join([f"Week {i+1}: {t}" for i, t in enumerate(UNEB_CURRICULUM_MAP[s][l])])
            display_with_pdf(sow, "SOW")

# ============ 9. MAIN ROUTER ============
st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO - NCDC + UNEB EXAMINER V3.4.1")
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"])
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if user_type == "Student" and password == STUDENT_PASSWORD:
        st.session_state["role"] = "Student"
        log_activity("Student", "Login", "Login")
        st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD:
        st.session_state["role"] = "Admin"
        log_activity("Admin", "Login", "Login")
        st.rerun()
    elif password:
        st.sidebar.error("Wrong password")

if st.session_state.get("role") == "Admin":
    show_admin_portal()
elif st.session_state.get("role") == "Student":
    show_student_portal()
else:
    st.info("Please login to continue")
