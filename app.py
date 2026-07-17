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

# HARDCODED APP BRANDING
st.set_page_config(
    page_title="UCE/UACE DIGITAL TUTOR 2026",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://wa.me/256751040731',
        'Report a bug': None,
        'About': "UCE/UACE DIGITAL TUTOR 2026\nAligned to NCDC Uganda Syllabus 2026\nFor S1-S4 Students"
    }
)

# LICENSE CONTROL
LICENSE_TIER = "FREE"
ADMIN_CONTACT = "0751040731"
APP_PASSWORD = st.secrets["APP_PASSWORD"]
UGANDA_TZ = pytz.timezone("Africa/Kampala")

# FIXED PATH: Files are in /assets/ not /assets/diagrams/
BASE_DIR = Path(__file__).parent.resolve()
DIAGRAMS_DIR = BASE_DIR / "assets"

# UPDATE SUBJECTS BASED ON LICENSE
if LICENSE_TIER == "FREE":
    SUBJECTS = ["Physics", "Chemistry", "Biology"]
    CLASSES = ["S1", "S2", "S3", "S4"]
else:
    SUBJECTS = ["Physics", "Chemistry", "Biology", "Mathematics"]
    CLASSES = ["S1", "S2", "S3", "S4", "S5", "S6"]

MODES = ["Smart Search", "Theory Mode", "Lesson Preparation", "Diagrams Library", "Practicals Lab", "Quiz Mode", "Predict Papers", "Voice Chat", "Progress Tracker"]

# SYLLABUS TOPICS - NCDC 2026 ONLY
SYLLABUS = {
    "Physics": {
        "S1": ["Introduction to Physics", "Matter", "Measurement", "Energy", "Light", "Sound", "Heat", "Electricity", "Magnetism", "Machines"],
        "S2": ["Motion", "Forces", "Work Energy Power", "Pressure", "Waves", "Electrostatics", "Current Electricity", "Optics"],
        "S3": ["Linear Motion", "Newton's Laws", "Momentum", "Gravitation", "Properties of Matter", "Thermal Physics", "Waves II", "Magnetism"],
        "S4": ["Radioactivity", "Electronics", "AC/DC", "Nuclear Physics", "Astrophysics", "Advanced Mechanics"]
    },
    "Chemistry": {
        "S1": ["Introduction to Chemistry", "Matter", "Atoms", "Molecules", "Acids Bases", "Air", "Water", "Chemical Reactions"],
        "S2": ["Periodic Table", "Chemical Bonding", "Acids Bases Salts", "Carbon", "Metals", "Non-metals", "Energy Changes"],
        "S3": ["Chemical Kinetics", "Equilibrium", "Electrochemistry", "Organic Chemistry", "Industrial Processes"],
        "S4": ["Advanced Organic", "Analytical Chemistry", "Environmental Chemistry", "Polymers"]
    },
    "Biology": {
        "S1": ["Introduction to Biology", "Cells", "Classification", "Nutrition", "Respiration", "Transport", "Ecology", "Transport in Plants"],
        "S2": ["Reproduction", "Genetics", "Growth", "Human Body Systems", "Disease", "Immunity", "Respiratory System", "Alveolus", "Human Ear", "Human Eye"],
        "S3": ["Ecology II", "Evolution", "Genetics II", "Physiology", "Microbiology"],
        "S4": ["Molecular Biology", "Biotechnology", "Conservation", "Human Health"]
    }
}

