import streamlit as st
import os, io, json, re, ast, numpy as np, difflib, time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sympy as sp
from datetime import datetime
from groq import Groq, RateLimitError
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
import base64
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS

LOG_FILE = "usage_log.json"
CONTACT = "256751040731"
AI_MODEL_LONG = "llama-3.3-70b-versatile"
AI_MODEL_FAST = "llama-3.1-8b-instant"

# ============ LOGGING SYSTEM ============
def load_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try: return json.load(f)
            except: return []
    return []

def save_log(entry):
    logs = load_logs()
    logs.append(entry)
    with open(LOG_FILE, "w") as f: json.dump(logs, f, indent=2)

def log_activity(user_type, action, details):
    entry = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user_type, "action": action, "details": details}
    save_log(entry)

# ============ PASSWORD GATE ============
def check_password():
    APP_PW = st.secrets.get("APP_PASSWORD", "UNEB2026")
    ADMIN_PW = st.secrets.get("ADMIN_PASSWORD", "ADMIN256")

    def password_entered():
        pw = st.session_state["password"]
        if pw == APP_PW: st.session_state["user_type"] = "Student"; st.session_state["password_correct"] = True
        elif pw == ADMIN_PW: st.session_state["user_type"] = "Admin"; st.session_state["password_correct"] = True
        else: st.session_state["password_correct"] = False
        if "password" in st.session_state: del st.session_state["password"]

    if "password_correct" not in st.session_state:
        st.title("🔒 DIGITAL UNEB TUTOR 2026 - Login")
        st.text_input("Enter Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔒 DIGITAL UNEB TUTOR 2026 - Login")
        st.text_input("Enter Password", type="password", on_change=password_entered, key="password")
        st.error("😞 Password incorrect")
        return False
    else: return True

if not check_password(): st.stop()

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026", page_icon="📚", layout="wide")

