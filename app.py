import streamlit as st
import os, io, pytz, random
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# ===============================
# LAZY IMPORTS + CACHING FOR SPEED
# ===============================
@st.cache_resource
def get_client():
    from groq import Groq
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

@st.cache_data
def create_pdf(content, filename):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 10)
    y = height - 50
    for line in content.split('\n'):
        for chunk in [line[i:i+95] for i in range(0, len(line), 95)]:
            c.drawString(50, y, chunk)
            y -= 15
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 50
    c.save()
    buffer.seek(0)
    return buffer

@st.cache_data
def generate_graph(data, x_col, y_col, title):
    import plotly.express as px
    fig = px.line(data, x=x_col, y=y_col, title=title, markers=True)
    fig.update_layout(template="plotly_white", height=400)
    return fig

# ===============================
# HARDCODED APP BRANDING
# ===============================
st.set_page_config(
    page_title="UCE/UACE DIGITAL TUTOR 2026 GOLD",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'Get Help': 'https://wa.me/256751040731', 'About': "NCDC S1-S6 Competency Based"}
)

# ===============================
# LICENSE CONTROL
# ===============================
ADMIN_CONTACT = "256751040731"
UGANDA_TZ = pytz.timezone("Africa/Kampala")

BASE_DIR = Path(__file__).parent.resolve()
DIAGRAMS_DIR = BASE_DIR / "assets"

SUBJECTS = ["Physics", "Chemistry", "Biology", "Mathematics"]
CLASSES = ["S1", "S2", "S3", "S4", "S5", "S6"]
GOLD_LOCKED_CLASSES = ["S5", "S6"]
GOLD_LOCKED_SUBJECTS = ["Physics", "Chemistry", "Biology", "Mathematics"]
MODES = ["Smart Search", "Theory Mode", "Lesson Preparation", "Diagrams Library", "Practicals Lab", "Quiz Mode", "Predict Papers", "Voice Chat", "Progress Tracker", "Admin Dashboard", "Practical Assessment Generator", "Bulk Revision Generator"]

# ===============================
# LOCKED NCDC S1-S6 CURRICULUM ENGINE - NO DATA LOST
# ===============================
CURRICULUM = {
    "Physics": {
        "S1": ["Intro to Physics", "Measurement", "Force", "Mechanical Properties"],
        "S2": ["Atmospheric/Fluid Pressure", "Work/Energy/Power", "Simple Machines", "Temperature/Heat Transfer"],
        "S3": ["Light/Optics", "Electrostatics", "Current Electricity", "Wave Motion/Sound"],
        "S4": ["Electromagnetism", "Electronics", "Radioactivity/Nuclear Physics"],
        "S5": ["Unit 1: Mechanics/Matter", "Unit 2: Waves/Optics", "Unit 3: Thermal Properties/Thermodynamics I"],
        "S6": ["Unit 4: Thermodynamics II", "Unit 5: Electricity/Magnetism", "Unit 6: Modern Physics/Electronics"],
    },
    "Chemistry": {
        "S1": ["Chemistry/Society", "Experimental Techniques", "States of Matter", "Classification of Matter"],
        "S2": ["Air/Burning/Rusting", "Water/Hydrogen", "Atomic Structure/Bonding", "Acids/Bases/Indicators"],
        "S3": ["Chemical Equations/Formulae", "Mole Concept", "Carbon/Compounds", "Sulfur/Nitrogen Compounds"],
        "S4": ["Periodicity", "Reactivity Series/Metal Extraction", "Organic Chemistry", "Thermochemistry", "Consumable Chemicals"],
        "S5": ["Unit 1: Moles/Equations", "Unit 2: Atomic/Electronic Structure", "Unit 3: Bonding/Crystal Structure", "Unit 4: Periodicity I", "Unit 5: Thermochemistry", "Unit 6: Intro Organic/Hydrocarbons"],
        "S6": ["Unit 7: Physical Equilibria/Kinetics", "Unit 8: Advanced Inorganic", "Unit 9: Advanced Organic", "Unit 10: Industrial/Environmental"],
    },
    "Biology": {
        "S1": ["Intro to Biology", "Cells", "Classification", "Interaction/Interdependence"],
        "S2": ["Nutrition", "Transport", "Gas Exchange/Respiration"],
        "S3": ["Excretion/Homeostasis", "Coordination/Response", "Locomotion/Support", "Reproduction"],
        "S4": ["Growth/Development", "Genetics/Inheritance", "Evolution/Selection"],
        "S5": ["Unit 1: Cell Bio/Biochem", "Unit 2: Nutrition/Autotrophic Systems", "Unit 3: Transport/Gas Exchange", "Unit 4: Cellular Respiration", "Unit 5: Homeostasis/Regulation"],
        "S6": ["Unit 6: Coordination/Response", "Unit 7: Growth/Development/Reproduction", "Unit 8: Inheritance/Genetics/Evolution", "Unit 9: Ecology/Environmental Management"],
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

def get_topics(subject, level):
    return CURRICULUM.get(subject, {}).get(level, [])

# ===============================
# 10 PRACTICALS PER SUBJECT - ALL RESTORED
# ===============================
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

# ===============================
# CORE FUNCTIONS
# ===============================
def generate_ai_response(client, prompt, subject, class_level):
    system_prompt = f"You are UCE/UACE DIGITAL TUTOR 2026. Teach {subject} for {class_level} Uganda. Use ONLY the NCDC 2026 curriculum. Ugandan examples. Step by step. No hallucination."
    resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}], temperature=0.3, max_tokens=1024)
    return resp.choices[0].message.content

