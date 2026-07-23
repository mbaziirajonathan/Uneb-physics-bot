import streamlit as st
import os, io, json, re, ast, numpy as np, difflib, time, math
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sympy as sp
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as patches
from matplotlib.patches import Arc, Polygon, Circle, Rectangle, FancyArrow
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

# ============ 2D + 3D DIAGRAM ENGINE: MATH + PHYSICS ============
def draw_2d_shape(shape_type, params={}):
    fig, ax = plt.subplots(figsize=(5,5))
    ax.set_aspect('equal'); ax.axis('off')

    # MATH
    if shape_type == "triangle":
        pts = [[0,0], [4,0], [2,3]]
        poly = Polygon(pts, closed=True, edgecolor='black', facecolor='lightblue', linewidth=2); ax.add_patch(poly)
        for i, label in enumerate(["A","B","C"]): ax.text(pts[i][0]-0.2, pts[i][1]-0.2, label, fontsize=12, weight='bold')
    elif shape_type == "rectangle":
        w, h = params.get("w",6), params.get("h",4)
        rect = Rectangle((0,0), w, h, edgecolor='black', facecolor='lightgreen', linewidth=2); ax.add_patch(rect)
    elif shape_type == "square":
        s = params.get("s",4); rect = Rectangle((0,0), s, s, edgecolor='black', facecolor='lightyellow', linewidth=2); ax.add_patch(rect)
    elif shape_type == "circle":
        r = params.get("r",2); circ = Circle((2,2), r, edgecolor='black', facecolor='lightcyan', linewidth=2); ax.add_patch(circ)
    elif shape_type == "angle":
        deg = params.get("deg",60); ax.plot([0,4],[0,0],'k-'); ax.plot([0,4*math.cos(math.radians(deg))],[0,4*math.sin(math.radians(deg))],'k-')
        arc = Arc((0,0), 2, 2, theta1=0, theta2=deg, color='red', linewidth=2); ax.add_patch(arc); ax.text(1.2,0.3,f"{deg}°", color='red')
    elif shape_type == "bisector":
        ax.plot([0,6],[0,0],'k-', lw=2); ax.plot([3,-1],[0,4],'k-', lw=2); ax.plot([3,1.5],[0,2],'r--', lw=2)
    elif shape_type == "bearing":
        ax.plot([2,2],[0,4],'k--'); ax.text(2.1,3.5,"N"); ax.plot([2,4],[2,2],'r-', lw=3)
        arc = Arc((2,2), 2, 2, theta1=90, theta2=30, color='red'); ax.add_patch(arc)
    elif shape_type == "polygon":
        sides = params.get("sides",5); pts = [(2+2*math.cos(2*math.pi*i/sides), 2+2*math.sin(2*math.pi*i/sides)) for i in range(sides)]
        poly = Polygon(pts, closed=True, edgecolor='black', facecolor='lavender', linewidth=2); ax.add_patch(poly)
    elif shape_type == "trig_triangle":
        ax.plot([0,3],[0,0],'k-'); ax.plot([3,3],[0,4],'k-'); ax.plot([0,3],[0,4],'k-'); ax.text(1.5,-0.3,"Adj"); ax.text(3.2,2,"Opp")

    # PHYSICS
    elif shape_type == "circuit":
        ax.plot([0,1],[2,2],'k-', lw=2); ax.plot([1,1],[2,3],'k-'); ax.plot([1,2],[3,3],'k-')
        rect = Rectangle((2,2.8), 0.5, 0.4, edgecolor='black', facecolor='white'); ax.add_patch(rect); ax.text(2.1,3.1,"R")
        ax.plot([2.5,3],[3,3],'k-'); ax.plot([3,3],[3,2],'k-'); ax.plot([3,2],[2,2],'k-'); ax.plot([2,2],[2,1],'k-'); ax.plot([0,2],[1,1],'k-')
    elif shape_type == "mirror":
        ax.plot([2,2],[0,4],'k-', lw=3); ax.plot([0.5,2],[3,2],'r--'); ax.plot([2,3.5],[2,1],'r--')
    elif shape_type == "wave":
        x = np.linspace(0, 4*np.pi, 200); y = np.sin(x); ax.plot(x, y, 'b-', lw=2); ax.axhline(0, color='k', linestyle='--')
    elif shape_type == "magnet":
        rect1 = Rectangle((1,2), 1, 0.5, edgecolor='black', facecolor='red'); ax.add_patch(rect1)
        rect2 = Rectangle((3,2), 1, 0.5, edgecolor='black', facecolor='blue'); ax.add_patch(rect2)
    elif shape_type == "vector":
        ax.arrow(2,2,2,1, head_width=0.2, head_length=0.2, fc='r', ec='r')

    ax.set_xlim(-1,6); ax.set_ylim(-1,6)
    path = f"/mnt/data/{shape_type}_{int(time.time())}.png"
    plt.savefig(path, dpi=150, bbox_inches='tight'); plt.close(); return path

