import streamlit as st
import os, io, json, re, ast, pytz, numpy as np, tempfile, random, glob
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime
from groq import Groq
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
import base64
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
from pathlib import Path
import speech_recognition as sr
import PyPDF2

# ===============================
# HARDCODED APP BRANDING
# ===============================
st.set_page_config(
    page_title="UCE/UACE DIGITAL TUTOR 2026 GOLD",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://wa.me/256751040731',
        'Report a bug': None,
        'About': "UCE/UACE DIGITAL TUTOR 2026 GOLD\nAligned to NCDC Uganda Syllabus 2026\nS1-S6 Competency Based"
    }
)

# ===============================
# LICENSE CONTROL - 2 TIERS
# ===============================
FREE_PASSWORD = "UNEB TEST 2026" # OLD FREE PASSWORD YOU ASKED
GOLD_PASSWORD = "TEST_123_ID" # GOLD UNLOCK
ADMIN_CONTACT = "256751040731"
UGANDA_TZ = pytz.timezone("Africa/Kampala")
MAX_QUESTIONS_FREE = 20 # FREE QUOTA
MAX_QUESTIONS_GOLD = 9999

BASE_DIR = Path(__file__).parent.resolve()
DIAGRAMS_DIR = BASE_DIR / "assets"

SUBJECTS = ["Physics", "Chemistry", "Biology", "Mathematics"]
CLASSES = ["S1", "S2", "S3", "S4", "S5", "S6"]
GOLD_LOCKED_CLASSES = ["S5", "S6"]
GOLD_LOCKED_SUBJECTS = ["Physics", "Chemistry", "Biology", "Mathematics"]
MODES = ["Smart Search", "Theory Mode", "Lesson Preparation", "Diagrams Library", "Practicals Lab", "Quiz Mode", "Predict Papers", "Voice Chat", "Progress Tracker", "Admin Dashboard", "Practical Assessment Generator", "Bulk Revision Generator"]

# ===============================
# SYLLABUS - S1-S4 FROM OLD CODE + NEW NCDC
# ===============================
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
        "S1": ["Unit 1: Number Bases", "Unit 2: Fractions, Decimals, Percentages", "Unit 3: Integers", "Unit 4: Sets", "Unit 5: Geometry", "Unit 6: Sequences", "Unit 7: Coordinates"],
        "S2": ["Unit 1: Equations", "Unit 2: Business Math", "Unit 3: Ratios", "Unit 4: Pythagoras & Trig", "Unit 5: Area/Volume", "Unit 6: Statistics"],
        "S3": ["Unit 1: Indices", "Unit 2: Quadratics", "Unit 3: Linear Programming", "Unit 4: Vectors", "Unit 5: Transformations", "Unit 6: Taxation"],
        "S4": ["Unit 1: Matrices", "Unit 2: Probability", "Unit 3: 3D Geometry", "Unit 4: Loci", "Unit 5: Functions", "Unit 6: Networks"],
        "S5": ["Paper 1: Advanced Algebra", "Paper 1: Geometry & Vectors", "Paper 1: Calculus I", "Paper 2: Statistics", "Paper 2: Mechanics I", "Paper 2: Numerical Methods"],
        "S6": ["Paper 1: Permutations & Complex", "Paper 1: Conics & 3D", "Paper 1: Calculus II", "Paper 2: Probability", "Paper 2: Mechanics II", "Paper 2: Numerical Methods II"]
    }
}

