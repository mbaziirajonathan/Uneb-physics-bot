import streamlit as st
import os, io, json, re, time, ast
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from groq import Groq, RateLimitError
import pandas as pd
import matplotlib
matplotlib.use('Agg') # CRITICAL: Prevents backend crashes on Streamlit Cloud
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Rectangle, Ellipse, FancyArrow

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
QBANK_FILE = "qbank.json"
AI_QBANK_FILE = "ai_qbank.json"
STUDENTS_FILE = "students.json"
CONTACT = "256751040731"

### DUAL ENGINE ###
AI_MODEL_SMART = "llama-3.3-70b-versatile"
AI_MODEL_INSTANT = "llama-3.2-3b-preview"
st.sidebar.warning(f"⚠️ LEGAL NOTICE: DIGITAL UNEB TUTOR 2026 PRO V3.9.8\nNCDC + UNEB EXAMINER MODE + SAFE RENDER ENGINE\n📞 {CONTACT}")

### 3-SHOT EXAMPLES ###
SHOT_1_CELL = '''fig, ax = plt.subplots(figsize=(9,9)); ax.set_xlim(0,1); ax.set_ylim(0,1)
ax.add_patch(Rectangle((0.05,0.05), 0.9, 0.9, fill=False, linewidth=3))
ax.add_patch(Circle((0.5,0.5), 0.12, color='#ffcdd2'))
ax.text(0.5,0.5,'1. Nucleus', ha='center', bbox=dict(boxstyle='round', facecolor='yellow'))
ax.annotate('2. Cell Wall', xy=(0.05,0.5), xytext=(0.02,0.6), arrowprops=dict(arrowstyle='->'))
ax.set_title('Plant Cell - S1 Biology'); ax.axis('off')
plt.savefig('diagram.png', dpi=300, bbox_inches='tight'); plt.close()'''

SYSTEM_SMART = f"""You are DIGITAL UNEB TUTOR 2026 PRO. Senior NCDC Examiner.
OUTPUT ONLY PYTHON CODE. NO EXPLANATIONS. NO MARKDOWN.
EXAMPLE TO COPY: {SHOT_1_CELL}
STRICT RULES:
1. Use only: Circle, Rectangle, Ellipse, FancyArrow
2. Must have: plt.subplots, ax.set_xlim(0,1), ax.set_ylim(0,1), Title, 5 numbered labels with yellow bbox
3. End with: plt.savefig('diagram.png', dpi=300, bbox_inches='tight') plt.close()
4. ax.axis('off')"""

SYSTEM_INSTANT = """OUTPUT ONLY PYTHON CODE. NO TEXT.
RULES: Use Circle Rectangle. 3 labels. Title. Save 'diagram.png' dpi 200. ax.axis('off')"""

### DATABASES - UNCHANGED ###
def load_db(file): return json.load(open(file,"r", encoding="utf-8")) if os.path.exists(file) else []
def save_db(file,data): json.dump(data,open(file,"w", encoding="utf-8"),indent=2)
if "students_db" not in st.session_state: st.session_state.students_db = load_db(STUDENTS_FILE)

UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Number Bases"], "S2": ["Angles"], "S3": ["Vectors"], "S4": ["Circle Geometry"], "S5": ["Differentiation"], "S6": ["Mechanics"]},
    "Physics": {"S1": ["Forces"], "S2": ["Electricity I"], "S3": ["Magnetism"], "S4": ["Electronics"], "S5": ["Optics"], "S6": ["Electric Fields"]},
    "Chemistry": {"S1": ["Atoms"], "S2": ["Acids Alkalis"], "S3": ["Bonding"], "S4": ["REDOX"], "S5": ["Kinetics"], "S6": ["Electrochemistry"]},
    "Biology": {"S1": ["Cells"], "S2": ["Respiration"], "S3": ["Genetics I"], "S4": ["Photosynthesis"], "S5": ["Cell Biology"], "S6": ["Hormones"]},
    "ICT": {"S1": ["Computer Basics"],"S2": ["Word Processing"],"S3": ["Spreadsheets"],"S4": ["Internet"],"S5": ["Programming Python"],"S6": ["Web Design"]},
    "Geography": {"S1": ["Map Reading"],"S2": ["Climate"],"S3": ["Rivers"],"S4": ["Population"],"S5": ["Industries"],"S6": ["GIS"]},
    "History": {"S1": ["Early Man"],"S2": ["Kingdoms"],"S3": ["Colonialism"],"S4": ["Independence"],"S5": ["World Wars"],"S6": ["Cold War"]},
    "CRE": {"S1": ["Creation"],"S2": ["Prophets"],"S3": ["Jesus"],"S4": ["Church"],"S5": ["Ethics"],"S6": ["Comparative"]},
    "IRE": {"S1": ["Tawheed"],"S2": ["Prophets"],"S3": ["Quran"],"S4": ["Hadith"],"S5": ["Fiqh"],"S6": ["History"]},
    "Literature": {"S1": ["Poetry"],"S2": ["Drama"],"S3": ["Novel"],"S4": ["Prose"],"S5": ["Shakespeare"],"S6": ["African Lit"]},
    "Commerce": {"S1": ["Business"],"S2": ["Trade"],"S3": ["Banking"],"S4": ["Insurance"],"S5": ["Marketing"],"S6": ["Entrepreneurship"]},
    "Economics": {"S1": ["Scarcity"],"S2": ["Demand"],"S3": ["Money"],"S4": ["Trade"],"S5": ["National Income"],"S6": ["Development"]},
    "Agriculture": {"S1": ["Soil"],"S2": ["Crops"],"S3": ["Livestock"],"S4": ["Tools"],"S5": ["Records"],"S6": ["Agribusiness"]},
    "Art": {"S1": ["Drawing"],"S2": ["Painting"],"S3": ["Sculpture"],"S4": ["Design"],"S5": ["Craft"],"S6": ["Art History"]}
}