def draw_3d_shape(shape_type, params={}):
    fig = plt.figure(figsize=(5,5)); ax = fig.add_subplot(111, projection='3d')

    if shape_type == "cube":
        s = params.get("s",2)
        vertices = [[0,0,0],[s,0,0],[s,s,0],[0,s,0],[0,0,s],[s,0,s],[s,s,s],[0,s]]
        edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
        for edge in edges: ax.plot3D([vertices[edge[0]][0], vertices[edge[1]][0]], [vertices[edge[0]][1], vertices[edge[1]][1]], [vertices[edge[0]][2], vertices[edge[1]][2]], 'k')
        ax.text(s/2, -0.5, -0.5, f"Cube side={s}cm")

    elif shape_type == "cuboid":
        l,w,h = params.get("l",4), params.get("w",2), params.get("h",3)
        vertices = [[0,0,0],[l,0,0],[l,w,0],[0,w,0],[0,0,h],[l,0,h],[l,w,h],[0,w,h]]
        edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
        for edge in edges: ax.plot3D([vertices[edge[0]][0], vertices[edge[1]][0]], [vertices[edge[0]][1], vertices[edge[1]][1]], [vertices[edge[0]][2], vertices[edge[1]][2]], 'b')

    elif shape_type == "vector3d":
        ax.quiver(0,0,0,3,2,1, color='r', arrow_length_ratio=0.1); ax.text(3.2,2.2,1.2,"Vector (3,2,1)")

    elif shape_type == "pyramid":
        base = [[0,0,0],[2,0,0],[2,2,0],[0,2,0]]; apex = [1,1,2]
        for i in range(4): ax.plot3D([base[i][0], base[(i+1)%4][0]], [base[i][1], base[(i+1)%4][1]], [base[i][2], base[(i+1)%4][2]], 'g')
        for b in base: ax.plot3D([b[0], apex[0]], [b[1], apex[1]], [b[2], apex[2]], 'g')

    ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
    path = f"/mnt/data/{shape_type}3d_{int(time.time())}.png"
    plt.savefig(path, dpi=150, bbox_inches='tight'); plt.close(); return path

def detect_and_draw_diagram(text, subject, level):
    text = text.lower()
    # 3D FIRST
    if level in ["S4","S5","S6"]:
        if "3d" in text or "three dimensional" in text or "cuboid" in text: return draw_3d_shape("cuboid")
        elif "cube" in text: return draw_3d_shape("cube")
        elif "vector" in text and "3d" in text: return draw_3d_shape("vector3d")
        elif "pyramid" in text: return draw_3d_shape("pyramid")
    # 2D MATH
    if "triangle" in text: return draw_2d_shape("triangle")
    elif "rectangle" in text: return draw_2d_shape("rectangle")
    elif "square" in text: return draw_2d_shape("square")
    elif "circle" in text: return draw_2d_shape("circle")
    elif "angle" in text: return draw_2d_shape("angle", {"deg":60})
    elif "bisect" in text: return draw_2d_shape("bisector")
    elif "bearing" in text: return draw_2d_shape("bearing")
    elif "polygon" in text: return draw_2d_shape("polygon")
    elif "sin" in text or "cos" in text or "tan" in text: return draw_2d_shape("trig_triangle")
    # 2D PHYSICS
    elif subject == "Physics":
        if "circuit" in text or "ohm" in text: return draw_2d_shape("circuit")
        elif "mirror" in text or "reflection" in text: return draw_2d_shape("mirror")
        elif "wave" in text: return draw_2d_shape("wave")
        elif "magnet" in text: return draw_2d_shape("magnet")
        elif "vector" in text: return draw_2d_shape("vector")
    return None