# 10 PRACTICALS
PRACTICALS = {
    "Physics": [
        {"name": "Measuring Length and Time", "aim": "Use rulers and stopwatches accurately", "materials": "Meter rule, Stopwatch, String", "procedure": "1. Measure length 10 times 2. Calculate average 3. Find error", "graph": "Length vs Time"},
        {"name": "Density of Regular Object", "aim": "Determine density using mass and volume", "materials": "Beam balance, Vernier calipers, Metal block", "procedure": "1. Measure mass 2. Measure dimensions 3. Calculate volume 4. Density = m/v", "graph": "Mass vs Volume"},
        {"name": "Simple Pendulum", "aim": "Investigate factors affecting period", "materials": "String, Bob, Stand, Stopwatch", "procedure": "1. Vary length 2. Time 20 oscillations 3. Plot T^2 vs L", "graph": "T^2 vs Length"},
        {"name": "Ohm's Law", "aim": "Verify V = IR", "materials": "Battery, Resistor, Ammeter, Voltmeter", "procedure": "1. Vary voltage 2. Record current 3. Plot V vs I", "graph": "V vs I"},
        {"name": "Focal Length of Lens", "aim": "Find focal length using object-image method", "materials": "Convex lens, Screen, Object pin", "procedure": "1. Vary object distance 2. Find image distance 3. Use lens formula", "graph": "1/u vs 1/v"},
        {"name": "Specific Heat Capacity", "aim": "Find specific heat of metal", "materials": "Calorimeter, Heater, Thermometer", "procedure": "1. Heat metal 2. Transfer to water 3. Measure temp change", "graph": "Temperature vs Time"},
        {"name": "Refraction of Light", "aim": "Find refractive index of glass", "materials": "Glass block, Pins, Protractor", "procedure": "1. Trace rays 2. Measure angles 3. Use Snell's Law", "graph": "sin i vs sin r"},
        {"name": "Surface Tension", "aim": "Determine surface tension by capillary rise", "materials": "Capillary tubes, Beaker, Water", "procedure": "1. Dip tube 2. Measure height 3. Calculate", "graph": "h vs 1/r"},
        {"name": "Resonance in Air Column", "aim": "Find speed of sound", "materials": "Resonance tube, Tuning fork", "procedure": "1. Find first and second resonance 2. Calculate wavelength", "graph": "L vs 1/f"},
        {"name": "Magnetic Field of Coil", "aim": "Investigate field strength", "materials": "Coil, Compass, Battery", "procedure": "1. Vary current 2. Measure deflection 3. Plot", "graph": "Deflection vs Current"}
    ],
    "Chemistry": [
        {"name": "Testing for Cations", "aim": "Identify metal ions", "materials": "Test tubes, NaOH, NH3", "procedure": "1. Add reagents 2. Observe precipitate 3. Record", "graph": None},
        {"name": "Testing for Anions", "aim": "Identify acid radicals", "materials": "BaCl2, AgNO3, HCl", "procedure": "1. Add reagents 2. Observe gas/precipitate", "graph": None},
        {"name": "Titration - Acid Base", "aim": "Find concentration of HCl", "materials": "Burette, Pipette, NaOH, Indicator", "procedure": "1. Titrate 2. Record volumes 3. Calculate", "graph": "Volume vs pH"},
        {"name": "Rate of Reaction", "aim": "Effect of concentration on rate", "materials": "HCl, Marble chips, Gas syringe", "procedure": "1. Vary concentration 2. Measure gas volume vs time", "graph": "Volume vs Time"},
        {"name": "Electrolysis of Water", "aim": "Decompose water", "materials": "Hoffman apparatus, Electrodes", "procedure": "1. Electrolyze 2. Collect gases 3. Test", "graph": "Volume H2 vs Volume O2"},
        {"name": "Solubility Curve", "aim": "Plot solubility vs temperature", "materials": "KNO3, Beaker, Thermometer", "procedure": "1. Dissolve at different T 2. Plot curve", "graph": "Solubility vs Temperature"},
        {"name": "Organic Preparation - Ethene", "aim": "Prepare ethene gas", "materials": "Ethanol, Conc H2SO4", "procedure": "1. Heat 2. Collect gas 3. Test", "graph": None},
        {"name": "Chromatography", "aim": "Separate ink components", "materials": "Filter paper, Solvent", "procedure": "1. Spot ink 2. Develop 3. Calculate Rf", "graph": None},
        {"name": "Enthalpy Change", "aim": "Find heat of reaction", "materials": "Calorimeter, Acid, Base", "procedure": "1. Mix 2. Measure temp change 3. Calculate", "graph": "Temperature vs Time"},
        {"name": "Redox Titration", "aim": "Find Fe2+ concentration", "materials": "KMnO4, FeSO4", "procedure": "1. Titrate 2. Use equation", "graph": None}
    ],
    "Biology": [
        {"name": "Microscope Use", "aim": "Observe plant and animal cells", "materials": "Microscope, Onion, Cheek cells", "procedure": "1. Prepare slide 2. Observe 3. Draw", "graph": None},
        {"name": "Food Tests", "aim": "Test for nutrients", "materials": "Food samples, Iodine, Benedicts", "procedure": "1. Add reagents 2. Observe color change", "graph": None},
        {"name": "Osmosis in Potato", "aim": "Investigate osmosis", "materials": "Potato, Salt solutions", "procedure": "1. Cut pieces 2. Soak 3. Measure change", "graph": "Concentration vs % Change"},
        {"name": "Transpiration Rate", "aim": "Measure water loss", "materials": "Potometer, Plant shoot", "procedure": "1. Set up 2. Measure bubble movement", "graph": "Time vs Distance"},
        {"name": "Photosynthesis", "aim": "Test for starch", "materials": "Leaf, Iodine, Alcohol", "procedure": "1. Destarch 2. Expose to light 3. Test", "graph": None},
        {"name": "Heart Rate Response", "aim": "Effect of exercise", "materials": "Stopwatch", "procedure": "1. Measure at rest 2. After exercise", "graph": "Time vs Heart Rate"},
        {"name": "Germination Factors", "aim": "Effect of water/light", "materials": "Seeds, Cotton", "procedure": "1. Set conditions 2. Observe daily", "graph": "% Germination vs Days"},
        {"name": "Enzyme Activity", "aim": "Effect of pH on amylase", "materials": "Amylase, Starch, Iodine", "procedure": "1. Vary pH 2. Time for digestion", "graph": "pH vs Time"},
        {"name": "Ecological Sampling", "aim": "Quadrat method", "materials": "Quadrat, String", "procedure": "1. Sample area 2. Count species", "graph": "Species vs Frequency"},
        {"name": "Blood Smear", "aim": "Identify blood cells", "materials": "Microscope, Prepared slide", "procedure": "1. Observe 2. Draw and label", "graph": None}
    ]
}

