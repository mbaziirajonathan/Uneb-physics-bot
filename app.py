import streamlit as st
import os, io, json, re, time, glob, difflib, requests, random, hashlib
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from groq import Groq, RateLimitError
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import fitz # PyMuPDF

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 PRO", page_icon="📚", layout="wide")

### 1. AUTO CREATE FILES + FOLDERS - PREVENTS BOOT CRASH ###
LOG_FILE = "usage_log.json"
CACHE_FILE = "ai_cache.json"
PARENTS_FILE = "parents.json"
ASSETS_FOLDER = "assets"
LABELS_FOLDER = "assets/labels"

for f, default in [(LOG_FILE, []), (CACHE_FILE, {}), (PARENTS_FILE, {})]:
    if not os.path.exists(f):
        with open(f, "w") as fp: json.dump(default, fp)

os.makedirs(ASSETS_FOLDER, exist_ok=True)
os.makedirs(LABELS_FOLDER, exist_ok=True)

### 2. SECRETS + DUAL KEY ###
try:
    GROQ_API_KEY_1 = st.secrets["GROQ_API_KEY_1"]
    GROQ_API_KEY_2 = st.secrets["GROQ_API_KEY_2"]
    STUDENT_PASSWORD = st.secrets["STUDENT_PASSWORD"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
    WHATSAPP_TOKEN = st.secrets.get("WHATSAPP_TOKEN", "")
    WHATSAPP_PHONE_ID = st.secrets.get("WHATSAPP_PHONE_ID", "")
except KeyError as e:
    st.error(f"Missing secret: {e}. Go to Manage app > Settings > Secrets")
    st.stop()

if "current_key" not in st.session_state: st.session_state.current_key = 1
def get_client():
    key = GROQ_API_KEY_1 if st.session_state.current_key == 1 else GROQ_API_KEY_2
    return Groq(api_key=key)
client = get_client()

### 3. OFFLINE + CACHE SYSTEM ###
OFFLINE_MODE = st.sidebar.toggle("🔌 OFFLINE MODE - No Internet, No Tokens", value=False)
if OFFLINE_MODE:
    st.sidebar.warning("OFFLINE MODE ON. Using local cache only. No API calls.")

def load_cache():
    with open(CACHE_FILE) as f: return json.load(f)
def save_cache(cache):
    with open(CACHE_FILE,"w") as f: json.dump(cache, f, indent=2)

def get_cache_key(prompt, level):
    return hashlib.md5((prompt + level).encode()).hexdigest()

### 4. YOUR FULL DATABASES - RESTORED FROM YOUR CODE ###
CONTACT = "256751040731"
AI_MODEL_LONG = "llama-3.3-70b-versatile"
AI_MODEL_FAST = "llama-3.1-8b-instant"
st.sidebar.success(f"⚠️ DIGITAL UNEB TUTOR 2026 PRO V5.2.5\nNCDC + UNEB EXAMINER MODE\n📞 {CONTACT}")

MASTER_SYSTEM_PROMPT = """You are DIGITAL UNEB TUTOR 2026 PRO.
Role: Senior NCDC Curriculum Specialist + UNEB Chief Examiner for Uganda S1-S6.
Chain of Thought Rule: For every problem solve in steps: 1. Understand 2. Formula 3. Substitute 4. Answer.
Rules: Use NCDC 2026 + UNEB ITEM/TASK/SCENARIO format. Diagrams must have title, numbered labels, arrows, pointers."""

### DATABASES - FULL RESTORED FROM YOUR ATTACHED CODE ###
UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Number Bases", "Integers", "Fractions", "Cartesian Coordinates", "Percentages", "Algebra I"], "S2": ["Patterns", "Bearings", "Angles", "Algebra II", "Sets", "Rates"], "S3": ["Quadratics", "Matrices", "Probability", "Vectors", "Similarity", "Trigonometry I"], "S4": ["Functions", "3D Geometry", "Statistics", "Circle Geometry", "Binomials"], "S5": ["Differentiation", "Integration", "Permutations", "Complex Numbers"], "S6": ["Differential Equations", "Mechanics", "Statistics II", "Linear Programming"]},
    "Physics": {"S1": ["Measurement", "Forces", "Work Energy Power", "Density", "Pressure"], "S2": ["Light", "Thermal Physics", "Electricity I", "Waves I", "Sound"], "S3": ["Electricity II", "Magnetism", "Waves II", "Atomic Physics"], "S4": ["Electromagnetism", "Electronics", "Radioactivity", "Astrophysics"], "S5": ["Gravitation", "Optics", "Fluid Mechanics", "Thermal Physics II"], "S6": ["Electric Fields", "Magnetic Fields", "Nuclear Physics", "Quantum Physics"]},
    "Chemistry": {"S1": ["States of Matter", "Mixtures", "Atoms", "Compounds"], "S2": ["Acids Alkalis", "Salts", "Air", "Water"], "S3": ["Bonding", "Stoichiometry", "Electrolysis", "Energy Changes"], "S4": ["REDOX", "Organic II", "Rate of Reaction", "Equilibrium I"], "S5": ["Energetics", "Kinetics", "Equilibrium II", "Acids and Bases"], "S6": ["Electrochemistry", "Organic III", "Industrial Chemistry"]},
    "Biology": {"S1": ["Cells", "Classification", "Nutrition in Plants", "Diversity"], "S2": ["Soil", "Nutrition in Animals", "Respiration", "Excretion"], "S3": ["Respiration", "Genetics I", "Reproduction", "Growth"], "S4": ["Coordination", "Ecology", "Photosynthesis", "Transport"], "S5": ["Cell Biology", "Enzymes", "Genetics II", "Microbiology"], "S6": ["Hormones", "Biotechnology", "Evolution", "Ecosystems"]},
    "English": {"S1": ["Grammar"], "S2": ["Literature"], "S3": ["Novel"], "S4": ["Shakespeare"], "S5": ["Advanced Grammar"], "S6": ["Criticism"]},
    "ICT": {"S1": ["Computer Basics"],"S2": ["Word Processing"],"S3": ["Databases"],"S4": ["Internet"],"S5": ["Programming Python"],"S6": ["Web Design"]},
    "Geography": {"S1": ["Map Reading"],"S2": ["Climate"],"S3": ["Rivers"],"S4": ["Population"],"S5": ["Industries"],"S6": ["GIS"]},
    "History": {"S1": ["Early Man"],"S2": ["Kingdoms"],"S3": ["Colonialism"],"S4": ["Independence"],"S5": ["World Wars"],"S6": ["Cold War"]},
    "CRE": {"S1": ["Creation"],"S2": ["Prophets"],"S3": ["Jesus"],"S4": ["Church"],"S5": ["Ethics"],"S6": ["Comparative"]},
    "IRE": {"S1": ["Tawheed"],"S2": ["Quran"],"S3": ["Fiqh"],"S4": ["History"],"S5": ["Islamic Law"],"S6": ["Comparative Religion"]},
    "Literature": {"S1": ["Poetry"],"S2": ["Drama"],"S3": ["African Literature"],"S4": ["Shakespeare"],"S5": ["Literary Devices"],"S6": ["Criticism"]},
    "Commerce": {"S1": ["Business"],"S2": ["Banking"],"S3": ["Marketing"],"S4": ["Entrepreneurship"],"S5": ["Finance"],"S6": ["Business Law"]},
    "Economics": {"S1": ["Scarcity"],"S2": ["Demand"],"S3": ["Money"],"S4": ["Trade"],"S5": ["National Income"],"S6": ["Development"]},
    "Agriculture": {"S1": ["Soil"],"S2": ["Livestock"],"S3": ["Crop Production"],"S4": ["Animal Health"],"S5": ["Records"],"S6": ["Agribusiness"]},
    "Art": {"S1": ["Drawing"],"S2": ["Painting"],"S3": ["Sculpture"],"S4": ["Graphics"],"S5": ["Photography"],"S6": ["Art History"]}
}

