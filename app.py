import streamlit as st
import os, io, json, re, time, glob, difflib
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from groq import Groq, RateLimitError
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 PRO", page_icon="📚", layout="wide")

### DUAL KEY + SECRETS ###
try:
    GROQ_API_KEY_1 = st.secrets["GROQ_API_KEY_1"]
    GROQ_API_KEY_2 = st.secrets["GROQ_API_KEY_2"]
    STUDENT_PASSWORD = st.secrets["STUDENT_PASSWORD"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("Set GROQ_API_KEY_1, GROQ_API_KEY_2, STUDENT_PASSWORD, ADMIN_PASSWORD in Streamlit secrets")
    st.stop()

if "current_key" not in st.session_state: st.session_state.current_key = 1
def get_client():
    key = GROQ_API_KEY_1 if st.session_state.current_key == 1 else GROQ_API_KEY_2
    return Groq(api_key=key)
client = get_client()

LOG_FILE = "usage_log.json"
ASSETS_FOLDER = "assets"
LABELS_FOLDER = "assets/labels"
os.makedirs(LABELS_FOLDER, exist_ok=True)
CONTACT = "256751040731"
AI_MODEL_LONG = "llama-3.3-70b-versatile"
AI_MODEL_FAST = "llama-3.1-8b-instant"
st.sidebar.warning(f"⚠️ LEGAL NOTICE: DIGITAL UNEB TUTOR 2026 PRO V4.4.0\nASSETS + LABEL EDITOR + DUAL KEY\n📞 {CONTACT}")

MASTER_SYSTEM_PROMPT = """You are DIGITAL UNEB TUTOR 2026 PRO.
Role: Senior NCDC Curriculum Specialist + UNEB Chief Examiner for Uganda S1-S6.
Chain of Thought Rule: For every problem solve in steps: 1. Understand 2. Formula 3. Substitute 4. Answer.
Rules: Use NCDC 2026 + UNEB ITEM/TASK/SCENARIO format."""

### DATABASES - FULL RESTORED + ENGLISH ADDED ###
UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Number Bases", "Integers", "Fractions", "Cartesian Coordinates", "Percentages", "Algebra I"], "S2": ["Patterns", "Bearings", "Angles", "Algebra II", "Sets", "Rates"], "S3": ["Quadratics", "Matrices", "Probability", "Vectors", "Similarity", "Trigonometry I"], "S4": ["Functions", "3D Geometry", "Statistics", "Circle Geometry", "Binomials"], "S5": ["Differentiation", "Integration", "Permutations", "Complex Numbers"], "S6": ["Differential Equations", "Mechanics", "Statistics II", "Linear Programming"]},
    "Physics": {"S1": ["Measurement", "Forces", "Work Energy Power", "Density", "Pressure"], "S2": ["Light", "Thermal Physics", "Electricity I", "Waves I", "Sound"], "S3": ["Electricity II", "Magnetism", "Waves II", "Atomic Physics"], "S4": ["Electromagnetism", "Electronics", "Radioactivity", "Astrophysics"], "S5": ["Gravitation", "Optics", "Fluid Mechanics", "Thermal Physics II"], "S6": ["Electric Fields", "Magnetic Fields", "Nuclear Physics", "Quantum Physics"]},
    "Chemistry": {"S1": ["States of Matter", "Mixtures", "Atoms", "Compounds"], "S2": ["Acids Alkalis", "Salts", "Air", "Water"], "S3": ["Bonding", "Stoichiometry", "Electrolysis", "Energy Changes"], "S4": ["REDOX", "Organic II", "Rate of Reaction", "Equilibrium I"], "S5": ["Energetics", "Kinetics", "Equilibrium II", "Acids and Bases"], "S6": ["Electrochemistry", "Organic III", "Industrial Chemistry"]},
    "Biology": {"S1": ["Cells", "Classification", "Nutrition in Plants", "Diversity"], "S2": ["Soil", "Nutrition in Animals", "Respiration", "Excretion"], "S3": ["Respiration", "Genetics I", "Reproduction", "Growth"], "S4": ["Coordination", "Ecology", "Photosynthesis", "Transport"], "S5": ["Cell Biology", "Enzymes", "Genetics II", "Microbiology"], "S6": ["Hormones", "Biotechnology", "Evolution", "Ecosystems"]},
    "English": {"S1": ["Grammar", "Comprehension", "Composition", "Parts of Speech"], "S2": ["Literature", "Summary", "Letter Writing", "Punctuation"], "S3": ["Novel", "Poetry", "Oral Skills", "Essay Writing"], "S4": ["Shakespeare", "Functional Writing", "Report Writing"], "S5": ["Advanced Grammar", "Literary Devices"], "S6": ["Literary Appreciation", "Criticism"]}, # ADDED
    "ICT": {"S1": ["Computer Basics","Hardware"],"S2": ["Word Processing","Spreadsheets"],"S3": ["Databases","Presentations"],"S4": ["Internet","Graphics"],"S5": ["Programming Python"],"S6": ["Web Design","Networks"]},
    "Geography": {"S1": ["Map Reading","Vegetation"],"S2": ["Climate","Soils"],"S3": ["Rivers","Lakes"],"S4": ["Population","Urbanization"],"S5": ["Industries","Mining"],"S6": ["GIS","Tourism"]},
    "History": {"S1": ["Early Man","Stone Age"],"S2": ["Kingdoms","Trade"],"S3": ["Colonialism","Scramble"],"S4": ["Independence","Governments"],"S5": ["World Wars","UNO"],"S6": ["Cold War","Decolonization"]},
    "CRE": {"S1": ["Creation","Fall"],"S2": ["Prophets","Covenants"],"S3": ["Jesus","Parables"],"S4": ["Church","Sacraments"],"S5": ["Ethics","Social Justice"],"S6": ["Comparative","World Religions"]},
    "IRE": {"S1": ["Tawheed","Prophets"],"S2": ["Quran","Hadith"],"S3": ["Fiqh","Pillars"],"S4": ["History","Sirah"],"S5": ["Islamic Law"],"S6": ["Comparative Religion"]},
    "Literature": {"S1": ["Poetry","Prose"],"S2": ["Drama","Novel"],"S3": ["African Literature"],"S4": ["Shakespeare","Essays"],"S5": ["Literary Devices"],"S6": ["Criticism"]},
    "Commerce": {"S1": ["Business","Trade"],"S2": ["Banking","Insurance"],"S3": ["Marketing","Advertising"],"S4": ["Entrepreneurship"],"S5": ["Finance"],"S6": ["Business Law"]},
    "Economics": {"S1": ["Scarcity","Needs"],"S2": ["Demand","Supply"],"S3": ["Money","Banking"],"S4": ["Trade","Taxation"],"S5": ["National Income"],"S6": ["Development","International Trade"]},
    "Agriculture": {"S1": ["Soil","Crops"],"S2": ["Livestock","Tools"],"S3": ["Crop Production"],"S4": ["Animal Health"],"S5": ["Records","Marketing"],"S6": ["Agribusiness"]},
    "Art": {"S1": ["Drawing","Color"],"S2": ["Painting","Design"],"S3": ["Sculpture","Craft"],"S4": ["Graphics","Textiles"],"S5": ["Photography"],"S6": ["Art History"]}
}

