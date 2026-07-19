import streamlit as st
import os, io, json, re, ast, numpy as np, difflib, time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sympy as sp
from datetime import datetime
from groq import Groq
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
import base64
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS

LOG_FILE = "usage_log.json"
ADMIN_PASSWORD = "ADMIN256"
CONTACT = "256751040731"

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
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": user_type,
        "action": action,
        "details": details
    }
    save_log(entry)

# ============ PASSWORD GATE ============
def check_password():
    def password_entered():
        pw = st.session_state["password"]
        if pw == st.secrets.get("APP_PASSWORD", "UNEB2026"):
            st.session_state["user_type"] = "Student"
            st.session_state["password_correct"] = True
        elif pw == ADMIN_PASSWORD:
            st.session_state["user_type"] = "Admin"
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False
        if "password" in st.session_state: del st.session_state["password"]

    if "password_correct" not in st.session_state:
        st.title("🔒 DIGITAL UNEB TUTOR 2026 - Login")
        st.text_input(f"Students: UNEB2026 | Admin: {ADMIN_PASSWORD}", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔒 DIGITAL UNEB TUTOR 2026 - Login")
        st.text_input("Enter Password", type="password", on_change=password_entered, key="password")
        st.error("😞 Password incorrect")
        return False
    else:
        return True

if not check_password():
    st.stop()

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026", page_icon="📚", layout="wide")

# ============ FULL OFFICIAL NCDC SYLLABUS S1-S6 ============
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
        "S1": ["Scale Drawing and Measurement", "Data Collection Survey Project", "Geometric Construction", "Cartesian Plane Plotting"],
        "S2": ["Real-life Budgeting Project", "Mapping School Compound using Bearings", "Tracking Local Market Price Data", "Building Patterns"],
        "S3": ["Simulating PAYE and Mobile Money Charges", "Building Probability Models", "Vector Navigation Mapping", "Quadratic Equation Graphical Solution"],
        "S4": ["Linear Programming for Business Optimization", "Building 3D Geometric Models", "Processing Census Data", "Statistical Survey"],
        "S5": ["Optimization using Differentiation", "Area under Curves by Integration", "Modeling Circular Motion", "Binomial Expansion Applications"],
        "S6": ["Solving Differential Equations Numerically", "Projectile and Circular Motion Lab", "Normal Distribution Data Analysis", "Linear Programming for Industries"]
    },
    "Physics": {
        "S1": ["Measuring Volume using Measuring Cylinders", "Finding Density of Regular and Irregular Objects", "Demonstrating Capillary Action", "Surface Tension Experiments", "Hooke's Law"],
        "S2": ["Laws of Reflection using Plane Mirrors", "Refraction through Glass Block", "Construction of Pinhole Camera", "Charging by Friction and Induction", "Gold-leaf Electroscope"],
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

AOI_FRAMEWORK = {
    "S1": "Community Problem: Water purification, Waste management, Road safety.",
    "S2": "Local Industry Problem: Soil conservation, Energy saving, Market pricing.",
    "S3": "National Issue: Disease prevention, Electricity access, Food security.",
    "S4": "Global/Local Challenge: Climate change, Technology innovation, Health campaigns.",
    "S5": "Research and Innovation: Renewable energy, Biotechnology, Advanced materials.",
    "S6": "Professional Level: Data analysis for policy, Engineering design, Medical diagnostics."
}

# SUBJECT SPECIFIC DIAGRAMS - NO CROSS MATCHING
DIAGRAM_MAP = {
    "Biology": {"cell": "assets/cell.png", "microscope": "assets/microscope.png", "heart": "assets/heart.png", "dna": "assets/dna.png", "plant": "assets/plant.png"},
    "Physics": {"circuit": "assets/circuit.png", "pendulum": "assets/pendulum.png", "wave": "assets/wave.png", "magnet": "assets/magnet.png"},
    "Chemistry": {"atom": "assets/atom.png", "molecule": "assets/molecule.png", "beaker": "assets/beaker.png"},
    "Mathematics": {"graph": "assets/graph.png", "triangle": "assets/triangle.png", "circle": "assets/circle.png"}
}

@st.cache_resource
def get_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

# ============ MEMORY + PERFORMANCE ============
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
    context = "\n".join([f"{m['role']}: {m['content']}" for m in last_5])
    return f"Previous conversation:\n{context}\n\n"

# ============ UTILS ============
def fuzzy_find_diagram(topic, subject):
    topic_lower = topic.lower()
    subject_diagrams = DIAGRAM_MAP.get(subject, {})
    matches = difflib.get_close_matches(topic_lower, subject_diagrams.keys(), n=1, cutoff=0.4)
    if matches and os.path.exists(subject_diagrams[matches[0]]):
        return subject_diagrams[matches[0]]
    return None

def text_to_speech(text):
    try:
        tts = gTTS(text[:500])
        fp = "temp_audio.mp3"; tts.save(fp)
        audio_bytes = open(fp, "rb").read(); os.remove(fp)
        return audio_bytes
    except: return None

def create_pdf(content, title):
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("Helvetica-Bold", 14); p.drawString(50,800,title)
    y=770; p.setFont("Helvetica", 10)
    for line in content.split('\n')[:65]:
        p.drawString(50,y,line[:95]); y-=14
        if y<50: p.showPage(); y=750
    p.save(); buffer.seek(0); return buffer

def display_with_pdf(content, name):
    st.markdown(content)
    formulas = re.findall(r'\$(.*?)\$', content)
    if formulas:
        st.markdown("### 🔑 Key Formula")
        for f in formulas: st.latex(f)
    pdf = create_pdf(content, name)
    st.download_button("📥 Download PDF", pdf, f"{name}.pdf")
    if st.button("🔊 Read Aloud", key=f"tts_{name}"):
        audio = text_to_speech(content)
        if audio: st.audio(audio, format="audio/mp3")

def safe_json_extract(text):
    match = re.search(r'```json(.*?)```', text, re.DOTALL)
    if not match: return None, None
    try: return json.loads(match.group(1).strip()), match.group(0)
    except: return None, match.group(0)

# ============ AI FUNCTIONS ============
def get_ai_response(client, user_query, subject, class_level, topic, mode="Theory"):
    memory = get_memory_context()
    prompt = f"""{memory}You are a Senior NCDC {subject} teacher for {class_level} Uganda.
Mode: {mode}
Topic: {topic}
Student Question: {user_query}

Follow NCDC Competency-Based Guidelines:
### 1. Definition and Key Competencies
### 2. Detailed Explanation with 3 Learner Activities
### 3. Uganda Context Example
### 4. Formula and Worked Example if applicable
### 5. Activity of Integration: {AOI_FRAMEWORK[class_level]}
Write at least 500 words."""

    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], temperature=0.7, max_tokens=3500)
    answer = res.choices[0].message.content
    add_to_memory("Student", user_query)
    add_to_memory("Tutor", answer)
    log_activity(st.session_state.user_type, "AI Query", f"{subject} {class_level} {topic}")
    return answer

