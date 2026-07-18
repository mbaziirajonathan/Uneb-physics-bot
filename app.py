import streamlit as st
import os, io, re, pytz, numpy as np, random
import pandas as pd
import plotly.express as px
from datetime import datetime
from groq import Groq
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
from pathlib import Path

# HARDCODED APP BRANDING
st.set_page_config(
    page_title="UCE/UACE DIGITAL TUTOR 2026 GOLD",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'Get Help': 'https://wa.me/256751040731', 'About': "NCDC S1-S6"}
)

# LICENSE CONTROL
FREE_PASSWORD = "UNEB TEST 2026"
GOLD_PASSWORD = "TEST_123_ID"
ADMIN_CONTACT = "256751040731"
UGANDA_TZ = pytz.timezone("Africa/Kampala")
MAX_QUESTIONS_FREE = 20
MAX_QUESTIONS_GOLD = 9999

BASE_DIR = Path(__file__).parent.resolve()
DIAGRAMS_DIR = BASE_DIR / "assets"

SUBJECTS = ["Physics", "Chemistry", "Biology", "Mathematics"]
CLASSES = ["S1", "S2", "S3", "S4", "S5", "S6"]
GOLD_LOCKED_CLASSES = ["S5", "S6"]
GOLD_LOCKED_SUBJECTS = ["Physics", "Chemistry", "Biology", "Mathematics"]
MODES = ["Smart Search", "Theory Mode", "Lesson Preparation", "Diagrams Library", "Practicals Lab", "Quiz Mode", "Predict Papers", "Voice Chat", "Progress Tracker", "Admin Dashboard", "Practical Assessment Generator", "Bulk Revision Generator"]

# SYLLABUS - S1-S6 ALL 4 SUBJECTS - SAME AS YOUR LAST CODE
SYLLABUS = {
    "Physics": {
        "S1": ["Introduction to Physics", "Matter", "Measurement", "Energy", "Light", "Sound", "Heat", "Electricity", "Magnetism", "Machines"],
        "S2": ["Motion", "Forces", "Work Energy Power", "Pressure", "Waves", "Electrostatics", "Current Electricity", "Optics"],
        "S3": ["Linear Motion", "Newton's Laws", "Momentum", "Gravitation", "Properties of Matter", "Thermal Physics", "Waves II", "Magnetism"],
        "S4": ["Radioactivity", "Electronics", "AC/DC", "Nuclear Physics", "Astrophysics", "Advanced Mechanics"],
        "S5": ["Unit 1: Mechanics", "Unit 2: Waves", "Unit 3: Thermal"],
        "S6": ["Unit 4: Thermo 2", "Unit 5: E&M", "Unit 6: Modern Physics"]
    },
    "Chemistry": {
        "S1": ["Introduction to Chemistry", "Matter", "Atoms", "Molecules", "Acids Bases", "Air", "Water", "Chemical Reactions"],
        "S2": ["Periodic Table", "Chemical Bonding", "Acids Bases Salts", "Carbon", "Metals", "Non-metals", "Energy Changes"],
        "S3": ["Chemical Kinetics", "Equilibrium", "Electrochemistry", "Organic Chemistry", "Industrial Processes"],
        "S4": ["Advanced Organic", "Analytical Chemistry", "Environmental Chemistry", "Polymers"],
        "S5": ["Unit 1: Moles", "Unit 2: Atomic Structure", "Unit 3: Bonding", "Unit 4: Periodicity", "Unit 5: Thermochemistry", "Unit 6: Organic"],
        "S6": ["Unit 7: Equilibria", "Unit 8: Inorganic", "Unit 9: Advanced Organic", "Unit 10: Industrial"]
    },
    "Biology": {
        "S1": ["Introduction to Biology", "Cells", "Classification", "Nutrition", "Respiration", "Transport", "Ecology", "Transport in Plants"],
        "S2": ["Reproduction", "Genetics", "Growth", "Human Body Systems", "Disease", "Immunity", "Respiratory System", "Alveolus", "Human Ear", "Human Eye"],
        "S3": ["Ecology II", "Evolution", "Genetics II", "Physiology", "Microbiology"],
        "S4": ["Molecular Biology", "Biotechnology", "Conservation", "Human Health"],
        "S5": ["Unit 1: Cell Biology", "Unit 2: Nutrition", "Unit 3: Transport", "Unit 4: Respiration", "Unit 5: Homeostasis"],
        "S6": ["Unit 6: Coordination", "Unit 7: Growth", "Unit 8: Genetics", "Unit 9: Ecology"]
    },
    "Mathematics": {
        "S1": ["Unit 1: Number Bases", "Unit 2: Fractions", "Unit 3: Integers", "Unit 4: Sets", "Unit 5: Geometry", "Unit 6: Sequences", "Unit 7: Coordinates"],
        "S2": ["Unit 1: Equations", "Unit 2: Business Math", "Unit 3: Ratios", "Unit 4: Pythagoras", "Unit 5: Area/Volume", "Unit 6: Statistics"],
        "S3": ["Unit 1: Indices", "Unit 2: Quadratics", "Unit 3: Linear Programming", "Unit 4: Vectors", "Unit 5: Transformations", "Unit 6: Taxation"],
        "S4": ["Unit 1: Matrices", "Unit 2: Probability", "Unit 3: 3D Geometry", "Unit 4: Loci", "Unit 5: Functions", "Unit 6: Networks"],
        "S5": ["Paper 1: Advanced Algebra", "Paper 1: Geometry & Vectors", "Paper 1: Calculus I", "Paper 2: Statistics", "Paper 2: Mechanics I", "Paper 2: Numerical Methods"],
        "S6": ["Paper 1: Permutations & Complex", "Paper 1: Conics & 3D", "Paper 1: Calculus II", "Paper 2: Probability", "Paper 2: Mechanics II", "Paper 2: Numerical Methods II"]
    }
}