### FULL PRACTICAL DATABASE RESTORED ###
PRACTICAL_DATABASE = {
    "Physics": {"S1-S4": {"Ohm's Law": {"objective": "To verify Ohm's Law V=IR", "apparatus": "Cell, Ammeter, Voltmeter, Rheostat, Connecting wires", "procedure": "1. Connect circuit in series. 2. Vary rheostat. 3. Record V and I.", "observations": "Table: Current I(A) | Voltage V(V)", "questions": ["State Ohm's law", "Plot V vs I graph", "Find slope"], "safety": "Do not short circuit the cell"}, "Simple Pendulum": {"objective": "To determine acceleration due to gravity g", "apparatus": "Bob, String, Meter rule, Stopwatch, Stand", "procedure": "1. Set up pendulum. 2. Time 20 oscillations. 3. Repeat for different lengths.", "observations": "Table: Length L(m) | Time t(s) | Period T(s)", "questions": ["What affects period?", "Plot T^2 vs L"], "safety": "Ensure bob does not hit anyone"}}, "S5-S6": {"RC Circuit": {"objective": "To determine time constant of RC circuit", "apparatus": "Capacitor, Resistor, Voltmeter, Stopwatch", "procedure": "1. Charge capacitor. 2. Discharge through resistor. 3. Record V vs t.", "observations": "Graph: Voltage vs Time", "questions": ["Define time constant tau", "Calculate tau"], "safety": "Discharge capacitor before handling"}}},
    "Chemistry": {"S1-S4": {"Separation of Mixtures": {"objective": "To separate sand and salt mixture", "apparatus": "Beaker, Filter paper, Funnel, Bunsen burner, Evaporating dish", "procedure": "1. Add water. 2. Filter. 3. Evaporate filtrate.", "observations": "Residue: Sand. Filtrate: Salt solution", "questions": ["Name methods used", "Why is filtration used"], "safety": "Wear goggles"}, "Titration": {"objective": "To determine concentration of NaOH", "apparatus": "Burette, Pipette, Conical flask, Indicator", "procedure": "1. Pipette acid. 2. Titrate with base. 3. Note titre.", "observations": "Table: Final burette reading | Initial | Titre", "questions": ["Calculate molarity", "Define titre"], "safety": "Acid can cause burns"}}, "S5-S6": {"Rate of Reaction": {"objective": "To investigate effect of temperature on rate", "apparatus": "Conical flask, Mg ribbon, HCl, Stopwatch", "procedure": "1. React Mg with HCl at different temps. 2. Time gas produced.", "observations": "Table: Temp | Time", "questions": ["Plot graph", "Explain effect"], "safety": "HCl fumes are dangerous"}}},
    "Biology": {"S1-S4": {"Use of Microscope": {"objective": "To observe plant and animal cells", "apparatus": "Microscope, Onion epidermis, Cheek cells, Slide, Cover slip", "procedure": "1. Place specimen. 2. Focus. 3. Draw.", "observations": "Draw and label cell parts", "questions": ["Function of nucleus", "Difference plant vs animal"], "safety": "Clean lens"}, "Food Tests": {"objective": "To test for food nutrients", "apparatus": "Iodine, Benedict's, Biuret, Test tubes", "procedure": "1. Add reagents. 2. Observe color change.", "observations": "Starch: Blue-black. Sugar: Brick red", "questions": ["Test for protein", "Test for lipids"], "safety": "Do not taste"}}, "S5-S6": {"Enzyme Action": {"objective": "To investigate effect of pH on amylase", "apparatus": "Amylase, Starch, Buffer solutions, Iodine", "procedure": "1. Mix at different pH. 2. Test every 2 min.", "observations": "Table: pH | Time for starch to disappear", "questions": ["Optimum pH", "Denaturation"], "safety": "Sterile conditions"}}}
}