PRACTICAL_DATABASE = {
    "Physics": {"S1-S4": {"Ohm's Law": {"objective": "To verify Ohm's Law V=IR", "apparatus": "Cell, Ammeter, Voltmeter, Rheostat, Connecting wires", "procedure": "1. Connect circuit in series. 2. Vary rheostat. 3. Record V and I.", "observations": "Table: Current I(A) | Voltage V(V)", "questions": ["State Ohm's law", "Plot V vs I graph", "Find slope"], "safety": "Do not short circuit the cell"}, "Simple Pendulum": {"objective": "To determine acceleration due to gravity g", "apparatus": "Bob, String, Meter rule, Stopwatch, Stand", "procedure": "1. Set up pendulum. 2. Time 20 oscillations. 3. Repeat for different lengths.", "observations": "Table: Length L(m) | Time t(s) | Period T(s)", "questions": ["What affects period?", "Plot T^2 vs L"], "safety": "Ensure bob does not hit anyone"}, "Refraction of Light": {"objective": "To find refractive index of glass", "apparatus": "Glass block, Pins, Paper, Ruler", "procedure": "1. Draw normal. 2. Trace rays. 3. Measure angles.", "observations": "Table: Angle i | Angle r", "questions": ["Define refractive index", "Snell's Law"], "safety": "Handle glass carefully"}}, "S5-S6": {"RC Circuit": {"objective": "To determine time constant of RC circuit", "apparatus": "Capacitor, Resistor, Voltmeter, Stopwatch", "procedure": "1. Charge capacitor. 2. Discharge through resistor. 3. Record V vs t.", "observations": "Graph: Voltage vs Time", "questions": ["Define time constant tau", "Calculate tau"], "safety": "Discharge capacitor before handling"}, "Young's Modulus": {"objective": "To determine Young's modulus of a wire", "apparatus": "Wire, Masses, Micrometer", "procedure": "1. Measure original length. 2. Add masses. 3. Measure extension.", "observations": "Table: Force(N) | Extension(m)", "questions": ["Plot F vs e", "Calculate Y"], "safety": "Wear goggles"}}},
    "Chemistry": {"S1-S4": {"Separation of Mixtures": {"objective": "To separate sand and salt mixture", "apparatus": "Beaker, Filter paper, Funnel, Bunsen burner, Evaporating dish", "procedure": "1. Add water. 2. Filter. 3. Evaporate filtrate.", "observations": "Residue: Sand. Filtrate: Salt solution", "questions": ["Name methods used", "Why is filtration used"], "safety": "Wear goggles. Handle Bunsen carefully"}, "Titration": {"objective": "To determine concentration of NaOH", "apparatus": "Burette, Pipette, Conical flask, Indicator", "procedure": "1. Pipette acid. 2. Titrate with base. 3. Note titre.", "observations": "Table: Final burette reading | Initial | Titre", "questions": ["Calculate molarity", "Define titre"], "safety": "Acid can cause burns"}, "Preparation of Oxygen": {"objective": "To prepare oxygen gas in lab", "apparatus": "Test tube, Bunsen, Manganese IV oxide, Potassium chlorate", "procedure": "1. Heat mixture. 2. Collect gas over water.", "observations": "Gas relights glowing splint", "questions": ["Equation", "Test for O2"], "safety": "Do not overheat"}}, "S5-S6": {"Rate of Reaction": {"objective": "To investigate effect of temperature on rate", "apparatus": "Conical flask, Mg ribbon, HCl, Stopwatch", "procedure": "1. React Mg with HCl at different temps. 2. Time gas produced.", "observations": "Table: Temp | Time", "questions": ["Plot graph", "Explain effect"], "safety": "HCl fumes are dangerous"}, "Electrolysis": {"objective": "To electrolyse copper II sulfate", "apparatus": "Carbon electrodes, Power supply, Beaker", "procedure": "1. Set up cell. 2. Pass current. 3. Observe electrodes.", "observations": "Anode: bubbles. Cathode: copper deposit", "questions": ["Write half equations"], "safety": "Low voltage only"}}},
    "Biology": {"S1-S4": {"Use of Microscope": {"objective": "To observe plant and animal cells", "apparatus": "Microscope, Onion epidermis, Cheek cells, Slide, Cover slip", "procedure": "1. Place specimen. 2. Focus. 3. Draw.", "observations": "Draw and label cell parts", "questions": ["Function of nucleus", "Difference plant vs animal"], "safety": "Clean lens with tissue"}, "Food Tests": {"objective": "To test for food nutrients", "apparatus": "Iodine, Benedict's, Biuret, Test tubes", "procedure": "1. Add reagents. 2. Observe color change.", "observations": "Starch: Blue-black. Sugar: Brick red", "questions": ["Test for protein", "Test for lipids"], "safety": "Do not taste chemicals"}, "Osmosis": {"objective": "To demonstrate osmosis in potato", "apparatus": "Potato, Sucrose solutions, Ruler, Weighing scale", "procedure": "1. Cut potato. 2. Place in solutions. 3. Measure after 1hr.", "observations": "Table: Concentration | Change in length", "questions": ["Define osmosis", "What is plasmolysis"], "safety": "Use sharp knife carefully"}}, "S5-S6": {"Enzyme Action": {"objective": "To investigate effect of pH on amylase", "apparatus": "Amylase, Starch, Buffer solutions, Iodine", "procedure": "1. Mix at different pH. 2. Test every 2 min.", "observations": "Table: pH | Time for starch to disappear", "questions": ["Optimum pH", "Denaturation"], "safety": "Sterile conditions"}, "Transpiration": {"objective": "To measure rate of transpiration", "apparatus": "Potometer, Plant shoot, Beaker", "procedure": "1. Set up potometer. 2. Record bubble movement.", "observations": "Distance moved in 5 min", "questions": ["Factors affecting rate"], "safety": "Keep plant hydrated"}}}
}