# ============ FULL OFFICIAL NCDC SYLLABUS S1-S6 - 100% INTACT ============
UNEB_CURRICULUM_MAP = {
    "Mathematics": {
        "S1": ["Number Bases", "Integers", "Fractions, Percentages and Decimals", "Cartesian Coordinates", "Geometric Construction", "Data Collection and Representation"],
        "S2": ["Patterns and Sequences", "Bearings", "Angle Properties", "Algebra I", "Business Arithmetic I", "Time and Time Tables", "Mapping and Relations"],
        "S3": ["Business Arithmetic II", "Quadratic Equations", "Matrices", "Probability", "Vectors", "Trigonometry I", "Mensuration"],
        "S4": ["Functions", "Three-Dimensional Geometry", "Statistics", "Linear Programming", "Trigonometry II", "Calculus Introduction"],
        "S5": ["Calculus: Differentiation", "Calculus: Integration", "Circular Measure", "Binomial Expansion", "Complex Numbers", "Sequences and Series"],
        "S6": ["Differential Equations", "Mechanics: Kinematics and Dynamics", "Probability Distributions", "Linear Programming Advanced", "Further Calculus", "Vectors in 3D"]
    },
    "Physics": {
        "S1": ["Introduction to Physics", "Measurement", "Forces and Their Effects", "Work, Energy and Power", "Pressure in Fluids", "Simple Machines"],
        "S2": ["Light: Reflection and Refraction", "Thermal Physics", "Static Electricity", "Current Electricity I", "Waves I"],
        "S3": ["Current Electricity II", "Magnetism", "Waves II: Sound", "Mechanics Continued", "Specific Heat Capacity"],
        "S4": ["Electromagnetism", "Electronics", "Modern Physics", "Nuclear Processes", "A.C Theory", "Astrophysics"],
        "S5": ["Mechanics: Motion and Dynamics", "Gravitation", "Thermal Physics Advanced", "Waves III: Interference and Diffraction", "Optics", "Fluid Mechanics"],
        "S6": ["Electric Fields", "Magnetic Fields", "Electromagnetic Induction", "Quantum Physics", "Radioactivity", "Solid State and Electronics"]
    },
    "Chemistry": {
        "S1": ["Chemistry and Society", "Experimental Chemistry", "States of Matter", "Temporary and Permanent Changes", "Mixtures, Elements and Compounds", "Air", "Water", "Rocks and Minerals"],
        "S2": ["Acids and Alkalis", "Salts", "The Periodic Table", "Carbon in the Environment", "Reactivity Series", "Metals and Non-Metals"],
        "S3": ["Structure and Bonding", "Stoichiometry and Mole Concept", "Fossil Fuels", "Properties and Structures of Substances", "Chemical Reactions", "Rates of Reaction"],
        "S4": ["REDOX Reactions", "Industrial Processes", "Trends in the Periodic Table", "Thermochemistry", "Consumable Chemicals", "Organic Chemistry II", "Nuclear Processes"],
        "S5": ["Atomic Structure Advanced", "Chemical Energetics", "Chemical Kinetics", "Equilibrium II", "Organic Chemistry III", "Acids, Bases and Buffers"],
        "S6": ["Electrochemistry Advanced", "Transition Metals and Complexes", "Organic Synthesis", "Analytical Chemistry", "Environmental Chemistry", "Polymers"]
    },
    "Biology": {
        "S1": ["Introduction to Biology", "Cells and the Microscope", "Classification of Living Things", "Insects", "Flowering Plants", "Ecosystems"],
        "S2": ["Soil Composition and Properties", "Soil Erosion and Conservation", "Nitrogen Cycle", "Nutrition in Plants", "Nutrition in Animals", "Transport in Living Things"],
        "S3": ["Transport in Plants and Animals", "Respiration and Gas Exchange", "Excretion and Homeostasis", "Cell Division", "Reproduction in Plants", "DNA and Genetics I"],
        "S4": ["Coordination and Receptors", "Locomotion", "Growth and Development", "Genetics and Inheritance", "Ecology", "Evolution", "Environmental Conservation"],
        "S5": ["Cell Biology", "Enzymes", "Transport in Plants Advanced", "Gas Exchange Systems", "Nutrition in Humans Advanced", "Respiration Cellular"],
        "S6": ["Hormonal Control and Feedback", "Coordination: Nervous System Advanced", "Population Ecology", "Biotechnology", "Genetic Engineering", "Immunity and Disease"]
    }
}