### SVG ENGINE - KEPT FROM YOUR CODE ###
def svg_header(title): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 700"><defs><marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="black"/></marker></defs><rect width="950" height="700" fill="white"/><text x="475" y="40" text-anchor="middle" font-family="Arial" font-size="24" font-weight="bold" fill="black">{title}</text>'
def svg_footer(): return '</svg>'
def render_universal_svg(raw_svg): return f'<div style="width:100%; max-width:1000px; margin:auto; background:white; padding:20px; border-radius:15px; border:4px solid #1a237e;">{raw_svg}</div>'
def draw_atom(): return svg_header("Bohr Model of Atom - S3 Chemistry") + '<circle cx="475" cy="350" r="25" fill="#d32f2f" stroke="black" stroke-width="4"/><text x="475" y="358" text-anchor="middle" fill="white" font-size="16" font-weight="bold">N</text>' + svg_footer()
def draw_cone(): return svg_header("Cone - S1 Mathematics") + '<ellipse cx="475" cy="480" rx="220" ry="80" fill="#bbdefb" stroke="black" stroke-width="4"/><path d="M 255 480 L 475 170 L 695 480" fill="#90caf9" stroke="black" stroke-width="4"/>' + svg_footer()
def draw_plant_cell(): return svg_header("Plant Cell - S1 Biology") + '<rect x="120" y="100" width="700" height="450" fill="#c8e6c9" stroke="black" stroke-width="5"/>' + svg_footer()
def draw_circuit(): return svg_header("Simple Electric Circuit - S2 Physics") + '<line x1="180" y1="350" x2="330" y2="350" stroke="black" stroke-width="5"/>' + svg_footer()
def draw_pendulum(): return svg_header("Simple Pendulum - S1 Physics") + '<circle cx="475" cy="150" r="8" fill="black"/><line x1="475" y1="158" x2="550" y2="420" stroke="black" stroke-width="4"/>' + svg_footer()
def draw_water_cycle(): return svg_header("Water Cycle - S1 Geography") + '<circle cx="750" cy="100" r="50" fill="yellow"/>' + svg_footer()
AUTO_DRAW_ENGINE = {"atom": draw_atom, "cone": draw_cone, "cell": draw_plant_cell, "circuit": draw_circuit, "pendulum": draw_pendulum, "water cycle": draw_water_cycle}

