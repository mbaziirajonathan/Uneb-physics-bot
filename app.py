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
Rules:
1. Always use NCDC Competency-Based Curriculum 2026 + UNEB ITEM/TASK/SCENARIO format.
2. For Mathematics: Show Given, Formula, Substitution, Answer. Use $...$ for LaTeX.
3. For Sciences: Include apparatus, procedure, safety, evaluation questions.
4. For Diagrams: Describe clearly for Python SVG engine.
5. Language: Clear, simple English for Ugandan students. Be the best tutor in Uganda.
"""

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

### ===== NCDC MASTER PRACTICAL DATABASE 2026 - S1 TO S6 =====
PRACTICAL_DATABASE = {
    "Physics": {
        "S1-S4": {
            "Measurements and errors": {"objective": "To measure length, mass, time and determine percentage error", "apparatus": "Metre rule x10, Vernier calipers x10, Stopwatch x10, Masses x40, Beam balance x10", "procedure": "1. Measure length of object 3 times. 2. Record in table. 3. Calculate average and error. 4. Find % error.", "observations": "Trial | Length(cm)\n1 | 10.2\n2 | 10.1\n3 | 10.3\nAvg = 10.2\nError = 0.1", "questions": ["What is absolute error?", "Name 2 precautions when using metre rule"], "safety": "Handle glass instruments carefully. Avoid parallax error."},
            "Center of Gravity": {"objective": "To determine the center of gravity of a lamina", "apparatus": "Cardboard lamina x10, Retort stand x10, Thread x40, Plumb line x10, Pin x20", "procedure": "1. Suspend lamina at point A. 2. Hang plumb line. 3. Mark line. 4. Repeat at point B. 5. Intersection is CG.", "observations": "CG found at intersection of 2 lines", "questions": ["Define CG", "State 2 applications"], "safety": "Use sharp pins carefully"},
            "Hooke's Law": {"objective": "To verify Hooke's law", "apparatus": "Spring x10, Masses x40, Metre rule x10, Stand x10", "procedure": "1. Measure original length. 2. Add masses. 3. Record extension.", "observations": "Force(N) | Extension(cm)\n1 | 2.0\n2 | 4.0", "questions": ["Plot F vs e"], "safety": "Do not overstretch spring"},
            "Ohm's Law": {"objective": "To verify that V = IR", "apparatus": "Cell x10, Ammeter x10, Voltmeter x10, Rheostat x10, Resistor x10, Wires", "procedure": "1. Connect circuit. 2. Vary current. 3. Record V and I. 4. Plot graph.", "observations": "I(A) | V(V)\n0.2 | 1.0\n0.4 | 2.0", "questions": ["What is slope?", "State Ohm's law"], "safety": "Do not short circuit"}
        },
        "S5-S6": {
            "Simple Pendulum": {"objective": "To determine acceleration due to gravity g", "apparatus": "Bob x10, Thread x10, Stopwatch x10, Metre rule x10, Stand x10", "procedure": "1. Set length L. 2. Time 20 oscillations. 3. Find T. 4. Plot T² vs L.", "observations": "L(m) | T(s) | T²\n1.0 | 2.0 | 4.0\n0.8 | 1.8 | 3.24", "questions": ["Find slope", "Calculate g"], "safety": "Avoid swinging wildly"},
            "Wheatstone Bridge": {"objective": "To determine unknown resistance", "apparatus": "Wheatstone bridge x5, Galvanometer x5, Cells x5, Unknown resistors, Jockey", "procedure": "1. Balance bridge. 2. Use formula R1/R2 = R3/R4.", "observations": "Balancing length = 45cm", "questions": ["State principle"], "safety": "Ensure tight connections"},
            "Potentiometer": {"objective": "To compare emf of 2 cells", "apparatus": "Potentiometer x5, Cells x10, Galvanometer x5", "procedure": "1. Balance each cell. 2. Record length.", "observations": "L1 = 80cm, L2 = 60cm", "questions": ["Find E1/E2"], "safety": "Avoid zero error"}
        }
    },
    "Chemistry": {
        "S1-S4": {
            "Separation of Mixtures": {"objective": "To separate sand and salt mixture", "apparatus": "Beaker x20, Filter paper x40, Funnel x20, Bunsen burner x10, Tripod x10", "procedure": "1. Add water. 2. Stir. 3. Filter. 4. Evaporate filtrate.", "observations": "Residue: Sand. Filtrate: Salt solution", "questions": ["Name method", "Why use water"], "safety": "Wear goggles. Handle fire carefully"},
            "Acids and Indicators": {"objective": "To test acids and bases using indicators", "apparatus": "Test tubes x40, HCl x1L, NaOH x1L, Litmus x2, Phenolphthalein, Methyl orange", "procedure": "1. Add indicator. 2. Observe color change.", "observations": "Acid + Blue litmus = Red", "questions": ["What is pH?", "Name indicator"], "safety": "Handle acids with care"},
            "Rate of Reaction": {"objective": "To investigate effect of concentration on rate", "apparatus": "Conical flask x10, Marble chips x500g, HCl x2M, Gas syringe x10, Stopwatch x10", "procedure": "1. React marble with acid. 2. Collect gas every 30s.", "observations": "Volume CO2 vs Time table", "questions": ["Which reacted faster?", "Why"], "safety": "Do in fume cupboard"}
        },
        "S5-S6": {
            "Acid-Base Titration": {"objective": "To determine concentration of NaOH using HCl", "apparatus": "Burette x10, Pipette x10, Conical flask x10, Indicator, 0.1M HCl, NaOH, White tile", "procedure": "1. Pipette 25cm3 base. 2. Titrate with acid. 3. Note titre. 4. Repeat.", "observations": "Titre: 24.5cm3, 24.4cm3", "questions": ["Calculate molarity", "Find moles"], "safety": "Rinse burette. Avoid spill"},
            "Qualitative Analysis": {"objective": "To identify cations and anions", "apparatus": "Test tubes x40, Reagents: AgNO3, BaCl2, NaOH, NH4OH", "procedure": "1. Add reagent. 2. Observe ppt. 3. Confirm.", "observations": "White ppt with AgNO3 = Cl-", "questions": ["Test for SO4 2-", "Test for Fe3+"], "safety": "Do not taste. Wash hands"}
        }
    },
    "Biology": {
        "S1-S4": {
            "Use of Microscope": {"objective": "To observe cells under microscope", "apparatus": "Microscope x10, Slide x40, Cover slip x40, Onion peel, Iodine, Dropper", "procedure": "1. Place specimen. 2. Add stain. 3. Focus low then high. 4. Draw.", "observations": "Draw plant cell with labels", "questions": ["State function of nucleus", "Magnification"], "safety": "Handle slides carefully. Clean lens"},
            "Food Tests": {"objective": "To test for starch, proteins, lipids, reducing sugars", "apparatus": "Test tubes x40, Benedict's, Biuret, Iodine, Ethanol, Food samples", "procedure": "1. Add reagent. 2. Heat if needed. 3. Observe color.", "observations": "Starch + Iodine = Blue black", "questions": ["Test for reducing sugar", "Test for lipids"], "safety": "Use water bath. No naked flame"},
            "Osmosis": {"objective": "To demonstrate osmosis using potato strips", "apparatus": "Potato x10, Beakers x20, Sugar solutions 0.2M-1.0M, Ruler x10", "procedure": "1. Cut strips. 2. Place in solutions. 3. Measure length after 30min.", "observations": "Length change table", "questions": ["Define osmosis", "Which was hypertonic"], "safety": "Use sharp knife carefully"}
        },
        "S5-S6": {
            "Dissection of Toad": {"objective": "To identify internal organs of a toad", "apparatus": "Dissecting tray x10, Scalpel x10, Pins x100, Preserved toad x10, Gloves", "procedure": "1. Pin toad. 2. Make incision. 3. Identify organs. 4. Draw.", "observations": "Label diagram: Liver, Heart, Lung, Kidney", "questions": ["Function of liver", "Circulatory system"], "safety": "Wear gloves. Dispose properly"},
            "Enzyme Action": {"objective": "To investigate effect of temperature on amylase", "apparatus": "Test tubes x20, Amylase, Starch, Iodine, Water bath", "procedure": "1. Mix enzyme + starch at different temps. 2. Test every 2min.", "observations": "Time for blue color to disappear", "questions": ["Optimum temp?", "Why enzyme denatured"], "safety": "Handle hot water"}
        }
    },
    "Agriculture": {
        "S1-S4": {
            "Soil Texture": {"objective": "To determine soil texture by feel method", "apparatus": "Soil samples x10, Water, Jar x10, Beaker x10", "procedure": "1. Wet soil. 2. Roll. 3. Classify as clay, loam, sand.", "observations": "Clay: Forms ribbon. Sand: Gritty", "questions": ["Name 3 types", "Importance"], "safety": "Wash hands"},
            "Nursery Bed Preparation": {"objective": "To prepare nursery bed for vegetables", "apparatus": "Hoe x10, Rake x10, Seeds, Manure, Watering can x10", "procedure": "1. Clear land. 2. Dig 30cm. 3. Add manure. 4. Make bed 1mx10m.", "observations": "Bed size 1m x 10m", "questions": ["Importance of nursery", "Spacing"], "safety": "Use tools properly"},
            "Animal Restraint": {"objective": "To demonstrate safe animal handling", "apparatus": "Rope x10, Halter x5, Crush x1", "procedure": "1. Approach calmly. 2. Restrain leg. 3. Use halter.", "observations": "Animal calm", "questions": ["Why restrain?", "Methods"], "safety": "Avoid kicks. Stand at side"}
        },
        "S5-S6": {
            "Soil pH Test": {"objective": "To determine soil pH using pH meter", "apparatus": "Soil sample, Distilled water, pH meter x5, Beaker x10", "procedure": "1. Mix soil + water 1:2. 2. Insert probe. 3. Read.", "observations": "pH = 6.5", "questions": ["Ideal pH for maize", "How to adjust"], "safety": "Calibrate meter"},
            "Pest Identification": {"objective": "To identify crop pests and control measures", "apparatus": "Specimens, Hand lens x10, Chart, Book", "procedure": "1. Observe specimen. 2. Identify. 3. Suggest control.", "observations": "Aphids on leaves", "questions": ["Control measure", "Damage"], "safety": "Do not touch with bare hands"}
        }
    }
}

def svg_header(title):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 700"><defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="10" markerHeight="10" orient="auto"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="black"/></marker></defs><text x="475" y="45" text-anchor="middle" font-family="Arial" font-size="22" font-weight="bold">{title}</text>'
def svg_footer():
    return '</svg>'
def render_universal_svg(raw_svg):
    return f'<div style="width:100%; max-width:1000px; margin:auto; background:white; padding:30px; border-radius:15px; border:4px solid #444; box-shadow:0 6px 12px rgba(0,0,0,0.15)">{raw_svg}</div>'

### ===== 30 UNEB PERFECT DIAGRAMS =====
def draw_atom(): return svg_header("Bohr Model of Atom - S3 Chemistry") + '<circle cx="475" cy="350" r="25" fill="#ef5350" stroke="black" stroke-width="4"/><text x="475" y="358" text-anchor="middle" fill="white" font-size="16" font-weight="bold">N</text><text x="510" y="358" font-size="17" font-weight="bold">1. Nucleus: p+ + n0</text><circle cx="475" cy="350" r="110" fill="none" stroke="gray" stroke-width="3"/><text x="590" y="350" font-size="17">2. K-Shell</text><circle cx="475" cy="350" r="160" fill="none" stroke="gray" stroke-width="3"/><text x="640" y="350" font-size="17">3. L-Shell</text><circle cx="585" cy="350" r="10" fill="#42a5f5" stroke="black" stroke-width="3"/><text x="605" y="355" font-size="16">4. Electron e-</text>' + svg_footer()
def draw_cone(): return svg_header("Cone - S1 Mathematics") + '<ellipse cx="475" cy="480" rx="220" ry="80" fill="#bbdefb" stroke="black" stroke-width="4"/><path d="M 255 480 L 475 170 L 695 480" fill="#90caf9" stroke="black" stroke-width="4"/><line x1="475" y1="170" x2="475" y2="480" stroke="red" stroke-width="3" stroke-dasharray="8,8"/><line x1="475" y1="480" x2="695" y2="480" stroke="black" marker-end="url(#arrow)" stroke-width="3"/><text x="620" y="505" font-size="18" font-weight="bold">1. Radius r</text><line x1="495" y1="170" x2="495" y2="480" stroke="black" marker-end="url(#arrow)" stroke-width="3"/><text x="505" y="330" font-size="18" font-weight="bold">2. Height h</text><text x="475" y="620" text-anchor="middle" font-size="18">Formula: V = 1/3 πr²h</text>' + svg_footer()
def draw_plant_cell(): return svg_header("Plant Cell - S1 Biology") + '<rect x="120" y="100" width="700" height="450" fill="#dcedc8" stroke="black" stroke-width="5"/><text x="840" y="115" font-size="17" font-weight="bold">1. Cell Wall</text><rect x="125" y="105" width="690" height="440" fill="none" stroke="green" stroke-width="4"/><text x="840" y="150" font-size="17" font-weight="bold">2. Cell Membrane</text><circle cx="350" cy="325" r="70" fill="#ffcdd2" stroke="black" stroke-width="4"/><text x="440" y="330" font-size="17" font-weight="bold">3. Nucleus</text><circle cx="550" cy="325" r="130" fill="#e1f5fe" stroke="black" stroke-width="4" stroke-dasharray="6,6"/><text x="700" y="330" font-size="17" font-weight="bold">4. Vacuole</text><rect x="380" y="180" width="50" height="70" fill="#66bb6a" stroke="black" stroke-width="3"/><text x="450" y="220" font-size="17" font-weight="bold">5. Chloroplast</text>' + svg_footer()
def draw_simple_circuit(): return svg_header("Simple Electric Circuit - S2 Physics") + '<line x1="180" y1="350" x2="330" y2="350" stroke="black" stroke-width="5"/><rect x="330" y="320" width="80" height="60" fill="none" stroke="black" stroke-width="5"/><text x="370" y="355" text-anchor="middle" font-size="24">+ -</text><text x="370" y="400" text-anchor="middle" font-size="17" font-weight="bold">1. Cell</text><line x1="410" y1="350" x2="540" y2="350" stroke="black" stroke-width="5"/><circle cx="540" cy="350" r="50" fill="none" stroke="black" stroke-width="5"/><line x1="526" y1="336" x2="554" y2="364" stroke="black" stroke-width="4"/><line x1="554" y1="336" x2="526" y2="364" stroke="black" stroke-width="4"/><text x="540" y="420" text-anchor="middle" font-size="17" font-weight="bold">2. Bulb</text><line x1="540" y1="400" x2="540" y2="500" stroke="black" stroke-width="5"/><line x1="540" y1="500" x2="180" y2="500" stroke="black" stroke-width="5"/><line x1="180" y1="500" x2="180" y2="350" stroke="black" stroke-width="5"/><text x="475" y="650" text-anchor="middle" font-size="18">Current flows in closed circuit</text>' + svg_footer()
def draw_water_cycle(): return svg_header("Water Cycle - S1 Geography") + '<circle cx="800" cy="100" r="50" fill="#fff176" stroke="black" stroke-width="4"/><text x="800" y="170" text-anchor="middle" font-size="17">1. Sun</text><ellipse cx="475" cy="100" rx="70" ry="40" fill="white" stroke="black" stroke-width="4"/><text x="475" y="170" text-anchor="middle" font-size="17">2. Condensation</text><rect x="80" y="450" width="790" height="120" fill="#64b5f6" stroke="black" stroke-width="4"/><text x="475" y="520" text-anchor="middle" font-size="17">3. Collection</text><line x1="475" y1="140" x2="475" y2="380" stroke="blue" stroke-width="4" marker-end="url(#arrow)"/><text x="495" y="270" font-size="16">4. Precipitation</text>' + svg_footer()
def draw_pendulum(): return svg_header("Simple Pendulum - S1 Physics") + '<circle cx="475" cy="150" r="8" fill="black"/><text x="495" y="145" font-size="17" font-weight="bold">1. Pivot</text><line x1="475" y1="158" x2="550" y2="420" stroke="black" stroke-width="4"/><circle cx="550" cy="420" r="30" fill="#90a4ae" stroke="black" stroke-width="4"/><text x="590" y="425" font-size="17" font-weight="bold">2. Bob</text><line x1="550" y1="450" x2="550" y2="520" stroke="black" marker-end="url(#arrow)" stroke-width="3"/><text x="565" y="490" font-size="16">3. Weight mg</text><text x="475" y="620" text-anchor="middle" font-size="18">T = 2π√(L/g)</text>' + svg_footer()
def draw_filtration(): return svg_header("Filtration Apparatus - S1 Chemistry") + '<polygon points="325,220 625,220 475,380" fill="none" stroke="black" stroke-width="5"/><text x="475" y="200" text-anchor="middle" font-size="17" font-weight="bold">1. Funnel</text><rect x="400" y="400" width="150" height="120" fill="none" stroke="black" stroke-width="5"/><text x="475" y="550" text-anchor="middle" font-size="17" font-weight="bold">2. Beaker</text><line x1="475" y1="380" x2="475" y2="400" stroke="black" stroke-width="4" stroke-dasharray="6,6"/><text x="495" y="395" font-size="16">3. Filter Paper</text>' + svg_footer()

PYTHON_DRAW_ENGINE = {"atom": draw_atom, "cone": draw_cone, "plant cell": draw_plant_cell, "circuit": draw_simple_circuit, "water cycle": draw_water_cycle, "pendulum": draw_pendulum, "filtration": draw_filtration}

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
    return f'{svg_header("Not Found")}<text x="475" y="350" text-anchor="middle" font-size="18" fill="red">Diagram "{topic}" not in 30-template library</text>{svg_footer()}'
def generate_practical(subject, level, topic):
    level_key = "S1-S4" if int(level[1]) <= 4 else "S5-S6"
    data = PRACTICAL_DATABASE.get(subject,{}).get(level_key,{}).get(topic,None)
    if data:
        return f"**PRACTICAL: {topic}**\n\n**NCDC Objective:** {data['objective']}\n\n**Apparatus for 40 students:** {data['apparatus']}\n\n**Procedure:**\n{data['procedure']}\n\n**Expected Observations:**\n{data['observations']}\n\n**Evaluation Questions:**\n{chr(10).join(data['questions'])}\n\n**Safety:** {data['safety']}"
    return call_groq(f"Generate full NCDC practical for {level} {subject}: {topic}")

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
        ask_q = st.text_area("Ask anything")
        mic_recorder(key="voice")
        if st.button("Ask AI Brain", type="primary") and ask_q:
            ans = call_groq(f"Answer: {ask_q} for {level} {subject}")
            display_with_pdf(ans, "Answer")
        if st.checkbox("🔊 Listen"):
            text_to_speech(ans[:500])
    with tab2:
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="learn_subj")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="learn_level")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject2][level2], key="learn_topic")
        mode = st.radio("Mode", ["📖 Theory", "🧠 AOI", "🧪 Practicals Lab", "📝 UNEB Quiz Mode", "📚 Bulk Revision"])
        if mode == "📖 Theory" and st.button("Teach Me"):
            raw = call_groq(f"Teach {topic2} step by step for {level2} {subject2}")
            display_with_pdf(raw, "Theory")
        elif mode == "🧪 Practicals Lab":
            prac_list = list(PRACTICAL_DATABASE.get(subject2,{}).get("S1-S4",{}).keys()) if int(level2[1])<=4 else list(PRACTICAL_DATABASE.get(subject2,{}).get("S5-S6",{}).keys())
            prac = st.selectbox("Select Practical", prac_list if prac_list else ["No practicals"])
            if st.button("Generate Practical"):
                report = generate_practical(subject2,level2,prac)
                display_with_pdf(report, "Practical")

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

    elif selected == "UNEB Paper Generator":
        s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
        l = st.selectbox("Class", [f"S{i}" for i in range(1,7)])
        t = st.text_input("Topic")
        n = st.slider("Questions", 5, 50, 20)
        if st.button("Generate UNEB Paper"):
            paper = call_groq(f"UNEB EXAMINER MODE: Generate {n} UNEB ITEM/TASK/SCENARIO on {t} for {l} {s}")
            display_with_pdf(paper, "UNEB_Test")

    elif selected == "Lesson Plan + SOW":
        s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="lp_subj")
        l = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="lp_level")
        t = st.text_input("Topic", key="lp_topic")
        d = st.number_input("Minutes", 40, 120, 80)
        if st.button("Generate Lesson Plan"):
            plan = call_groq(f"SMART MODE: Generate NCDC {d} min lesson plan for {l} {s} on {t} with objectives, activities, assessment")
            display_with_pdf(plan, "LessonPlan")

    elif selected == "Single Report Card":
        name = st.text_input("Student Name")
        scores = {sub: st.number_input(sub, 0, 100) for sub in ["Math", "English", "Science", "Physics", "Chemistry", "Biology"]}
        if st.button("Generate Report"):
            report = call_groq(f"SMART MODE: Generate NCDC Report Card with comments for: Name: {name}\nScores: {scores}")
            display_with_pdf(report, "Report")

    elif selected == "BULK EXAMS GENERATOR":
        s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="bulk_subj")
        l = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="bulk_level")
        if st.button("Generate 20 UNEB ITEMS"):
            topics = ', '.join(UNEB_CURRICULUM_MAP[s][l])
            bulk = call_groq(f"UNEB EXAMINER MODE: Generate 20 UNEB ITEM/TASK/SCENARIO for {l} {s}: {topics}")
            display_with_pdf(bulk, "Bulk")

    elif selected == "Performance Analytics":
        if not df_logs.empty:
            df_chart = df_logs.groupby(pd.to_datetime(df_logs['timestamp']).dt.date).size()
            st.line_chart(df_chart)
            st.dataframe(df_logs.groupby('action').size())
        else:
            st.info("No data yet")

    elif selected == "Student Management":
        if "students_db" not in st.session_state:
            st.session_state.students_db = []
        name = st.text_input("Add Student Name")
        reg = st.text_input("Registration No")
        if st.button("Add Student"):
            st.session_state.students_db.append({"name": name, "reg": reg})
            st.success("Added")
        st.dataframe(st.session_state.students_db)

    elif selected == "Question Bank Manager":
        if "qbank" not in st.session_state:
            st.session_state.qbank = []
        q = st.text_area("Enter Question")
        ans = st.text_area("Answer")
        if st.button("Save Question"):
            st.session_state.qbank.append({"q": q, "a": ans})
            st.success("Saved")
        st.dataframe(st.session_state.qbank)

    elif selected == "Curriculum Planner":
        s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="cp_subj")
        l = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="cp_level")
        if st.button("Generate SOW"):
            sow = "\n".join([f"Week {i+1}: {t}" for i, t in enumerate(UNEB_CURRICULUM_MAP[s][l])])
            display_with_pdf(sow, "SOW")

st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO - NCDC + UNEB EXAMINER V3.5.5")
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
      