PRACTICAL_TOPICS = {
    "Mathematics": {
        "S1": ["Scale Drawing and Measurement", "Data Collection Survey Project", "Geometric Construction of Angles and Triangles", "Cartesian Plane Plotting Activity"],
        "S2": ["Real-life Budgeting Project", "Mapping School Compound using Bearings", "Tracking Local Market Price Data", "Building Patterns with Matchsticks"],
        "S3": ["Simulating PAYE and Mobile Money Charges", "Building Probability Models with Dice/Coins", "Vector Navigation Mapping of School", "Quadratic Equation Graphical Solution"],
        "S4": ["Linear Programming for Business Optimization", "Building 3D Geometric Models", "Processing Census Data", "Statistical Survey and Report Writing"],
        "S5": ["Optimization using Differentiation", "Area under Curves by Integration", "Modeling Circular Motion", "Binomial Expansion Applications"],
        "S6": ["Solving Differential Equations Numerically", "Projectile and Circular Motion Lab", "Normal Distribution Data Analysis", "Linear Programming for Industries"]
    },
    "Physics": {
        "S1": ["Measuring Volume using Measuring Cylinders", "Finding Density of Regular and Irregular Objects", "Demonstrating Capillary Action", "Surface Tension Experiments", "Hooke's Law - Stretching Springs"],
        "S2": ["Laws of Reflection using Plane Mirrors", "Refraction through Glass Block", "Construction of Pinhole Camera", "Charging by Friction and Induction", "Gold-leaf Electroscope", "Thermometer Calibration"],
        "S3": ["Series and Parallel Circuits", "Verifying Ohm's Law V=IR", "Mapping Magnetic Fields", "Speed of Sound using Resonance", "Simple Pendulum", "Specific Heat Capacity"],
        "S4": ["Electromagnetic Induction", "Transformers Step-up/down", "Logic Gates AND OR NOT", "Properties of Cathode Rays", "Rectification using Diodes", "Radioactivity Simulation"],
        "S5": ["Projectile Motion Experiment", "Verification of Laws of Gravitation", "Thermal Conductivity of Metals", "Wave Interference using Ripple Tank", "Lens and Mirror Experiments"],
        "S6": ["Electric Field Mapping", "Magnetic Force on Current Carrying Wire", "Faraday's Law Induction", "Photoelectric Effect Demo", "Half-life of Radioactive Material", "Semiconductor Diode Characteristics"]
    },
    "Chemistry": {
        "S1": ["Criteria for Purity", "Filtration and Evaporation", "Simple and Fractional Distillation", "Paper Chromatography", "Heating Copper(II) Sulfate", "Testing for Air Components"],
        "S2": ["Testing with Litmus and pH Indicators", "Investigating pH Scale", "Preparation of Soluble Salts", "Preparation of Insoluble Salts", "Effect of Heat on Carbonates", "Reactivity Series"],
        "S3": ["Conductivity of Ionic vs Covalent", "Acid-Base Volumetric Titrations", "Calculating Molarity", "Rates of Reaction", "Testing for Hard Water", "Extraction of Metals"],
        "S4": ["Qualitative Analysis: Cations", "Qualitative Analysis: Anions", "Testing for Gases", "Saponification: Making Soap", "Fermentation of Sugar", "Heat of Reaction"],
        "S5": ["Enthalpy Change Experiments", "Rate of Reaction: Collision Theory", "Equilibrium and Le Chatelier", "Organic Preparation: Esterification", "Buffer Solutions", "Electrolysis"],
        "S6": ["Redox Titrations", "Complex Ion Formation", "Organic Synthesis: Aspirin", "Gravimetric and Volumetric Analysis", "Water Quality Testing", "Polymerization"]
    },
    "Biology": {
        "S1": ["Using Light Microscope", "Preparing Onion and Cheek Cell Slides", "Drawing Biological Specimens", "Dichotomous Keys", "Dissection of Flower"],
        "S2": ["Soil Water Retention", "Soil Capillarity", "Soil Organic Matter", "Food Tests: Sugars, Starch, Protein, Lipids", "Factors Affecting Photosynthesis", "Testing for Vitamin C"],
        "S3": ["Osmosis using Potato Osmometers", "Transpiration using Potometer", "Examining Gills and Lungs", "Pulse Rate Before/After Exercise", "Testing Urine for Glucose", "Observing Mitosis"],
        "S4": ["Knee-jerk and Pupillary Reflex", "Geotropism and Phototropism", "Growth Curves in Plants", "Quadrats and Line Transects", "DNA Extraction", "Blood Grouping"],
        "S5": ["Enzyme Activity: Amylase", "Transport in Plants: Xylem/Phloem", "Gas Exchange in Leaf", "Human Digestive System Dissection", "Cellular Respiration Experiment"],
        "S6": ["Hormone Effect on Plants", "Reflex Arc Model", "Population Sampling Techniques", "Bacterial Culture and Staining", "DNA Model Building", "Antibody-Antigen Reaction Demo"]
    }
}

AOI_FRAMEWORK = {"S1": "Community Problem: Water purification, Waste management, Road safety.", "S2": "Local Industry Problem: Soil conservation, Energy saving, Market pricing.", "S3": "National Issue: Disease prevention, Electricity access, Food security.", "S4": "Global/Local Challenge: Climate change, Technology innovation, Health campaigns.", "S5": "Research and Innovation: Renewable energy, Biotechnology, Advanced materials.", "S6": "Professional Level: Data analysis for policy, Engineering design, Medical diagnostics."}

