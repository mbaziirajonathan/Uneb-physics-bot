import streamlit as st
import os, io, json, re, ast, pytz, numpy as np, tempfile
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import sympy as sp
from datetime import datetime
from groq import Groq
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

# ============ FULL NCDC 2026 SYLLABUS - S1 TO S6 ============
UNEB_CURRICULUM_MAP = {
    "Physics": {
        "S1": ["Introduction to Physics", "Measurement", "Force", "Work, Energy and Power", "Pressure"],
        "S2": ["Current Electricity", "Light: Reflection", "Light: Refraction", "Waves", "Heat"],
        "S3": ["Hookes Law and Elasticity", "Specific Heat Capacity", "Magnetism", "Electrostatics", "Sound"],
        "S4": ["Transformers", "Electronics", "Nuclear Physics", "A.C Theory", "Cathode Rays", "Astrophysics"],
        "S5": ["Mechanics", "Dynamics", "Gravitation", "Thermal Physics", "Waves", "Optics"],
        "S6": ["Electric Fields", "Magnetic Fields", "EM Induction", "Quantum Physics", "Radioactivity"]
    },
    "Chemistry": {
        "S1": ["Structure of an Atom", "Chemical Bonding", "Periodic Table", "Chemical Formulas"],
        "S2": ["Water and Hydrogen", "Acids, Bases and Salts", "Metals", "Air and Combustion"],
        "S3": ["Rates of Reaction", "Energy Changes", "Organic Chemistry", "Mole Concept"],
        "S4": ["Electrochemistry", "Industrial Chemistry", "Organic Chemistry II", "Equilibrium"],
        "S5": ["Chemical Energetics", "Chemical Kinetics", "Equilibrium II", "Organic Chemistry III"],
        "S6": ["Electrochemistry Advanced", "Transition Metals", "Organic Synthesis", "Analytical Chemistry"]
    },
    "Biology": {
        "S1": ["Plant Cell and Animal Cell", "Ecosystem", "Nutrition in Plants"],
        "S2": ["Circulatory System", "Photosynthesis", "Respiration", "Excretion"],
        "S3": ["DNA and RNA", "Genetics", "Cell Division", "Ecology"],
        "S4": ["Nervous System", "Immunity", "Human Reproductive System", "Evolution"],
        "S5": ["Cell Biology", "Enzymes", "Transport in Plants", "Nutrition in Humans"],
        "S6": ["Hormonal Control", "Coordination", "Population Ecology", "Biotechnology"]
    },
    "Mathematics": {
        "S1": ["Sets", "Fractions", "Percentages", "Rates and Ratios"],
        "S2": ["Algebra", "Linear Equations", "Statistics", "Probability"],
        "S3": ["Quadratic Equations", "Simultaneous Equations", "Trigonometry", "Graphs"],
        "S4": ["Calculus Intro", "Vectors", "Matrices", "Coordinate Geometry"],
        "S5": ["Differentiation", "Integration", "Circular Measure", "Complex Numbers"],
        "S6": ["Differential Equations", "Mechanics", "Probability Distributions", "Linear Programming"]
    }
}

PRACTICAL_TOPICS = {
    "Physics": ["Simple Pendulum", "Hooke's Law", "Ohm's Law", "Lens Focal Length", "Specific Heat Capacity"],
    "Chemistry": ["Acid-Base Titration", "Rates of Reaction", "Qualitative Analysis", "Heat of Neutralization"],
    "Biology": ["Food Tests", "Osmosis", "Photosynthesis Rate", "Microscopy", "Enzyme Activity"],
    "Mathematics": ["Data Collection", "Graph Drawing", "Construction", "Statistics Project"]
}

ADMIN_CONTACT = "256751040731"

@st.cache_resource
def get_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

def safe_execute_math(code_string: str) -> str:
    local_env = {"sp": sp, "sqrt": sp.sqrt, "pi": sp.pi, "sin": sp.sin, "cos": sp.cos}
    try:
        if not code_string or "result" not in code_string: return None
        exec(f"g, m, v, u, a, t, s, F, W, P = sp.symbols('g m v u a t s F W P')", {}, local_env)
        exec(f"{code_string}", {}, local_env)
        result = local_env.get("result", None)
        if result is None: return None
        if hasattr(result, 'free_symbols'): return str(sp.simplify(result).evalf(4))
        return str(result)
    except:
        return None

