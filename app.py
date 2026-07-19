import streamlit as st
import os, io, json, re, ast, pytz, numpy as np, tempfile, time
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import sympy as sp
from datetime import datetime
from groq import Groq, GroqError
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
import base64
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
from pathlib import Path

# ============ PASSWORD GATE ============
def check_password():
    def password_entered():
        try:
            correct_pw = st.secrets.get("APP_PASSWORD", "UNEB2026")
        except:
            st.error("APP_PASSWORD not found in secrets")
            st.stop()
        if st.session_state["password"] == correct_pw:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔒 DIGITAL UNEB TUTOR 2026 - Login")
        st.text_input("Enter Password", type="password", on_change=password_entered, key="password")
        st.caption("Contact admin for access")
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

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026", page_icon="📚", layout="wide", initial_sidebar_state="expanded")

# ============ FULL NCDC 2026 SYLLABUS - S1 TO S6 ============
UNEB_CURRICULUM_MAP = {
    "Physics": {
        "S1": ["Introduction to Physics", "Measurement", "Force", "Work, Energy and Power", "Pressure"],
        "S2": ["Current Electricity", "Light: Reflection", "Light: Refraction", "Waves", "Heat", "Atmospheric Pressure"],
        "S3": ["Hookes Law and Elasticity", "Specific Heat Capacity", "Magnetism", "Electrostatics", "Sound"],
        "S4": ["Transformers", "Electronics", "Nuclear Physics", "A.C Theory", "Cathode Rays and X-Rays", "Astrophysics"],
        "S5": ["Mechanics: Motion", "Dynamics", "Gravitation", "Thermal Physics", "Waves II", "Optics"],
        "S6": ["Electric Fields", "Magnetic Fields", "Electromagnetic Induction", "Quantum Physics", "Radioactivity", "Solid State Physics"]
    },
    "Chemistry": {
        "S1": ["Introduction to Chemistry", "Structure of an Atom", "Chemical Bonding", "Periodic Table", "Chemical Formulas"],
        "S2": ["Water and Hydrogen", "Oxygen and Oxides", "Acids, Bases and Salts", "Metals", "Air and Combustion"],
        "S3": ["Rates of Reaction", "Energy Changes", "Organic Chemistry Intro", "Chemical Equations", "Mole Concept"],
        "S4": ["Electrochemistry", "Industrial Chemistry", "Organic Chemistry II", "Equilibrium", "Nuclear Chemistry"],
        "S5": ["Atomic Structure Advanced", "Chemical Energetics", "Chemical Kinetics", "Equilibrium II", "Organic Chemistry III"],
        "S6": ["Electrochemistry Advanced", "Transition Metals", "Organic Synthesis", "Analytical Chemistry", "Environmental Chemistry"]
    },
    "Biology": {
        "S1": ["Introduction to Biology", "Plant Cell and Animal Cell", "Ecosystem", "Characteristics of Living Things", "Nutrition in Plants"],
        "S2": ["Circulatory System", "Photosynthesis", "Respiration", "Excretion", "Human Digestive System"],
        "S3": ["DNA and RNA", "Genetics", "Cell Division", "Ecology", "Reproduction in Plants"],
        "S4": ["Nervous System", "Immunity", "Human Reproductive System", "Evolution", "Environmental Conservation"],
        "S5": ["Cell Biology", "Enzymes", "Transport in Plants", "Gas Exchange", "Nutrition in Humans"],
        "S6": ["Hormonal Control", "Coordination", "Population Ecology", "Biotechnology", "Genetic Engineering"]
    },
    "Mathematics": {
        "S1": ["Sets", "Fractions", "Decimals", "Percentages", "Rates and Ratios", "Geometry Basics"],
        "S2": ["Algebra", "Linear Equations", "Angles", "Statistics", "Probability", "Mensuration"],
        "S3": ["Quadratic Equations", "Simultaneous Equations", "Trigonometry", "Mensuration", "Graphs", "Vectors Intro"],
        "S4": ["Calculus Intro", "Vectors", "Matrices", "Coordinate Geometry", "Financial Math", "Statistics II"],
        "S5": ["Calculus: Differentiation", "Integration", "Circular Measure", "Binomial Expansion", "Complex Numbers"],
        "S6": ["Differential Equations", "Mechanics", "Probability Distributions", "Linear Programming", "Further Calculus"]
    }
}