# ===============================
# PRACTICALS - RESTORED ALL 10 FROM OLD CODE
# ===============================
PRACTICALS = {
    "Physics": [
        {"name": "Measuring Length and Time", "aim": "Use rulers and stopwatches accurately", "materials": "Meter rule, Stopwatch", "procedure": "1. Measure 10 times 2. Average", "graph": "Length vs Time"},
        {"name": "Density of Regular Object", "aim": "Determine density", "materials": "Beam balance, Vernier", "procedure": "1. Mass 2. Volume 3. Density=m/v", "graph": "Mass vs Volume"},
        {"name": "Simple Pendulum", "aim": "Investigate period", "materials": "String, Bob", "procedure": "1. Vary length 2. Time 20 osc", "graph": "T^2 vs L"},
        {"name": "Ohm's Law", "aim": "Verify V = IR", "materials": "Battery, Resistor", "procedure": "1. Vary V 2. Record I", "graph": "V vs I"},
        {"name": "Focal Length of Lens", "aim": "Find focal length", "materials": "Convex lens", "procedure": "1. u and v 2. Lens formula", "graph": "1/u vs 1/v"},
        {"name": "Specific Heat Capacity", "aim": "Find specific heat", "materials": "Calorimeter", "procedure": "1. Heat 2. Transfer", "graph": "Temp vs Time"},
        {"name": "Refraction of Light", "aim": "Find refractive index", "materials": "Glass block", "procedure": "1. Trace rays 2. Snell's Law", "graph": "sin i vs sin r"},
        {"name": "Surface Tension", "aim": "Capillary rise", "materials": "Capillary tubes", "procedure": "1. Dip 2. Measure h", "graph": "h vs 1/r"},
        {"name": "Resonance in Air Column", "aim": "Speed of sound", "materials": "Resonance tube", "procedure": "1. Find resonance", "graph": "L vs 1/f"},
        {"name": "Magnetic Field of Coil", "aim": "Field strength", "materials": "Coil", "procedure": "1. Vary current", "graph": "Deflection vs Current"}
    ],
    "Chemistry": [
        {"name": "Testing for Cations", "aim": "Identify metal ions", "materials": "NaOH, NH3", "procedure": "1. Add reagents", "graph": None},
        {"name": "Testing for Anions", "aim": "Identify acid radicals", "materials": "BaCl2, AgNO3", "procedure": "1. Add reagents", "graph": None},
        {"name": "Titration - Acid Base", "aim": "Find concentration", "materials": "Burette", "procedure": "1. Titrate", "graph": "Volume vs pH"},
        {"name": "Rate of Reaction", "aim": "Effect of concentration", "materials": "HCl", "procedure": "1. Vary conc", "graph": "Volume vs Time"},
        {"name": "Electrolysis of Water", "aim": "Decompose water", "materials": "Hoffman apparatus", "procedure": "1. Electrolyze", "graph": "H2 vs O2"},
        {"name": "Solubility Curve", "aim": "Solubility vs T", "materials": "KNO3", "procedure": "1. Dissolve", "graph": "Solubility vs T"},
        {"name": "Organic Preparation - Ethene", "aim": "Prepare ethene", "materials": "Ethanol", "procedure": "1. Heat", "graph": None},
        {"name": "Chromatography", "aim": "Separate ink", "materials": "Filter paper", "procedure": "1. Spot", "graph": None},
        {"name": "Enthalpy Change", "aim": "Heat of reaction", "materials": "Calorimeter", "procedure": "1. Mix", "graph": "Temp vs Time"},
        {"name": "Redox Titration", "aim": "Find Fe2+", "materials": "KMnO4", "procedure": "1. Titrate", "graph": None}
    ],
    "Biology": [
        {"name": "Microscope Use", "aim": "Observe cells", "materials": "Microscope", "procedure": "1. Prepare slide", "graph": None},
        {"name": "Food Tests", "aim": "Test nutrients", "materials": "Iodine", "procedure": "1. Add reagents", "graph": None},
        {"name": "Osmosis in Potato", "aim": "Investigate osmosis", "materials": "Potato", "procedure": "1. Soak", "graph": "Conc vs % Change"},
        {"name": "Transpiration Rate", "aim": "Measure water loss", "materials": "Potometer", "procedure": "1. Measure bubble", "graph": "Time vs Distance"},
        {"name": "Photosynthesis", "aim": "Test for starch", "materials": "Leaf", "procedure": "1. Destarch", "graph": None},
        {"name": "Heart Rate Response", "aim": "Effect of exercise", "materials": "Stopwatch", "procedure": "1. Measure", "graph": "Time vs HR"},
        {"name": "Germination Factors", "aim": "Effect of water", "materials": "Seeds", "procedure": "1. Set conditions", "graph": "% vs Days"},
        {"name": "Enzyme Activity", "aim": "Effect of pH", "materials": "Amylase", "procedure": "1. Vary pH", "graph": "pH vs Time"},
        {"name": "Ecological Sampling", "aim": "Quadrat method", "materials": "Quadrat", "procedure": "1. Sample", "graph": "Species vs Freq"},
        {"name": "Blood Smear", "aim": "Identify blood cells", "materials": "Slide", "procedure": "1. Observe", "graph": None}
    ],
    "Mathematics": [
        {"name": "Budgeting Project", "aim": "Use fractions and %", "materials": "Paper", "procedure": "Share money", "graph": None},
        {"name": "Business Analysis", "aim": "Profit and Loss", "materials": "Receipts", "procedure": "Calculate profit", "graph": "Sales vs Profit"},
        {"name": "Linear Programming", "aim": "Maximize profit", "materials": "Graph paper", "procedure": "Plot feasible region", "graph": "Feasible Region"},
        {"name": "Network Project", "aim": "Critical path", "materials": "Paper", "procedure": "Draw network", "graph": "Network Graph"}
    ]
}