### CORE FUNCTIONS ###
def load_logs(): return json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []
def save_log(entry): logs = load_logs(); logs.append(entry); json.dump(logs, open(LOG_FILE,"w"))
def log_activity(user_type, action, details): save_log({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user_type, "action": action, "details": details})
def create_pdf(content, title):
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); p.setFont("Helvetica-Bold", 14); p.drawString(50,800,title); y=770; p.setFont("Helvetica", 10)
    for i,line in enumerate(content.split('\n')[:80]): p.drawString(50,y-(i*14),line[:95])
    p.save(); buffer.seek(0); return buffer

### DUAL KEY ROTATION ###
def switch_key():
    st.session_state.current_key = 2 if st.session_state.current_key == 1 else 1
    global client
    client = get_client()
    st.warning(f"🔄 Rate limit hit. Switched to API Key {st.session_state.current_key}")

def call_groq(user_prompt):
    try:
        res = client.chat.completions.create(model=AI_MODEL_LONG, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}], max_tokens=4000, temperature=0.7)
        return res.choices[0].message.content
    except RateLimitError:
        switch_key()
        res = client.chat.completions.create(model=AI_MODEL_FAST, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}], max_tokens=2000)
        return res.choices[0].message.content

### ASSETS + FUZZY MATCH + LABEL EDITOR ###
def sanitize(s): return re.sub(r'[^a-z0-9]', '', s.lower())
@st.cache_data
def get_all_assets():
    if not os.path.exists(ASSETS_FOLDER): return []
    return glob.glob(f"{ASSETS_FOLDER}/*.png") + glob.glob(f"{ASSETS_FOLDER}/*.jpg") + glob.glob(f"{ASSETS_FOLDER}/*.jpeg")

def find_best_asset(level, subject, topic):
    assets = get_all_assets()
    if not assets: return None
    target = sanitize(f"{level}{subject}{topic}")
    best_match = None
    best_score = 0
    for path in assets:
        filename = sanitize(os.path.basename(path).split('.')[0])
        score = difflib.SequenceMatcher(None, target, filename).ratio()
        if sanitize(level) in filename and sanitize(subject) in filename: score += 0.2
        if score > best_score:
            best_score = score
            best_match = path
    return best_match if best_score > 0.4 else None

def load_labels(level, subject, topic):
    path = f"{LABELS_FOLDER}/{sanitize(level+subject+topic)}.json"
    return json.load(open(path)) if os.path.exists(path) else []

def save_labels(level, subject, topic, labels):
    path = f"{LABELS_FOLDER}/{sanitize(level+subject+topic)}.json"
    json.dump(labels, open(path,"w"), indent=2)

def display_image_with_labels(img_path, labels):
    img = Image.open(img_path)
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.imshow(img)
    ax.axis('off')
    for label in labels:
        x_perc, y_perc = label["x"], label["y"]
        x_px = x_perc * img.width
        y_px = y_perc * img.height
        ax.annotate(f"{label['num']}. {label['name']}",
                    xy=(x_px, y_px),
                    xytext=(x_px + 40, y_px - 20),
                    arrowprops=dict(arrowstyle='->', color='red', lw=2),
                    bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="black", alpha=0.9),
                    fontsize=11, fontweight='bold', color='black')
    st.pyplot(fig)