# ============ SYSTEM PROMPTS ============
SYSTEM_PROMPT_S1_S4 = """
You are DIGITAL UNEB TUTOR, the #1 NCDC 2026 Uganda Examiner for SECONDARY S1-S4.
GOLDEN RULES:
1. CURRICULUM LOCK: ONLY NCDC 2026 S1-S4.
2. NO JSON, NO CODE, NO [] BRACKETS. ONLY PLAIN MARKDOWN TEXT.
3. QUANTITY RULE: When asked for questions, ALWAYS give AT LEAST 10.
4. DIAGRAM RULE: If topic is Geometry, 3D, Bearings, Trigonometry, Physics Circuits, add at end: DIAGRAM_TYPE: [triangle/cube/circuit]

FORMAT FOR EACH QUESTION:
### **SCENARIO X: [Ugandan Title]**
4 sentence Uganda story.
**TASK:** What learner must do.
**QUESTION X:** [4 marks]
**SOLUTION - STEP BY STEP**
Step 1: State formula/concept
Step 2: Substitute values
Step 3: Calculate with units
**Answer: ___**
---
"""

SYSTEM_PROMPT_S5_S6 = """
You are DIGITAL UNEB TUTOR, a Senior NCDC 2026 Uganda Examiner for SECONDARY S5-S6.
Give advanced, detailed university-entry level explanations. Follow NCDC S5-S6 syllabus. 800 words. Include derivations and AOI. NO JSON.
"""

# ============ FULL NCDC CURRICULUM - 100% INTACT ============
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
    "Mathematics": {"S1": ["Geometric Construction"], "S2": ["Bearings Mapping"], "S4": ["Building 3D Geometric Models"]},
    "Physics": {"S2": ["Reflection using Plane Mirrors"], "S3": ["Series and Parallel Circuits", "Mapping Magnetic Fields"]}
}
AOI_FRAMEWORK = {"S1": "Community Problem: Water purification", "S2": "Local Industry Problem: Soil conservation", "S3": "National Issue: Disease prevention", "S4": "Global/Local Challenge: Climate change", "S5": "Research and Innovation", "S6": "Professional Level"}

@st.cache_resource
def get_client(): return Groq(api_key=st.secrets["GROQ_API_KEY"])

def add_to_memory(role, content):
    if "chat_memory" not in st.session_state: st.session_state.chat_memory = []
    st.session_state.chat_memory.append({"role": role, "content": content, "time": datetime.now().strftime("%H:%M")})

def get_memory_context():
    if "chat_memory" not in st.session_state: return ""
    last_5 = st.session_state.chat_memory[-5:]
    return "Previous conversation:\n" + "\n".join([f"{m['role']}: {m['content']}" for m in last_5]) + "\n\n"

def create_pdf(content, title):
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); p.setFont("Helvetica-Bold", 14); p.drawString(50,800,title); y=770; p.setFont("Helvetica", 10)
    for line in content.split('\n')[:80]: p.drawString(50,y,line[:95]); y-=14;
    p.save(); buffer.seek(0); return buffer

def display_with_pdf(content, name, subject, level):
    st.markdown(content)
    formulas = re.findall(r'\$(.*?)\$', content)
    if formulas: st.markdown("### 🔑 Key Formula"); [st.latex(f) for f in formulas]

    diagram_path = detect_and_draw_diagram(content, subject, level)
    if diagram_path: st.image(diagram_path, caption="Diagram")

    pdf = create_pdf(content, name); st.download_button("📥 Download PDF", pdf, f"{name}.pdf")

def get_model_for_mode(mode, lab_mode):
    if lab_mode: return AI_MODEL_FAST
    if mode in ["Theory", "Practical", "Bulk", "Mock", "AOI", "Quiz"]: return AI_MODEL_LONG
    return AI_MODEL_FAST

def call_groq_safe(client, messages, model, max_tokens=4000, temperature=0.7):
    for attempt in range(3):
        try: res = client.chat.completions.create(model=model, messages=messages, max_tokens=max_tokens, temperature=temperature); return res.choices[0].message.content
        except RateLimitError:
            if attempt < 2: time.sleep(2 ** attempt)
            else: res = client.chat.completions.create(model=AI_MODEL_FAST, messages=messages, max_tokens=2000); return res.choices[0].message.content
        except Exception as e: return f"AI Error: {e}"