PRACTICAL_DATABASE = {"Physics": {"S1-S4": {"Ohm's Law": {"objective": "Verify Ohm's Law", "apparatus": "Cell", "procedure": "Connect", "questions": ["State law"], "safety": "No short"}}}}

### CORE FUNCTIONS ###
def load_logs(): return json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []
def save_log(entry): logs = load_logs(); logs.append(entry); json.dump(logs, open(LOG_FILE,"w"))
def log_activity(user_type, action, details): save_log({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user_type, "action": action, "details": details})
def create_pdf(content, title):
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); p.setFont("Helvetica-Bold", 14); p.drawString(50,800,title); y=770; p.setFont("Helvetica", 10)
    for i,line in enumerate(content.split('\n')[:80]): p.drawString(50,y-(i*14),line[:95])
    p.save(); buffer.seek(0); return buffer

### FIX 1: RETRY + TOKEN SAFE CALL ###
def call_groq_dual(user_prompt, mode="Smart", retries=2):
    system = SYSTEM_SMART if mode=="Smart" else SYSTEM_INSTANT
    model = AI_MODEL_SMART if mode=="Smart" else AI_MODEL_INSTANT
    tokens = 3500 if mode=="Smart" else 700

    for i in range(retries):
        try:
            res = client.chat.completions.create(model=model, messages=[{"role":"system","content":system},{"role":"user","content":user_prompt}], max_tokens=tokens, temperature=0.1)
            return res.choices[0].message.content
        except RateLimitError:
            time.sleep(2)
            continue
        except Exception as e:
            if i == retries-1: return f"GROQ_ERROR: {e}"
    return "GROQ_ERROR: Failed after retries"

### FIX 2: CODE EXTRACTOR + VALIDATOR ###
def extract_code(raw):
    if not raw or "GROQ_ERROR" in raw: return raw
    # Remove markdown
    code = re.sub(r'```python|```', '', raw).strip()
    # Take only from first import/fig to end
    match = re.search(r'(from matplotlib|import matplotlib|fig, ax = plt).*', code, re.DOTALL)
    return match.group(0) if match else code

def validate_code_syntax(code):
    try: ast.parse(code); return True
    except SyntaxError as e: return f"SyntaxError line {e.lineno}: {e.msg}"

### FIX 3: SAFE RENDER ENGINE ###
def auto_render_pixel_diagram(topic, subject, level, mode="Smart"):
    st.info(f"🤖 Running {mode} Engine...")

    prompt = f"Task: Draw '{topic}' for {level} {subject}. Use matplotlib. 5 labels with arrows. Save diagram.png"
    raw_code = call_groq_dual(prompt, mode)

    if "GROQ_ERROR" in raw_code: return raw_code

    code = extract_code(raw_code)

    # Force header
    header = "from matplotlib.patches import Circle, Rectangle, Ellipse, FancyArrow\nimport matplotlib.pyplot as plt\nimport numpy as np\n"
    code = header + code
    code = code.replace("/mnt/data/diagram.png", "diagram.png")

    # Validate before exec
    valid = validate_code_syntax(code)
    if valid!= True: return f"ERROR: {valid}"

    with st.expander(f"View {mode} AI Code"):
        st.code(code, language="python")

    try:
        plt.close('all') # Clear previous plots
        safe_globals = {"plt": plt, "np": np, "Circle": Circle, "Rectangle": Rectangle, "Ellipse": Ellipse, "FancyArrow": FancyArrow}
        exec(code, {"__builtins__": {}}, safe_globals) # Sandbox exec

        if os.path.exists("diagram.png"):
            return "diagram.png"
        else:
            return "ERROR: plt.savefig was not called by AI"

    except Exception as e:
        return f"ERROR: Runtime {type(e).__name__}: {e}"

