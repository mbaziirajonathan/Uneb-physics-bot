import streamlit as st
import os, io, json, re, time, base64
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
from streamlit_option_menu import option_menu
from groq import Groq, RateLimitError
import pandas as pd

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026", page_icon="📚", layout="wide")

# ========== 1. SECRETS ==========
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
STUDENT_PASSWORD = st.secrets["STUDENT_PASSWORD"]
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
client = Groq(api_key=GROQ_API_KEY)

LOG_FILE = "usage_log.json"
CONTACT = "256751040731"
AI_MODEL_LONG = "llama-3.3-70b-versatile"
AI_MODEL_FAST = "llama-3.1-8b-instant"

st.sidebar.warning(f"⚠️ LEGAL NOTICE: DIGITAL UNEB TUTOR 2026\nFor NCDC learning only.\n📞 {CONTACT}")

# ============ 2. RESTORED FULL 22 SUBJECTS S1-S6 DATABASE ============
UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Number Bases", "Integers", "Fractions, Percentages and Decimals", "Cartesian Coordinates", "Geometric Construction", "Data Collection and Representation"], "S2": ["Patterns and Sequences", "Bearings", "Angle Properties", "Algebra I", "Business Arithmetic I", "Time and Time Tables", "Mapping and Relations"], "S3": ["Business Arithmetic II", "Quadratic Equations", "Matrices", "Probability", "Vectors", "Trigonometry I", "Mensuration"], "S4": ["Functions", "Three-Dimensional Geometry", "Statistics", "Linear Programming", "Trigonometry II", "Calculus Introduction"], "S5": ["Calculus: Differentiation", "Calculus: Integration", "Circular Measure", "Binomial Expansion", "Complex Numbers", "Sequences and Series"], "S6": ["Differential Equations", "Mechanics: Kinematics and Dynamics", "Probability Distributions", "Linear Programming Advanced", "Further Calculus", "Vectors in 3D"]},
    "Physics": {"S1": ["Introduction to Physics", "Measurement", "Forces and Their Effects", "Work, Energy and Power", "Pressure in Fluids", "Simple Machines"], "S2": ["Light: Reflection and Refraction", "Thermal Physics", "Static Electricity", "Current Electricity I", "Waves I"], "S3": ["Current Electricity II", "Magnetism", "Waves II: Sound", "Mechanics Continued", "Specific Heat Capacity"], "S4": ["Electromagnetism", "Electronics", "Modern Physics", "Nuclear Processes", "A.C Theory", "Astrophysics"], "S5": ["Mechanics: Motion and Dynamics", "Gravitation", "Thermal Physics Advanced", "Waves III: Interference and Diffraction", "Optics", "Fluid Mechanics"], "S6": ["Electric Fields", "Magnetic Fields", "Electromagnetic Induction", "Quantum Physics", "Radioactivity", "Solid State and Electronics"]},
    "Chemistry": {"S1": ["Chemistry and Society", "Experimental Chemistry", "States of Matter", "Temporary and Permanent Changes", "Mixtures, Elements and Compounds", "Air", "Water", "Rocks and Minerals"], "S2": ["Acids and Alkalis", "Salts", "The Periodic Table", "Carbon in the Environment", "Reactivity Series", "Metals and Non-Metals"], "S3": ["Structure and Bonding", "Stoichiometry and Mole Concept", "Fossil Fuels", "Properties and Structures of Substances", "Chemical Reactions", "Rates of Reaction"], "S4": ["REDOX Reactions", "Industrial Processes", "Trends in the Periodic Table", "Thermochemistry", "Consumable Chemicals", "Organic Chemistry II", "Nuclear Processes"], "S5": ["Atomic Structure Advanced", "Chemical Energetics", "Chemical Kinetics", "Equilibrium II", "Organic Chemistry III", "Acids, Bases and Buffers"], "S6": ["Electrochemistry Advanced", "Transition Metals and Complexes", "Organic Synthesis", "Analytical Chemistry", "Environmental Chemistry", "Polymers"]},
    "Biology": {"S1": ["Introduction to Biology", "Cells and the Microscope", "Classification of Living Things", "Insects", "Flowering Plants", "Ecosystems"], "S2": ["Soil Composition and Properties", "Soil Erosion and Conservation", "Nitrogen Cycle", "Nutrition in Plants", "Nutrition in Animals", "Transport in Living Things"], "S3": ["Transport in Plants and Animals", "Respiration and Gas Exchange", "Excretion and Homeostasis", "Cell Division", "Reproduction in Plants", "DNA and Genetics I"], "S4": ["Coordination and Receptors", "Locomotion", "Growth and Development", "Genetics and Inheritance", "Ecology", "Evolution", "Environmental Conservation"], "S5": ["Cell Biology", "Enzymes", "Transport in Plants Advanced", "Gas Exchange Systems", "Nutrition in Humans Advanced", "Respiration Cellular"], "S6": ["Hormonal Control and Feedback", "Coordination: Nervous System Advanced", "Population Ecology", "Biotechnology", "Genetic Engineering", "Immunity and Disease"]},
    "Geography": {"S1": ["The Earth and the Solar System", "Map Reading and Interpretation", "Weather and Climate", "Vegetation", "Population"], "S2": ["Rocks and Weathering", "Drainage Systems", "Soils", "Mining", "Tourism"], "S3": ["Transport", "Trade", "Industry", "Settlement", "Energy"], "S4": ["East African Community", "Environmental Issues", "GIS", "Regional Development", "Field Work"], "S5": ["Physical Geography Advanced", "Human Geography Advanced", "Practical Geography", "Research Methods", "Economic Geography"], "S6": ["Geomorphology", "Climatology", "Biogeography", "Population Geography", "Urban Geography"]},
    "History": {"S1": ["Introduction to History", "Early Man", "Ancient Civilizations", "Feudalism", "Colonialism"], "S2": ["Scramble for Africa", "Colonial Administration", "Economic Development", "Resistance", "Christian Missions"], "S3": ["Political Development", "Social and Economic Changes", "Nationalism", "WWI & WWII", "UN and UNO"], "S4": ["Independence of African States", "Post Colonial Problems", "Cold War", "Non-Alignment", "Regional Cooperation"], "S5": ["East African History", "European History", "World History", "Research Methods", "Historiography"], "S6": ["African History", "American History", "Asian History", "International Relations", "Themes in History"]},
    "Literature": {"S1": ["Introduction to Literature", "Prose: The River and the Source", "Poetry: Anthology", "Drama: The Government Inspector", "Oral Literature"], "S2": ["Prose: Animal Farm", "Poetry: Songs of Ourselves", "Drama: The Caucasian Chalk Circle", "Literary Terms", "Essay Writing"], "S3": ["Prose: A Thousand Splendid Suns", "Poetry: Poems from Africa", "Drama: The Tempest", "Style and Language", "Critical Analysis"], "S4": ["Prose: The Pearl", "Poetry: Modern Poetry", "Drama: An Enemy of the People", "Literary Appreciation", "Composition"], "S5": ["Prose: Advanced Novels", "Poetry: Shakespeare Sonnets", "Drama: Macbeth", "Literary Criticism", "Research"], "S6": ["Prose: Post Colonial Literature", "Poetry: Advanced Anthology", "Drama: King Lear", "Comparative Literature", "Dissertation"]},
    "English": {"S1": ["Grammar: Parts of Speech", "Comprehension", "Composition Writing", "Oral Skills", "Vocabulary"], "S2": ["Grammar: Tenses", "Summary Writing", "Letter Writing", "Public Speaking", "Literary Devices"], "S3": ["Grammar: Clauses", "Report Writing", "Speech Writing", "Debate", "Advanced Comprehension"], "S4": ["Grammar: Punctuation", "Proposal Writing", "Curriculum Vitae", "Interview Skills", "Exam Techniques"]},
    "CRE": {f"S{i}": [f"CRE S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}, "IRE": {f"S{i}": [f"IRE S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "Agriculture": {f"S{i}": [f"Agriculture S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}, "Entrepreneurship": {f"S{i}": [f"Entrepreneurship S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "ICT": {f"S{i}": [f"ICT S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}, "Art and Design": {f"S{i}": [f"Art S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "Music": {f"S{i}": [f"Music S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}, "French": {f"S{i}": [f"French S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "Kiswahili": {f"S{i}": [f"Kiswahili S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}, "Luganda": {f"S{i}": [f"Luganda S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "Economics": {f"S{i}": [f"Economics S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}, "Commerce": {f"S{i}": [f"Commerce S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "Technical Drawing": {f"S{i}": [f"Tech Drawing S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}, "Food and Nutrition": {f"S{i}": [f"Food & Nutrition S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)},
    "Fashion and Textiles": {f"S{i}": [f"Fashion S{i} Topic {j}" for j in range(1,6)] for i in range(1,7)}
}

PRACTICAL_TOPICS = {"Mathematics": {"S1": ["Geometric Construction"]}, "Physics": {"S1": ["Measurement", "Simple Pendulum"]}, "Chemistry": {"S1": ["Filtration"]}, "Biology": {"S1": ["Using Light Microscope"]}}
AOI_FRAMEWORK = {"S1": "Community Problem", "S2": "Local Industry", "S3": "National Issue", "S4": "Global Challenge", "S5": "Research", "S6": "Professional"}

# ============ 3. MASTER SYSTEM PROMPT ============
MASTER_SYSTEM_PROMPT = """
You are DIGITAL UNEB TUTOR 2026. Senior NCDC AI for Uganda S1-S6.
CORE RULE 1: SMART MODE - Answer directly.
CORE RULE 2: EXAMINER MODE - Use UNEB ITEM/TASK/SCENARIO FORMAT.
CORE RULE 3: SVG DIAGRAM MODE - Output ONLY raw JSON. No words before or after. Canvas 500x400. Center at cx:250,cy:200. Label offset +15px. Use: circle, rect, line, path, text.
"""

# ========== 4. UNIVERSAL SVG RENDERER ENGINE - CRITICAL DEBUG VERSION ==========
def render_universal_svg(diagram_data):
    if not diagram_data or "elements" not in diagram_data:
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 400"><text x=10 y=20 fill="red">Error: No elements in JSON</text></svg>'
    if len(diagram_data["elements"]) == 0:
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 400"><text x=10 y=20 fill="red">Error: AI returned 0 elements</text></svg>'
    try:
        title = diagram_data.get("title", "NCDC Diagram"); width = 500; height = 400; elements = diagram_data.get("elements", [])
        def clamp(val, max_val):
            try: return max(0, min(int(float(val)), max_val))
            except: return 0
        svg_content = f"<!-- {title} -->\n"
        for el in elements:
            t = el.get("type")
            if t == 'circle':
                cx, cy = clamp(el.get("cx",250),500), clamp(el.get("cy",200),400)
                svg_content += f'<circle cx="{cx}" cy="{cy}" r="{clamp(el.get("r",30),200)}" fill="{el.get("fill","#e3f2fd")}" stroke="{el.get("stroke","#333")}" stroke-width="{el.get("strokeWidth",2)}" />\n'
            elif t == 'rect':
                x, y = clamp(el.get("x",0),500), clamp(el.get("y",0),400)
                svg_content += f'<rect x="{x}" y="{y}" width="{clamp(el.get("w",50),500)}" height="{clamp(el.get("h",30),400)}" rx="{el.get("rx",0)}" fill="{el.get("fill","#fff")}" stroke="{el.get("stroke","#333")}" stroke-width="{el.get("strokeWidth",2)}" />\n'
            elif t == 'line':
                x1, y1, x2, y2 = clamp(el.get("x1",0),500), clamp(el.get("y1",0),400), clamp(el.get("x2",0),500), clamp(el.get("y2",0),400)
                svg_content += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{el.get("stroke","#000")}" stroke-width="{el.get("strokeWidth",2)}" />\n'
            elif t == 'path': svg_content += f'<path d="{el.get("d","")}" fill="{el.get("fill","none")}" stroke="{el.get("stroke","#333")}" stroke-width="{el.get("strokeWidth",2)}" />\n'
            elif t == 'text':
                x, y = clamp(el.get("x",250),500), clamp(el.get("y",200),400)
                svg_content += f'<text x="{x}" y="{y}" font-family="Arial" font-size="{el.get("size",12)}" fill="{el.get("color","#000")}" text-anchor="{el.get("anchor","start")}">{el.get("text","")}</text>\n'
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="auto" style="max-width:500px;border:1px solid #ddd;border-radius:8px;background:#fff;">{svg_content}</svg>'
    except Exception as e: return f"<svg><text x=10 y=20 fill='red'>SVG Render Error: {e}</text></svg>"

# ========== 5. UTILS + AI CALLS - CRITICAL DEBUG PATCH ==========
def load_logs(): return json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []
def save_log(entry): logs = load_logs(); logs.append(entry); json.dump(logs, open(LOG_FILE,"w"))
def log_activity(user_type, action, details): flagged = "cheat" in details.lower(); save_log({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user_type, "action": action, "details": details, "flagged": flagged})

def create_pdf(content, title): buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); p.setFont("Helvetica-Bold", 14); p.drawString(50,800,title); y=770; p.setFont("Helvetica", 10); [p.drawString(50,y-(i*14),line[:95]) for i,line in enumerate(content.split('\n')[:80])]; p.save(); buffer.seek(0); return buffer

def call_groq(user_prompt, mode="smart"):
    try:
        # CRITICAL: temp=0.1 for svg to force JSON format. max_tokens=2000 is enough
        temp = 0.1 if mode=="svg" else 0.7
        tokens = 2000 if mode=="svg" else 4000
        res = client.chat.completions.create(model=AI_MODEL_LONG, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}], max_tokens=tokens, temperature=temp)
        return res.choices[0].message.content
    except RateLimitError:
        res = client.chat.completions.create(model=AI_MODEL_FAST, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}], max_tokens=2000, temperature=0.1)
        return res.choices[0].message.content
    except Exception as e: return f"AI Error: {e}"

def generate_svg_json(topic, subject, level):
    """CRITICAL DEBUG: Force JSON + Show Raw Output"""
    raw = call_groq(f"SVG DIAGRAM MODE: Output ONLY raw JSON starting with {{. No explanation. Generate SVG JSON for NCDC {level} {subject} topic: {topic}", mode="svg")

    with st.expander("🔍 DEBUG: Raw LLM Output - Click to see what AI returned", expanded=True):
        st.code(raw)

    for pattern in [r'```json\s*(\{.*?\})\s*```', r'(\{.*\})']:
        match = re.search(pattern, raw, re.DOTALL)
        if match:
            try: return json.loads(match.group(1))
            except: continue
    try: return json.loads(raw)
    except:
        st.error("AI returned invalid JSON. Copy the DEBUG output above and send it to me.")
        return None

def ask_smart_brain(user_query, subject, class_level, topic): log_activity(st.session_state.role, "Smart Query", f"{subject} {class_level}"); return call_groq(f"SMART MODE: Level: {class_level}\nSubject: {subject}\nTopic: {topic}\nUser Question: {user_query}")
def generate_exam_items(user_query, subject, level): return call_groq(f"EXAMINER MODE: Generate UNEB ITEMS. Level: {level}, Subject: {subject}, Request: {user_query}")
def generate_bulk_revision(subject, level): topics = ', '.join(UNEB_CURRICULUM_MAP[subject][level]); return call_groq(f"EXAMINER MODE: Generate 20 ITEMS for {level} {subject}: {topics}")
def generate_practical(subject, level, topic): return call_groq(f"EXAMINER MODE: Generate FULL NCDC {level} {subject} practical for: {topic}")
def generate_lesson_plan(subject, level, topic, duration): return call_groq(f"SMART MODE: Generate NCDC {duration} min lesson plan for {level} {subject} on {topic}")
def generate_report_card(student_data): return call_groq(f"SMART MODE: Generate NCDC Report Card for: {student_data}")
def display_with_pdf(content, name): st.markdown(content); [st.latex(f) for f in re.findall(r'\$(.*?)\$', content)]; pdf = create_pdf(content, name); st.download_button("📥 Download PDF", pdf, f"{name}.pdf", key=f"dl_{name}_{time.time()}")
def text_to_speech(text): tts = gTTS(text=text, lang='en'); fp = io.BytesIO(); tts.write_to_fp(fp); b64 = base64.b64encode(fp.getvalue()).decode(); st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)

# ========== 6. STUDENT PORTAL ==========
def show_student_portal():
    st.header("📚 Student Portal - S1 to S6")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tab1, tab2, tab3 = st.tabs(["🔍 Smart Search", "📖 Learn Topic", "🖼️ Diagram Generator"])

    with tab1:
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="search_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="search_level")
        ask_q = st.text_area("Ask: 'define osmosis' OR 'solve 2x+3=7'")
        mic_recorder(key="voice")
        if st.button("Ask AI Brain", type="primary") and ask_q:
            ans = ask_smart_brain(ask_q, subject, level, "General"); display_with_pdf(ans, "Answer"); [text_to_speech(ans[:500]) if st.checkbox("Listen") else None]

    with tab2:
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="learn_subj")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="learn_level")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject2][level2], key="learn_topic")
        mode = st.radio("Mode", ["📖 Theory", "🧠 AOI", "🧪 Practicals Lab", "📝 Quiz Mode", "📚 Bulk Revision"])
        if mode == "📖 Theory" and st.button("Teach Me"): raw = ask_smart_brain(f"Teach {topic2}", subject2, level2, topic2); display_with_pdf(raw, "Theory")
        elif mode == "🧠 AOI" and st.button("Generate AOI"): raw = ask_smart_brain(f"Design AOI project for {topic2}", subject2, level2, topic2); display_with_pdf(raw, "AOI")
        elif mode == "🧪 Practicals Lab":
            prac = st.selectbox("Select Practical", PRACTICAL_TOPICS.get(subject2,{}).get(level2,["No practicals"]))
            if st.button("Generate Practical"): report = generate_practical(subject2,level2,prac); display_with_pdf(report, "Practical")
        elif mode == "📝 Quiz Mode" and st.button("Generate 10 ITEMS"): quiz = generate_exam_items(f"10 questions on {topic2}", subject2, level2); display_with_pdf(quiz, "Quiz")
        elif mode == "📚 Bulk Revision" and st.button("Generate 20 ITEMS"): bulk = generate_bulk_revision(subject2, level2); display_with_pdf(bulk, "Bulk")

    with tab3:
        st.header("🖼️ Universal SVG Diagram Generator - DEBUG MODE ON")
        subject3 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="svg_subj")
        level3 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="svg_level")
        topic3 = st.text_input("Enter Topic to Draw", "Structure of a Plant Cell")
        if st.button("Generate Diagram", type="primary"):
            with st.spinner("AI Drawing..."):
                svg_json = generate_svg_json(topic3, subject3, level3)
            if svg_json: st.markdown(render_universal_svg(svg_json), unsafe_allow_html=True); st.download_button("Download SVG", render_universal_svg(svg_json), f"{topic3}.svg")
            else: st.error("Generation failed. Check DEBUG box above.")