### FIXED AI RENDER ###
def auto_render_pixel_diagram(topic, subject, level):
    st.info("🤖 AI is writing Python code and rendering HD image...")
    prompt = f"Generate ONLY python matplotlib code to draw '{topic}' for {level} {subject}. MUST include: plt.savefig('auto_diagram.png', dpi=300, bbox_inches='tight') and plt.close(). No plt.show()"
    code = call_groq(prompt).replace("```python","").replace("```","")
    try:
        code = code.replace("/mnt/data/auto_diagram.png", "auto_diagram.png")
        exec_globals = {"plt": plt, "np": np}
        exec(code, exec_globals)
        return "auto_diagram.png" if os.path.exists("auto_diagram.png") else "ERROR: AI did not generate savefig command"
    except Exception as e: return f"ERROR: {e}"

def generate_practical(subject, level, prac_name):
    level_group = "S1-S4" if int(level[1]) <= 4 else "S5-S6"
    data = PRACTICAL_DATABASE.get(subject,{}).get(level_group,{}).get(prac_name,{})
    if not data: return "Practical not found in database"
    prompt = f"Expand this NCDC practical into full UNEB report format: {data} for {subject} {level}"
    return call_groq(prompt)

def display_with_pdf(content, name):
    st.markdown(content)
    for f in re.findall(r'\$(.*?)\$', content): st.latex(f)
    pdf = create_pdf(content, name); st.download_button("📥 Download PDF", pdf, f"{name}.pdf", key=f"dl_{name}_{time.time()}")

### PORTALS ###
def show_student_portal():
    st.header("📚 Student Portal - S1 to S6 - NCDC PRO MODE")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Smart Search + Solver", "📖 Learn Topic", "🎨 Diagram Generator", "🖼️ Assets Library"])

    with tab1:
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="search_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="search_level")
        ask_q = st.text_area("Ask any question / Solve any problem")
        if st.button("Ask AI Brain", type="primary") and ask_q:
            log_activity("Student", "Ask Question", ask_q)
            ans = call_groq(f"Use Chain of Thought. Answer step by step: {ask_q} for {level} {subject}")
            display_with_pdf(ans, "Answer")

    with tab2:
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="learn_subj")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="learn_level")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject2][level2], key="learn_topic")
        mode = st.radio("Mode", ["📖 Theory", "🧠 AOI", "🧪 Practicals Lab", "📝 UNEB Quiz Mode", "📚 Bulk Revision"])
        log_activity("Student", "Learn Mode", mode)

        if mode == "📖 Theory" and st.button("Teach Me"):
            raw = call_groq(f"Teach {topic2} step by step with examples for {level2} {subject2}")
            display_with_pdf(raw, "Theory")
        elif mode == "🧠 AOI" and st.button("Generate Activity of Integration"):
            aoi = call_groq(f"Generate NCDC Activity of Integration for {level2} {subject2} topic: {topic2}")
            display_with_pdf(aoi, "AOI")
        elif mode == "🧪 Practicals Lab":
            level_group = "S1-S4" if int(level2[1]) <= 4 else "S5-S6"
            prac_list = list(PRACTICAL_DATABASE.get(subject2,{}).get(level_group,{}).keys())
            if not prac_list: prac_list = ["No practicals in DB for this subject"]
            prac = st.selectbox("Select Practical", prac_list)
            if st.button("Generate Practical"):
                report = generate_practical(subject2,level2,prac)
                display_with_pdf(report, "Practical")
        elif mode == "📝 UNEB Quiz Mode" and st.button("Generate Quiz"):
            quiz = call_groq(f"Generate 10 UNEB ITEM/TASK/SCENARIO questions with answers on {topic2} for {level2} {subject2}")
            display_with_pdf(quiz, "Quiz")
        elif mode == "📚 Bulk Revision" and st.button("Generate Revision"):
            rev = call_groq(f"Generate full revision notes + 20 questions for {topic2} {level2} {subject2}")
            display_with_pdf(rev, "Revision")

    with tab3:
        st.header("🎨 Diagram Generator - SVG + AI Render")
        subject3 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="svg_subj")
        level3 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="svg_level")
        topic3 = st.text_input("Describe Diagram:", "Draw atom")
        diagram_mode = st.radio("Choose Output Mode", ["1. Instant SVG [Auto Draw]", "2. HD Pixel Image [AI Render]"])

        if st.button("Generate Diagram", type="primary"):
            log_activity("Student", "Generate Diagram", topic3)
            if diagram_mode == "1. Instant SVG [Auto Draw]":
                topic_lower = topic3.lower()
                found = False
                for key, func in AUTO_DRAW_ENGINE.items():
                    if key in topic_lower:
                        st.markdown(render_universal_svg(func()), unsafe_allow_html=True)
                        st.success("✅ Instant SVG with labels")
                        found = True; break
                if not found: st.warning("Not in AutoDraw. Try: atom, cone, cell, circuit, pendulum, water cycle")
            else:
                img_path = auto_render_pixel_diagram(topic3, subject3, level3)
                if "ERROR" in str(img_path): st.error(f"Rendering failed: {img_path}")
                else:
                    st.image(img_path, caption=f"HD: {topic3}", use_container_width=True)
                    with open(img_path, "rb") as file: st.download_button("📥 Download HD PNG", file, f"{topic3}.png")

    with tab4: # NEW ASSETS TAB
        st.header("🖼️ Assets Library - Fuzzy Match + Labels")
        subject4 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="asset_subj")
        level4 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="asset_level")
        topic4 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject4][level4], key="asset_topic")
        if st.button("Load Best Match Diagram", type="primary"):
            img_path = find_best_asset(level4, subject4, topic4)
            labels = load_labels(level4, subject4, topic4)
            if img_path:
                st.success(f"✅ Best Match: {os.path.basename(img_path)}")
                if labels: display_image_with_labels(img_path, labels)
                else: st.image(img_path, use_container_width=True)
                with open(img_path, "rb") as file: st.download_button("📥 Download PNG", file, f"{topic4}.png")
            else: st.error("No matching PNG found in /assets/")