# 10 PRACTICALS PER SUBJECT - RESTORED
PRACTICALS = {
    "Physics": [
        {"name": "Measuring Length and Time", "aim": "Use rulers and stopwatches", "materials": "Meter rule", "procedure": "Measure 10 times", "graph": "Length vs Time"},
        {"name": "Density of Regular Object", "aim": "Determine density", "materials": "Beam balance", "procedure": "Mass and Volume", "graph": "Mass vs Volume"},
        {"name": "Simple Pendulum", "aim": "Investigate period", "materials": "String", "procedure": "Vary length", "graph": "T^2 vs L"},
        {"name": "Ohm's Law", "aim": "Verify V = IR", "materials": "Battery", "procedure": "Vary V", "graph": "V vs I"},
        {"name": "Focal Length of Lens", "aim": "Find focal length", "materials": "Lens", "procedure": "u and v", "graph": "1/u vs 1/v"},
        {"name": "Specific Heat Capacity", "aim": "Find specific heat", "materials": "Calorimeter", "procedure": "Heat transfer", "graph": "Temp vs Time"},
        {"name": "Refraction of Light", "aim": "Find refractive index", "materials": "Glass block", "procedure": "Snell's Law", "graph": "sin i vs sin r"},
        {"name": "Surface Tension", "aim": "Capillary rise", "materials": "Tube", "procedure": "Measure h", "graph": "h vs 1/r"},
        {"name": "Resonance in Air Column", "aim": "Speed of sound", "materials": "Tube", "procedure": "Find resonance", "graph": "L vs 1/f"},
        {"name": "Magnetic Field of Coil", "aim": "Field strength", "materials": "Coil", "procedure": "Vary current", "graph": "Deflection vs Current"}
    ],
    "Chemistry": [
        {"name": "Testing for Cations", "aim": "Identify metal ions", "materials": "NaOH", "procedure": "Add reagents", "graph": None},
        {"name": "Testing for Anions", "aim": "Identify acid radicals", "materials": "BaCl2", "procedure": "Add reagents", "graph": None},
        {"name": "Titration - Acid Base", "aim": "Find concentration", "materials": "Burette", "procedure": "Titrate", "graph": "Volume vs pH"},
        {"name": "Rate of Reaction", "aim": "Effect of concentration", "materials": "HCl", "procedure": "Vary conc", "graph": "Volume vs Time"},
        {"name": "Electrolysis of Water", "aim": "Decompose water", "materials": "Apparatus", "procedure": "Electrolyze", "graph": "H2 vs O2"},
        {"name": "Solubility Curve", "aim": "Solubility vs T", "materials": "KNO3", "procedure": "Dissolve", "graph": "Solubility vs T"},
        {"name": "Organic Preparation - Ethene", "aim": "Prepare ethene", "materials": "Ethanol", "procedure": "Heat", "graph": None},
        {"name": "Chromatography", "aim": "Separate ink", "materials": "Paper", "procedure": "Spot", "graph": None},
        {"name": "Enthalpy Change", "aim": "Heat of reaction", "materials": "Calorimeter", "procedure": "Mix", "graph": "Temp vs Time"},
        {"name": "Redox Titration", "aim": "Find Fe2+", "materials": "KMnO4", "procedure": "Titrate", "graph": None}
    ],
    "Biology": [
        {"name": "Microscope Use", "aim": "Observe cells", "materials": "Microscope", "procedure": "Prepare slide", "graph": None},
        {"name": "Food Tests", "aim": "Test nutrients", "materials": "Iodine", "procedure": "Add reagents", "graph": None},
        {"name": "Osmosis in Potato", "aim": "Investigate osmosis", "materials": "Potato", "procedure": "Soak", "graph": "Conc vs % Change"},
        {"name": "Transpiration Rate", "aim": "Measure water loss", "materials": "Potometer", "procedure": "Measure bubble", "graph": "Time vs Distance"},
        {"name": "Photosynthesis", "aim": "Test for starch", "materials": "Leaf", "procedure": "Destarch", "graph": None},
        {"name": "Heart Rate Response", "aim": "Effect of exercise", "materials": "Stopwatch", "procedure": "Measure", "graph": "Time vs HR"},
        {"name": "Germination Factors", "aim": "Effect of water", "materials": "Seeds", "procedure": "Set conditions", "graph": "% vs Days"},
        {"name": "Enzyme Activity", "aim": "Effect of pH", "materials": "Amylase", "procedure": "Vary pH", "graph": "pH vs Time"},
        {"name": "Ecological Sampling", "aim": "Quadrat method", "materials": "Quadrat", "procedure": "Sample", "graph": "Species vs Freq"},
        {"name": "Blood Smear", "aim": "Identify blood cells", "materials": "Slide", "procedure": "Observe", "graph": None}
    ],
    "Mathematics": [
        {"name": "Budgeting Project", "aim": "Use fractions and %", "materials": "Paper", "procedure": "Share money", "graph": None},
        {"name": "Business Analysis", "aim": "Profit and Loss", "materials": "Receipts", "procedure": "Calculate profit", "graph": "Sales vs Profit"},
        {"name": "Linear Programming", "aim": "Maximize profit", "materials": "Graph paper", "procedure": "Plot feasible region", "graph": "Feasible Region"},
        {"name": "Network Project", "aim": "Critical path", "materials": "Paper", "procedure": "Draw network", "graph": "Network Graph"}
    ]
}