def find_diagram(topic):
    if not DIAGRAMS_DIR.exists(): return None
    all_pngs = list(DIAGRAMS_DIR.glob("*.png"))
    search_key = topic.lower().replace(" ", "_").replace("/", "_")
    for png_path in all_pngs:
        if search_key in png_path.name.lower(): return str(png_path)
    return None

def log_activity(activity, subject, class_level):
    if "activities_log" not in st.session_state: st.session_state.activities_log = []
    st.session_state.activities_log.append({"time": datetime.now(UGANDA_TZ).strftime("%Y-%m-%d %H:%M:%S"), "activity": activity, "subject": subject, "class": class_level, "license": st.session_state.license})

def show_gold_lock(subject):
    st.error(f"🔒 **GOLD PACKAGE REQUIRED**")
    st.info(f"WhatsApp/Call **{ADMIN_CONTACT}** to get your access key")
    st.link_button(f"📱 WhatsApp {ADMIN_CONTACT}", f"https://wa.me/{ADMIN_CONTACT}")

# ===============================
# MAIN APP
# ===============================
def main():
    if "activities_log" not in st.session_state: st.session_state.activities_log = []
    if "license" not in st.session_state: st.session_state.license = "FREE"

    st.markdown("""<div style="background:linear-gradient(90deg, #FFD700 0%, #FFA500 100%); padding:15px;"><h1 style="color:black; text-align:center">📚 UCE/UACE DIGITAL TUTOR 2026 GOLD</h1></div>""", unsafe_allow_html=True)

    # LOGIN GATE
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("🔒 Login")
        password = st.text_input("Enter Access Key", type="password")
        if st.button("Login", type="primary"):
            FREE_PASS = st.secrets.get("FREE_PASSWORD")
            GOLD_PASS = st.secrets.get("GOLD_PASSWORD")
            if password == GOLD_PASS: st.session_state.authenticated = True; st.session_state.license = "GOLD"; st.rerun()
            elif password == FREE_PASS: st.session_state.authenticated = True; st.session_state.license = "FREE"; st.rerun()
            else: st.error("Invalid Access Key. Contact Admin.")
        st.stop()

    client = get_client()

    with st.sidebar:
        st.success(f"License: {st.session_state.license}")
        subject = st.selectbox("Subject", SUBJECTS)
        available_classes = ["S1", "S2", "S3", "S4"] if st.session_state.license == "FREE" and subject in GOLD_LOCKED_SUBJECTS else CLASSES
        class_level = st.selectbox("Class", available_classes)
        with st.expander(f"📖 {subject} {class_level} Topics"):
            for topic in get_topics(subject, class_level): st.write(f"• {topic}")
        mode = st.radio("Mode", MODES)
        st.markdown(f"[📞 WhatsApp Admin](https://wa.me/256{ADMIN_CONTACT[1:]})")

    # LOCK CHECK
    if class_level in GOLD_LOCKED_CLASSES and subject in GOLD_LOCKED_SUBJECTS and st.session_state.license == "FREE":
        show_gold_lock(subject); st.stop()

    # ===============================
    # ALL 12 MODES
    # ===============================
    if mode == "Smart Search":
        st.header("🧠 Smart Search")
        query = st.text_input("Ask any question")
        if st.button("Search") and query:
            resp = generate_ai_response(client, f"Explain {query}", subject, class_level)
            st.write(resp); log_activity(f"Smart: {query}", subject, class_level)

    elif mode == "Theory Mode":
        st.header("📘 Theory Mode")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Generate Notes"):
            resp = generate_ai_response(client, f"Detailed NCDC 2026 notes on {topic} for {class_level}", subject, class_level)
            st.write(resp); log_activity(f"Theory: {topic}", subject, class_level)

    elif mode == "Lesson Preparation":
        st.header("👨‍🏫 Lesson Preparation")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Generate Lesson Plan + AoI"):
            resp = generate_ai_response(client, f"40min competency-based lesson plan with AoI for {topic} in Ugandan context", subject, class_level)
            st.write(resp)
            pdf = create_pdf(resp, "lesson.pdf")
            st.download_button("Download PDF", pdf, "lesson.pdf")
            log_activity(f"Lesson: {topic}", subject, class_level)

    elif mode == "Diagrams Library":
        st.header("🖼️ Diagrams Library")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        path = find_diagram(topic)
        if path and os.path.exists(path):
            st.image(path, caption=topic, use_container_width=True)
        else: st.warning("Diagram not found in /assets folder")

    elif mode == "Practicals Lab":
        st.header("🧪 Practicals Lab")
        practical = st.selectbox("Select Practical", [p["name"] for p in PRACTICALS[subject]])
        if st.button("Show Practical"):
            p = next(p for p in PRACTICALS[subject] if p["name"] == practical)
            st.write(f"**Aim:** {p['aim']}")
            st.write(f"**Materials:** {p['materials']}")
            st.write(f"**Procedure:** {p['procedure']}")
            if p["graph"]:
                if st.button("Generate Sample Graph"):
                    x = np.linspace(0,10,20)
                    y = x * random.uniform(0.5,2) + np.random.randn(20)*2
                    fig = generate_graph(pd.DataFrame({"X":x,"Y":y}), "X","Y", p["graph"])
                    st.plotly_chart(fig, use_container_width=True)
            log_activity(f"Practical: {practical}", subject, class_level)

    elif mode == "Quiz Mode":
        st.header("📝 Quiz Mode")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Generate 5 MCQs"):
            resp = generate_ai_response(client, f"Generate 5 competency-based MCQs with answers on {topic} for {class_level}", subject, class_level)
            st.write(resp); log_activity(f"Quiz: {topic}", subject, class_level)

    elif mode == "Bulk Revision Generator":
        st.header("📚 Bulk Revision Generator")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        num_q = st.slider("Questions", 10, 50, 20)
        if st.button("Generate"):
            resp = generate_ai_response(client, f"Generate {num_q} UCE/UACE revision questions with answers on {topic}", subject, class_level)
            st.write(resp)
            pdf = create_pdf(resp, "revision.pdf")
            st.download_button("Download PDF", pdf, "revision.pdf")
            log_activity(f"Bulk: {topic}", subject, class_level)

    elif mode == "Predict Papers":
        st.header("📄 Predict Papers")
        if st.button("Predict Full Subject"):
            resp = generate_ai_response(client, f"Predict UCE/UACE competency-based questions for {class_level} {subject} with Ugandan context", subject, class_level)
            st.write(resp)
            pdf = create_pdf(resp, "predict.pdf")
            st.download_button("Download PDF", pdf, "predict.pdf")
            log_activity("Predict", subject, class_level)

    elif mode == "Voice Chat":
        st.header("🎤 Voice Chat")
        try:
            from streamlit_mic_recorder import mic_recorder
            from gtts import gTTS
            audio = mic_recorder(start_prompt="Record", stop_prompt="Stop")
            query = st.text_input("Or type question")
            if st.button("Send") and query:
                resp = generate_ai_response(client, query, subject, class_level)
                st.write(resp)
                tts = gTTS(resp)
                tts.save("resp.mp3")
                st.audio("resp.mp3")
                log_activity(f"Voice: {query}", subject, class_level)
        except Exception as e:
            st.error("Voice Chat library not available. " + str(e))

    elif mode == "Progress Tracker":
        st.header("📊 Progress Tracker")
        if st.session_state.activities_log:
            df = pd.DataFrame(st.session_state.activities_log)
            st.dataframe(df, use_container_width=True)
        else: st.info("No activities yet")

    elif mode == "Admin Dashboard":
        st.header("📈 Admin Dashboard")
        if st.session_state.activities_log:
            df = pd.DataFrame(st.session_state.activities_log)
            st.metric("Total Activities", len(df))
            st.dataframe(df, use_container_width=True)
            st.download_button("Download CSV", df.to_csv().encode(), "log.csv")

    elif mode == "Practical Assessment Generator":
        st.header("🧪 Practical AoI Generator")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Generate AoI"):
            resp = generate_ai_response(client, f"Generate Competency-based Activity of Integration for {topic} with Ugandan household scenario", subject, class_level)
            st.write(resp)
            log_activity(f"AoI: {topic}", subject, class_level)

if __name__ == "__main__":
    main()