# ===============================
# CORE FUNCTIONS - RESTORED FROM OLD
# ===============================
def get_client():
    api_key = st.secrets["GROQ_API_KEY"]
    if not api_key: st.error("GROQ_API_KEY not set in secrets"); st.stop()
    return Groq(api_key=api_key)

def generate_ai_response(client, prompt, subject, class_level):
    system_prompt = f"You are UCE/UACE DIGITAL TUTOR 2026. You teach {subject} for {class_level} in Uganda. Answer ONLY according to NCDC Uganda Syllabus 2026 and UNEB guidelines. Be accurate. Use Ugandan examples. Step-by-step."
    resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}], temperature=0.3, max_tokens=1024)
    return resp.choices[0].message.content

def generate_graph(data, x_col, y_col, title):
    fig = px.line(data, x=x_col, y=y_col, title=title, markers=True)
    fig.update_layout(template="plotly_white")
    return fig

def create_pdf(content, filename):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 12); y = height - 50
    for line in content.split('\n'):
        c.drawString(50, y, line[:90]); y -= 20
        if y < 50: c.showPage(); y = height - 50
    c.save(); buffer.seek(0)
    return buffer

def sanitize_filename(name):
    name = name.lower(); name = re.sub(r'[^a-z0-9\s]', '', name); return name

def find_diagram(topic):
    debug_info = [f"App Root: {BASE_DIR}", f"Looking in: {DIAGRAMS_DIR}", f"Folder Exists: {DIAGRAMS_DIR.exists()}"]
    if not DIAGRAMS_DIR.exists(): return None, debug_info
    all_pngs = list(DIAGRAMS_DIR.glob("*.png"))
    search_key = sanitize_filename(topic)
    for png_path in all_pngs:
        if search_key in png_path.name.lower(): return str(png_path), debug_info
    return None, debug_info

def log_activity(activity, subject, class_level):
    if "activities_log" not in st.session_state: st.session_state.activities_log = []
    st.session_state.activities_log.append({"time": datetime.now(UGANDA_TZ).strftime("%Y-%m-%d %H:%M:%S"), "activity": activity, "subject": subject, "class": class_level, "license": st.session_state.license})

def show_gold_lock(subject):
    st.error(f"🔒 **GOLD PACKAGE REQUIRED**")
    st.warning(f"S5-S6 {subject} is locked.")
    st.info(f"**To Unlock:** WhatsApp or Call **{ADMIN_CONTACT}** and request key: `{GOLD_PASSWORD}`")
    st.link_button(f"📱 WhatsApp {ADMIN_CONTACT}", f"https://wa.me/{ADMIN_CONTACT}")