### SVG ENGINE ###
def svg_header(title): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 700"><defs><marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="black"/></marker></defs><rect width="950" height="700" fill="white"/><text x="475" y="40" text-anchor="middle" font-family="Arial" font-size="24" font-weight="bold" fill="black">{title}</text>'
def svg_footer(): return '</svg>'
def render_universal_svg(raw_svg): return f'<div style="width:100%; max-width:1000px; margin:auto; background:white; padding:20px; border-radius:15px; border:4px solid #1a237e;">{raw_svg}</div>'

def draw_atom(): return svg_header("Bohr Model of Atom - S3 Chemistry") + '<circle cx="475" cy="350" r="25" fill="#d32f2f" stroke="black" stroke-width="4"/><text x="475" y="358" text-anchor="middle" fill="white" font-size="16" font-weight="bold">N</text><line x1="500" y1="350" x2="650" y2="320" stroke="black" stroke-width="3" marker-end="url(#arrowhead)"/><text x="660" y="325" font-size="18" font-weight="bold">1. Nucleus</text><circle cx="475" cy="350" r="110" fill="none" stroke="#1976d2" stroke-width="3"/><circle cx="585" cy="350" r="10" fill="#42a5f5" stroke="black" stroke-width="3"/>' + svg_footer()
def draw_cone(): return svg_header("Cone - S1 Mathematics") + '<ellipse cx="475" cy="480" rx="220" ry="80" fill="#bbdefb" stroke="black" stroke-width="4"/><path d="M 255 480 L 475 170 L 695 480" fill="#90caf9" stroke="black" stroke-width="4"/><line x1="475" y1="170" x2="475" y2="480" stroke="red" stroke-width="3" stroke-dasharray="8,8"/><text x="475" y="650" text-anchor="middle" font-size="20" font-weight="bold">Formula: V = 1/3 πr²h</text>' + svg_footer()
def draw_plant_cell(): return svg_header("Plant Cell - S1 Biology") + '<rect x="120" y="100" width="700" height="450" fill="#c8e6c9" stroke="black" stroke-width="5"/><circle cx="350" cy="325" r="70" fill="#ffcdd2" stroke="black" stroke-width="4"/><ellipse cx="550" cy="325" rx="130" ry="100" fill="#e1f5fe" stroke="black" stroke-width="4" stroke-dasharray="6,6"/><rect x="380" y="180" width="50" height="70" fill="#43a047" stroke="black" stroke-width="3"/>' + svg_footer()
def draw_circuit(): return svg_header("Simple Electric Circuit - S2 Physics") + '<line x1="180" y1="350" x2="330" y2="350" stroke="black" stroke-width="5"/><rect x="330" y="320" width="80" height="60" fill="none" stroke="black" stroke-width="5"/><circle cx="540" cy="350" r="50" fill="none" stroke="black" stroke-width="5"/><line x1="540" y1="400" x2="540" y2="500" stroke="black" stroke-width="5"/><line x1="540" y1="500" x2="180" y2="500" stroke="black" stroke-width="5"/><line x1="180" y1="500" x2="180" y2="350" stroke="black" stroke-width="5"/>' + svg_footer()
def draw_pendulum(): return svg_header("Simple Pendulum - S1 Physics") + '<circle cx="475" cy="150" r="8" fill="black"/><line x1="475" y1="158" x2="550" y2="420" stroke="black" stroke-width="4"/><circle cx="550" cy="420" r="30" fill="#78909c" stroke="black" stroke-width="4"/><line x1="400" y1="420" x2="700" y2="420" stroke="gray" stroke-width="2"/>' + svg_footer()
def draw_water_cycle(): return svg_header("Water Cycle - S1 Geography") + '<circle cx="750" cy="100" r="50" fill="yellow"/><path d="M100 500 Q475 350 850 500" fill="#90caf9" stroke="blue" stroke-width="4"/><text x="475" y="650" text-anchor="middle" font-size="20" font-weight="bold">1.Evaporation 2.Condensation 3.Precipitation</text>' + svg_footer()