DIAGRAM_MAP = {"Biology": {"cell": "assets/cell.png", "microscope": "assets/microscope.png", "heart": "assets/heart.png", "dna": "assets/dna.png", "plant": "assets/plant.png", "flower": "assets/flower.png"}, "Physics": {"circuit": "assets/circuit.png", "pendulum": "assets/pendulum.png", "wave": "assets/wave.png", "magnet": "assets/magnet.png", "lens": "assets/lens.png"}, "Chemistry": {"atom": "assets/atom.png", "molecule": "assets/molecule.png", "beaker": "assets/beaker.png", "bunsen": "assets/bunsen.png"}, "Mathematics": {"graph": "assets/graph.png", "triangle": "assets/triangle.png", "circle": "assets/circle.png", "matrix": "assets/matrix.png"}}

@st.cache_resource
def get_client(): return Groq(api_key=st.secrets["GROQ_API_KEY"])

def add_to_memory(role, content):
    if "chat_memory" not in st.session_state: st.session_state.chat_memory = []
    st.session_state.chat_memory.append({"role": role, "content": content, "time": datetime.now().strftime("%H:%M")})

def add_performance(subject, topic, score):
    today = datetime.now().strftime("%Y-%m-%d")
    if "performance" not in st.session_state: st.session_state.performance = {}
    if today not in st.session_state.performance: st.session_state.performance[today] = []
    st.session_state.performance[today].append({"subject":subject, "topic":topic, "score":score})

def get_memory_context():
    if "chat_memory" not in st.session_state: return ""
    last_5 = st.session_state.chat_memory[-5:]
    return "Previous conversation:\n" + "\n".join([f"{m['role']}: {m['content']}" for m in last_5]) + "\n\n"

def fuzzy_find_diagram(topic, subject):
    topic_lower = topic.lower(); subject_diagrams = DIAGRAM_MAP.get(subject, {})
    matches = difflib.get_close_matches(topic_lower, subject_diagrams.keys(), n=1, cutoff=0.35)
    if matches and os.path.exists(subject_diagrams[matches[0]]): return subject_diagrams[matches[0]]
    return None

def text_to_speech(text):
    try: tts = gTTS(text[:500]); fp = "temp_audio.mp3"; tts.save(fp); audio_bytes = open(fp, "rb").read(); os.remove(fp); return audio_bytes
    except: return None

def create_pdf(content, title):
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); p.setFont("Helvetica-Bold", 14); p.drawString(50,800,title); y=770; p.setFont("Helvetica", 10)
    for line in content.split('\n')[:70]: p.drawString(50,y,line[:95]); y-=14;
    if y<50: p.showPage(); y=750
    p.save(); buffer.seek(0); return buffer

def display_with_pdf(content, name):
    st.markdown(content)
    formulas = re.findall(r'\$(.*?)\$', content)
    if formulas: st.markdown("### 🔑 Key Formula"); [st.latex(f) for f in formulas]
    pdf = create_pdf(content, name); st.download_button("📥 Download PDF", pdf, f"{name}.pdf")
    audio = None
    if st.button("🔊 Read Aloud", key=f"tts_{name}"):
        with st.spinner("Generating audio..."): audio = text_to_speech(content)
    if audio: st.audio(audio, format="audio/mp3")

def safe_json_extract(text):
    match = re.search(r'```json(.*?)```', text, re.DOTALL)
    if not match: return None, None
    try: return json.loads(match.group(1).strip()), match.group(0)
    except: return None, match.group(0)

def get_model_for_mode(mode, lab_mode):
    if lab_mode: return AI_MODEL_FAST
    if mode in ["Theory", "Practical", "Bulk", "Mock", "AOI"]: return AI_MODEL_LONG
    return AI_MODEL_FAST

