import streamlit as st
import os, io, json, re, time, traceback
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from groq import Groq, RateLimitError
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Rectangle, Ellipse, Polygon, Arrow

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 PRO", page_icon="📚", layout="wide")

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    STUDENT_PASSWORD = st.secrets["STUDENT_PASSWORD"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("Set GROQ_API_KEY, STUDENT_PASSWORD, ADMIN_PASSWORD in Streamlit secrets")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)
CONTACT = "256751040731"
AI_MODEL_SMART = "llama-3.3-70b-versatile"
AI_MODEL_INSTANT = "llama-3.2-3b-preview"
st.sidebar.success(f"V3.9.1 FULL RESTORE\n📞 {CONTACT}")

### DATABASES RESTORED ###
LOG_FILE = "usage_log.json"
QBANK_FILE = "qbank.json"
AI_QBANK_FILE = "ai_qbank.json"
STUDENTS_FILE = "students.json"

def load_db(file): return json.load(open(file,"r")) if os.path.exists(file) else []
def save_db(file,data): json.dump(data,open(file,"w"),indent=2)

if "students_db" not in st.session_state: st.session_state.students_db = load_db(STUDENTS_FILE)
if "log" not in st.session_state: st.session_state.log = load_db(LOG_FILE)
if "qbank" not in st.session_state: st.session_state.qbank = load_db(QBANK_FILE)
if "ai_qbank" not in st.session_state: st.session_state.ai_qbank = load_db(AI_QBANK_FILE)

### FULL NCDC 2026 CURRICULUM DB - RESTORED ALL 14 SUBJECTS ###
UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Integers","Fractions","Decimals"],"S2": ["Angles","Statistics","Algebra"],"S3": ["Vectors","Matrices","Quadratic"],"S4": ["Circle Geometry","Trigonometry"],"S5": ["Differentiation","Integration"],"S6": ["Mechanics","Probability","Linear Programming"]},
    "Biology": {"S1": ["Cells","Classification"],"S2": ["Nutrition","Respiration"],"S3": ["Circulation","Excretion"],"S4": ["Photosynthesis","Ecology"],"S5": ["Cell Biology","Genetics"],"S6": ["Hormones","Evolution","Ecology"]},
    "Chemistry": {"S1": ["States of Matter"],"S2": ["Acids, Bases, Salts"],"S3": ["Bonding","Periodic Table"],"S4": ["REDOX","Mole Concept"],"S5": ["Energetics","Kinetics","Equilibrium"],"S6": ["Electrochemistry","Organic Chemistry"]},
    "Physics": {"S1": ["Forces","Motion"],"S2": ["Waves I","Light"],"S3": ["Electricity","Magnetism"],"S4": ["Electromagnetism","Electronics"],"S5": ["Optics","Nuclear Physics"],"S6": ["Fields","Mechanics","Modern Physics"]},
    "ICT": {"S1": ["Computer Basics","Hardware"],"S2": ["Word Processing"],"S3": ["Spreadsheets","Databases"],"S4": ["Internet","Networking"],"S5": ["Programming Python"],"S6": ["Web Design","Data Analysis"]},
    "Geography": {"S1": ["Map Reading"],"S2": ["Climate","Vegetation"],"S3": ["Rivers","Lakes"],"S4": ["Population","Settlement"],"S5": ["Industries","Trade"],"S6": ["GIS","Environmental Issues"]},
    "History": {"S1": ["Early Man"],"S2": ["Kingdoms of Uganda"],"S3": ["Colonialism"],"S4": ["Independence"],"S5": ["World Wars"],"S6": ["Cold War"]},
    "CRE": {"S1": ["Creation"],"S2": ["Prophets"],"S3": ["Jesus Ministry"],"S4": ["Church"],"S5": ["Ethics"],"S6": ["Comparative Religion"]},
    "IRE": {"S1": ["Tawheed"],"S2": ["Prophets"],"S3": ["Quran"],"S4": ["Hadith"],"S5": ["Fiqh"],"S6": ["Islamic History"]},
    "Literature": {"S1": ["Poetry"],"S2": ["Drama"],"S3": ["Novel"],"S4": ["Prose"],"S5": ["Shakespeare"],"S6": ["African Literature"]},
    "Commerce": {"S1": ["Business Basics"],"S2": ["Trade"],"S3": ["Banking"],"S4": ["Insurance"],"S5": ["Marketing"],"S6": ["Entrepreneurship"]},
    "Economics": {"S1": ["Scarcity"],"S2": ["Demand Supply"],"S3": ["Money"],"S4": ["Trade"],"S5": ["National Income"],"S6": ["Development"]},
    "Agriculture": {"S1": ["Soil"],"S2": ["Crops"],"S3": ["Livestock"],"S4": ["Farm Tools"],"S5": ["Farm Records"],"S6": ["Agribusiness"]},
    "Art": {"S1": ["Drawing"],"S2": ["Painting"],"S3": ["Sculpture"],"S4": ["Design"],"S5": ["Craft"],"S6": ["Art History"]}
}