def show_admin_portal():
    st.header("🏫 Admin Portal - V4.4.0")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tab1, tab2, tab3 = st.tabs(["📊 Analytics", "📖 Curriculum Manager", "✏️ Label Editor"])

    with tab1:
        logs = load_logs()
        st.metric("Total Logs", len(logs))
        if logs: st.dataframe(pd.DataFrame(logs))
    with tab2:
        st.subheader("NCDC Curriculum")
        subj = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)])
        st.write(UNEB_CURRICULUM_MAP[subj][level])

    with tab3: # NEW
        st.subheader("Label Editor")
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="a_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="a_level")
        topic = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject][level], key="a_topic")
        uploaded_file = st.file_uploader("Upload PNG", type=["png","jpg","jpeg"])
        key = f"labels_{level}_{subject}_{topic}"

        if uploaded_file:
            save_path = f"{ASSETS_FOLDER}/{level} {subject} {topic}.png"
            with open(save_path, "wb") as f: f.write(uploaded_file.getbuffer())
            img = Image.open(uploaded_file)
            st.image(img, use_container_width=True)
            if key not in st.session_state: st.session_state[key] = load_labels(level, subject, topic)
            col1, col2, col3 = st.columns(3)
            with col1: x = st.slider("X %", 0.0, 1.0, 0.5, 0.01, key=f"x_{key}")
            with col2: y = st.slider("Y %", 0.0, 1.0, 0.5, 0.01, key=f"y_{key}")
            with col3: name = st.text_input("Label Name", "Nucleus", key=f"name_{key}")
            if st.button("Add Label"):
                st.session_state[key].append({"num": len(st.session_state[key])+1, "name": name, "x": x, "y": y})
            st.write("Current Labels:", st.session_state[key])
            if st.button("💾 Save Labels"):
                save_labels(level, subject, topic, st.session_state[key])
                st.success("Saved")

st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO - V4.4.0 FULL MERGE")
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"])
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    if user_type == "Student" and password == STUDENT_PASSWORD: st.session_state["role"] = "Student"; st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD: st.session_state["role"] = "Admin"; st.rerun()
    elif password: st.sidebar.error("Wrong password")

if st.session_state.get("role") == "Admin": show_admin_portal()
elif st.session_state.get("role") == "Student": show_student_portal()
else: st.info("Please login to continue")