def call_groq_safe(client, messages, model, max_tokens=4000, temperature=0.7):
    for attempt in range(3):
        try: res = client.chat.completions.create(model=model, messages=messages, max_tokens=max_tokens, temperature=temperature); return res.choices[0].message.content
        except RateLimitError:
            if attempt < 2: st.warning(f"AI busy. Retrying in {2**attempt}s..."); time.sleep(2 ** attempt)
            else: st.error("70B overloaded. Falling back to 8B."); res = client.chat.completions.create(model=AI_MODEL_FAST, messages=messages, max_tokens=2000); return res.choices[0].message.content
        except Exception as e: return f"AI Error: {e}"

def get_ai_response(client, user_query, subject, class_level, topic, mode, lab_mode):
    memory = get_memory_context(); model = get_model_for_mode(mode, lab_mode)
    prompt = f"{memory}You are a Senior NCDC {subject} teacher for {class_level} Uganda. Mode: {mode} Topic: {topic} Question: {user_query} Follow NCDC: 1.Definition 2.Explanation with 3 Activities 3.Uganda Example 4.Formula 5.AOI: {AOI_FRAMEWORK[class_level]} Write 600 words."
    answer = call_groq_safe(client, [{"role":"user","content":prompt}], model, max_tokens=4000 if model==AI_MODEL_LONG else 2000)
    add_to_memory("Student", user_query); add_to_memory("Tutor", answer); log_activity(st.session_state.user_type, "AI Query", f"{subject} {class_level} {topic} | Model:{model}")
    return answer

def generate_graph_data(client, subject, topic, level):
    np.random.seed(hash(topic) % 1000); x = np.arange(1, 7)
    if "growth" in topic.lower(): y = x * 2 + np.random.randint(-1, 2, size=6); x_label, y_label = "Time (Weeks)", "Growth"
    elif "temperature" in topic.lower(): y = 25 + x + np.random.randint(-2, 3, size=6); x_label, y_label = "Time (Minutes)", "Temperature (°C)"
    elif "math" in subject.lower(): y = x**2; x_label, y_label = "x", "y = x²"
    else: y = np.random.randint(10, 100, size=6); x_label, y_label = "Sample", "Measurement"
    return {"x_label": x_label, "y_label": y_label, "data": list(zip(x, y))}

def generate_practical(client, subject, level, topic, lab_mode):
    model = get_model_for_mode("Practical", lab_mode)
    prompt = f"Generate FULL detailed NCDC {level} {subject} practical for: {topic}. Must include: AIM, APPARATUS, PROCEDURE, DATA TABLE, OBSERVATIONS, CONCLUSION, SAFETY."
    return call_groq_safe(client, [{"role":"user","content":prompt}], model, max_tokens=3000 if model==AI_MODEL_LONG else 1500, temperature=0.5)

def generate_bulk_revision(client, subject, level, lab_mode):
    model = get_model_for_mode("Bulk", lab_mode)
    return call_groq_safe(client, [{"role":"user","content":f"Generate 20 revision questions for {level} {subject}: {', '.join(UNEB_CURRICULUM_MAP[subject][level])}. Mix MCQ, Theory, Practical with answers."}], model, max_tokens=4000 if model==AI_MODEL_LONG else 2000)

def generate_mock_paper(client, subject, level, paper, lab_mode):
    model = get_model_for_mode("Mock", lab_mode)
    prompts = {"P1":f"40 MCQ for {subject} {level} P1","P2":f"5 Theory for {subject} {level} P2","P3":f"3 Practical for {subject} {level} P3"};
    return call_groq_safe(client, [{"role":"user","content":prompts[paper]}], model, max_tokens=4000 if model==AI_MODEL_LONG else 2000)

def admin_dashboard():
    st.title("👨‍💼 ADMIN DASHBOARD"); logs = load_logs()
    if not logs: st.warning("No activity yet"); return
    df = pd.DataFrame(logs); col1,col2,col3 = st.columns(3)
    col1.metric("Total Activities", len(df)); col2.metric("Today", len(df[df['timestamp'].str.startswith(datetime.now().strftime("%Y-%m-%d"))])); col3.metric("Users", df['user'].nunique())
    st.subheader("Live Activity Feed"); st.dataframe(df.tail(50), use_container_width=True)