def get_client():
    api_key = st.secrets["GROQ_API_KEY"]
    if not api_key: st.error("GROQ_API_KEY not set in secrets"); st.stop()
    return Groq(api_key=api_key)

def generate_ai_response(client, prompt, subject, class_level):
    system_prompt = f"You are UCE/UACE DIGITAL TUTOR 2026. You teach {subject} for {class_level} in Uganda. Answer ONLY according to NCDC Uganda Syllabus 2026 and UNEB guidelines. Be accurate, cite NCDC where possible. Use Ugandan examples. Be clear and step-by-step. If question is outside NCDC syllabus, say 'This is outside NCDC 2026 syllabus'."
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
            temperature=0.3, max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

def generate_graph(data, x_col, y_col, title):
    fig = px.line(data, x=x_col, y=y_col, title=title, markers=True)
    fig.update_layout(template="plotly_white")
    return fig

def create_pdf(content, filename):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 12)
    y = height - 50
    for line in content.split('\n'):
        c.drawString(50, y, line[:90])
        y -= 20
        if y < 50: c.showPage(); y = height - 50
    c.save()
    buffer.seek(0)
    return buffer

def sanitize_filename(name):
    name = name.lower()
    name = re.sub(r'[^a-z0-9\s]', '', name)
    return name

def find_diagram(topic):
    """FIXED: Now looks in /assets/ directly"""
    debug_info = []
    debug_info.append(f"App Root: {BASE_DIR}")
    debug_info.append(f"Looking in: {DIAGRAMS_DIR}")
    debug_info.append(f"Folder Exists: {DIAGRAMS_DIR.exists()}")

    if not DIAGRAMS_DIR.exists():
        try:
            root_files = [f.name for f in BASE_DIR.iterdir()]
            debug_info.append(f"Files in root: {root_files}")
        except: pass
        return None, debug_info

    all_pngs = list(DIAGRAMS_DIR.glob("*.png"))
    all_filenames = [f.name for f in all_pngs]
    debug_info.append(f"Found {len(all_filenames)} PNGs")

    search_key = sanitize_filename(topic)
    search_words = [w for w in search_key.split() if len(w) > 2]

    KEYWORD_MAP = {
        "respiration": ["respiratory_system"], "transport in plants": ["transport_in_plants"],
        "microbiology": ["prokaryotic_eukaryotic", "chemical_cell"], "human eye": ["human_eye"],
        "human ear": ["human_ear"], "alveolus": ["alveolus", "respiratory_system"],
        "cells": ["animal_cell", "plant_cell", "chemical_cell"], "chemical bonding": ["chemical_bonding", "covalent_water"],
        "waves": ["transverse_wave", "longitudinal_wave"], "light": ["light_reflection", "convex_concave_lens"],
        "electricity": ["simple_circuit", "ac_dc_electricity"], "ac/dc": ["ac_dc_electricity", "ac_generator"],
        "electronics": ["transformer", "ac_generator", "cro"], "magnetism": ["bar_magnet", "electroscope"],
        "measurement": ["vernier", "spring_balance"], "motion": ["linear_motion", "pendulum"],
        "heat": ["heat_capacity", "colorimeter"], "radioactivity": ["radioactivity"],
        "dna": ["dna"], "ecology": ["ecology"], "atoms": ["atom"], "leaf": ["leaf"],
        "neurone": ["neurone"], "nephron": ["nephron"], "growth": ["human_growth_cycle"],
        "body systems": ["body_systems", "heart", "human_brain"],
    }

    for key, possible_files in KEYWORD_MAP.items():
        if key in search_key:
            for pf in possible_files:
                for f in all_pngs:
                    if pf in f.name.lower():
                        return str(f), debug_info + all_filenames

    best_match = None; best_score = 0
    for png_path in all_pngs:
        filename = png_path.name.lower().replace(".png", "")
        score = sum(1 for word in search_words if word in filename)
        if score > best_score: best_score = score; best_match = png_path

    if best_score >= 1: return str(best_match), debug_info + all_filenames
    return None, debug_info + all_filenames

