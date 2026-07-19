import streamlit as st
import os, io, json, re, ast, numpy as np, difflib
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

# ============ PASSWORD GATE ============
def check_password():
    def password_entered():
        correct_pw = st.secrets.get("APP_PASSWORD", "UNEB2026")
        if st.session_state["password"] == correct_pw:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔒 DIGITAL UNEB TUTOR 2026 - Login")
        st.text_input("Enter Password", type="password", on_change=password_entered, key="password")
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
# ============ END PASSWORD GATE ============

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026", page_icon="📚", layout="wide")

# ============ DISCLAIMER ============
st.markdown("""
<div style='background:#fff3cd; padding:10px; border-left:5px solid #ffc107; margin-bottom:10px'>
<b>⚠️ DISCLAIMER:</b> This AI Tutor is for learning support only.
For any confusion, exam guidance, or official clarification, students MUST confirm with their Head Teacher / Class Teacher / Subject Teacher.
</div>
""", unsafe_allow_html=True)

# ============ FULL NCDC S1-S6 ============
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
        "S5": ["Mechanics: Motion and Dynamics", "Gravitation", "Thermal Physics Advanced", "Waves III", "Optics", "Fluid Mechanics"],
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
        "S1": ["Scale Drawing", "Data Collection Survey", "Geometric Construction", "Cartesian Plotting"],
        "S2": ["Budgeting Project", "Mapping with Bearings", "Market Data Tracking", "Patterns"],
        "S3": ["PAYE Simulation", "Probability Models", "Vector Navigation", "Quadratic Graphs"],
        "S4": ["Linear Programming", "3D Models", "Census Data", "Statistical Survey"],
        "S5": ["Optimization", "Area by Integration", "Circular Motion", "Binomial Applications"],
        "S6": ["Differential Equations", "Projectile Motion", "Normal Distribution", "Advanced LP"]
    },
    "Physics": {
        "S1": ["Measuring Volume", "Finding Density", "Capillary Action", "Surface Tension", "Hooke's Law"],
        "S2": ["Laws of Reflection", "Refraction Glass Block", "Pinhole Camera", "Static Electricity", "Thermometer Calibration"],
        "S3": ["Series and Parallel Circuits", "Ohm's Law", "Magnetic Fields", "Speed of Sound", "Simple Pendulum", "Specific Heat"],
        "S4": ["Electromagnetic Induction", "Transformers", "Logic Gates", "Cathode Rays", "Rectification", "Radioactivity"],
        "S5": ["Projectile Motion", "Gravitation", "Thermal Conductivity", "Wave Interference", "Lens Experiments"],
        "S6": ["Electric Field Mapping", "Magnetic Force", "Faraday's Law", "Photoelectric Effect", "Half-life", "Diodes"]
    },
    "Chemistry": {
        "S1": ["Purity Tests", "Filtration", "Distillation", "Chromatography", "Heating CuSO4", "Air Components"],
        "S2": ["Litmus and pH", "pH Scale", "Soluble Salts", "Insoluble Salts", "Carbonates", "Reactivity Series"],
        "S3": ["Conductivity", "Titrations", "Molarity", "Rates of Reaction", "Hard Water", "Metal Extraction"],
        "S4": ["Cation Tests", "Anion Tests", "Gas Tests", "Saponification", "Fermentation", "Heat of Reaction"],
        "S5": ["Enthalpy Change", "Rate of Reaction", "Equilibrium", "Esterification", "Buffers", "Electrolysis"],
        "S6": ["Redox Titrations", "Complex Ions", "Organic Synthesis", "Gravimetric Analysis", "Water Quality", "Polymerization"]
    },
    "Biology": {
        "S1": ["Using Microscope", "Cell Slides", "Drawing Specimens", "Dichotomous Keys", "Flower Dissection"],
        "S2": ["Soil Water Retention", "Soil Capillarity", "Soil Organic Matter", "Food Tests", "Photosynthesis Factors", "Vitamin C Test"],
        "S3": ["Osmosis", "Transpiration", "Respiratory Structures", "Pulse Rate", "Urine Tests", "Mitosis"],
        "S4": ["Reflex Tests", "Tropism", "Growth Curves", "Quadrats", "DNA Extraction", "Blood Grouping"],
        "S5": ["Enzyme Activity", "Xylem/Phloem", "Gas Exchange", "Digestive System", "Cellular Respiration"],
        "S6": ["Hormone Effects", "Reflex Arc", "Population Sampling", "Bacterial Culture", "DNA Model", "Antibody Reaction"]
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

DIAGRAM_MAP = {
    "cell": "assets/cell.png", "microscope": "assets/microscope.png", "heart": "assets/heart.png",
    "circuit": "assets/circuit.png", "atom": "assets/atom.png", "dna": "assets/dna.png",
    "graph": "assets/graph.png", "plant": "assets/plant.png", "pendulum": "assets/pendulum.png"
}

@st.cache_resource
def get_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

# ============ MEMORY SYSTEM ============
def add_to_memory(role, content):
    if "chat_memory" not in st.session_state: st.session_state.chat_memory = []
    st.session_state.chat_memory.append({"role": role, "content": content, "time": datetime.now().strftime("%H:%M")})

def get_memory_context():
    if "chat_memory" not in st.session_state: return ""
    last_5 = st.session_state.chat_memory[-5:]
    context = "\n".join([f"{m['role']}: {m['content']}" for m in last_5])
    return f"Previous conversation:\n{context}\n\n"

# ============ UTILS ============
def fuzzy_find_diagram(topic):
    topic_lower = topic.lower()
    matches = difflib.get_close_matches(topic_lower, DIAGRAM_MAP.keys(), n=1, cutoff=0.4)
    if matches: return DIAGRAM_MAP[matches[0]]
    return None

def text_to_speech(text):
    tts = gTTS(text[:500])
    fp = "temp_audio.mp3"; tts.save(fp)
    audio_bytes = open(fp, "rb").read(); os.remove(fp)
    return audio_bytes

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
    pdf = create_pdf(content, name)
    st.download_button("📥 Download PDF", pdf, f"{name}.pdf")
    if st.button("🔊 Read Aloud", key=f"tts_{name}"):
        audio = text_to_speech(content)
        st.audio(audio, format="audio/mp3")

# ============ AI FUNCTIONS ============
def get_ai_response(client, user_query, subject, class_level, topic, mode="Theory"):
    memory = get_memory_context()
    prompt = f"""{memory}You are a Senior NCDC CBC {subject} teacher for {class_level} Uganda.
Mode: {mode}
Topic: {topic}
Student Question: {user_query}

Follow NCDC Guidelines:
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
    return answer

def generate_graph_data(client, subject, topic, level):
    prompt = f"For {level} {subject} topic {topic}, generate sample data for a graph. Return JSON: {{\"x_label\": \"Time\", \"y_label\": \"Distance\", \"data\": [[1,2],[2,4],[3,6]]}}"
    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], max_tokens=500)
    match = re.search(r'```json(.*?)```', res.choices[0].message.content, re.DOTALL)
    if match: return json.loads(match.group(1).strip())
    return None

def math_workout(client, query):
    prompt = f"Solve this {query} step by step. Show formula, substitution, working, final answer. Use LaTeX for math."
    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], max_tokens=1500)
    return res.choices[0].message.content

# ============ MAIN APP ============
def main():
    client = get_client()
    if "chat_memory" not in st.session_state: st.session_state.chat_memory = []

    st.markdown("<h1 style='text-align:center; background:gold; color:black; padding:10px'>📚 DIGITAL UNEB TUTOR 2026 - NCDC CBC S1 TO S6</h1>", unsafe_allow_html=True)

    with st.sidebar:
        st.success(f"Chat Memory: {len(st.session_state.chat_memory)} messages")
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
        diagram = fuzzy_find_diagram(topic)
        if diagram: st.image(diagram, caption=f"Diagram: {topic}")
        if st.button("Generate Full NCDC Notes", type="primary"):
            raw = get_ai_response(client, "Explain fully", subject, level, topic)
            display_with_pdf(raw, f"Theory_{topic}")

    elif mode == "🧠 AOI/Research":
        research_q = st.text_area("Describe a real-life problem to solve")
        if st.button("Generate AOI Project"):
            prompt = f"Design full Activity of Integration for {level} {subject} on {topic}. Problem: {research_q}"
            raw = get_ai_response(client, prompt, subject, level, topic, "AOI")
            display_with_pdf(raw, f"AOI_{topic}")

    elif mode == "🧪 Practicals Lab":
        prac = st.selectbox("Select Practical", PRACTICAL_TOPICS[subject][level])
        if st.button("Generate Practical"):
            report = get_ai_response(client, "Generate full practical", subject, level, prac, "Practical")
            display_with_pdf(report, f"Practical_{prac}")

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
            quiz = get_ai_response(client, "Generate 10 MCQ", subject, level, topic, "Quiz")
            display_with_pdf(quiz, f"Quiz_{topic}")

    elif mode == "📚 Bulk Revision":
        if st.button("Generate 20 Revision Questions", type="primary"):
            topics = ", ".join(UNEB_CURRICULUM_MAP[subject][level])
            bulk = get_ai_response(client, f"Generate 20 revision Qs for: {topics}", subject, level, "All Topics", "Revision")
            display_with_pdf(bulk, f"Bulk_{subject}_{level}")

    elif mode == "📄 Mock Exams":
        col1,col2,col3 = st.columns(3)
        with col1:
            if st.button("Generate P1 MCQ"): mock = get_ai_response(client, "40 MCQ P1", subject, level, "All", "Mock")
            display_with_pdf(mock, "MockP1")
        with col2:
            if st.button("Generate P2 Theory"): mock = get_ai_response(client, "5 Theory P2", subject, level, "All", "Mock")
            display_with_pdf(mock, "MockP2")
        with col3:
            if st.button("Generate P3 Practical"): mock = get_ai_response(client, "3 Practical P3", subject, level, "All", "Mock")
            display_with_pdf(mock, "MockP3")

    elif mode == "🔐 Math Workouts":
        st.header("🔐 Mathematics Calculations Page")
        calc_q = st.text_area("Enter Math/Physics/Chemistry calculation")
        if st.button("Work it Out Step by Step"):
            steps = math_workout(client, calc_q)
            display_with_pdf(steps, "Workout")

    elif mode == "🎙️ Voice Ask/Chat":
        st.header("🎙️ Voice Ask and Chat")
        audio = mic_recorder(start_prompt="🎤 Ask", stop_prompt="⏹️ Stop", key='recorder')
        if audio:
            st.audio(audio['bytes'])
            st.success("Voice recorded. AI will answer in text below and you can click Read Aloud")
            voice_ans = get_ai_response(client, "Explain this topic", subject, level, topic)
            display_with_pdf(voice_ans, "VoiceResponse")

    with st.expander("💾 View Chat Memory"):
        for m in st.session_state.chat_memory:
            st.markdown(f"**{m['role']}** [{m['time']}]: {m['content'][:200]}...")

if __name__ == "__main__": main()