### 1-SHOT EXAMPLE ###
PERFECT_EXAMPLE = '''fig, ax = plt.subplots(figsize=(8,8)); ax.set_xlim(0,1); ax.set_ylim(0,1)
ax.add_patch(Rectangle((0.05,0.05), 0.9, 0.9, fill=False, linewidth=3))
ax.add_patch(Circle((0.5,0.5), 0.12, color='pink')); ax.add_patch(Ellipse((0.3,0.7), 0.1, 0.05, color='green'))
ax.text(0.5,0.5,'1. Nucleus', bbox=dict(boxstyle='round', facecolor='yellow')); ax.set_title('Plant Cell S1'); ax.axis('off')
plt.savefig('example.png', dpi=300, bbox_inches='tight'); plt.close()'''

SYSTEM_SMART = f"COPY STYLE: {PERFECT_EXAMPLE}. Use ONLY Circle Rectangle Ellipse. 5 labels. DPI 300. NO coords. NO 3D."
SYSTEM_INSTANT = "FAST DIAGRAM BOT. Simple 2D. Use Circle Rectangle. 3 labels. DPI 200."

def call_groq_dual(prompt, mode="Smart"):
    model = AI_MODEL_SMART if mode=="Smart" else AI_MODEL_INSTANT
    system = SYSTEM_SMART if mode=="Smart" else SYSTEM_INSTANT
    tokens = 3000 if mode=="Smart" else 800
    try:
        res = client.chat.completions.create(model=model, messages=[{"role":"system","content":system},{"role":"user","content":prompt}], max_tokens=tokens, temperature=0.05)
        return res.choices[0].message.content
    except RateLimitError: return call_groq_dual(prompt, "Instant")

def render_diagram(description, subject, level, mode="Smart"):
    safe_name = re.sub(r'[^\w_]', '_', description[:15])
    dpi = 300 if mode=="Smart" else 200
    fname = f"diagram_{mode}_{safe_name}.png"
    prompt = f"TASK: {description} SUBJECT: {subject} {level}. Save as '{fname}'"
    code = call_groq_dual(prompt, mode).replace("```python","").replace("```","")
    code = "from matplotlib.patches import Circle, Rectangle, Ellipse\nimport matplotlib.pyplot as plt\nimport numpy as np\n" + code
    code = re.sub(r"plt\.savefig\('.*?\.png'", f"plt.savefig('{fname}'", code)
    try:
        exec(code, {"plt": plt, "np": np, "Circle": Circle, "Rectangle": Rectangle, "Ellipse": Ellipse})
        return {"status": "OK", "path": fname} if os.path.exists(fname) else {"status": "ERROR"}
    except Exception as e: return {"status": "ERROR", "msg": str(e)}