def generate_practical(subject, level, prac_name):
    level_group = "S1-S4" if int(level[1]) <= 4 else "S5-S6"
    data = PRACTICAL_DATABASE.get(subject,{}).get(level_group,{}).get(prac_name,{})
    if not data: return "Practical not found"
    return call_groq_dual(f"Expand to UNEB report: {data} for {subject} {level}", "Smart")

def display_with_pdf(content, name):
    st.markdown(content)
    for f in re.findall(r'\$(.*?)\$', content): st.latex(f)
    pdf = create_pdf(content, name); st.download_button("📥 Download PDF", pdf, f"{name}.pdf", key=f"dl_{name}_{time.time()}")

### PORTALS - UNCHANGED ###
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
            ans = call_groq_dual(f"Use Chain of Thought: {ask_q} for {level} {subject}", "Smart")
            display_with_pdf(ans, "Answer")

    with tab2:
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="learn_subj")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="learn_level")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject2][level2], key="learn_topic")
        mode = st.radio("Mode", ["📖 Theory", "🧠 AOI", "🧪 Practicals Lab", "📝 UNEB Quiz Mode", "📚 Bulk Revision"])

        if mode == "📖 Theory" and st.button("Teach Me"):
            raw = call_groq_dual(f"Teach {topic2} step by step for {level2} {subject2}", "Smart")
            display_with_pdf(raw, "Theory")
        elif mode == "🧠 AOI" and st.button("Generate AOI"):
            aoi = call_groq_dual(f"Generate NCDC AOI for {level2} {subject2} topic: {topic2}", "Smart")
            display_with_pdf(aoi, "AOI")
        elif mode == "🧪 Practicals Lab":
            prac_list = list(PRACTICAL_DATABASE.get(subject2,{}).get("S1-S4",{}).keys())
            prac = st.selectbox("Select Practical", prac_list if prac_list else ["None"])
            if st.button("Generate Practical"):
                report = generate_practical(subject2,level2,prac)
                display_with_pdf(report, "Practical")
        elif mode == "📝 UNEB Quiz Mode" and st.button("Generate Quiz"):
            quiz = call_groq_dual(f"Generate 10 UNEB questions on {topic2} for {level2} {subject2}", "Smart")
            display_with_pdf(quiz, "Quiz")
        elif mode == "📚 Bulk Revision" and st.button("Generate Revision"):
            rev = call_groq_dual(f"Generate revision + 20 questions for {topic2} {level2} {subject2}", "Smart")
            display_with_pdf(rev, "Revision")

    with tab3:
        st.header("🎨 Diagram Generator - V3.9.8 SAFE RENDER")
        subject3 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="svg_subj")
        level3 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="svg_level")
        topic3 = st.text_input("Describe Diagram:", "Draw Human Heart S4 Biology")
        diagram_mode = st.radio("Choose Output Mode", ["2. HD Pixel [AI Smart 70B - Perfect Labels]", "3. HD Pixel [AI Instant 3B - Fast]"])

        if st.button("Generate Diagram", type="primary"):
            log_activity("Student", "Generate Diagram", topic3)
            m = "Smart" if "Smart" in diagram_mode else "Instant"
            img_path = auto_render_pixel_diagram(topic3, subject3, level3, m)
            if "ERROR" in str(img_path) or "GROQ_ERROR" in str(img_path): st.error(f"Rendering failed: {img_path}")
            else:
                st.image(img_path, caption=f"HD: {topic3}", use_container_width=True)
                with open(img_path, "rb") as file: st.download_button("📥 Download HD PNG", file, f"{topic3}.png")

def show_admin_portal():
    st.header("🏫 Admin Portal - V3.9.8")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tab1, tab2, tab3 = st.tabs(["📊 Analytics", "📖 Curriculum Manager", "🤖 AI QBank Generator"])
    with tab1:
        logs = load_logs()
        st.metric("Total Logs", len(logs))
        if logs: st.dataframe(pd.DataFrame(logs))
    with tab2:
        st.subheader("NCDC Curriculum")
        subj = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)])
        st.write(UNEB_CURRICULUM_MAP[subj][level])
    with tab3:
        st.subheader("AI Generate QBank")
        subj = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="qgen_subj")
        lvl = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="qgen_lvl")
        if st.button("Generate 20 Questions"):
            res = call_groq_dual(f"Generate 20 UNEB MCQ for {lvl} {subj}. Return JSON", "Smart")
            try: save_db(AI_QBANK_FILE, json.loads(res)); st.success("Saved")
            except: st.error("Bad JSON"); st.code(res)

st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO - V3.9.8")
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"])
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    if user_type == "Student" and password == STUDENT_PASSWORD: st.session_state["role"] = "Student"; st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD: st.session_state["role"] = "Admin"; st.rerun()
    elif password: st.sidebar.error("Wrong password")

if st.session_state.get("role") == "Admin": show_admin_portal()
elif st.session_state.get("role") == "Student": show_student_portal()
else: st.info("Please login to continue")
