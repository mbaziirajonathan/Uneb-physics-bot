import streamlit as st
import os, io, json, re, time
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from groq import Groq, RateLimitError
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 PRO", page_icon="📚", layout="wide")

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    STUDENT_PASSWORD = st.secrets["STUDENT_PASSWORD"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("Set GROQ_API_KEY, STUDENT_PASSWORD, ADMIN_PASSWORD in Streamlit secrets")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)
LOG_FILE = "usage_log.json"
CONTACT = "256751040731"
AI_MODEL_LONG = "llama-3.3-70b-versatile"
AI_MODEL_FAST = "llama-3.1-8b-instant"
st.sidebar.warning(f"⚠️ LEGAL NOTICE: DIGITAL UNEB TUTOR 2026 PRO\nNCDC + UNEB EXAMINER MODE\n📞 {CONTACT}")

MASTER_SYSTEM_PROMPT = """You are DIGITAL UNEB TUTOR 2026 PRO.
Role: Senior NCDC Curriculum Specialist + UNEB Chief Examiner for Uganda S1-S6.
Chain of Thought Rule: For every problem solve in steps: 1. Understand 2. Formula 3. Substitute 4. Answer.
Rules: Use NCDC 2026 + UNEB ITEM/TASK/SCENARIO format. Diagrams must have title, numbered labels, arrows, pointers."""

### DATABASES - FULL RESTORED ###
UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Number Bases", "Integers", "Fractions", "Cartesian Coordinates", "Percentages", "Algebra I"], "S2": ["Patterns", "Bearings", "Angles", "Algebra II", "Sets", "Rates"], "S3": ["Quadratics", "Matrices", "Probability", "Vectors", "Similarity", "Trigonometry I"], "S4": ["Functions", "3D Geometry", "Statistics", "Circle Geometry", "Binomials"], "S5": ["Differentiation", "Integration", "Permutations", "Complex Numbers"], "S6": ["Differential Equations", "Mechanics", "Statistics II", "Linear Programming"]},
    "Physics": {"S1": ["Measurement", "Forces", "Work Energy Power", "Density", "Pressure"], "S2": ["Light", "Thermal Physics", "Electricity I", "Waves I", "Sound"], "S3": ["Electricity II", "Magnetism", "Waves II", "Atomic Physics"], "S4": ["Electromagnetism", "Electronics", "Radioactivity", "Astrophysics"], "S5": ["Gravitation", "Optics", "Fluid Mechanics", "Thermal Physics II"], "S6": ["Electric Fields", "Magnetic Fields", "Nuclear Physics", "Quantum Physics"]},
    "Chemistry": {"S1": ["States of Matter", "Mixtures", "Atoms", "Compounds"], "S2": ["Acids Alkalis", "Salts", "Air", "Water"], "S3": ["Bonding", "Stoichiometry", "Electrolysis", "Energy Changes"], "S4": ["REDOX", "Organic II", "Rate of Reaction", "Equilibrium I"], "S5": ["Energetics", "Kinetics", "Equilibrium II", "Acids and Bases"], "S6": ["Electrochemistry", "Organic III", "Industrial Chemistry"]},
    "Biology": {"S1": ["Cells", "Classification", "Nutrition in Plants", "Diversity"], "S2": ["Soil", "Nutrition in Animals", "Respiration", "Excretion"], "S3": ["Respiration", "Genetics I", "Reproduction", "Growth"], "S4": ["Coordination", "Ecology", "Photosynthesis", "Transport"], "S5": ["Cell Biology", "Enzymes", "Genetics II", "Microbiology"], "S6": ["Hormones", "Biotechnology", "Evolution", "Ecosystems"]}
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

