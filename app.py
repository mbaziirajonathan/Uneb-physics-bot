import streamlit as st
import os, io, json, re, time, traceback
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

### DESCRIPTION ENGINE SYSTEM PROMPT ###
MASTER_SYSTEM_PROMPT = """You are DIGITAL UNEB TUTOR 2026 PRO - NCDC SCIENTIFIC ILLUSTRATOR.
TASK: Read user description and convert to PERFECT matplotlib code.
RULES FOR COMPLEXITY AUTO-TUNE:
1. SIMPLE: 2D line, bar, graph. DPI 200. 3 labels.
2. MEDIUM: Cell, Atom, Circuit. DPI 300. 5-8 labels + arrows.
3. COMPLEX: Heart, Brain, Geometric Construction, Organic Molecule. DPI 400. 3D if needed. 10+ labels.
4. ALWAYS: Title, Scale, Numbered Labels 1.2.3, Arrows, Legend, Caption with Formula.
5. SUBJECT CONTEXT: Biology=cell parts, Chemistry=bonding, Physics=vectors/forces, Math=accurate geometry.
6. Ugandan Context when relevant.
7. MUST SAVE: plt.savefig('FILENAME', dpi=X, bbox_inches='tight'); plt.close()"""

### 14 NCDC SUBJECTS ###
UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Number Bases", "Integers"], "S2": ["Patterns", "Bearings", "Angles"], "S3": ["Quadratics", "Matrices", "Vectors"], "S4": ["Functions", "3D Geometry", "Circle Geometry"], "S5": ["Differentiation", "Integration"], "S6": ["Mechanics", "Statistics II"]},
    "Physics": {"S1": ["Measurement", "Forces"], "S2": ["Light", "Thermal Physics", "Electricity I", "Waves I", "Sound"], "S3": ["Electricity II", "Magnetism"], "S4": ["Electromagnetism", "Electronics"], "S5": ["Gravitation", "Optics"], "S6": ["Electric Fields", "Nuclear Physics"]},
    "Chemistry": {"S1": ["States of Matter", "Mixtures"], "S2": ["Acids Alkalis", "Salts"], "S3": ["Bonding", "Stoichiometry"], "S4": ["REDOX", "Organic II"], "S5": ["Energetics", "Kinetics"], "S6": ["Electrochemistry", "Organic III"]},
    "Biology": {"S1": ["Cells", "Classification"], "S2": ["Soil", "Nutrition"], "S3": ["Respiration", "Genetics I"], "S4": ["Coordination", "Ecology", "Photosynthesis"], "S5": ["Cell Biology", "Enzymes"], "S6": ["Hormones", "Biotechnology"]},
    "Geography": {"S1": ["Map Reading"], "S2": ["Rocks"], "S3": ["Industry"], "S4": ["Agriculture"], "S5": ["Geomorphology"], "S6": ["GIS"]},
    "History": {"S1": ["Early Man"], "S2": ["Kingdoms of Uganda"], "S3": ["Scramble"], "S4": ["Decolonization"], "S5": ["Political"], "S6": ["Governance"]},
    "Agriculture": {"S1": ["Soil"], "S2": ["Livestock"], "S3": ["Crop Production"], "S4": ["Farm Management"], "S5": ["Crop Science"], "S6": ["Agribusiness"]},
    "CRE": {"S1": ["Creation"], "S2": ["Moses"], "S3": ["Jesus"], "S4": ["Church"], "S5": ["Ethics"], "S6": ["Philosophy"]},
    "IRE": {"S1": ["Tawheed"], "S2": ["Quran"], "S3": ["Pillars"], "S4": ["History"], "S5": ["Fiqh"], "S6": ["Economics"]},
    "Commerce": {"S1": ["Business"], "S2": ["Money"], "S3": ["Organizations"], "S4": ["Insurance"], "S5": ["Public Finance"], "S6": ["Trade"]},
    "Economics": {"S1": ["Basic"], "S2": ["Demand"], "S3": ["Production"], "S4": ["National Income"], "S5": ["Public Finance"], "S6": ["International"]},
    "Literature": {"S1": ["Poetry"], "S2": ["Drama"], "S3": ["Shakespeare"], "S4": ["Themes"], "S5": ["Analysis"], "S6": ["Comparative"]},
    "ICT": {"S1": ["Computer"], "S2": ["Spreadsheet"], "S3": ["Programming"], "S4": ["Web"], "S5": ["Python"], "S6": ["AI"]},
    "Fine Art": {"S1": ["Drawing"], "S2": ["Painting"], "S3": ["Craft"], "S4": ["Art History"], "S5": ["Advanced"], "S6": ["Exhibition"]}
}