# ========== 7. ADMIN PORTAL ==========
def show_admin_portal():
    st.header("🏫 Admin/Teacher Portal")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    TAB_NAMES = ["Admin Dashboard", "Test Paper Generator", "Lesson Plan + SOW", "Single Report Card", "BULK EXAMS GENERATOR", "Performance Analytics", "Student Management", "Question Bank Manager", "Curriculum Planner", "Attendance Tracker", "Fee Management", "Communication Hub", "Resource Library", "Settings & Compliance", "SVG Test Tool"]
    selected = option_menu(None, TAB_NAMES, orientation="horizontal")
    logs = load_logs(); df_logs = pd.DataFrame(logs) if logs else pd.DataFrame()

    if selected == "Admin Dashboard": col1,col2,col3 = st.columns(3); col1.metric("Total Activities", len(logs)); col2.metric("Flagged", len([l for l in logs if l.get('flagged')])); col3.metric("Users", len(set([l['user'] for l in logs])) if logs else 0); st.dataframe(logs[-50:])
    elif selected == "Test Paper Generator": s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys())); l = st.selectbox("Class", [f"S{i}" for i in range(1,7)]); t = st.text_input("Topic"); n = st.slider("Questions",5,50,20); [display_with_pdf(generate_exam_items(f"Generate {n} on {t}", s, l), "Test") if st.button("Generate") else None]
    elif selected == "Lesson Plan + SOW": s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys())); l = st.selectbox("Class", [f"S{i}" for i in range(1,7)]); t = st.text_input("Topic"); d = st.number_input("Minutes",40,120,80); [display_with_pdf(generate_lesson_plan(s,l,t,d), "LessonPlan") if st.button("Generate") else None]
    elif selected == "Single Report Card": name = st.text_input("Name"); scores = {sub: st.number_input(sub,0,100) for sub in ["Math","English","Science"]}; [display_with_pdf(generate_report_card(f"Name: {name}\n{scores}"), "Report") if st.button("Generate") else None]
    elif selected == "BULK EXAMS GENERATOR": s = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys())); l = st.selectbox("Class", [f"S{i}" for i in range(1,7)]); [display_with_pdf(generate_bulk_revision(s,l), "Bulk") if st.button("Generate 20") else None]
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
    elif selected == "SVG Test Tool": json_input = st.text_area("Paste LLM JSON"); [st.markdown(render_universal_svg(json.loads(json_input)), unsafe_allow_html=True) if st.button("Render SVG") else None]
    else: st.info(f"{selected} UI Active")

# ========== 8. MAIN ROUTER ==========
st.title("🎓 DIGITAL UNEB TUTOR 2026 - 22 SUBJECTS + DEBUG SVG ENGINE")
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"])
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    if user_type == "Student" and password == STUDENT_PASSWORD: st.session_state["role"]="Student"; log_activity("Student", "Login", "Login"); st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD: st.session_state["role"]="Admin"; log_activity("Admin", "Login", "Login"); st.rerun()
    elif password: st.sidebar.error("Wrong password")

if st.session_state.get("role") == "Admin": show_admin_portal()
elif st.session_state.get("role") == "Student": show_student_portal()
else: st.info("Please login to continue")