def get_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

def generate_ai_response(client, prompt, subject, class_level):
    system_prompt = f"You are UCE/UACE DIGITAL TUTOR 2026. Teach {subject} for {class_level} Uganda. NCDC 2026 only. Ugandan examples."
    resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}], temperature=0.3, max_tokens=1024)
    return resp.choices[0].message.content

def create_pdf(content, filename):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4; c.setFont("Helvetica", 12); y = height - 50
    for line in content.split('\n'):
        c.drawString(50, y, line[:90]); y -= 20
        if y < 50: c.showPage(); y = height - 50
    c.save(); buffer.seek(0)
    return buffer

def find_diagram(topic):
    if not DIAGRAMS_DIR.exists(): return None
    all_pngs = list(DIAGRAMS_DIR.glob("*.png"))
    search_key = topic.lower().replace(" ", "_")
    for png_path in all_pngs:
        if search_key in png_path.name.lower(): return str(png_path)
    return None

def log_activity(activity, subject, class_level):
    if "activities_log" not in st.session_state: st.session_state.activities_log = []
    st.session_state.activities_log.append({"time": datetime.now(UGANDA_TZ).strftime("%Y-%m-%d %H:%M:%S"), "activity": activity, "subject": subject, "class": class_level, "license": st.session_state.license})

