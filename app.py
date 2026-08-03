import streamlit as st
import os, io, json, re, time, base64, math
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
from streamlit_option_menu import option_menu
from groq import Groq, RateLimitError
import pandas as pd

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 PRO", page_icon="📚", layout="wide")

# ========== 1. SECRETS ==========
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
STUDENT_PASSWORD = st.secrets["STUDENT_PASSWORD"]
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
client = Groq(api_key=GROQ_API_KEY)

LOG_FILE = "usage_log.json"
CONTACT = "256751040731"
AI_MODEL_LONG = "llama-3.3-70b-versatile"
AI_MODEL_FAST = "llama-3.1-8b-instant"

st.sidebar.warning(f"⚠️ LEGAL NOTICE: DIGITAL UNEB TUTOR 2026 PRO\nNCDC + UNEB EXAMINER MODE\n📞 {CONTACT}")

# ============ 2. FULL 22 SUBJECTS S1-S6 DATABASE - NO DATA LOST ============
UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Number Bases", "Integers", "Fractions", "Cartesian Coordinates", "Geometric Construction", "Data"], "S2": ["Patterns", "Bearings", "Angles", "Algebra I", "Business Arithmetic", "Time"], "S3": ["Quadratics", "Matrices", "Probability", "Vectors", "Trigonometry", "Mensuration"], "S4": ["Functions", "3D Geometry", "Statistics", "Linear Programming", "Calculus Intro"], "S5": ["Differentiation", "Integration", "Circular Measure", "Complex Numbers"], "S6": ["Differential Equations", "Mechanics", "Probability Distributions", "Further Calculus"]},
    "Physics": {"S1": ["Measurement", "Forces", "Work Energy Power", "Pressure", "Simple Machines"], "S2": ["Light", "Thermal Physics", "Electricity I", "Waves"], "S3": ["Electricity II", "Magnetism", "Sound", "Mechanics"], "S4": ["Electromagnetism", "Electronics", "Modern Physics", "A.C Theory"], "S5": ["Gravitation", "Optics", "Fluid Mechanics", "Waves Advanced"], "S6": ["Electric Fields", "Magnetic Fields", "EMI", "Quantum Physics"]},
    "Chemistry": {"S1": ["States of Matter", "Mixtures", "Air", "Water"], "S2": ["Acids Alkalis", "Salts", "Periodic Table"], "S3": ["Bonding", "Stoichiometry", "Rates"], "S4": ["REDOX", "Industrial Processes", "Organic II"], "S5": ["Energetics", "Kinetics", "Equilibrium", "Organic III"], "S6": ["Electrochemistry", "Transition Metals", "Organic Synthesis"]},
    "Biology": {"S1": ["Cells", "Classification", "Ecosystems"], "S2": ["Soil", "Nutrition", "Transport"], "S3": ["Respiration", "Excretion", "Genetics I"], "S4": ["Coordination", "Genetics", "Ecology"], "S5": ["Cell Biology", "Enzymes", "Gas Exchange"], "S6": ["Hormones", "Biotechnology", "Immunity"]},
    "Geography": {"S1": ["Earth", "Maps", "Weather"], "S2": ["Rocks", "Drainage", "Soils"], "S3": ["Transport", "Trade", "Industry"], "S4": ["EAC", "GIS", "Regional Development"], "S5": ["Physical Geo Advanced", "Research"], "S6": ["Geomorphology", "Climatology"]},
    "History": {"S1": ["Early Man", "Ancient Civilizations"], "S2": ["Scramble for Africa", "Colonialism"], "S3": ["Nationalism", "WWI WWII"], "S4": ["Independence", "Cold War"], "S5": ["East African History", "World History"], "S6": ["International Relations"]},
    "Literature": {"S1": ["Prose: River and Source", "Poetry", "Drama"], "S2": ["Animal Farm", "Shakespeare"], "S3": ["A Thousand Splendid Suns", "The Tempest"], "S4": ["The Pearl", "An Enemy of the People"], "S5": ["Macbeth", "Sonnets"], "S6": ["King Lear", "Post Colonial"]},
    "English": {"S1": ["Grammar", "Comprehension", "Composition"], "S2": ["Tenses", "Summary", "Letters"], "S3": ["Clauses", "Reports", "Debate"], "S4": ["Punctuation", "CV", "Interview"]},
    "CRE": {f"S{i}": [f"CRE S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}, "IRE": {f"S{i}": [f"IRE S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "Agriculture": {f"S{i}": [f"Agriculture S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}, "Entrepreneurship": {f"S{i}": [f"Entrepreneurship S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "ICT": {f"S{i}": [f"ICT S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}, "Art and Design": {f"S{i}": [f"Art S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "Music": {f"S{i}": [f"Music S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}, "French": {f"S{i}": [f"French S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "Kiswahili": {f"S{i}": [f"Kiswahili S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}, "Luganda": {f"S{i}": [f"Luganda S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "Economics": {f"S{i}": [f"Economics S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}, "Commerce": {f"S{i}": [f"Commerce S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "Technical Drawing": {f"S{i}": [f"Tech Drawing S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}, "Food and Nutrition": {f"S{i}": [f"Food & Nutrition S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "Fashion and Textiles": {f"S{i}": [f"Fashion S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}
}

PRACTICAL_TOPICS = {"Mathematics": {"S1": ["Geometric Construction"]}, "Physics": {"S1": ["Simple Pendulum"]}, "Chemistry": {"S1": ["Filtration"]}, "Biology": {"S1": ["Light Microscope"]}}

# ============ 3. MASTER SYSTEM PROMPT V3.2 - SUBJECT AWARE RULES ============
MASTER_SYSTEM_PROMPT = """
You are DIGITAL UNEB TUTOR 2026 PRO. Senior NCDC Examiner for Uganda S1-S6.

LAW 1: UNEB EXAMINER MODE - ITEM/TASK/SCENARIO
When setting questions you MUST use Ugandan context.
FORMAT:
ITEM: A real Ugandan scenario. e.g. "A boda boda rider in Kampala..."
TASK: What student must do. e.g. "Calculate the..."
SCENARIO: Link to NCDC Syllabus + daily life.

LAW 2: MATH & PHYSICS SOLVER MODE - STEP BY STEP
For calculations show:
Step 1: Given data WITH UNITS
Step 2: Formula
Step 3: Substitution WITH UNITS
Step 4: Final Answer WITH CORRECT UNITS and 2dp

LAW 3: SVG DIAGRAM MODE - SUBJECT AWARE RULES. OUTPUT ONLY VALID JSON. NO TEXT.
SCHEMA:
{"title": "string", "width": 600, "height": 450, "shapes": [{"label": "string", "type": "circle/rectangle/triangle", "x": number, "y": number, "width": number, "height": number}], "connections": [{"from": "string", "to": "string", "arrow": bool, "dashed": bool}]}

SUBJECT RULES - YOU MUST FOLLOW:
1. IF TOPIC HAS: refraction, reflection, lens, mirror, light -> RAY DIAGRAM RULE
   MUST INCLUDE: "Air", "Glass/Water" as rectangles, "Normal" as dashed line, "Incident Ray" and "Refracted Ray" as lines with arrows. Show boundary.

2. IF TOPIC HAS: circuit, battery, bulb, resistor, current -> CIRCUIT RULE
   MUST INCLUDE: "Battery", "Bulb", "Resistor" as rectangles. MUST USE manual x,y to form a loop. Connect with lines.

3. IF TOPIC HAS: cell, cycle, ecosystem, food web, heart, organ -> BIOLOGY CYCLE RULE
   USE AUTO-LAYOUT. Use circles and rectangles. Connect with arrows to show flow.

4. IF TOPIC HAS: bar graph, statistics, data -> GRAPH RULE
   Use rectangles for bars. Label axes.

5. IF TOPIC HAS: triangle, angle, vector, force -> GEOMETRY RULE
   Use triangle and arrow shapes. Include units in labels: "Force: 20N"

GENERAL RULES: 1. NEVER use dots for rays. 2. Labels must be clear and not overlap. 3. NEVER return ```json fences.
"""

# ============ 4. UNIVERSAL SVG ENGINE V3.2 - SCALED ============
def render_universal_svg(smart_json):
    if not smart_json or "shapes" not in smart_json:
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 450"><text x="10" y="20" fill="red" font-family="Arial">Error: Bad Diagram Data</text></svg>'

    width = smart_json.get("width", 600)
    height = smart_json.get("height", 450)
    shapes = smart_json.get("shapes", [])
    connections = smart_json.get("connections", [])
    title = smart_json.get("title", "Educational Diagram")

    n = len(shapes)
    if n == 0: return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"></svg>'

    svg_content = (
        f' <defs>\n'
        f' <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">\n'
        f' <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#2c3e50"/>\n'
        f' </marker>\n'
        f' </defs>\n'
        f' <text x="{width/2}" y="35" font-family="system-ui" font-size="16" text-anchor="middle" font-weight="700" fill="#1a252f">{title}</text>\n'
    )

    positions = {}
    shape_dimensions = {}
    center_x, center_y = width / 2, height / 2 + 20
    radius_x, radius_y = (width * 0.35), (height * 0.32)

    for i, shape in enumerate(shapes):
        label = shape.get("label", f"Node_{i}")
        if "x" in shape and "y" in shape:
            cx, cy = shape["x"], shape["y"]
        else:
            angle = (2 * math.pi * i / n) - (math.pi / 2)
            cx = center_x + radius_x * math.cos(angle)
            cy = center_y + radius_y * math.sin(angle)
        positions[label] = (cx, cy)

        stype = shape.get("type", "circle")
        if stype == "rectangle":
            w = shape.get("width", 90)
            h = shape.get("height", 45)
            shape_dimensions[label] = {"type": "rectangle", "w": w, "h": h}
        elif stype == "triangle":
            shape_dimensions[label] = {"type": "triangle", "r": 30}
        else:
            r = shape.get("radius", 32)
            shape_dimensions[label] = {"type": "circle", "r": r}

    svg_content += " <!-- Connections -->\n"
    for conn in connections:
        start_node = conn.get("from")
        end_node = conn.get("to")
        if start_node in positions and end_node in positions:
            x1, y1 = positions[start_node]
            x2, y2 = positions[end_node]
            dx, dy = x2 - x1, y2 - y1
            distance = math.hypot(dx, dy)
            if distance < 1: continue
            ux, uy = dx / distance, dy / distance

            s_dim = shape_dimensions[start_node]
            offset_s = s_dim.get("r", max(s_dim.get("w",40)/2, s_dim.get("h",40)/2))
            x1_trimmed, y1_trimmed = x1 + ux * offset_s, y1 + uy * offset_s

            e_dim = shape_dimensions[end_node]
            offset_e = e_dim.get("r", max(e_dim.get("w",40)/2, e_dim.get("h",40)/2))
            x2_trimmed, y2_trimmed = x2 - ux * offset_e, y2 - uy * offset_e

            has_arrow = 'marker-end="url(#arrow)"' if conn.get("arrow", True) else ''
            stroke_style = 'stroke-dasharray="4,4"' if conn.get("dashed", False) else ''
            svg_content += f' <line x1="{x1_trimmed:.1f}" y1="{y1_trimmed:.1f}" x2="{x2_trimmed:.1f}" y2="{y2_trimmed:.1f}" stroke="#2c3e50" stroke-width="2.5" {has_arrow} {stroke_style}/>\n'

    svg_content += " <!-- Shapes -->\n"
    for shape in shapes:
        label = shape.get("label", "")
        cx, cy = positions[label]
        color = shape.get("color", "#e3f2fd")
        stroke = shape.get("stroke", "#1e88e5")
        dim = shape_dimensions[label]

        if dim["type"] == "circle":
            svg_content += f' <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{dim["r"]}" fill="{color}" stroke="{stroke}" stroke-width="2.5"/>\n'
        elif dim["type"] == "rectangle":
            w, h = dim["w"], dim["h"]
            svg_content += f' <rect x="{(cx - w/2):.1f}" y="{(cy - h/2):.1f}" width="{w}" height="{h}" rx="6" fill="{color}" stroke="{stroke}" stroke-width="2.5"/>\n'
        elif dim["type"] == "triangle":
            points = f"{cx},{cy-30} {cx-30},{cy+20} {cx+30},{cy+20}"
            svg_content += f' <polygon points="{points}" fill="{color}" stroke="{stroke}" stroke-width="2.5"/>\n'

        vx, vy = cx - center_x, cy - center_y
        v_len = math.hypot(vx, vy)
        ux, uy = (vx / v_len, vy / v_len) if v_len > 0 else (0, 1)
        offset = (dim.get("r", 32) + 25) if dim["type"] == "circle" else (max(dim.get("w",90), dim.get("h",45))/2 + 25)
        lx, ly = cx + ux * offset, cy + uy * offset
        anchor = "start" if ux > 0.3 else "end" if ux < -0.3 else "middle"
        text_color = "#ffffff" if st.get_option("theme.base") == "dark" else "#2c3e50"
        svg_content += f' <line x1="{cx + ux*(offset-12):.1f}" y1="{cy + uy*(offset-12):.1f}" x2="{lx:.1f}" y2="{ly:.1f}" stroke="#7f8c8d" stroke-width="1" stroke-dasharray="2,2"/>\n'
        svg_content += f' <text x="{lx:.1f}" y="{ly+4:.1f}" font-family="system-ui" font-size="14" font-weight="600" fill="{text_color}" text-anchor="{anchor}">{label}</text>\n'

    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" style="background:#ffffff; border:1px solid #e2e8f0; border-radius:8px;">\n{svg_content}</svg>'

# ============ 5. CORE FUNCTIONS ============
def load_logs(): return json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []
def save_log(entry): logs = load_logs(); logs.append(entry); json.dump(logs, open(LOG_FILE,"w"))
def log_activity(user_type, action, details): flagged = "cheat" in details.lower(); save_log({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user_type, "action": action, "details": details, "flagged": flagged})

def create_pdf(content, title):
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); p.setFont("Helvetica-Bold", 14); p.drawString(50,800,title); y=770; p.setFont("Helvetica", 10)
    for i,line in enumerate(content.split('\n')[:80]): p.drawString(50,y-(i*14),line[:95])
    p.save(); buffer.seek(0); return buffer

def call_groq(user_prompt, mode="smart"):
    try:
        temp = 0.1 if mode=="svg" else 0.7
        tokens = 1500 if mode=="svg" else 4000
        res = client.chat.completions.create(model=AI_MODEL_LONG, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}], max_tokens=tokens, temperature=temp)
        return res.choices[0].message.content
    except RateLimitError:
        res = client.chat.completions.create(model=AI_MODEL_FAST, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}], max_tokens=2000, temperature=0.1)
        return res.choices[0].message.content
    except Exception as e: return f"AI Error: {e}"

def extract_json_from_text(raw):
    for pattern in [r'```json\s*(\{.*?\})\s*```', r'(\{.*\})']:
        match = re.search(pattern, raw, re.DOTALL)
        if match:
            try: return json.loads(match.group(1))
            except: continue
    return None

def generate_diagram(topic, subject, level):
    raw = call_groq(f"SVG MODE: Generate diagram for {level} {subject}: {topic}. Follow SUBJECT RULES strictly.", mode="svg")
    return extract_json_from_text(raw)

def ask_smart_brain(user_query, subject, class_level, topic):
    log_activity(st.session_state.role, "Smart Query", f"{subject} {class_level}")
    return call_groq(f"SMART MODE + STEP BY STEP: Level: {class_level}\nSubject: {subject}\nTopic: {topic}\nUser Question: {user_query}")

def generate_exam_items(user_query, subject, level):
    return call_groq(f"UNEB EXAMINER MODE ITEM/TASK/SCENARIO: Level: {level}, Subject: {subject}, Request: {user_query}")

def generate_bulk_revision(subject, level):
    topics = ', '.join(UNEB_CURRICULUM_MAP[subject][level])
    return call_groq(f"UNEB EXAMINER MODE: Generate 20 UNEB ITEM/TASK/SCENARIO for {level} {subject}: {topics}")

def generate_practical(subject, level, topic):
    return call_groq(f"UNEB EXAMINER MODE: Generate FULL NCDC {level} {subject} practical with method, apparatus, results table for: {topic}")

def generate_lesson_plan(subject, level, topic, duration):
    return call_groq(f"SMART MODE: Generate NCDC {duration} min lesson plan for {level} {subject} on {topic}")

def generate_report_card(student_data):
    return call_groq(f"SMART MODE: Generate NCDC Report Card for: {student_data}")

def display_with_pdf(content, name):
    st.markdown(content)
    for f in re.findall(r'\$(.*?)\$', content): st.latex(f)
    pdf = create_pdf(content, name)
    st.download_button("📥 Download PDF", pdf, f"{name}.pdf", key=f"dl_{name}_{time.time()}")

def text_to_speech(text):
    tts = gTTS(text=text, lang='en'); fp = io.BytesIO(); tts.write_to_fp(fp)
    b64 = base64.b64encode(fp.getvalue()).decode()
    st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)

# ============ 6. STUDENT PORTAL ============
def show_student_portal():
    st.header("📚 Student Portal - S1 to S6 - NCDC PRO MODE")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tab1, tab2, tab3 = st.tabs(["🔍 Smart Search + Solver", "📖 Learn Topic", "🖼️ Diagram Generator"])

    with tab1:
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="search_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="search_level")
        ask_q = st.text_area("Ask anything: 'Solve: A car moves 100m in 5s. Find speed' OR 'Explain osmosis'")
        mic_recorder(key="voice")
        if st.button("Ask AI Brain", type="primary") and ask_q:
            ans = ask_smart_brain(ask_q, subject, level, "General"); display_with_pdf(ans, "Answer")
            if st.checkbox("🔊 Listen"): text_to_speech(ans[:500])

    with tab2:
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="learn_subj")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="learn_level")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject2][level2], key="learn_topic")
        mode = st.radio("Mode", ["📖 Theory", "🧠 AOI", "🧪 Practicals Lab", "📝 UNEB Quiz Mode", "📚 Bulk Revision"])
        if mode == "📖 Theory" and st.button("Teach Me"): raw = ask_smart_brain(f"Teach {topic2} step by step with examples", subject2, level2, topic2); display_with_pdf(raw, "Theory")
        elif mode == "🧠 AOI" and st.button("Generate AOI"): raw = ask_smart_brain(f"Design AOI project for {topic2} in Uganda with materials", subject2, level2, topic2); display_with_pdf(raw, "AOI")
        elif mode == "🧪 Practicals Lab":
            prac = st.selectbox("Select Practical", PRACTICAL_TOPICS.get(subject2,{}).get(level2,["No practicals"]))
            if st.button("Generate Practical"): report = generate_practical(subject2,level2,prac); display_with_pdf(report, "Practical")
        elif mode == "📝 UNEB Quiz Mode" and st.button("Generate 10 UNEB ITEMS"): quiz = generate_exam_items(f"Generate 10 UNEB ITEM/TASK/SCENARIO on {topic2}", subject2, level2); display_with_pdf(quiz, "Quiz")
        elif mode == "📚 Bulk Revision" and st.button("Generate 20 UNEB ITEMS"): bulk = generate_bulk_revision(subject2, level2); display_with_pdf(bulk, "Bulk")

    with tab3:
        st.header("🖼️ UNEB Diagram Generator - Scaled")
        subject3 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="svg_subj")
        level3 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="svg_level")
        topic3 = st.text_input("Describe Diagram", "Draw ray diagram of refraction from Air to Glass S2 Physics")
        if st.button("Generate Diagram", type="primary"):
            with st.spinner("AI is designing diagram..."):
                svg_json = generate_diagram(topic3, subject3, level3)
            if svg_json: st.markdown(render_universal_svg(svg_json), unsafe_allow_html=True)
            else: st.error("Failed to generate diagram. Try: 'Draw Carbon Cycle S2 Biology'")

# ============ 7. ADMIN PORTAL - NO JSON SHOWN ============
def show_admin_portal():
    st.header("🏫 Admin/Teacher Portal PRO")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    TAB_NAMES = ["Admin Dashboard", "UNEB Paper Generator", "Lesson Plan + SOW", "Single Report Card", "BULK EXAMS GENERATOR", "Performance Analytics", "Student Management", "Question Bank Manager", "Curriculum Planner"]
    selected = option_menu(None, TAB_NAMES, orientation="horizontal")
    logs = load_logs(); df_logs = pd.DataFrame(logs) if logs else pd.DataFrame()

    if selected == "Admin Dashboard": col1,col2,col3 = st.columns(3); col1.metric("Total Activities", len(logs)); col2.metric("Flagged", len([l for l in logs if l.get('flagged')])); col3.metric("Users", len(set([l['user'] for l in logs])) if logs else 0); st.dataframe(logs[-50:])
    elif selected == "UNEB Paper Generator":
        s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys())); l = st.selectbox("Class", [f"S{i}" for i in range(1,7)]); t = st.text_input("Topic"); n = st.slider("Questions",5,50,20)
        if st.button("Generate UNEB Paper"): display_with_pdf(generate_exam_items(f"Generate {n} UNEB ITEM/TASK/SCENARIO on {t}", s, l), "UNEB_Test")
    elif selected == "Lesson Plan + SOW": s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys())); l = st.selectbox("Class", [f"S{i}" for i in range(1,7)]); t = st.text_input("Topic"); d = st.number_input("Minutes",40,120,80); [display_with_pdf(generate_lesson_plan(s,l,t,d), "LessonPlan") if st.button("Generate") else None]
    elif selected == "Single Report Card": name = st.text_input("Name"); scores = {sub: st.number_input(sub,0,100) for sub in ["Math","English","Science"]}; [display_with_pdf(generate_report_card(f"Name: {name}\n{scores}"), "Report") if st.button("Generate") else None]
    elif selected == "BULK EXAMS GENERATOR": s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys())); l = st.selectbox("Class", [f"S{i}" for i in range(1,7)]); [display_with_pdf(generate_bulk_revision(s,l), "Bulk") if st.button("Generate 20 UNEB ITEMS") else None]
    elif selected == "Performance Analytics": [st.line_chart(df_logs.groupby(pd.to_datetime(df_logs['timestamp']).dt.date).size()) if not df_logs.empty else st.info("No data")]
    elif selected == "Student Management":
        if "students_db" not in st.session_state: st.session_state.students_db = []
        name = st.text_input("Add Student")
        if st.button("Add"): st.session_state.students_db.append({"name": name}); st.success("Added")
        st.dataframe(st.session_state.students_db)
    elif selected == "Question Bank Manager":
        if "qbank" not in st.session_state: st.session_state.qbank = []
        q = st.text_area("Question")
        if st.button("Save"): st.session_state.qbank.append({"q": q}); st.success("Saved")
        st.dataframe(st.session_state.qbank)
    elif selected == "Curriculum Planner": s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys())); l = st.selectbox("Class", [f"S{i}" for i in range(1,7)]); [display_with_pdf("\n".join([f"Week {i+1}: {t}" for i,t in enumerate(UNEB_CURRICULUM_MAP[s][l])]), "SOW") if st.button("Generate SOW") else None]

# ============ 8. MAIN ROUTER ============
st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO - NCDC + UNEB EXAMINER V3.2")
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"])
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    if user_type == "Student" and password == STUDENT_PASSWORD: st.session_state["role"]="Student"; log_activity("Student", "Login", "Login"); st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD: st.session_state["role"]="Admin"; log_activity("Admin", "Login", "Login"); st.rerun()
    elif password: st.sidebar.error("Wrong password")

if st.session_state.get("role") == "Admin": show_admin_portal()
elif st.session_state.get("role") == "Student": show_student_portal()
else: st.info("Please login to continue")