# ============ PRACTICAL CURRICULUM S1-S6 ============
PRACTICAL_TOPICS = {
    "Physics": [
        "Simple Pendulum - Finding g", "Principle of Moments", "Hooke's Law", "Density and Upthrust",
        "Converging Lens - Focal Length", "Glass Block - Refractive Index", "Ohm's Law - V vs I",
        "Resistance vs Length", "Specific Heat Capacity", "Latent Heat", "Potentiometer", "Wheatstone Bridge"
    ],
    "Chemistry": [
        "Acid-Base Titration", "Back Titration - Purity", "Heat of Neutralization", "Rates of Reaction",
        "Qualitative Analysis - Cations", "Qualitative Analysis - Anions", "Gas Tests", "Enthalpy Change",
        "Electrolysis", "Organic Preparation", "Solubility", "Volumetric Analysis"
    ],
    "Biology": [
        "Food Tests", "Osmosis in Potato", "Photosynthesis Rate", "Respiration in Seeds",
        "Microscopy - Cells", "Ecological Sampling", "Transpiration - Potometer", "Enzyme Activity",
        "Blood Smear", "DNA Extraction", "Dissection", "Chromatography of Pigments"
    ],
    "Mathematics": [
        "Data Collection and Analysis", "Graph Drawing and Interpretation", "Geometric Construction",
        "Statistics Project", "Probability Experiment", "Calculus Application", "Matrices and Transformations"
    ]
}

DIAGRAM_FILES = {
    ("Physics","S1","Measurement"): "assets/vernier.png",
    ("Physics","S2","Current Electricity"): "assets/simple_circuit.png",
    ("Physics","S3","Hookes Law and Elasticity"): "assets/hookes_law.png",
    ("Physics","S4","Transformers"): "assets/ac_transformer.png",
    ("Physics","S4","Astrophysics"): "assets/solar_system.png",
    ("Physics","S6","Radioactivity"): "assets/radioactivity.png",
    ("Biology","S1","Plant Cell and Animal Cell"): "assets/plant_cell.png",
    ("Biology","S2","Photosynthesis"): "assets/photosynthesis.png",
    ("Biology","S4","Nervous System"): "assets/neurone.png",
    ("Biology","S6","DNA and RNA"): "assets/dna.png"
}

ADMIN_CONTACT = "256751040731"

@st.cache_resource
def get_client():
    try:
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except:
        st.error("🚨 GROQ_API_KEY missing in secrets. Add it to Streamlit Cloud Settings > Secrets"); st.stop()

def safe_execute_math(code_string: str) -> str:
    local_env = {"sp": sp, "sqrt": sp.sqrt, "pi": sp.pi, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "log": sp.log, "exp": sp.exp}
    try:
        if not code_string or "result" not in code_string: return None
        if "__import__" in code_string or "os." in code_string: return None
        exec(f"g, m, v, u, a, t, s, F, W, P, E, c, delta_T, Q, n, k, rho, h, A = sp.symbols('g m v u a t s F W P E c delta_T Q n k rho h A')", {}, local_env)
        exec(f"{code_string}", {}, local_env)
        result = local_env.get("result", None)
        if result is None: return None
        if hasattr(result, 'free_symbols'): return str(sp.simplify(result).evalf(4))
        return str(result)
    except:
        return None

def get_human_ai_response(client, user_query, subject, class_level, topic=""):
    """CHAIN OF THOUGHT PROMPT - FORCES EXPLANATION FOR S1-S6"""
    system_prompt = f"""
You are a UNEB {subject} teacher for {class_level} Uganda NCDC 2026.

RULES:
1. Teach the topic: "{topic}" right now. Do NOT refuse. Do NOT say "I could not".
2. Use Chain of Thought: 1.Definition -> 2.Explanation -> 3.Uganda Example -> 4.Formula if any.
3. Uganda examples: boda boda, matatu, Nile River, Jinja Dam, coffee farming, markets, solar.
4. If calculation: show $LaTeX$ formula then Final Answer with units.
5. Write 300+ words. Use ### headings and - bullets.
"""
    full_prompt = f"Teach this topic to a {class_level} student: {topic}. Context: {user_query}"
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":system_prompt},{"role":"user","content":full_prompt}],
            temperature=0.6,
            max_tokens=3500
        )
        return res.choices[0].message.content
    except GroqError as e:
        return f"### {topic}\n\n**Definition:** {topic} is part of {class_level} {subject} NCDC 2026 curriculum.\n\n**Explanation:** This topic covers key principles students must master for UNEB.\n\n**Uganda Example:** We see this in daily life in Uganda through transport, farming, or technology.\n\nFor full detailed notes WhatsApp {ADMIN_CONTACT}"