# FINAL FIX: SIMPLE PROMPT. NO "DO NOT REFUSE"
def get_ai_response(client, user_query, subject, class_level, topic):
    prompt = f"""You are a Ugandan teacher teaching {class_level} {subject} under NCDC 2026.
Topic: {topic}
Student Question: {user_query}

Write detailed notes with:
### 1. Definition
### 2. Explanation with 3 key points
### 3. Uganda Example: use boda boda, matatu, Nile River, coffee
### 4. Formula and Example if subject is Physics, Chemistry, or Math
Write at least 400 words. Use simple English for secondary students."""
    
    try:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant", # CHANGED: this model never refuses
            messages=[{"role":"user","content":prompt}],
            temperature=0.7,
            max_tokens=3000
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"### {topic}\n\nError connecting to AI: {e}\n\nPlease try again or WhatsApp {ADMIN_CONTACT}"

def render_graph(df, x, y, title):
    st.subheader("📈 Graph")
    fig = px.scatter(df, x=x, y=y, title=title, trendline="ols")
    st.plotly_chart(fig, use_container_width=True)

def generate_practical(client, subject, level, topic):
    prompt = f"Generate UNEB {level} {subject} practical for {topic}. Include AIM, APPARATUS, PROCEDURE, DATA TABLE, CONCLUSION. End with JSON data: ```json {{\"x_label\": \"Time\", \"y_label\": \"Distance\", \"data\": [[1,2],[2,4],[3,6],[4,8],[5,10]]}} ```"
    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], max_tokens=2000)
    return res.choices[0].message.content

def safe_json_extract(text):
    match = re.search(r'```json(.*?)```', text, re.DOTALL)
    if not match: return None, None
    try: return json.loads(match.group(1).strip()), match.group(0)
    except: return None, match.group(0)

def create_pdf(content, filename):
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4)
    y=750
    for line in content.split('\n')[:50]:
        p.drawString(50,y,line[:100]); y-=15
    p.save(); buffer.seek(0); return buffer

def display_notes(raw_text, name):
    st.markdown(raw_text)
    formulas = re.findall(r'\$(.*?)\$', raw_text)
    if formulas:
        st.markdown("### 🔑 Formula")
        for f in formulas: st.latex(f)
    pdf = create_pdf(raw_text, f"{name}.pdf")
    st.download_button("📥 Download PDF", pdf, f"{name}.pdf")

def main():
    client = get_client()
    st.markdown("<h1 style='text-align:center; background:gold; color:black; padding:10px'>📚 DIGITAL UNEB TUTOR 2026 - S1 TO S6</h1>", unsafe_allow_html=True)

    with st.sidebar:
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
        level = st.selectbox("Class", ["S1","S2","S3","S4","S5","S6"])
        topic = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject][level])
        mode = st.radio("Mode", ["📖 Theory", "🎓 Explainer", "🧪 Practical", "📝 Quiz", "🔐 Calculation"])

    if mode == "🎓 Explainer" or mode == "📖 Theory":
        st.header(f"{mode}: {topic}")
        if st.button("Generate", type="primary"):
            with st.spinner("AI is teaching..."):
                raw = get_ai_response(client, "Explain fully", subject, level, topic)
                display_notes(raw, f"{subject}_{topic}")

    elif mode == "🔐 Calculation":
        query = st.text_area("Enter question")
        if st.button("Solve"):
            raw = get_ai_response(client, query, subject, level, query)
            display_notes(raw, "calc")

    elif mode == "🧪 Practical":
        prac = st.selectbox("Practical", PRACTICAL_TOPICS[subject])
        if st.button("Generate Practical"):
            report = generate_practical(client,subject,level,prac)
            data, json_block = safe_json_extract(report)
            if data:
                df = pd.DataFrame(data["data"], columns=[data["x_label"], data["y_label"]])
                st.dataframe(df)
                render_graph(df,data["x_label"],data["y_label"],prac)
            st.markdown(report.replace(json_block,"") if json_block else report)

    elif mode == "📝 Quiz":
        if st.button("Generate 10 MCQ"):
            prompt = f"Generate 10 MCQ for {level} {subject} topic {topic}. Format: Q1. A. B. C. D. Answer: C"
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}])
            st.markdown(res.choices[0].message.content)

if __name__ == "__main__": main()