def main():
    client = get_client()
    if "chat_memory" not in st.session_state: st.session_state.chat_memory = []
    if "performance" not in st.session_state: st.session_state.performance = {}
    st.markdown("<h1 style='text-align:center; background:gold; color:black; padding:10px'>📚 DIGITAL UNEB TUTOR 2026 - S1 TO S6</h1>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"<div style='background:#2b2b2b; color:white; padding:12px; border-left:4px solid #ffc107; border-radius:5px; margin-bottom:15px'><b>⚠️ DISCLAIMER</b><br>For learning support only.<br>Confirm with Teacher.<br><b>📞 Support:</b> {CONTACT}</div>", unsafe_allow_html=True)
        st.success(f"Logged in as: {st.session_state.user_type}")

        lab_mode = st.toggle("🚀 SCHOOL LAB MODE", value=True, help="ON = Fast 8B for 100 students. OFF = Best Quality 70B")
        if lab_mode: st.info("⚡ Lab Mode ON: Max Speed, Max Students")
        else: st.info("🧠 Quality Mode: Best Answers, Slower")

        if st.session_state.user_type == "Admin": admin_dashboard();
        if st.button("Logout Admin"): st.session_state.clear(); st.rerun(); return
        st.header("📊 Daily Performance Review"); today = datetime.now().strftime("%Y-%m-%d")
        if today in st.session_state.performance: [st.write(f"- {p['subject']}: {p['topic']} | Score: {p['score']}/10") for p in st.session_state.performance[today]]
        else: st.info("No lessons done today yet")
        st.divider()
        if st.button("🗑️ Clear Memory"): st.session_state.chat_memory = []; st.rerun()
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
        level = st.selectbox("Class", ["S1","S2","S3","S4","S5","S6"])
        topic = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject][level])
        mode = st.radio("Mode", ["🔍 Smart Search", "📖 Theory + AOI", "🧠 AOI/Research", "🧪 Practicals Lab", "📈 Graph Generator", "📝 Quiz Mode", "📚 Bulk Revision", "📄 Mock Exams", "🔐 Math Workouts", "🎙️ Voice Ask/Chat"])

    st.subheader("❓ Ask Anything About This Topic"); ask_q = st.text_input("Type your question here", key="universal_ask")
    if st.button("Ask AI", key="ask_btn"): ans = get_ai_response(client, ask_q, subject, level, topic, "Search", lab_mode); display_with_pdf(ans, f"Ask_{topic}")
    st.divider()

    if mode == "🔍 Smart Search":
        search_q = st.text_input("Search any concept");
        if st.button("Search"): result = get_ai_response(client, search_q, subject, level, search_q, "Search", lab_mode); display_with_pdf(result, "SearchResult")
    elif mode == "📖 Theory + AOI":
        st.header(f"{subject} {level}: {topic}"); st.info(f"**AOI Focus**: {AOI_FRAMEWORK[level]}")
        diagram = fuzzy_find_diagram(topic, subject);
        if diagram: st.image(diagram, caption=f"Diagram: {topic}")
        if st.button("Generate Full NCDC Notes", type="primary"): raw = get_ai_response(client, "Explain fully", subject, level, topic, "Theory", lab_mode); display_with_pdf(raw, f"Theory_{topic}"); add_performance(subject, topic, 8)
    elif mode == "🧠 AOI/Research":
        st.header(f"🧠 AOI Research: {subject} {level}"); st.warning(f"**Current AOI Theme**: {AOI_FRAMEWORK[level]}")
        research_q = st.text_area("Describe a real-life problem")
        if st.button("Generate AOI Project"): prompt = f"Design full AOI for {level} {subject} on {topic}. Problem: {research_q}. Include Problem, Tasks, Resources, Assessment."; raw = get_ai_response(client, prompt, subject, level, topic, "AOI", lab_mode); display_with_pdf(raw, f"AOI_{topic}")
    elif mode == "🧪 Practicals Lab":
        st.header(f"Practical: {subject} {level}"); prac = st.selectbox("Select NCDC Practical", PRACTICAL_TOPICS[subject][level])
        if st.button("Generate Full Practical"):
            with st.spinner("Generating detailed practical..."): report = generate_practical(client,subject,level,prac, lab_mode)
            data, json_block = safe_json_extract(report)
            if data: df = pd.DataFrame(data["data"], columns=[data["x_label"], data["y_label"]]); st.dataframe(df); fig = px.scatter(df, x=data["x_label"], y=data["y_label"]); st.plotly_chart(fig)
            display_with_pdf(report.replace(json_block,"") if json_block else report, f"Practical_{prac}"); add_performance(subject, prac, 9)
    elif mode == "📈 Graph Generator":
        st.header("📈 Graph Explainer"); graph_type = st.selectbox("Graph Type", ["Line", "Bar", "Scatter", "Histogram"])
        if st.button("Generate Graph Data", type="primary"):
            data = generate_graph_data(client, subject, topic, level)
            if data:
                df = pd.DataFrame(data["data"], columns=[data["x_label"], data["y_label"]]); st.dataframe(df, use_container_width=True)
                if graph_type == "Line": fig = px.line(df, x=data["x_label"], y=data["y_label"], title=topic)
                elif graph_type == "Bar": fig = px.bar(df, x=data["x_label"], y=data["y_label"], title=topic)
                elif graph_type == "Scatter": fig = px.scatter(df, x=data["x_label"], y=data["y_label"], title=topic)
                else: fig = px.histogram(df, x=data["x_label"], title=topic)
                st.plotly_chart(fig, use_container_width=True)
                explanation = get_ai_response(client, f"Explain this {graph_type} graph for {topic}. Interpret trend. Data:\n{df.to_string()}", subject, level, topic, "Search", lab_mode)
                display_with_pdf(explanation, f"Graph_{topic}")
    elif mode == "📝 Quiz Mode":
        if st.button("Generate 10 MCQ"): quiz = get_ai_response(client, "Generate 10 competency-based MCQ with 1 AOI. Provide answers.", subject, level, topic, "Quiz", lab_mode); display_with_pdf(quiz, f"Quiz_{topic}"); add_performance(subject, topic, 7)
    elif mode == "📚 Bulk Revision":
        st.header(f"📚 Bulk Revision: {subject} {level}")
        if st.button("Generate 20 Revision Questions", type="primary"): bulk = generate_bulk_revision(client, subject, level, lab_mode); display_with_pdf(bulk, f"BulkRevision_{subject}_{level}")
    elif mode == "📄 Mock Exams":
        st.header(f"📄 Mock Exams: {subject} {level}"); col1,col2,col3 = st.columns(3)
        with col1:
            if st.button("Generate P1 MCQ", use_container_width=True): mock = generate_mock_paper(client, subject, level, "P1", lab_mode); display_with_pdf(mock, "MockP1")
        with col2:
            if st.button("Generate P2 Theory", use_container_width=True): mock = generate_mock_paper(client, subject, level, "P2", lab_mode); display_with_pdf(mock, "MockP2")
        with col3:
            if st.button("Generate P3 Practical", use_container_width=True): mock = generate_mock_paper(client, subject, level, "P3", lab_mode); display_with_pdf(mock, "MockP3")
    elif mode == "🔐 Math Workouts":
        st.header("🔐 Mathematics Workouts"); calc_q = st.text_area("Enter calculation")
        if st.button("Work it Out Step by Step"): steps = get_ai_response(client, f"Solve step by step with LaTeX: {calc_q}", subject, level, topic, "Calculation", lab_mode); display_with_pdf(steps, "Workout")
    elif mode == "🎙️ Voice Ask/Chat":
        st.header("🎙️ Voice Mode"); audio = mic_recorder(start_prompt="Record", stop_prompt="Stop", key="rec")
        if audio: st.audio(audio['bytes']); st.info("Transcription would go here. Type question above for now.")

if __name__ == "__main__": main()