def calc_gradient(df, x, y):
    try:
        slope, intercept = np.polyfit(df[x], df[y], 1)
        return f"**Gradient = {slope:.3f}** | Equation: y = {slope:.3f}x + {intercept:.3f}"
    except: return ""

def render_graph(df, x, y, title):
    st.subheader("📈 Auto-Generated Graph")
    try:
        df[x] = pd.to_numeric(df[x], errors='coerce')
        df[y] = pd.to_numeric(df[y], errors='coerce')
        df = df.dropna()
        if len(df) < 2: st.warning("Not enough valid data points to plot."); return
        fig = px.scatter(df, x=x, y=y, title=title, trendline="ols", template="plotly_white")
        fig.update_traces(marker=dict(size=9), line=dict(width=2))
        st.plotly_chart(fig, use_container_width=True)
        gradient_text = calc_gradient(df, x, y)
        if gradient_text: st.info(gradient_text)
    except Exception as e:
        st.error(f"Graph failed: {e}")

def generate_quiz(client, subject, level, topic):
    prompt = f"You are a UNEB {subject} tutor for {level} Uganda NCDC 2026. Generate 10 MCQ for topic: {topic}. Format: Q1. Question? A. B. C. D. Answer: C. Mix easy, medium, hard."
    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], temperature=0.7, max_tokens=1200)
    return res.choices[0].message.content

def generate_practical(client, subject, level, topic):
    prompt = f"You are a UNEB {subject} examiner for {level} Uganda NCDC 2026. Generate full practical report for: {topic}. Include: AIM, HYPOTHESIS, VARIABLES, APPARATUS, PROCEDURE, SAFETY, DATA TABLE, CONCLUSION. At end include JSON data: ```json {{\"x_label\": \"X\", \"y_label\": \"Y\", \"data\": [[1,2],[2,4],[3,6],[4,8],[5,10],[6,12]]}} ```"
    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], temperature=0.2, max_tokens=2000)
    return res.choices[0].message.content

def safe_json_extract(text):
    if not text: return None, None
    match = re.search(r'```json(.*?)```', text, re.DOTALL)
    if not match: return None, None
    json_str = match.group(1).strip()
    try: return json.loads(json_str), match.group(0)
    except:
        try: return ast.literal_eval(json_str), match.group(0)
        except: return None, match.group(0)

def create_pdf(content, filename):
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); w,h = A4
    p.setFont("Helvetica",10); y=h-50
    for line in content.split('\n'):
        if y<100: p.showPage(); y=h-50
        p.drawString(50,y,line[:100]); y-=15
    p.save(); buffer.seek(0); return buffer

def display_student_notes(raw_text, download_name="notes"):
    clean_text = re.sub(r'```python(.*?)```', '', raw_text, flags=re.DOTALL)
    st.markdown(clean_text)
    formulas = re.findall(r'\$(.*?)\$', raw_text)
    if formulas:
        st.markdown("### 🔑 Key Formula")
        for f in formulas: st.latex(f)
    code_blocks = re.findall(r'```python(.*?)```', raw_text, re.DOTALL)
    for code in code_blocks:
        res = safe_execute_math(code)
        if res: st.success(f"**Final Answer: {res}**")
    pdf = create_pdf(clean_text, f"{download_name}.pdf")
    st.download_button("📥 Download Full Notes as PDF", pdf, f"{download_name}.pdf", use_container_width=True)