AUTO_DRAW_ENGINE = {"atom": draw_atom, "atomic": draw_atom, "cone": draw_cone, "cylinder": draw_cone, "plant cell": draw_plant_cell, "cell": draw_plant_cell, "circuit": draw_circuit, "electric": draw_circuit, "pendulum": draw_pendulum, "water cycle": draw_water_cycle}

### 5. CORE FUNCTIONS ###
def load_db(file):
    with open(file) as f: return json.load(f)
def save_db(file,data):
    with open(file,"w") as f: json.dump(data,f,indent=2)
def load_logs():
    with open(LOG_FILE) as f: return json.load(f)
def save_log(entry):
    logs = load_logs(); logs.append(entry); save_db(LOG_FILE, logs)

def read_uploaded_file(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in doc])
    elif uploaded_file.name.endswith(".docx"):
        from docx import Document
        doc = Document(uploaded_file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif uploaded_file.name.endswith(".txt"):
        return uploaded_file.read().decode()
    return ""

def create_download(content, filename, fmt="pdf"):
    if fmt == "pdf":
        buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); p.setFont("Helvetica", 10)
        for i,line in enumerate(content.split('\n')[:90]): p.drawString(50,800-(i*14),line[:100])
        p.save(); buffer.seek(0); return buffer, f"{filename}.pdf"
    elif fmt == "excel":
        df = pd.DataFrame({"Content": content.split('\n')}); buffer = io.BytesIO(); df.to_excel(buffer, index=False, engine='openpyxl'); buffer.seek(0); return buffer, f"{filename}.xlsx"
    elif fmt == "html":
        html = f"<html><body><pre>{content}</pre></body></html>"; return io.BytesIO(html.encode()), f"{filename}.html"
    elif fmt == "docx":
        from docx import Document
        doc = Document(); doc.add_paragraph(content); buffer = io.BytesIO(); doc.save(buffer); buffer.seek(0); return buffer, f"{filename}.docx"