def generate_graph_data(client, subject, topic, level):
    prompt = f"For {level} {subject} topic {topic}, generate sample data for a graph. Return JSON: {{\"x_label\": \"Time\", \"y_label\": \"Distance\", \"data\": [[1,2],[2,4],[3,6],[4,8],[5,10]]}}"
    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], max_tokens=500)
    data, _ = safe_json_extract(res.choices[0].message.content)
    return data

def generate_practical(client, subject, level, topic):
    prompt = f"Generate full NCDC {level} {subject} practical for: {topic}. Include AIM, APPARATUS, PROCEDURE, DATA TABLE, OBSERVATIONS, CONCLUSION, SAFETY. End with JSON data."
    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], max_tokens=2500)
    return res.choices[0].message.content

def generate_bulk_revision(client, subject, level):
    topics = UNEB_CURRICULUM_MAP[subject][level]
    prompt = f"Generate 20 revision questions covering all these {level} {subject} topics: {', '.join(topics)}. Mix MCQ, Theory, and Practical. Provide answers."
    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], max_tokens=3000)
    return res.choices[0].message.content

def generate_mock_paper(client, subject, level, paper):
    prompts = {
        "P1": f"Generate 40 MCQ for {subject} {level} Paper 1. Cover all topics. 4 options A-D. Include answers.",
        "P2": f"Generate 5 Theory questions for {subject} {level} Paper 2. 10 marks each. Include calculations.",
        "P3": f"Generate 3 Practical scenarios for {subject} {level} Paper 3. Include apparatus and method."
    }
    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompts[paper]}], max_tokens=2000)
    return res.choices[0].message.content