### CORE FUNCTIONS ###
def load_logs(): return json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []
def save_log(entry): logs = load_logs(); logs.append(entry); json.dump(logs, open(LOG_FILE,"w"))
def log_activity(user_type, action, details): save_log({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user_type, "action": action, "details": details})
def create_pdf(content, title):
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); p.setFont("Helvetica-Bold", 14); p.drawString(50,800,title); y=770; p.setFont("Helvetica", 10)
    for i,line in enumerate(content.split('\n')[:80]): p.drawString(50,y-(i*14),line[:95])
    p.save(); buffer.seek(0); return buffer
def call_groq(user_prompt):
    try: res = client.chat.completions.create(model=AI_MODEL_LONG, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}], max_tokens=4000, temperature=0.7); return res.choices[0].message.content
    except RateLimitError: res = client.chat.completions.create(model=AI_MODEL_FAST, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}], max_tokens=2000); return res.choices[0].message.content

### FIXED RENDER FUNCTION ###
def auto_render_pixel_diagram(topic, subject, level):
    st.info("🤖 AI is writing Python code and rendering HD image...")
    prompt = f"Generate ONLY python matplotlib code to draw '{topic}' for {level} {subject}. MUST include: plt.savefig('auto_diagram.png', dpi=300, bbox_inches='tight') and plt.close(). No plt.show()"
    code = call_groq(prompt).replace("```python","").replace("```","")
    try:
        # Force save to current folder, not /mnt/data
        code = code.replace("/mnt/data/auto_diagram.png", "auto_diagram.png")
        exec_globals = {"plt": plt, "np": np}
        exec(code, exec_globals)

        if os.path.exists("auto_diagram.png"):
            return "auto_diagram.png"
        else:
            return "ERROR: AI did not generate savefig command"
    except Exception as e: return f"ERROR: {e}"

def generate_practical(subject, level, prac_name):
    level_group = "S1-S4" if int(level[1]) <= 4 else "S5-S6"
    data = PRACTICAL_DATABASE.get(subject,{}).get(level_group,{}).get(prac_name,{})
    if not data: return "Practical not found in database"
    prompt = f"Expand this NCDC practical into full UNEB report format with objective, apparatus, procedure, observations, questions, safety: {data} for {subject} {level}"
    return call_groq(prompt)

def display_with_pdf(content, name):
    st.markdown(content)
    for f in re.findall(r'\$(.*?)\$', content): st.latex(f)
    pdf = create_pdf(content, name); st.download_button("📥 Download PDF", pdf, f"{name}.pdf", key=f"dl_{name}_{time.time()}")

### PORTALS ###
def show_student_portal():
    st.header("📚 Student Portal - S1 to S6 - NCDC PRO MODE")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tab1, tab2, tab3 = st.tabs(["🔍 Smart Search + Solver", "📖 Learn Topic", "🎨 Diagram Generator"])

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
            prac_list = list(PRACTICAL_DATABASE.get(subject2,{}).get("S1-S4",{}).keys()) if int(level2[1])<=4 else list(PRACTICAL_DATABASE.get(subject2,{}).get("S5-S6",{}).keys())
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
        st.header("🎨 Diagram Generator - V3.7.5.1")
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

def show_admin_portal():
    st.header("🏫 Admin Portal - V3.7.5.1")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tab1, tab2 = st.tabs(["📊 Analytics", "📖 Curriculum Manager"])
    with tab1:
        logs = load_logs()
        st.metric("Total Logs", len(logs))
        if logs: st.dataframe(pd.DataFrame(logs))
    with tab2:
        st.subheader("NCDC Curriculum")
        subj = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)])
        st.write(UNEB_CURRICULUM_MAP[subj][level])

st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO - V3.7.5.1 RESTORED")
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"])
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    if user_type == "Student" and password == STUDENT_PASSWORD: st.session_state["role"] = "Student"; st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD: st.session_state["role"] = "Admin"; st.rerun()
    elif password: st.sidebar.error("Wrong password")

if st.session_state.get("role") == "Admin": show_admin_portal()
elif st.session_state.get("role") == "Student": show_student_portal()
else: st.info("Please login to continue")