def get_level_group(level):
    n = int(level[1])
    return "S1-S4" if n <= 4 else "S5-S6"

def get_mixed_topics(level, subject):
    level_num = int(level[1])
    topics = []; weights = {level_num: 0.7}
    if level_num-1 >= 1: weights[level_num-1] = 0.2
    if level_num-2 >= 1: weights[level_num-2] = 0.1
    for l, w in weights.items():
        l_str = f"S{l}"
        all_topics = UNEB_CURRICULUM_MAP[subject][l_str]
        num_topics = max(1, int(len(all_topics) * w))
        topics.extend(random.sample(all_topics, min(num_topics, len(all_topics))))
    return topics

def switch_key():
    st.session_state.current_key = 2 if st.session_state.current_key == 1 else 1
    global client
    client = get_client()

### 6. SMART CALL WITH CACHE ###
def call_groq(user_prompt, level="S1", sample="", instructions=""):
    cache = load_cache()
    key = get_cache_key(user_prompt + sample + instructions, level)

    if key in cache:
        st.info("⚡ Loaded from Local Cache. 0 Tokens used.")
        return cache[key]

    if OFFLINE_MODE:
        return "❌ OFFLINE MODE: This question not in cache. Please go online once to generate and cache it."

    level_instruction = "LOWER SECONDARY S1-S4. Simple, Ugandan examples." if int(level[1]) <=4 else "ADVANCED S5-S6. Deep, detailed."
    full_prompt = f"{level_instruction}\nTEACHER SAMPLE:\n{sample}\nTEACHER INSTRUCTIONS: {instructions}\n\nGENERATE:\n{user_prompt}"
    try:
        res = client.chat.completions.create(model=AI_MODEL_LONG, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":full_prompt}], max_tokens=4000)
        answer = res.choices[0].message.content
    except RateLimitError:
        switch_key()
        res = client.chat.completions.create(model=AI_MODEL_FAST, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":full_prompt}], max_tokens=2000)
        answer = res.choices[0].message.content

    cache[key] = answer
    save_cache(cache)
    st.success("✅ Saved to Local Cache for next time")
    return answer

def sanitize(s): return re.sub(r'[^a-z0-9]', '', s.lower())
@st.cache_data(ttl=60)
def get_all_assets(): return glob.glob(f"{ASSETS_FOLDER}/*.*")

def find_asset_strict(level, subject, topic):
    assets = get_all_assets(); level_clean = sanitize(level); subject_clean = sanitize(subject); topic_clean = sanitize(topic)
    candidates = [p for p in assets if level_clean in sanitize(p) and subject_clean in sanitize(p)]
    best_match = None; best_score = 0
    for path in candidates:
        score = difflib.SequenceMatcher(None, topic_clean, sanitize(os.path.basename(path))).ratio()
        if score > best_score: best_score = score; best_match = path
    return (best_match, candidates) if best_score > 0.5 else (None, candidates)

def display_image_with_zoom(img_path):
    img = Image.open(img_path)
    zoom = st.slider("Zoom %", 50, 200, 100, key=f"zoom_{img_path}")
    width = int(img.width * zoom / 100)
    st.image(img.resize((width, int(img.height * zoom / 100))))

def display_with_preview(content, name):
    edited = st.text_area("AI Preview - EDIT BEFORE DOWNLOAD", content, height=350, key=f"preview_{name}")
    cols = st.columns(4)
    formats = ["pdf","excel","html","docx"]
    for i, fmt in enumerate(formats):
        buf, fname = create_download(edited, name, fmt)
        cols[i].download_button(f"📥 {fmt.upper()}", buf, fname, key=f"{name}_{fmt}_{time.time()}")

def teacher_input_section(tab_name):
    st.info(f"🤖 AI Assistant Mode: Upload sample. Type instructions. AI follows.")
    col1, col2 = st.columns(2)
    with col1: sample_file = st.file_uploader(f"Upload Sample for {tab_name}", type=["pdf","docx","txt"], key=f"sample_{tab_name}")
    with col2: instructions = st.text_area(f"Teacher Instructions for {tab_name}", key=f"instr_{tab_name}")
    sample_text = read_uploaded_file(sample_file) if sample_file else ""
    return sample_text, instructions

### 7. FIXED RENDER FUNCTION ###
def auto_render_pixel_diagram(topic, subject, level):
    st.info("🤖 AI is writing Python code and rendering HD image...")
    prompt = f"Generate ONLY python matplotlib code to draw '{topic}' for {level} {subject}. MUST include: plt.savefig('auto_diagram.png', dpi=300, bbox_inches='tight') and plt.close(). No plt.show()"
    code = call_groq(prompt).replace("```python","").replace("```","")
    try:
        code = code.replace("/mnt/data/auto_diagram.png", "auto_diagram.png")
        exec_globals = {"plt": plt, "np": np}
        exec(code, exec_globals)
        if os.path.exists("auto_diagram.png"):
            return "auto_diagram.png"
        else:
            return "ERROR: AI did not generate savefig command"
    except Exception as e: return f"ERROR: {e}"

def generate_practical(subject, level, prac_name):
    level_group = get_level_group(level)
    data = PRACTICAL_DATABASE.get(subject,{}).get(level_group,{}).get(prac_name,{})
    if not data: return "Practical not found in database"
    prompt = f"Expand this NCDC practical into full UNEB report format with objective, apparatus, procedure, observations, questions, safety: {data} for {subject} {level}"
    return call_groq(prompt, level)

### 8. STUDENT PORTAL ###
def show_student_portal():
    st.header("📚 Student Portal - S1 to S6 - NCDC PRO MODE")
    if st.button("Logout"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Smart Search + Solver", "📖 Learn Topic", "🧪 Practicals Lab", "🎨 Diagram Generator"])

    with tab1:
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)])
        ask_q = st.text_area("Ask any question / Solve any problem")
        if st.button("Ask AI Brain", type="primary") and ask_q:
            ans = call_groq(f"Use Chain of Thought. Answer step by step: {ask_q} for {level} {subject}", level)
            display_with_preview(ans, "Answer")

    with tab2:
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="s2")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="l2")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject2][level2])
        mode = st.radio("Mode", ["📖 Theory", "🧠 AOI", "🧪 Practicals", "📝 UNEB Quiz Mode", "📚 Bulk Revision"])

        if mode == "📖 Theory" and st.button("Teach Me"):
            raw = call_groq(f"Teach {topic2} step by step with examples for {level2} {subject2}", level2)
            display_with_preview(raw, "Theory")
        elif mode == "🧠 AOI" and st.button("Generate Activity of Integration"):
            aoi = call_groq(f"Generate NCDC Activity of Integration for {level2} {subject2} topic: {topic2}", level2)
            display_with_preview(aoi, "AOI")
        elif mode == "🧪 Practicals":
            prac_list = list(PRACTICAL_DATABASE.get(subject2,{}).get(get_level_group(level2),{}).keys())
            if not prac_list: st.warning("No practicals in DB for this subject/level")
            prac = st.selectbox("Select Practical", prac_list)
            if st.button("Generate Practical") and prac:
                report = generate_practical(subject2,level2,prac)
                display_with_preview(report, "Practical")
        elif mode == "📝 UNEB Quiz Mode" and st.button("Generate Quiz"):
            topics = get_mixed_topics(level2, subject2)
            quiz = call_groq(f"Generate 10 UNEB ITEM/TASK/SCENARIO questions with answers on {topic2} for {level2} {subject2}", level2)
            display_with_preview(quiz, "Quiz")
        elif mode == "📚 Bulk Revision" and st.button("Generate Revision"):
            rev = call_groq(f"Generate full revision notes + 20 questions for {topic2} {level2} {subject2}", level2)
            display_with_preview(rev, "Revision")

    with tab3:
        st.subheader("🧪 Practical Experiments from DATABASE")
        subject3 = st.selectbox("Subject", list(PRACTICAL_DATABASE.keys()), key="prac_subj")
        level3 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="prac_level")
        group = get_level_group(level3)
        prac_list = list(PRACTICAL_DATABASE.get(subject3, {}).get(group, {}).keys())
        if not prac_list: st.warning("No practicals in database for this level")
        topic3 = st.selectbox("Select Practical", prac_list)
        if st.button("Generate Full Practical") and topic3:
            report = generate_practical(subject3,level3,topic3)
            display_with_preview(report, f"Practical_{topic3}")

    with tab4:
        st.header("🎨 Diagram Generator - V3.7.5.1")
        subject4 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="svg_subj")
        level4 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="svg_level")
        topic4 = st.text_input("Describe Diagram:", "Draw atom")
        diagram_mode = st.radio("Choose Output Mode", ["1. Instant SVG [Auto Draw]", "2. HD Pixel Image [AI Render]"])

        if st.button("Generate Diagram", type="primary"):
            if diagram_mode == "1. Instant SVG [Auto Draw]":
                topic_lower = topic4.lower()
                found = False
                for key, func in AUTO_DRAW_ENGINE.items():
                    if key in topic_lower:
                        st.markdown(render_universal_svg(func()), unsafe_allow_html=True)
                        st.success("✅ Instant SVG with labels")
                        found = True; break
                if not found: st.warning("Not in AutoDraw. Try: atom, cone, cell, circuit, pendulum, water cycle")
            else:
                img_path = auto_render_pixel_diagram(topic4, subject4, level4)
                if "ERROR" in str(img_path): st.error(f"Rendering failed: {img_path}")
                else:
                    st.image(img_path, caption=f"HD: {topic4}", use_container_width=True)
                    with open(img_path, "rb") as file: st.download_button("📥 Download HD PNG", file, f"{topic4}.png")