PRACTICAL_DATABASE = {
    "Physics": {"S1-S4": {"Ohm's Law": {"objective": "Verify V=IR"}, "Pendulum": {"objective": "Find g"}}, "S5-S6": {"RC": {"objective": "Find tau"}}},
    "Chemistry": {"S1-S4": {"Separation": {"objective": "Separate"}, "Titration": {"objective": "Find conc"}}, "S5-S6": {"Rate": {"objective": "Temp"}}},
    "Biology": {"S1-S4": {"Microscope": {"objective": "Observe"}, "Food": {"objective": "Test"}}, "S5-S6": {"Enzyme": {"objective": "pH"}}}
}

def load_logs(): return json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []
def save_log(entry): logs = load_logs(); logs.append(entry); json.dump(logs, open(LOG_FILE,"w"))
def log_activity(user_type, action, details): save_log({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user_type, "action": action, "details": details})
def create_pdf(content, title):
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); p.setFont("Helvetica-Bold", 14); p.drawString(50,800,title); y=770; p.setFont("Helvetica", 10)
    for i,line in enumerate(content.split('\n')[:80]): p.drawString(50,y-(i*14),line[:95])
    p.save(); buffer.seek(0); return buffer
def call_groq(user_prompt, temp=0.2):
    try: res = client.chat.completions.create(model=AI_MODEL_LONG, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}], max_tokens=3000, temperature=temp); return res.choices[0].message.content
    except RateLimitError: res = client.chat.completions.create(model=AI_MODEL_FAST, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}], max_tokens=2000, temperature=temp); return res.choices[0].message.content

### DESCRIPTION ENGINE + COMPLEXITY CLASSIFIER ###
def classify_complexity(description):
    prompt = f"Classify diagram complexity as SIMPLE, MEDIUM, or COMPLEX. Description: {description}. Return only 1 word."
    return call_groq(prompt, temp=0.1).strip().upper()

def description_to_code(description, subject, level):
    complexity = classify_complexity(description)
    dpi = 200 if complexity=="SIMPLE" else 300 if complexity=="MEDIUM" else 400
    use_3d = "YES" if any(word in description.lower() for word in ["3d", "cell", "heart", "atom", "molecule", "cone", "sphere"]) else "NO"

    safe_name = re.sub(r'[^\w_]', '_', description[:30])
    fname = f"desc_diagram_{safe_name}.png"

    prompt = f"""User Description: "{description}"
    Subject: {subject} | Class: {level}
    Complexity: {complexity} | DPI: {dpi} | 3D: {use_3d}

    Generate ONLY executable python matplotlib code.
    RULES: Title, {dpi} DPI, Numbered labels 1.2.3 with bbox, arrows, legend, grid, caption with formula.
    If 3D=YES use mpl_toolkits.mplot3d.
    MUST SAVE: plt.savefig('{fname}', dpi={dpi}, bbox_inches='tight'); plt.close()
    Return only code."""

    code = call_groq(prompt, temp=0.1).replace("```python","").replace("```","")
    code = re.sub(r"plt\.savefig\('.*?\.png'", f"plt.savefig('{fname}'", code)

    try:
        exec_globals = {"plt": plt, "np": np}
        exec(code, exec_globals)
        return {"status": "OK", "path": fname, "complexity": complexity} if os.path.exists(fname) else {"status": "ERROR", "msg": "File not created"}
    except Exception as e:
        return {"status": "ERROR", "msg": str(e)}