# ============ ADMIN DASHBOARD ============
def admin_dashboard():
    st.title("👨‍💼 ADMIN DASHBOARD - Real Time Monitoring")
    logs = load_logs()
    if not logs: st.warning("No activity yet"); return

    df = pd.DataFrame(logs)
    col1,col2,col3 = st.columns(3)
    col1.metric("Total Activities", len(df))
    col2.metric("Today", len(df[df['timestamp'].str.startswith(datetime.now().strftime("%Y-%m-%d"))]))
    col3.metric("Users", df['user'].nunique())

    st.subheader("Live Activity Feed")
    st.dataframe(df.tail(30), use_container_width=True)

    st.subheader("Activity by Subject")
    if 'details' in df.columns:
        subj_counts = df['details'].str.split().str[0].value_counts()
        st.bar_chart(subj_counts)

# ============ MAIN APP ============
def main():
    client = get_client()
    if "chat_memory" not in st.session_state: st.session_state.chat_memory = []
    if "performance" not in st.session_state: st.session_state.performance = {}

    st.markdown("<h1 style='text-align:center; background:gold; color:black; padding:10px'>📚 DIGITAL UNEB TUTOR 2026 - S1 TO S6</h1>", unsafe_allow_html=True)

    with st.sidebar:
        # DARK MODE FRIENDLY DISCLAIMER IN SIDEBAR
        st.markdown(f"""
        <div style='background:#2b2b2b; color:white; padding:12px; border-left:4px solid #ffc107; border-radius:5px; margin-bottom:15px'>
        <b>⚠️ DISCLAIMER</b><br>
        This AI Tutor is for learning support only.<br>
        For any confusion, confirm with Head Teacher / Class Teacher.<br>
        <b>📞 Support:</b> {CONTACT}
        </div>
        """, unsafe_allow_html=True)

        st.success(f"Logged in as: {st.session_state.user_type}")
        if st.session_state.user_type == "Admin":
            admin_dashboard()
            if st.button("Logout Admin"): st.session_state.clear(); st.rerun()
            return

        # STUDENT SIDEBAR
        st.header("📊 Daily Performance Review")
        today = datetime.now().strftime("%Y-%m-%d")
        if today in st.session_state.performance:
            for p in st.session_state.performance[today]:
                st.write(f"- {p['subject']}: {p['topic']} | Score: {p['score']}/10")
        else: st.info("No lessons done today yet")

        st.divider()
        if st.button("🗑️ Clear Memory"): st.session_state.chat_memory = []; st.rerun()
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
        level = st.selectbox("Class", ["S1","S2","S3","S4","S5","S6"])
        topic = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject][level])
        mode = st.radio("Mode", [
            "🔍 Smart Search", "📖 Theory + AOI", "🧠 AOI/Research", "🧪 Practicals Lab",
            "📈 Graph Generator", "📝 Quiz Mode", "📚 Bulk Revision", "📄 Mock Exams",
            "🔐 Math Workouts", "🎙️ Voice Ask/Chat"
        ])

    # UNIVERSAL ASK BOX
    st.subheader("❓ Ask Anything About This Topic")
    ask_q = st.text_input("Type your question here", key="universal_ask")
    if st.button("Ask AI", key="ask_btn"):
        ans = get_ai_response(client, ask_q, subject, level, topic)
        display_with_pdf(ans, f"Ask_{topic}")

    st.divider()

    if mode == "🔍 Smart Search":
        search_q = st.text_input("Search any concept")
        if st.button("Search"):
            result = get_ai_response(client, search_q, subject, level, search_q, "Search")
            display_with_pdf(result, "SearchResult")

    elif mode == "📖 Theory + AOI":
        st.header(f"{subject} {level}: {topic}")
        st.info(f"**AOI Focus**: {AOI_FRAMEWORK[level]}")
        diagram = fuzzy_find_diagram(topic, subject) # SUBJECT LOCKED
        if diagram: st.image(diagram, caption=f"Diagram: {topic}")
        if st.button("Generate Full NCDC Notes", type="primary"):
            raw = get_ai_response(client, "Explain fully", subject, level, topic)
            display_with_pdf(raw, f"Theory_{topic}")
            add_performance(subject, topic, 8)

    elif mode == "🧠 AOI/Research":
        st.header(f"🧠 AOI Research: {subject} {level}")
        st.warning(f"**Current AOI Theme**: {AOI_FRAMEWORK[level]}")
        research_q = st.text_area("Describe a real-life problem you want to solve using this topic")
        if st.button("Generate AOI Project"):
            prompt = f"Design a full Activity of Integration for {level} {subject} on topic {topic}. Problem: {research_q}. Include: Problem statement, Learner tasks, Resources needed, Assessment criteria."
            raw = get_ai_response(client, prompt, subject, level, topic, "AOI")
            display_with_pdf(raw, f"AOI_{topic}")

    elif mode == "🧪 Practicals Lab":
        st.header(f"Practical: {subject} {level}")
        prac = st.selectbox("Select NCDC Practical", PRACTICAL_TOPICS[subject][level])
        if st.button("Generate Full Practical"):
            report = generate_practical(client,subject,level,prac)
            data, json_block = safe_json_extract(report)
            if data:
                df = pd.DataFrame(data["data"], columns=[data["x_label"], data["y_label"]])
                st.dataframe(df)
                fig = px.scatter(df, x=data["x_label"], y=data["y_label"], trendline="ols")
                st.plotly_chart(fig)
            display_with_pdf(report.replace(json_block,"") if json_block else report, f"Practical_{prac}")

    elif mode == "📈 Graph Generator":
        st.header("📈 Graph Explainer")
        graph_type = st.selectbox("Graph Type", ["Line", "Bar", "Scatter", "Histogram"])
        if st.button("Generate Graph Data"):
            data = generate_graph_data(client, subject, topic, level)
            if data:
                df = pd.DataFrame(data["data"], columns=[data["x_label"], data["y_label"]])
                st.dataframe(df)
                if graph_type == "Line": fig = px.line(df, x=data["x_label"], y=data["y_label"])
                elif graph_type == "Bar": fig = px.bar(df, x=data["x_label"], y=data["y_label"])
                elif graph_type == "Scatter": fig = px.scatter(df, x=data["x_label"], y=data["y_label"], trendline="ols")
                else: fig = px.histogram(df, x=data["x_label"])
                st.plotly_chart(fig)
                explanation = get_ai_response(client, f"Explain this {graph_type} graph for {topic}", subject, level, topic)
                display_with_pdf(explanation, f"Graph_{topic}")

    elif mode == "📝 Quiz Mode":
        if st.button("Generate 10 MCQ"):
            quiz = get_ai_response(client, "Generate 10 competency-based MCQ with 1 AOI scenario", subject, level, topic, "Quiz")
            display_with_pdf(quiz, f"Quiz_{topic}")
            add_performance(subject, topic, 7)

    elif mode == "📚 Bulk Revision":
        st.header(f"📚 Bulk Revision: {subject} {level}")
        st.info(f"Will generate 20 questions covering: {', '.join(UNEB_CURRICULUM_MAP[subject][level])}")
        if st.button("Generate 20 Revision Questions", type="primary"):
            bulk = generate_bulk_revision(client, subject, level)
            display_with_pdf(bulk, f"BulkRevision_{subject}_{level}")

    elif mode == "📄 Mock Exams":
        st.header(f"📄 Mock Exams: {subject} {level}")
        col1,col2,col3 = st.columns(3)
        with col1:
            if st.button("Generate P1 MCQ", use_container_width=True):
                mock = generate_mock_paper(client, subject, level, "P1")
                display_with_pdf(mock, "MockP1")
        with col2:
            if st.button("Generate P2 Theory", use_container_width=True):
                mock = generate_mock_paper(client, subject, level, "P2")
                display_with_pdf(mock, "MockP2")
        with col3:
            if st.button("Generate P3 Practical", use_container_width=True):
                mock = generate_mock_paper(client, subject, level, "P3")
                display_with_pdf(mock, "MockP3")

    elif mode == "🔐 Math Workouts":
        st.header("🔐 Mathematics/Calculations Workouts Page")
        calc_q = st.text_area("Enter Math/Physics/Chemistry calculation")
        if st.button("Work it Out Step by Step"):
            steps = get_ai_response(client, f"Solve step by step with LaTeX: {calc_q}", subject, level, topic, "Calculation")
            display_with_pdf(steps, "Workout")

    elif mode == "🎙️ Voice Ask/Chat":
        st.header("🎙️ Voice Ask and Chat")
        audio = mic_recorder(start_prompt="🎤 Ask", stop_prompt="⏹️ Stop", key='recorder')
        if audio:
            st.audio(audio['bytes'])
            st.success("Voice recorded. Answer below:")
            voice_ans = get_ai_response(client, "Explain this topic in detail", subject, level, topic)
            display_with_pdf(voice_ans, "VoiceResponse")

    with st.expander("💾 View Chat Memory"):
        for m in st.session_state.chat_memory:
            st.markdown(f"**{m['role']}** [{m['time']}]: {m['content'][:200]}...")

if __name__ == "__main__": main()