# ===============================
# MAIN APP
# ===============================
def main():
    client = get_client()
    if "activities_log" not in st.session_state: st.session_state.activities_log = []
    if "license" not in st.session_state: st.session_state.license = "FREE"

    st.markdown("""<div style="background:linear-gradient(90deg, #FFD700 0%, #FFA500 100%); padding:15px; border-radius:10px;"><h1 style="color:black; text-align:center">📚 UCE/UACE DIGITAL TUTOR 2026 GOLD</h1></div>""", unsafe_allow_html=True)

    # LOGIN
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("🔒 Login")
        password = st.text_input("Enter Password", type="password")
        st.caption("FREE: `UNEB TEST 2026` for S1-S4. GOLD: `TEST_123_ID` for S5-S6 + Math")
        if st.button("Login"):
            if password == GOLD_PASSWORD: st.session_state.authenticated = True; st.session_state.license = "GOLD"; st.rerun()
            elif password == FREE_PASSWORD: st.session_state.authenticated = True; st.session_state.license = "FREE"; st.rerun()
            else: st.error("Incorrect Password")
        st.stop()

    # SIDEBAR
    with st.sidebar:
        st.header("Settings")
        st.success(f"License: {st.session_state.license}")
        subject = st.selectbox("Select Subject", SUBJECTS)
        available_classes = ["S1", "S2", "S3", "S4"] if st.session_state.license == "FREE" and subject in GOLD_LOCKED_SUBJECTS else CLASSES
        class_level = st.selectbox("Select Class", available_classes)
        with st.expander(f"View {subject} {class_level} Topics"):
            for topic in SYLLABUS[subject][class_level]: st.write(f"• {topic}")
        mode = st.radio("Select Mode", MODES)
        st.markdown(f"[📞 WhatsApp Admin: {ADMIN_CONTACT}](https://wa.me/256{ADMIN_CONTACT[1:]})")

    # LOCK CHECK
    if class_level in GOLD_LOCKED_CLASSES and subject in GOLD_LOCKED_SUBJECTS and st.session_state.license == "FREE":
        show_gold_lock(subject); st.stop()

    # MODES - ALL RESTORED
    if mode == "Smart Search":
        st.header("🧠 Smart Search")
        query = st.text_input("Ask any question")
        if st.button("Search") and query:
            resp = generate_ai_response(client, f"Explain {query}", subject, class_level)
            st.write(resp); log_activity(f"Smart Search: {query}", subject, class_level)

    elif mode == "Theory Mode":
        st.header("📘 Theory Mode")
        topic = st.selectbox("Select Topic", SYLLABUS[subject][class_level])
        if st.button("Generate Notes"):
            resp = generate_ai_response(client, f"Detailed notes on {topic}", subject, class_level)
            st.write(resp); log_activity(f"Theory: {topic}", subject, class_level)

    elif mode == "Lesson Preparation":
        st.header("👨‍🏫 Lesson Preparation")
        topic = st.selectbox("Select Topic", SYLLABUS[subject][class_level])
        if st.button("Generate Lesson Plan"):
            resp = generate_ai_response(client, f"40min lesson plan for {topic}", subject, class_level)
            st.write(resp)
            pdf = create_pdf(resp, "lesson.pdf")
            st.download_button("Download PDF", pdf, "lesson.pdf")
            log_activity(f"Lesson: {topic}", subject, class_level)

    elif mode == "Diagrams Library": # RESTORED
        st.header("🖼️ Diagrams Library")
        topic = st.selectbox("Select Topic", SYLLABUS[subject][class_level])
        path, debug = find_diagram(topic)
        if path and os.path.exists(path):
            st.image(Image.open(path), caption=topic)
            with open(path, "rb") as f: st.download_button("Download", f, os.path.basename(path))
        else: st.error("Not found"); st.code("\n".join(debug))

    elif mode == "Practicals Lab": # RESTORED 10 PRACTICALS
        st.header("🧪 Practicals Lab")
        practical = st.selectbox("Select Practical", [p["name"] for p in PRACTICALS[subject]])
        if st.button("Show Practical"):
            p = next(p for p in PRACTICALS[subject] if p["name"] == practical)
            st.write(f"**Aim:** {p['aim']}"); st.write(f"**Materials:** {p['materials']}"); st.write(f"**Procedure:** {p['procedure']}")
            if p["graph"]:
                if st.button("Generate Sample Graph"):
                    x = np.linspace(0,10,20); y = x * random.uniform(0.5,2)
                    fig = generate_graph(pd.DataFrame({"X":x,"Y":y}), "X","Y", p["graph"])
                    st.plotly_chart(fig)
            log_activity(f"Practical: {practical}", subject, class_level)

    elif mode == "Quiz Mode":
        st.header("📝 Quiz Mode")
        topic = st.selectbox("Select Topic", SYLLABUS[subject][class_level])
        if st.button("Generate 5 MCQs"):
            resp = generate_ai_response(client, f"5 MCQs on {topic} with answers", subject, class_level)
            st.write(resp); log_activity(f"Quiz: {topic}", subject, class_level)

    elif mode == "Bulk Revision Generator": # NEW: LIKE A-LEVEL GOLD
        st.header("📚 Bulk Revision Generator - 50 Questions")
        topic = st.selectbox("Select Topic", SYLLABUS[subject][class_level])
        num_q = st.slider("Number of Questions", 10, 50, 20)
        if st.button("Generate Bulk Questions"):
            resp = generate_ai_response(client, f"Generate {num_q} revision questions with answers on {topic} for {class_level} {subject}. Mix MCQ and structured.", subject, class_level)
            st.write(resp)
            pdf = create_pdf(resp, "revision.pdf")
            st.download_button("Download Revision PDF", pdf, "revision.pdf")
            log_activity(f"Bulk Rev: {topic}", subject, class_level)

    elif mode == "Predict Papers":
        st.header("📄 Predict Papers")
        if st.button("Predict Full Subject"):
            resp = generate_ai_response(client, f"Predict UCE/UACE questions for {class_level} {subject}", subject, class_level)
            st.write(resp)
            pdf = create_pdf(resp, "predict.pdf")
            st.download_button("Download PDF", pdf, "predict.pdf")
            log_activity("Predict", subject, class_level)

    elif mode == "Voice Chat": # RESTORED
        st.header("🎤 Voice Chat")
        audio = mic_recorder(start_prompt="Record", stop_prompt="Stop")
        query = st.text_input("Or type question")
        if st.button("Send") and query:
            resp = generate_ai_response(client, query, subject, class_level)
            st.write(resp)
            tts = gTTS(resp); tts.save("resp.mp3"); st.audio("resp.mp3")
            log_activity(f"Voice: {query}", subject, class_level)

    elif mode == "Progress Tracker": # RESTORED
        st.header("📊 Progress Tracker")
        if st.session_state.activities_log:
            df = pd.DataFrame(st.session_state.activities_log)
            st.dataframe(df)
        else: st.info("No activities yet")

    elif mode == "Admin Dashboard": # RESTORED
        st.header("📈 Admin Dashboard")
        if st.session_state.activities_log:
            df = pd.DataFrame(st.session_state.activities_log)
            st.metric("Total Activities", len(df))
            st.dataframe(df)
            st.download_button("Download CSV", df.to_csv().encode(), "log.csv")
        else: st.warning("No activity yet")

    elif mode == "Practical Assessment Generator":
        st.header("🧪 Practical AoI Generator")
        st.info("Use this for competency-based lab guides")

if __name__ == "__main__":
    main()