def get_ai_response(client, user_query, subject, class_level, topic, mode, lab_mode):
    memory = get_memory_context(); model = get_model_for_mode(mode, lab_mode)
    system = SYSTEM_PROMPT_S1_S4 if class_level in ["S1","S2","S3","S4"] else SYSTEM_PROMPT_S5_S6
    prompt = f"{memory}{system}\n\nLevel: {class_level}, Subject: {subject}, Topic: {topic}\nStudent Request: {user_query}\n\nCRITICAL: Generate AT LEAST 10 DIFFERENT SCENARIOS WITH FULL STEP-BY-STEP SOLUTIONS. NO JSON."
    answer = call_groq_safe(client, [{"role":"system","content":system},{"role":"user","content":prompt}], model, max_tokens=4000 if model==AI_MODEL_LONG else 2000, temperature=0.2)
    add_to_memory("Student", user_query); add_to_memory("Tutor", answer); log_activity(st.session_state.user_type, "AI Query", f"{subject} {class_level} {topic}")
    return answer

def generate_mock_paper(client, subject, level, paper, lab_mode):
    model = get_model_for_mode("Mock", lab_mode)
    system = SYSTEM_PROMPT_S1_S4
    prompts = {"P1":f"Generate 40 MCQ for {subject} {level}. NO JSON.","P2":f"Generate 10 Theory questions for {subject} {level}. Each with Uganda scenario + full solution. NO JSON.","P3":f"Generate 5 Practical questions for {subject} {level}. NO JSON."}
    return call_groq_safe(client, [{"role":"system","content":system},{"role":"user","content":prompts[paper]}], model, max_tokens=4000, temperature=0.3)

def main():
    client = get_client()
    if "chat_memory" not in st.session_state: st.session_state.chat_memory = []
    st.markdown("<h1 style='text-align:center; background:gold; color:black; padding:10px'>📚 DIGITAL UNEB TUTOR 2026 - S1 TO S6</h1>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"<div style='background:#2b2b2b; color:white; padding:12px; border-left:4px solid #ffc107; border-radius:5px; margin-bottom:15px'><b>⚠️ DISCLAIMER</b><br>For learning support only.<br><b>📞 Support:</b> {CONTACT}</div>", unsafe_allow_html=True)
        st.success(f"Logged in as: {st.session_state.user_type}")
        lab_mode = st.toggle("🚀 SCHOOL LAB MODE", value=True)
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
        level = st.selectbox("Class", ["S1","S2","S3","S4","S5","S6"])
        topic = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject][level])
        mode = st.radio("Mode", ["🔍 Smart Search", "📖 Theory + AOI", "📝 Quiz Mode", "📄 Mock Exams"])

    st.subheader("❓ Ask Anything About This Topic"); ask_q = st.text_input("Type your question here", key="universal_ask")
    if st.button("Ask AI", key="ask_btn"): ans = get_ai_response(client, ask_q, subject, level, topic, "Search", lab_mode); display_with_pdf(ans, f"Ask_{topic}", subject, level)
    st.divider()

    if mode == "🔍 Smart Search":
        search_q = st.text_input("Search any concept");
        if st.button("Search"): result = get_ai_response(client, search_q, subject, level, search_q, "Search", lab_mode); display_with_pdf(result, "SearchResult", subject, level)
    elif mode == "📖 Theory + AOI":
        st.header(f"{subject} {level}: {topic}"); st.info(f"**AOI Focus**: {AOI_FRAMEWORK[level]}")
        if st.button("Generate Full NCDC Notes + 10 Examples", type="primary"): raw = get_ai_response(client, "Explain fully with 10 scenario examples", subject, level, topic, "Theory", lab_mode); display_with_pdf(raw, f"Theory_{topic}", subject, level)
    elif mode == "📝 Quiz Mode":
        if st.button("Generate 10 Scenario Questions"): quiz = get_ai_response(client, "Generate 10 competency-based questions with unique Uganda scenarios and full answers.", subject, level, topic, "Quiz", lab_mode); display_with_pdf(quiz, f"Quiz_{topic}", subject, level)
    elif mode == "📄 Mock Exams":
        st.header(f"📄 Mock Exams: {subject} {level}"); col1,col2,col3 = st.columns(3)
        with col1:
            if st.button("Generate P1 MCQ"): mock = generate_mock_paper(client, subject, level, "P1", lab_mode); display_with_pdf(mock, "MockP1", subject, level)
        with col2:
            if st.button("Generate P2 Theory"): mock = generate_mock_paper(client, subject, level, "P2", lab_mode); display_with_pdf(mock, "MockP2", subject, level)
        with col3:
            if st.button("Generate P3 Practical"): mock = generate_mock_paper(client, subject, level, "P3", lab_mode); display_with_pdf(mock, "MockP3", subject, level)

if __name__ == "__main__": main()