def loop_all_subjects_diagrams(description):
    results = []
    st.info("🔍 DESCRIPTION ENGINE: Analyzing complexity and looping all relevant subjects...")
    for subject in UNEB_CURRICULUM_MAP.keys():
        for level in [f"S{i}" for i in range(1,7)]:
            res = description_to_code(description, subject, level)
            if res["status"]=="OK":
                results.append({"subject": subject, "level": level, "path": res["path"], "complexity": res["complexity"]})
            time.sleep(0.3)
    return results

def display_with_pdf(content, name):
    st.markdown(content)
    for f in re.findall(r'\$(.*?)\$', content): st.latex(f)
    pdf = create_pdf(content, name); st.download_button("📥 Download PDF", pdf, f"{name}.pdf", key=f"dl_{name}_{time.time()}")

### PORTALS ###
def show_student_portal():
    st.header("📚 Student Portal - NCDC S1 to S6 - DESCRIPTION ENGINE")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tab1, tab2, tab3 = st.tabs(["🔍 Smart Search", "📖 Learn Topic", "🎨 Description Diagram Engine"])

    with tab1:
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)])
        ask_q = st.text_area("Ask any NCDC question")
        if st.button("Ask AI Brain") and ask_q:
            ans = call_groq(f"Answer with Ugandan examples: {ask_q} for {level} {subject}")
            display_with_pdf(ans, "Answer")

    with tab2:
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="s2")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="l2")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject2][level2])
        if st.button("Teach Me"):
            raw = call_groq(f"Teach {topic2} with Ugandan examples for {level2} {subject2}")
            display_with_pdf(raw, "Theory")

    with tab3:
        st.header("🎨 DESCRIPTION ENGINE - DESCRIBE TO DRAW")
        st.caption("Example: 'Draw plant cell showing cell wall, nucleus, chloroplast, vacuole with arrows and labels for S1 Biology'")

        mode = st.radio("Engine Mode", ["Describe 1 Diagram", "Loop All Subjects With This Description"])

        description = st.text_area("Describe the diagram in detail:",
        "Draw a plant cell. Show cell wall, cell membrane, nucleus, chloroplast, large vacuole. Use green for chloroplast. Label 1-5 with arrows. Add title 'Plant Cell S1 Biology'")

        subject_sel = st.selectbox("Target Subject", list(UNEB_CURRICULUM_MAP.keys()))
        level_sel = st.selectbox("Target Class", [f"S{i}" for i in range(1,7)])

        if st.button("Generate From Description", type="primary"):
            log_activity("Student", "Describe Diagram", description)

            if mode == "Describe 1 Diagram":
                res = description_to_code(description, subject_sel, level_sel)
                if res["status"]=="OK":
                    st.success(f"Generated {res['complexity']} complexity diagram")
                    st.image(res["path"], use_container_width=True)
                    with open(res["path"], "rb") as file: st.download_button("📥 Download HD", file, res["path"])
                else: st.error(res["msg"])

            else: # Loop all
                results = loop_all_subjects_diagrams(description)
                st.success(f"Generated {len(results)} diagrams across all subjects")
                for r in results:
                    st.write(f"**{r['subject']} {r['level']}** - {r['complexity']}")
                    st.image(r["path"], use_container_width=True)

def show_admin_portal():
    st.header("🏫 Admin Portal")
    if st.button("Logout"): st.session_state.clear(); st.rerun()

st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO - V3.8.0 DESCRIPTION ENGINE")
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"])
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    if user_type == "Student" and password == STUDENT_PASSWORD: st.session_state["role"] = "Student"; st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD: st.session_state["role"] = "Admin"; st.rerun()

if st.session_state.get("role") == "Admin": show_admin_portal()
elif st.session_state.get("role") == "Student": show_student_portal()