### 9. ADMIN PORTAL ###
def show_admin_portal():
    st.header("🏫 Admin Portal - TEACHER DRIVEN AI")
    if st.button("Logout"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
    tabs = st.tabs(["📊 Analytics","📖 Curriculum","✏️ Labels","📤 Exam Generator","📈 Performance","📱 WhatsApp","📑 MOES","📝 Marking","📅 SOW","🏆 Report Cards"])

    with tabs[0]: st.dataframe(pd.DataFrame(load_logs()))
    with tabs[1]:
        sample, instr = teacher_input_section("Curriculum")
        subj = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)])
        if st.button("Generate Curriculum Doc"):
            out = call_groq(f"Generate curriculum document for {level} {subj}", level, sample, instr)
            display_with_preview(out, "Curriculum")

    with tabs[2]:
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="a1")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="a2")
        topic = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject][level])
        uploaded = st.file_uploader("Upload PNG Diagram")
        if uploaded:
            with open(f"{ASSETS_FOLDER}/{level} {subject} {topic}.png","wb") as f: f.write(uploaded.getbuffer())
            st.success("Uploaded")

    with tabs[3]:
        sample, instr = teacher_input_section("Exam")
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="ex_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="ex_level")
        num_q = st.slider("Number of Questions", 10, 50, 50)
        if st.button("Generate Exam"):
            topics = get_mixed_topics(level, subject)
            prompt = f"Generate {num_q} UNEB exam questions for {level} {subject}. Topics: {topics}. Use SCENARIO, ITEM, TASK."
            exam = call_groq(prompt, level, sample, instr)
            display_with_preview(exam, f"{level}_{subject}_Exam")

    with tabs[4]:
        sample, instr = teacher_input_section("Performance Report")
        uploaded = st.file_uploader("Upload Results CSV: Name,Subject,Score,Term", type="csv")
        if uploaded:
            df=pd.read_csv(uploaded)
            st.dataframe(df)
            st.bar_chart(df.groupby("Subject")["Score"].mean())
            if st.button("Generate Performance Report"):
                data_summary = df.describe().to_string()
                report = call_groq(f"Generate performance analysis report. Data: {data_summary}", "S4", sample, instr)
                display_with_preview(report, "Performance_Report")

    with tabs[5]:
        parents = load_db(PARENTS_FILE)
        name = st.text_input("Student Name"); number = st.text_input("Number +256")
        if st.button("Save"): parents[name]=number; save_db(PARENTS_FILE, parents); st.success("Saved")
        msg = st.text_area("Message")
        if st.button("Send"): st.warning("WhatsApp needs internet. Disabled in Offline Mode" if OFFLINE_MODE else "Send logic here")

    with tabs[6]:
        sample, instr = teacher_input_section("MOES")
        if st.button("Generate MOES Report"):
            report = call_groq("Generate MOES termly report", "S4", sample, instr)
            display_with_preview(report, "MOES")

    with tabs[7]:
        sample, instr = teacher_input_section("Marking Guide")
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="m1")
        ans = st.text_area("Paste Student Answer")
        if st.button("Mark"):
            marked = call_groq(f"Mark this answer for {subject}. Give marks and feedback", "S4", sample, instr)
            st.markdown(marked)

    with tabs[8]:
        sample, instr = teacher_input_section("SOW")
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="sow1")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="sow2")
        if st.button("Generate SOW"):
            sow = call_groq(f"Generate SOW + 12 lesson plans for {level} {subject}", level, sample, instr)
            display_with_preview(sow, "SOW")

    with tabs[9]:
        sample, instr = teacher_input_section("Report Card")
        uploaded = st.file_uploader("Upload Results CSV: Name,Subject,Score,Grade,Remarks", type="csv", key="rc")
        if uploaded:
            df = pd.read_csv(uploaded)
            st.dataframe(df)
            for student in df["Name"].unique():
                s_df = df[df["Name"]==student]
                data = s_df.to_string()
                if st.button(f"Generate Report for {student}", key=f"btn_{student}"):
                    report_text = call_groq(f"Generate report card for {student}. Data: {data}", "S4", sample, instr)
                    st.text_area(f"Preview {student}", report_text, height=300, key=f"prev_{student}")
                    buf,fname = create_download(report_text, f"Report_{student}", "pdf")
                    st.download_button(f"Download {student}", buf, fname, key=f"dl{student}")

### 10. MAIN APP ###
st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO - V5.2.5 RESTORED")
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"])
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    if user_type == "Student" and password == STUDENT_PASSWORD: st.session_state["role"] = "Student"; st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD: st.session_state["role"] = "Admin"; st.rerun()
    elif password: st.sidebar.error("Wrong password")

if st.session_state.get("role") == "Admin": show_admin_portal()
elif st.session_state.get("role") == "Student": show_student_portal()
else: st.info("Please login to continue")
