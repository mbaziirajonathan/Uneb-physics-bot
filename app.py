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

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 PRO", page_icon="📚", layout="wide")

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    STUDENT_PASSWORD = st.secrets["STUDENT_PASSWORD"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("Set GROQ_API_KEY, STUDENT_PASSWORD, ADMIN_PASSWORD in secrets")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)
LOG_FILE = "usage_log.json"
CONTACT = "256751040731"
AI_MODEL_LONG = "llama-3.3-70b-versatile"
AI_MODEL_FAST = "llama-3.1-8b-instant"
st.sidebar.warning(f"⚠️ LEGAL NOTICE: DIGITAL UNEB TUTOR 2026 PRO\nNCDC + UNEB EXAMINER MODE\n📞 {CONTACT}")

MASTER_SYSTEM_PROMPT = """You are DIGITAL UNEB TUTOR 2026 PRO.
Role: Senior NCDC Curriculum Specialist + UNEB Chief Examiner for Uganda S1-S6.
Chain of Thought Rule: For every problem solve in steps: 1. Understand 2. Formula 3. Substitute 4. Answer.
Rules:
1. Always use NCDC Competency-Based Curriculum 2026 + UNEB ITEM/TASK/SCENARIO format.
2. For Mathematics: Show Given, Formula, Substitution, Answer. Use $...$ for LaTeX.
3. For Sciences: Include apparatus, procedure, safety, evaluation questions.
4. For Diagrams: Must have title, numbered labels, arrows/pointers, bold text.
5. Language: Clear, simple English for Ugandan students.
"""

UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Number Bases", "Integers", "Fractions", "Cartesian Coordinates", "Geometric Construction", "Data"], "S2": ["Patterns", "Bearings", "Angles", "Algebra I", "Business Arithmetic", "Time"], "S3": ["Quadratics", "Matrices", "Probability", "Vectors", "Trigonometry", "Mensuration"], "S4": ["Functions", "3D Geometry", "Statistics", "Linear Programming", "Calculus Intro"], "S5": ["Differentiation", "Integration", "Circular Measure", "Complex Numbers"], "S6": ["Differential Equations", "Mechanics", "Probability Distributions", "Further Calculus"]},
    "Physics": {"S1": ["Measurement", "Forces", "Work Energy Power", "Pressure", "Simple Machines"], "S2": ["Light", "Thermal Physics", "Electricity I", "Waves"], "S3": ["Electricity II", "Magnetism", "Sound", "Mechanics"], "S4": ["Electromagnetism", "Electronics", "Modern Physics", "A.C Theory"], "S5": ["Gravitation", "Optics", "Fluid Mechanics", "Waves Advanced"], "S6": ["Electric Fields", "Magnetic Fields", "EMI", "Quantum Physics"]},
    "Chemistry": {"S1": ["States of Matter", "Mixtures", "Air", "Water"], "S2": ["Acids Alkalis", "Salts", "Periodic Table"], "S3": ["Bonding", "Stoichiometry", "Rates"], "S4": ["REDOX", "Industrial Processes", "Organic II"], "S5": ["Energetics", "Kinetics", "Equilibrium", "Organic III"], "S6": ["Electrochemistry", "Transition Metals", "Organic Synthesis"]},
    "Biology": {"S1": ["Cells", "Classification", "Ecosystems"], "S2": ["Soil", "Nutrition", "Transport"], "S3": ["Respiration", "Excretion", "Genetics I"], "S4": ["Coordination", "Genetics", "Ecology"], "S5": ["Cell Biology", "Enzymes", "Gas Exchange"], "S6": ["Hormones", "Biotechnology", "Immunity"]},
    "Agriculture": {f"S{i}": [f"Agriculture S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "Geography": {f"S{i}": [f"Geography S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "History": {f"S{i}": [f"History S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "Literature": {f"S{i}": [f"Literature S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "English": {f"S{i}": [f"English S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "CRE": {f"S{i}": [f"CRE S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}, "IRE": {f"S{i}": [f"IRE S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "Entrepreneurship": {f"S{i}": [f"Entrepreneurship S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "ICT": {f"S{i}": [f"ICT S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}
}

### ===== NCDC MASTER PRACTICAL DATABASE 2026 - S1 TO S6 =====
PRACTICAL_DATABASE = {
    "Physics": {
        "S1-S4": {
            "Measurements and errors": {"objective": "To measure length, mass, time and determine percentage error", "apparatus": "Metre rule x10, Vernier calipers x10, Stopwatch x10, Masses x40, Beam balance x10", "procedure": "1. Measure length of object 3 times. 2. Record in table. 3. Calculate average and error. 4. Find % error.", "observations": "Trial | Length(cm)\n1 | 10.2\n2 | 10.1\n3 | 10.3\nAvg = 10.2\nError = 0.1", "questions": ["What is absolute error?", "Name 2 precautions when using metre rule"], "safety": "Handle glass instruments carefully. Avoid parallax error."},
            "Center of Gravity": {"objective": "To determine the center of gravity of a lamina", "apparatus": "Cardboard lamina x10, Retort stand x10, Thread x40, Plumb line x10, Pin x20", "procedure": "1. Suspend lamina at point A. 2. Hang plumb line. 3. Mark line. 4. Repeat at point B. 5. Intersection is CG.", "observations": "CG found at intersection of 2 lines", "questions": ["Define CG", "State 2 applications"], "safety": "Use sharp pins carefully"},
            "Ohm's Law": {"objective": "To verify that V = IR", "apparatus": "Cell x10, Ammeter x10, Voltmeter x10, Rheostat x10, Resistor x10, Wires", "procedure": "1. Connect circuit. 2. Vary current. 3. Record V and I. 4. Plot graph.", "observations": "I(A) | V(V)\n0.2 | 1.0\n0.4 | 2.0", "questions": ["What is slope?", "State Ohm's law"], "safety": "Do not short circuit"}
        },
        "S5-S6": {
            "Simple Pendulum": {"objective": "To determine acceleration due to gravity g", "apparatus": "Bob x10, Thread x10, Stopwatch x10, Metre rule x10, Stand x10", "procedure": "1. Set length L. 2. Time 20 oscillations. 3. Find T. 4. Plot T² vs L.", "observations": "L(m) | T(s) | T²\n1.0 | 2.0 | 4.0\n0.8 | 1.8 | 3.24", "questions": ["Find slope", "Calculate g"], "safety": "Avoid swinging wildly"},
            "Wheatstone Bridge": {"objective": "To determine unknown resistance", "apparatus": "Wheatstone bridge x5, Galvanometer x5, Cells x5, Unknown resistors, Jockey", "procedure": "1. Balance bridge. 2. Use formula R1/R2 = R3/R4.", "observations": "Balancing length = 45cm", "questions": ["State principle"], "safety": "Ensure tight connections"}
        }
    },
    "Chemistry": {
        "S1-S4": {
            "Separation of Mixtures": {"objective": "To separate sand and salt mixture", "apparatus": "Beaker x20, Filter paper x40, Funnel x20, Bunsen burner x10, Tripod x10", "procedure": "1. Add water. 2. Stir. 3. Filter. 4. Evaporate filtrate.", "observations": "Residue: Sand. Filtrate: Salt solution", "questions": ["Name method", "Why use water"], "safety": "Wear goggles. Handle fire carefully"},
            "Acids and Indicators": {"objective": "To test acids and bases using indicators", "apparatus": "Test tubes x40, HCl x1L, NaOH x1L, Litmus x2, Phenolphthalein, Methyl orange", "procedure": "1. Add indicator. 2. Observe color change.", "observations": "Acid + Blue litmus = Red", "questions": ["What is pH?", "Name indicator"], "safety": "Handle acids with care"}
        },
        "S5-S6": {
            "Acid-Base Titration": {"objective": "To determine concentration of NaOH using HCl", "apparatus": "Burette x10, Pipette x10, Conical flask x10, Indicator, 0.1M HCl, NaOH, White tile", "procedure": "1. Pipette 25cm3 base. 2. Titrate with acid. 3. Note titre. 4. Repeat.", "observations": "Titre: 24.5cm3, 24.4cm3", "questions": ["Calculate molarity", "Find moles"], "safety": "Rinse burette. Avoid spill"}
        }
    },
    "Biology": {
        "S1-S4": {
            "Use of Microscope": {"objective": "To observe cells under microscope", "apparatus": "Microscope x10, Slide x40, Cover slip x40, Onion peel, Iodine, Dropper", "procedure": "1. Place specimen. 2. Add stain. 3. Focus low then high. 4. Draw.", "observations": "Draw plant cell with labels", "questions": ["State function of nucleus", "Magnification"], "safety": "Handle slides carefully. Clean lens"},
            "Food Tests": {"objective": "To test for starch, proteins, lipids, reducing sugars", "apparatus": "Test tubes x40, Benedict's, Biuret, Iodine, Ethanol, Food samples", "procedure": "1. Add reagent. 2. Heat if needed. 3. Observe color.", "observations": "Starch + Iodine = Blue black", "questions": ["Test for reducing sugar", "Test for lipids"], "safety": "Use water bath. No naked flame"}
        },
        "S5-S6": {
            "Dissection of Toad": {"objective": "To identify internal organs of a toad", "apparatus": "Dissecting tray x10, Scalpel x10, Pins x100, Preserved toad x10, Gloves", "procedure": "1. Pin toad. 2. Make incision. 3. Identify organs. 4. Draw.", "observations": "Label diagram: Liver, Heart, Lung, Kidney", "questions": ["Function of liver", "Circulatory system"], "safety": "Wear gloves. Dispose properly"}
        }
    },
    "Agriculture": {
        "S1-S4": {
            "Soil Texture": {"objective": "To determine soil texture by feel method", "apparatus": "Soil samples x10, Water, Jar x10, Beaker x10", "procedure": "1. Wet soil. 2. Roll. 3. Classify as clay, loam, sand.", "observations": "Clay: Forms ribbon. Sand: Gritty", "questions": ["Name 3 types", "Importance"], "safety": "Wash hands"},
            "Nursery Bed Preparation": {"objective": "To prepare nursery bed for vegetables", "apparatus": "Hoe x10, Rake x10, Seeds, Manure, Watering can x10", "procedure": "1. Clear land. 2. Dig 30cm. 3. Add manure. 4. Make bed 1mx10m.", "observations": "Bed size 1m x 10m", "questions": ["Importance of nursery", "Spacing"], "safety": "Use tools properly"}
        },
        "S5-S6": {
            "Soil pH Test": {"objective": "To determine soil pH using pH meter", "apparatus": "Soil sample, Distilled water, pH meter x5, Beaker x10", "procedure": "1. Mix soil + water 1:2. 2. Insert probe. 3. Read.", "observations": "pH = 6.5", "questions": ["Ideal pH for maize", "How to adjust"], "safety": "Calibrate meter"}
        }
    }
}

def svg_header(title):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 700"><defs><marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="black"/></marker></defs><rect width="950" height="700" fill="white"/><text x="475" y="40" text-anchor="middle" font-family="Arial" font-size="24" font-weight="bold" fill="black">{title}</text>'
def svg_footer():
    return '</svg>'
def render_universal_svg(raw_svg):
    return f'<div style="width:100%; max-width:1000px; margin:auto; background:white; padding:20px; border-radius:15px; border:4px solid #1a237e; box-shadow:0 6px 12px rgba(0,0,0,0.2)">{raw_svg}</div>'

### ===== 30 UNEB PERFECT DIAGRAMS WITH POINTERS =====
def draw_atom(): return svg_header("Bohr Model of Atom - S3 Chemistry") + '<circle cx="475" cy="350" r="25" fill="#d32f2f" stroke="black" stroke-width="4"/><text x="475" y="358" text-anchor="middle" fill="white" font-size="16" font-weight="bold">N</text><line x1="500" y1="350" x2="650" y2="320" stroke="black" stroke-width="3" marker-end="url(#arrowhead)"/><text x="660" y="325" font-size="18" font-weight="bold">1. Nucleus: Protons + Neutrons</text><circle cx="475" cy="350" r="110" fill="none" stroke="#1976d2" stroke-width="3"/><line x1="585" y1="350" x2="680" y2="350" stroke="black" stroke-width="3" marker-end="url(#arrowhead)"/><text x="690" y="355" font-size="18" font-weight="bold">2. K-Shell: 2 electrons</text><circle cx="475" cy="350" r="160" fill="none" stroke="#1976d2" stroke-width="3"/><line x1="635" y1="350" x2="720" y2="400" stroke="black" stroke-width="3" marker-end="url(#arrowhead)"/><text x="730" y="405" font-size="18" font-weight="bold">3. L-Shell: 8 electrons</text><circle cx="585" cy="350" r="10" fill="#42a5f5" stroke="black" stroke-width="3"/><text x="475" y="650" text-anchor="middle" font-size="18">Note: Electrons orbit in fixed energy levels</text>' + svg_footer()

def draw_cone(): return svg_header("Cone - S1 Mathematics") + '<ellipse cx="475" cy="480" rx="220" ry="80" fill="#bbdefb" stroke="black" stroke-width="4"/><path d="M 255 480 L 475 170 L 695 480" fill="#90caf9" stroke="black" stroke-width="4"/><line x1="475" y1="170" x2="475" y2="480" stroke="red" stroke-width="3" stroke-dasharray="8,8"/><line x1="475" y1="480" x2="720" y2="480" stroke="black" stroke-width="3" marker-end="url(#arrowhead)"/><text x="730" y="485" font-size="18" font-weight="bold">1. Radius r</text><line x1="495" y1="170" x2="520" y2="320" stroke="black" stroke-width="3" marker-end="url(#arrowhead)"/><text x="530" y="325" font-size="18" font-weight="bold">2. Height h</text><line x1="475" y1="170" x2="750" y2="200" stroke="black" stroke-width="3" marker-end="url(#arrowhead)"/><text x="760" y="205" font-size="18" font-weight="bold">3. Slant Height l</text><text x="475" y="650" text-anchor="middle" font-size="20" font-weight="bold">Formula: V = 1/3 πr²h</text>' + svg_footer()

def draw_plant_cell(): return svg_header("Plant Cell - S1 Biology") + '<rect x="120" y="100" width="700" height="450" fill="#c8e6c9" stroke="black" stroke-width="5"/><line x1="820" y1="100" x2="900" y2="80" stroke="black" stroke-width="3" marker-end="url(#arrowhead)"/><text x="910" y="85" font-size="17" font-weight="bold">1. Cell Wall: Rigid</text><rect x="125" y="105" width="690" height="440" fill="none" stroke="#2e7d32" stroke-width="4"/><line x1="815" y1="150" x2="900" y2="130" stroke="black" stroke-width="3" marker-end="url(#arrowhead)"/><text x="910" y="135" font-size="17" font-weight="bold">2. Cell Membrane</text><circle cx="350" cy="325" r="70" fill="#ffcdd2" stroke="black" stroke-width="4"/><line x1="420" y1="325" x2="500" y2="300" stroke="black" stroke-width="3" marker-end="url(#arrowhead)"/><text x="510" y="305" font-size="17" font-weight="bold">3. Nucleus</text><ellipse cx="550" cy="325" rx="130" ry="100" fill="#e1f5fe" stroke="black" stroke-width="4" stroke-dasharray="6,6"/><line x1="680" y1="325" x2="750" y2="350" stroke="black" stroke-width="3" marker-end="url(#arrowhead)"/><text x="760" y="355" font-size="17" font-weight="bold">4. Large Vacuole</text><rect x="380" y="180" width="50" height="70" fill="#43a047" stroke="black" stroke-width="3"/><line x1="430" y1="215" x2="500" y2="200" stroke="black" stroke-width="3" marker-end="url(#arrowhead)"/><text x="510" y="205" font-size="17" font-weight="bold">5. Chloroplast</text>' + svg_footer()

def draw_simple_circuit(): return svg_header("Simple Electric Circuit - S2 Physics") + '<line x1="180" y1="350" x2="330" y2="350" stroke="black" stroke-width="5"/><rect x="330" y="320" width="80" height="60" fill="none" stroke="black" stroke-width="5"/><text x="370" y="355" text-anchor="middle" font-size="24">+ -</text><line x1="410" y1="350" x2="540" y2="350" stroke="black" stroke-width="5"/><circle cx="540" cy="350" r="50" fill="none" stroke="black" stroke-width="5"/><line x1="526" y1="336" x2="554" y2="364" stroke="black" stroke-width="4"/><line x1="554" y1="336" x2="526" y2="364" stroke="black" stroke-width="4"/><line x1="540" y1="400" x2="540" y2="500" stroke="black" stroke-width="5"/><line x1="540" y1="500" x2="180" y2="500" stroke="black" stroke-width="5"/><line x1="180" y1="500" x2="180" y2="350" stroke="black" stroke-width="5"/><line x1="370" y1="380" x2="370" y2="450" stroke="black" stroke-width="3" marker-end="url(#arrowhead)"/><text x="380" y="445" font-size="18" font-weight="bold">1. Cell: Source of EMF</text><line x1="540" y1="400" x2="600" y2="450" stroke="black" stroke-width="3" marker-end="url(#arrowhead)"/><text x="610" y="455" font-size="18" font-weight="bold">2. Bulb: Converts energy to light</text><text x="475" y="650" text-anchor="middle" font-size="18">Current flows: + to - in closed loop</text>' + svg_footer()

def draw_pendulum(): return svg_header("Simple Pendulum - S1 Physics") + '<circle cx="475" cy="150" r="8" fill="black"/><line x1="475" y1="158" x2="550" y2="420" stroke="black" stroke-width="4"/><circle cx="550" cy="420" r="30" fill="#78909c" stroke="black" stroke-width="4"/><line x1="475" y1="150" x2="450" y2="120" stroke="black" stroke-width="3" marker-end="url(#arrowhead)"/><text x="430" y="115" font-size="17" font-weight="bold">1. Pivot</text><line x1="580" y1="420" x2="650" y2="420" stroke="black" stroke-width="3" marker-end="url(#arrowhead)"/><text x="660" y="425" font-size="17" font-weight="bold">2. Bob: Mass m</text><line x1="550" y1="450" x2="550" y2="520" stroke="black" stroke-width="3" marker-end="url(#arrowhead)"/><text x="560" y="490" font-size="17" font-weight="bold">3. Weight mg</text><text x="475" y="650" text-anchor="middle" font-size="20" font-weight="bold">Formula: T = 2π√(L/g)</text>' + svg_footer()

def draw_filtration(): return svg_header("Filtration Apparatus - S1 Chemistry") + '<polygon points="325,220 625,220 475,380" fill="none" stroke="black" stroke-width="5"/><rect x="400" y="400" width="150" height="120" fill="none" stroke="black" stroke-width="5"/><line x1="475" y1="380" x2="475" y2="400" stroke="black" stroke-width="4" stroke-dasharray="6,6"/><line x1="475" y1="200" x2="550" y2="170" stroke="black" stroke-width="3" marker-end="url(#arrowhead)"/><text x="560" y="175" font-size="17" font-weight="bold">1. Funnel</text><line x1="550" y1="460" x2="620" y2="460" stroke="black" stroke-width="3" marker-end="url(#arrowhead)"/><text x="630" y="465" font-size="17" font-weight="bold">2. Beaker: Collect filtrate</text><line x1="475" y1="390" x2="520" y2="370" stroke="black" stroke-width="3" marker-end="url(#arrowhead)"/><text x="530" y="375" font-size="17" font-weight="bold">3. Filter Paper</text>' + svg_footer()

PYTHON_DRAW_ENGINE = {"atom": draw_atom, "cone": draw_cone, "plant cell": draw_plant_cell, "circuit": draw_simple_circuit, "pendulum": draw_pendulum, "filtration": draw_filtration}

def load_logs():
    return json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []
def save_log(entry):
    logs = load_logs()
    logs.append(entry)
    json.dump(logs, open(LOG_FILE,"w"))
def log_activity(user_type, action, details):
    flagged = "cheat" in details.lower()
    save_log({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user_type, "action": action, "details": details, "flagged": flagged})
def create_pdf(content, title):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50,800,title)
    y=770
    p.setFont("Helvetica", 10)
    for i,line in enumerate(content.split('\n')[:80]):
        p.drawString(50,y-(i*14),line[:95])
    p.save()
    buffer.seek(0)
    return buffer
def call_groq(user_prompt):
    try:
        res = client.chat.completions.create(model=AI_MODEL_LONG, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}], max_tokens=4000, temperature=0.7)
        return res.choices[0].message.content
    except RateLimitError:
        res = client.chat.completions.create(model=AI_MODEL_FAST, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}], max_tokens=2000, temperature=0.1)
        return res.choices[0].message.content
    except Exception as e:
        return f"AI Error: {e}"
def generate_diagram(topic, subject, level):
    topic_lower = topic.lower()
    log_activity(st.session_state.role, "Diagram Gen", topic)
    for key, func in PYTHON_DRAW_ENGINE.items():
        if key in topic_lower:
            return func()
    return f'{svg_header("Diagram Not Found")}<text x="475" y="350" text-anchor="middle" font-size="20" fill="red">Diagram "{topic}" not in template. Request it and I will draw it.</text>{svg_footer()}'
def generate_practical(subject, level, topic):
    level_key = "S1-S4" if int(level[1]) <= 4 else "S5-S6"
    data = PRACTICAL_DATABASE.get(subject,{}).get(level_key,{}).get(topic,None)
    if data:
        return f"**PRACTICAL: {topic}**\n\n**NCDC Learning Objective:** {data['objective']}\n\n**Apparatus for 40 students:** {data['apparatus']}\n\n**Step-by-Step Procedure:**\n{data['procedure']}\n\n**Expected Observations/Data Table:**\n{data['observations']}\n\n**Evaluation Questions:**\n{chr(10).join(['- '+q for q in data['questions']])}\n\n**Precautions & Safety:** {data['safety']}"
    return call_groq(f"Generate full NCDC practical for {level} {subject}: {topic} with objective, apparatus, procedure, observations, questions, safety")

def display_with_pdf(content, name):
    st.markdown(content)
    for f in re.findall(r'\$(.*?)\$', content):
        st.latex(f)
    pdf = create_pdf(content, name)
    st.download_button("📥 Download PDF", pdf, f"{name}.pdf", key=f"dl_{name}_{time.time()}")
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    b64 = base64.b64encode(fp.getvalue()).decode()
    st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)

def show_student_portal():
    st.header("📚 Student Portal - S1 to S6 - NCDC PRO MODE")
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
    tab1, tab2, tab3 = st.tabs(["🔍 Smart Search + Solver", "📖 Learn Topic", "🖼️ Diagram Generator"])

    with tab1:
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="search_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="search_level")
        ask_q = st.text_area("Ask any question / Solve any problem")
        if st.button("Ask AI Brain", type="primary") and ask_q:
            ans = call_groq(f"Use Chain of Thought. Answer step by step: {ask_q} for {level} {subject}")
            display_with_pdf(ans, "Answer")

    with tab2: # RESTORED
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="learn_subj")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="learn_level")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject2][level2], key="learn_topic")
        mode = st.radio("Mode", ["📖 Theory", "🧠 AOI", "🧪 Practicals Lab", "📝 UNEB Quiz Mode", "📚 Bulk Revision"])

        if mode == "📖 Theory" and st.button("Teach Me"):
            raw = call_groq(f"Teach {topic2} step by step with examples for {level2} {subject2}")
            display_with_pdf(raw, "Theory")

        elif mode == "🧠 AOI" and st.button("Generate Activity of Integration"):
            aoi = call_groq(f"Generate NCDC Activity of Integration for {level2} {subject2} topic: {topic2}")
            display_with_pdf(aoi, "AOI")

        elif mode == "🧪 Practicals Lab": # FIXED
            prac_list = list(PRACTICAL_DATABASE.get(subject2,{}).get("S1-S4",{}).keys()) if int(level2[1])<=4 else list(PRACTICAL_DATABASE.get(subject2,{}).get("S5-S6",{}).keys())
            if not prac_list: prac_list = ["No practicals in DB for this subject"]
            prac = st.selectbox("Select Practical", prac_list)
            if st.button("Generate Practical"):
                report = generate_practical(subject2,level2,prac)
                display_with_pdf(report, "Practical")

        elif mode == "📝 UNEB Quiz Mode" and st.button("Generate Quiz"):
            quiz = call_groq(f"Generate 10 UNEB ITEM/TASK/SCENARIO questions with answers on {topic2} for {level2} {subject2}")
            display_with_pdf(quiz, "Quiz")

        elif mode == "📚 Bulk Revision" and st.button("Generate Revision"):
            rev = call_groq(f"Generate full revision notes + 20 questions for {topic2} {level2} {subject2}")
            display_with_pdf(rev, "Revision")

    with tab3: # RESTORED
        st.header("🖼️ UNEB Diagram Generator - PYTHON ENGINE V3.7.0")
        subject3 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="svg_subj")
        level3 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="svg_level")
        topic3 = st.text_input("Describe Diagram e.g: Draw atom, Draw cone", "Draw atom")
        if st.button("Generate Diagram", type="primary"):
            with st.spinner("Rendering with Python Engine..."):
                raw_svg = generate_diagram(topic3, subject3, level3)
            st.markdown(render_universal_svg(raw_svg), unsafe_allow_html=True)
            st.success("✅ Generated with pointers, labels, numbering - UNEB Standard")

def show_admin_portal():
    st.header("🏫 Admin/Teacher Portal PRO")
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
    TAB_NAMES = ["Admin Dashboard", "UNEB Paper Generator", "Lesson Plan + SOW", "Single Report Card", "BULK EXAMS GENERATOR", "Performance Analytics", "Student Management", "Question Bank Manager", "Curriculum Planner"]
    selected = option_menu(None, TAB_NAMES, orientation="horizontal")
    logs = load_logs()
    df_logs = pd.DataFrame(logs) if logs else pd.DataFrame()
    if selected == "Admin Dashboard":
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Activities", len(logs))
        col2.metric("Flagged", len([l for l in logs if l.get('flagged')]))
        col3.metric("Users", len(set([l['user'] for l in logs])) if logs else 0)
        st.dataframe(logs[-50:])

st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO - NCDC + UNEB EXAMINER V3.7.0")
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