def main():
    client = get_client()
    if "activities_log" not in st.session_state: st.session_state.activities_log = []
    if "chat_history" not in st.session_state: st.session_state.chat_history = []

    st.markdown("""<div style="background:linear-gradient(90deg, #0E4D92 0%, #1a75ff 100%); padding:15px; border-radius:10px; margin-bottom:20px"><h1 style="color:white; margin:0; text-align:center">📚 UCE/UACE DIGITAL TUTOR 2026</h1><p style="color:#d9e8ff; margin:0; text-align:center">Aligned to NCDC Uganda Syllabus 2026 | S1-S4 | Physics | Chemistry | Biology</p></div>""", unsafe_allow_html=True)

    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("🔒 UCE/UACE DIGITAL TUTOR 2026 - Login")
        password = st.text_input("Enter Password", type="password")
        if st.button("Login"):
            if password == APP_PASSWORD: st.session_state.authenticated = True; st.rerun()
            else: st.error("Incorrect Password")
        st.stop()

    with st.sidebar:
        st.header("Settings")
        subject = st.selectbox("Select Subject", SUBJECTS)
        class_level = st.selectbox("Select Class", CLASSES)
        st.markdown("---")
        st.subheader("📖 Topics in Syllabus")
        with st.expander(f"View {subject} {class_level} Topics"):
            for topic in SYLLABUS[subject][class_level]: st.write(f"• {topic}")
        if LICENSE_TIER == "FREE": st.warning(f"🔒 Upgrade to Pro to unlock: Mathematics + S5 + S6")
        mode = st.radio("Select Mode", MODES)
        st.markdown("---")
        st.subheader("Need Help?")
        st.write(f"**Contact Admin to Upgrade or Report Issue**")
        st.markdown(f"[📞 WhatsApp/Call: {ADMIN_CONTACT}](https://wa.me/256{ADMIN_CONTACT[1:]})")
        st.caption("Disclaimer: This app is aligned to NCDC Uganda Syllabus 2026 for practice purposes only.")

    if mode == "Smart Search":
        st.header("🧠 Smart Search")
        query = st.text_input("Ask any question from the syllabus", key="ask_smart")
        if st.button("Search", key="btn_smart") and query:
            prompt = f"Explain {query} for {class_level} {subject} in Uganda according to NCDC 2026 syllabus. Give examples."
            response = generate_ai_response(client, prompt, subject, class_level)
            st.write(response)
            st.session_state.activities_log.append({"time": datetime.now(UGANDA_TZ), "activity": f"Smart Search: {query}"})

    elif mode == "Theory Mode":
        st.header("📘 Theory Mode")
        query = st.text_input("Ask about any theory topic", key="ask_theory")
        topic_dropdown = st.selectbox("Or Select Topic", SYLLABUS[subject][class_level], key="topic_theory")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Ask AI", key="btn_theory_ask") and query:
                prompt = f"Give detailed theory notes on {query} for {class_level} {subject} Uganda NCDC 2026 syllabus. Include definitions, examples, formulas."
                response = generate_ai_response(client, prompt, subject, class_level)
                st.write(response)
                st.session_state.activities_log.append({"time": datetime.now(UGANDA_TZ), "activity": f"Theory Ask: {query}"})
        with col2:
            if st.button("Explain Selected Topic", key="btn_theory_topic"):
                prompt = f"Give detailed theory notes on {topic_dropdown} for {class_level} {subject} Uganda NCDC 2026 syllabus. Include definitions, examples, formulas."
                response = generate_ai_response(client, prompt, subject, class_level)
                st.write(response)
                st.session_state.activities_log.append({"time": datetime.now(UGANDA_TZ), "activity": f"Theory: {topic_dropdown}"})

    elif mode == "Lesson Preparation":
        st.header("👨‍🏫 Lesson Preparation")
        query = st.text_input("Ask to prepare a lesson on any topic", key="ask_lesson")
        topic_dropdown = st.selectbox("Or Select Topic", SYLLABUS[subject][class_level], key="topic_lesson")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate Lesson Plan", key="btn_lesson_ask") and query:
                prompt = f"Prepare a 40-minute lesson plan for {query} for {class_level} {subject} in Uganda according to NCDC 2026. Include objectives, materials, introduction, procedure, activities, conclusion, assessment."
                response = generate_ai_response(client, prompt, subject, class_level)
                st.write(response)
                pdf = create_pdf(response, "lesson_plan.pdf")
                st.download_button("Download Lesson Plan PDF", pdf, "lesson_plan.pdf", key="dl_lesson_ask")
                st.session_state.activities_log.append({"time": datetime.now(UGANDA_TZ), "activity": f"Lesson Plan Ask: {query}"})
        with col2:
            if st.button("Generate for Selected Topic", key="btn_lesson_topic"):
                prompt = f"Prepare a 40-minute lesson plan for {topic_dropdown} for {class_level} {subject} in Uganda according to NCDC 2026. Include objectives, materials, introduction, procedure, activities, conclusion, assessment."
                response = generate_ai_response(client, prompt, subject, class_level)
                st.write(response)
                pdf = create_pdf(response, "lesson_plan.pdf")
                st.download_button("Download Lesson Plan PDF", pdf, "lesson_plan.pdf", key="dl_lesson_topic")
                st.session_state.activities_log.append({"time": datetime.now(UGANDA_TZ), "activity": f"Lesson Plan: {topic_dropdown}"})

    elif mode == "Diagrams Library":
        st.header("🖼️ Diagrams Library")
        st.write("Visual aids aligned to NCDC 2026. Download and use in class.")
        topic = st.selectbox("Select Topic to View Diagram", SYLLABUS[subject][class_level], key="diagram_topic")
        diagram_path, debug_list = find_diagram(topic)

        if diagram_path and os.path.exists(diagram_path):
            image = Image.open(diagram_path)
            st.image(image, caption=f"{subject} {class_level} - {topic}", use_column_width=True)
            with open(diagram_path, "rb") as file:
                st.download_button("⬇️ Download PNG", file, file_name=os.path.basename(diagram_path), mime="image/png", key=f"dl_diagram_{topic}")
            st.success(f"Found: `{os.path.basename(diagram_path)}`")
        else:
            st.error(f"Diagram for '{topic}' not found yet.")
            st.markdown("**DEBUG INFO:**")
            st.code("\n".join(debug_list))

        st.session_state.activities_log.append({"time": datetime.now(UGANDA_TZ), "activity": f"Diagram: {topic}"})

    elif mode == "Practicals Lab":
        st.header("🧪 Practicals Lab")
        query = st.text_input("Ask about any practical", key="ask_practical")
        practical = st.selectbox("Or Select Practical", [p["name"] for p in PRACTICALS[subject]], key="practical_select")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Ask AI About Practical", key="btn_practical_ask") and query:
                prompt = f"Explain the practical '{query}' for {class_level} {subject} according to NCDC 2026. Give aim, materials, procedure, precautions."
                response = generate_ai_response(client, prompt, subject, class_level)
                st.write(response)
                st.session_state.activities_log.append({"time": datetime.now(UGANDA_TZ), "activity": f"Practical Ask: {query}"})
        with col2:
            if st.button("Show Selected Practical", key="btn_practical_show"):
                p_data = next(p for p in PRACTICALS[subject] if p["name"] == practical)
                st.subheader(p_data["name"])
                st.write(f"**Aim:** {p_data['aim']}")
                st.write(f"**Materials:** {p_data['materials']}")
                st.write(f"**Procedure:** {p_data['procedure']}")
                if p_data["graph"]:
                    st.info(f"Suggested Graph: {p_data['graph']}")
                    if st.button("Generate Sample Graph", key="btn_graph"):
                        x = np.linspace(0, 10, 20)
                        y = x * random.uniform(0.5, 2)
                        df = pd.DataFrame({"X": x, "Y": y})
                        fig = generate_graph(df, "X", "Y", p_data["graph"])
                        st.plotly_chart(fig)
                st.session_state.activities_log.append({"time": datetime.now(UGANDA_TZ), "activity": f"Practical: {practical}"})

    elif mode == "Quiz Mode":
        st.header("📝 Quiz Mode")
        query = st.text_input("Ask to generate quiz on any topic", key="ask_quiz")
        topic_dropdown = st.selectbox("Or Select Topic", SYLLABUS[subject][class_level], key="topic_quiz")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate Quiz", key="btn_quiz_ask") and query:
                prompt = f"Generate 5 MCQ questions on {query} for {class_level} {subject} based on NCDC 2026 syllabus. Include answers."
                response = generate_ai_response(client, prompt, subject, class_level)
                st.write(response)
                st.session_state.activities_log.append({"time": datetime.now(UGANDA_TZ), "activity": f"Quiz Ask: {query}"})
        with col2:
            if st.button("Generate for Selected Topic", key="btn_quiz_topic"):
                prompt = f"Generate 5 MCQ questions on {topic_dropdown} for {class_level} {subject} based on NCDC 2026 syllabus. Include answers."
                response = generate_ai_response(client, prompt, subject, class_level)
                st.write(response)
                st.session_state.activities_log.append({"time": datetime.now(UGANDA_TZ), "activity": f"Quiz: {topic_dropdown}"})

    elif mode == "Predict Papers":
        st.header("📄 Predict Papers")
        query = st.text_input("Ask to predict papers for specific topic", key="ask_predict")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Predict for Asked Topic", key="btn_predict_ask") and query:
                prompt = f"Predict likely exam questions on {query} for {class_level} {subject} UCE/UACE based on NCDC 2026 syllabus only."
                response = generate_ai_response(client, prompt, subject, class_level)
                st.write(response)
                pdf = create_pdf(response, "prediction.pdf")
                st.download_button("Download PDF", pdf, "prediction.pdf", key="dl_predict_ask")
                st.session_state.activities_log.append({"time": datetime.now(UGANDA_TZ), "activity": f"Predict Ask: {query}"})
        with col2:
            if st.button("Predict Full Subject", key="btn_predict_full"):
                prompt = f"Predict likely exam questions for {class_level} {subject} UCE/UACE based on NCDC 2026 syllabus only."
                response = generate_ai_response(client, prompt, subject, class_level)
                st.write(response)
                pdf = create_pdf(response, "prediction.pdf")
                st.download_button("Download PDF", pdf, "prediction.pdf", key="dl_predict_full")
                st.session_state.activities_log.append({"time": datetime.now(UGANDA_TZ), "activity": "Predict Paper"})

    elif mode == "Voice Chat":
        st.header("🎤 Voice Chat")
        query = st.text_input("Type your question here too", key="ask_voice")
        audio = mic_recorder(start_prompt="Record", stop_prompt="Stop", key="recorder")
        if audio: st.audio(audio["bytes"])
        if st.button("Send Typed Question", key="btn_voice_text") and query:
            response = generate_ai_response(client, query, subject, class_level)
            st.write(response)
            tts = gTTS(response)
            tts.save("response.mp3")
            st.audio("response.mp3")
            st.session_state.activities_log.append({"time": datetime.now(UGANDA_TZ), "activity": f"Voice Ask: {query}"})

    elif mode == "Progress Tracker":
        st.header("📊 Progress Tracker")
        query = st.text_input("Ask about your progress", key="ask_progress")
        if st.button("Ask AI", key="btn_progress") and query:
            prompt = f"A student is using UCE/UACE DIGITAL TUTOR for {subject} {class_level} NCDC 2026. They ask: {query}. Give helpful advice."
            response = generate_ai_response(client, prompt, subject, class_level)
            st.write(response)
        if st.session_state.activities_log:
            st.subheader("Activity Log")
            df = pd.DataFrame(st.session_state.activities_log)
            st.dataframe(df)
        else: st.info("No activities yet")

if __name__ == "__main__":
    main()