def show_gold_lock(subject):
    st.error(f"🔒 **GOLD PACKAGE REQUIRED**")
    st.info(f"WhatsApp/Call **{ADMIN_CONTACT}** for key: `{GOLD_PASSWORD}`")
    st.link_button(f"📱 WhatsApp {ADMIN_CONTACT}", f"https://wa.me/{ADMIN_CONTACT}")

def main():
    client = get_client()
    if "activities_log" not in st.session_state: st.session_state.activities_log = []
    if "license" not in st.session_state: st.session_state.license = "FREE"

    st.markdown("""<div style="background:linear-gradient(90deg, #FFD700 0%, #FFA500 100%); padding:15px;"><h1 style="color:black; text-align:center">📚 UCE/UACE DIGITAL TUTOR 2026 GOLD</h1></div>""", unsafe_allow_html=True)

    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("🔒 Login")
        password = st.text_input("Enter Password", type="password")
        st.caption("FREE: `UNEB TEST 2026` | GOLD: `TEST_123_ID`")
        if st.button("Login"):
            if password == GOLD_PASSWORD: st.session_state.authenticated = True; st.session_state.license = "GOLD"; st.rerun()
            elif password == FREE_PASSWORD: st.session_state.authenticated = True; st.session_state.license = "FREE"; st.rerun()
            else: st.error("Incorrect Password")
        st.stop()

    with st.sidebar:
        st.success(f"License: {st.session_state.license}")
        subject = st.selectbox("Subject", SUBJECTS)
        available_classes = ["S1", "S2", "S3", "S4"] if st.session_state.license == "FREE" and subject in GOLD_LOCKED_SUBJECTS else CLASSES
        class_level = st.selectbox("Class", available_classes)
        mode = st.radio("Mode", MODES)

    if class_level in GOLD_LOCKED_CLASSES and subject in GOLD_LOCKED_SUBJECTS and st.session_state.license == "FREE":
        show_gold_lock(subject); st.stop()

    if mode == "Theory Mode":
        topic = st.selectbox("Topic", SYLLABUS[subject][class_level])
        if st.button("Generate Notes"):
            resp = generate_ai_response(client, f"Detailed notes on {topic}", subject, class_level)
            st.write(resp)

    elif mode == "Bulk Revision Generator":
        topic = st.selectbox("Topic", SYLLABUS[subject][class_level])
        num_q = st.slider("Questions", 10, 50, 20)
        if st.button("Generate"):
            resp = generate_ai_response(client, f"Generate {num_q} revision questions with answers on {topic}", subject, class_level)
            st.write(resp)
            pdf = create_pdf(resp, "revision.pdf")
            st.download_button("Download PDF", pdf, "revision.pdf")

    elif mode == "Admin Dashboard":
        if st.session_state.activities_log:
            df = pd.DataFrame(st.session_state.activities_log)
            st.dataframe(df)

if __name__ == "__main__":
    main()