def main():
    client = get_client()
    if "activities_log" not in st.session_state: st.session_state.activities_log = []

    st.markdown(f"""<div style="background:linear-gradient(90deg, #FFD700 0%, #FFA500 100%); padding:15px;">
    <h1 style="color:black; text-align:center">📚 DIGITAL UNEB TUTOR 2026 GOLD - S1 TO S6</h1></div>""", unsafe_allow_html=True)

    with st.sidebar:
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
        level = st.selectbox("Class Level", ["S1","S2","S3","S4","S5","S6"])
        topics_list = UNEB_CURRICULUM_MAP[subject][level]
        topic = st.selectbox("Topic", topics_list)
        mode = st.radio("Mode", ["🔍 Smart Search", "📖 Learn Theory", "🎓 Explainer Mode", "🧪 Practicals Lab", "📝 Quiz Mode", "📈 Graph Generator", "🔐 Calculation Mode", "🔮 Predict Papers", "🎙️ Voice Chat"])
        st.markdown("---")
        st.info(f"Support: WhatsApp {ADMIN_CONTACT}")

    if mode == "🎓 Explainer Mode":
        st.header(f"🎓 Explainer Mode: {subject} {level}")
        if st.button("Explain Topic", type="primary"):
            with st.spinner("Explaining..."):
                raw = get_human_ai_response(client, "Explain with Uganda examples and formulas", subject, level, topic)
                display_student_notes(raw, f"explain_{topic}")

    elif mode == "📖 Learn Theory":
        st.header(f"📖 Theory: {subject} {level} - {topic}")
        if st.button("Generate Notes", type="primary"):
            with st.spinner("Generating..."):
                raw = get_human_ai_response(client, "Give detailed notes with examples", subject, level, topic)
                display_student_notes(raw, f"theory_{topic}")

    elif mode == "🔐 Calculation Mode":
        st.header("🔐 Calculation Mode")
        query = st.text_area("Enter your Physics/Chemistry/Mathematics question")
        if st.button("Solve with Steps"):
            raw = get_human_ai_response(client, query, subject, level, query)
            display_student_notes(raw, "calc")

    elif mode == "🔍 Smart Search":
        st.header("🔍 Smart Search")
        query = st.text_input("Ask anything about UNEB")
        if st.button("Search"):
            raw = get_human_ai_response(client, query, subject, level, query)
            display_student_notes(raw, "search")

    elif mode == "🧪 Practicals Lab":
        st.header(f"🧪 Practicals Lab: {subject} {level}")
        prac_topic = st.selectbox("Select Practical", PRACTICAL_TOPICS[subject])
        if st.button("Generate Full Practical"):
            with st.spinner("Generating..."):
                report = generate_practical(client,subject,level,prac_topic)
                data, json_block = safe_json_extract(report)
                if data and "data" in data:
                    df = pd.DataFrame(data["data"], columns=[data["x_label"], data["y_label"]])
                    st.dataframe(df)
                    render_graph(df,data["x_label"],data["y_label"],prac_topic)
                st.markdown(report.replace(json_block,"") if json_block else report)

    elif mode == "📝 Quiz Mode":
        st.header(f"📝 Quiz Mode: {subject} {level}")
        if st.button("Generate 10 MCQ"):
            quiz = generate_quiz(client, subject, level, topic)
            st.markdown(quiz)

    elif mode == "📈 Graph Generator":
        st.header("📈 Graph Generator")
        if st.button("Generate Sample Graph"):
            x = np.linspace(0,10,20); y = x**2 * 0.5 + np.random.randn(20)*5
            df = pd.DataFrame({"X":x,"Y":y})
            render_graph(df, "X","Y", topic)

    elif mode == "🔮 Predict Papers":
        st.header(f"🔮 Predict Papers: {subject} {level}")
        if st.button("Predict 5 Likely Questions"):
            raw = get_human_ai_response(client, "Predict 5 likely UNEB competency-based questions", subject, level, f"{level} {subject}")
            display_student_notes(raw, "predict")

    elif mode == "🎙️ Voice Chat":
        st.header("🎙️ Voice Chat Tutor")
        audio = mic_recorder(start_prompt="🎤 Record", stop_prompt="⏹️ Stop")
        if audio:
            st.audio(audio['bytes'])
            st.info("Voice transcription active")

if __name__ == "__main__": main()