### STUDENT PORTAL - FULL TABS RESTORED ###
def show_student_portal(student):
    st.header(f"👋 Welcome {student['name']} - {student['class']}")
    tabs = st.tabs(["📖 Syllabus Explorer", "📝 Practice Engine", "🎨 Diagram Engine", "📄 Past Papers", "👤 Profile"])

    with tabs[0]:
        st.subheader("NCDC 2026 Syllabus Explorer")
        subj = st.selectbox("Select Subject", list(UNEB_CURRICULUM_MAP.keys()), key="syll_subj")
        st.write(f"### {subj} - {student['class']} Topics")
        for topic in UNEB_CURRICULUM_MAP[subj][student['class']]: st.write(f"✅ {topic}")

    with tabs[1]:
        st.subheader("AI Practice Engine")
        subj = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="prac_subj")
        topic = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subj][student['class']])
        if st.button("Generate 5 UNEB Questions"):
            prompt = f"Generate 5 UNEB MCQ for {student['class']} {subj} Topic: {topic}. JSON with question,options,answer"
            res = call_groq_dual(prompt, "Smart"); st.code(res)

    with tabs[2]:
        st.subheader("Textbook Diagram Engine")
        mode = st.radio("AI Engine", ["Smart 70B - Perfect", "Instant 3B - Fast"], horizontal=True, key="diag_mode")
        desc = st.text_area("Describe Diagram", "Draw Plant Cell with nucleus chloroplast vacuole cell wall")
        subj = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="diag_subj")
        if st.button("Generate Diagram"):
            m = "Smart" if "Smart" in mode else "Instant"
            res = render_diagram(desc, subj, student['class'], m)
            if res["status"]=="OK": st.image(res["path"])
            else: st.error(res.get("msg",""))

    with tabs[3]:
        st.subheader("Past Papers")
        st.info("Past papers will appear here after Admin upload")

    with tabs[4]:
        st.json(student)

### ADMIN PORTAL - FULL TABS RESTORED ###
def show_admin_portal():
    st.header("🔒 Admin Dashboard")
    tabs = st.tabs(["📤 Upload QBank", "📊 Monitor Usage", "🤖 AI QBank Generator", "📈 Analytics"])

    with tabs[0]:
        st.subheader("Upload QBank CSV")
        file = st.file_uploader("CSV columns: question,options,answer,subject,class,topic")
        if file and st.button("Save to Database"):
            df = pd.read_csv(file); save_db(QBANK_FILE, df.to_dict('records')); st.success(f"Saved {len(df)} questions")

    with tabs[1]:
        st.subheader("Usage Monitor")
        st.dataframe(pd.DataFrame(st.session_state.log))

    with tabs[2]:
        st.subheader("AI QBank Generator")
        subj = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
        lvl = st.selectbox("Class", [f"S{i}" for i in range(1,7)])
        topic = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subj][lvl])
        if st.button("Generate 20 Questions"):
            prompt = f"Generate 20 UNEB MCQ for {lvl} {subj} Topic: {topic}. Return valid JSON list"
            res = call_groq_dual(prompt, "Smart")
            try: data = json.loads(res); save_db(AI_QBANK_FILE, data); st.success("Generated")
            except: st.error("AI returned bad JSON")

    with tabs[3]:
        st.subheader("Analytics")
        st.metric("Total Students", len(st.session_state.students_db))
        st.metric("Total QBank Qns", len(st.session_state.qbank))

### LOGIN ARCHITECTURE RESTORED ###
st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO - V3.9.1")
role = st.sidebar.radio("Login As", ["Student","Admin"])
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if role=="Admin" and password==ADMIN_PASSWORD: st.session_state["role"]="Admin"; st.rerun()
    elif role=="Student" and password==STUDENT_PASSWORD:
        name = st.sidebar.text_input("Student Name")
        cls = st.sidebar.selectbox("Class", [f"S{i}" for i in range(1,7)])
        if name:
            student = {"name":name, "class":cls, "login":str(datetime.now())}
            st.session_state.students_db.append(student); save_db(STUDENTS_FILE, st.session_state.students_db)
            st.session_state["role"]="Student"; st.session_state["student"]=student; st.rerun()
    else: st.sidebar.error("Wrong Password")

if st.session_state.get("role")=="Admin": show_admin_portal()
elif st.session_state.get("role")=="Student": show_student_portal(st.session_state["student"])
else: st.info("Login to continue")
