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

MASTER_SYSTEM_PROMPT = """You are DIGITAL UNEB TUTOR 2026 PRO - NCDC UGANDA EXAMINER + SCIENTIFIC ILLUSTRATOR.
CRITICAL DIAGRAM RULES:
1. EXAMINER STANDARD: Title, Scale, Numbered Labels 1.2.3 with arrows, Formula, Caption, Grid, Legend.
2. 3D WHEN POSSIBLE: Use mpl_toolkits.mplot3d for atoms, cells, cones, heart.
3. Ugandan Context: Use examples: Kampala, Lake Victoria, Matoke, Boda.
4. CODE: Must save to EXACT filename given. DPI 300. bbox_inches='tight'. plt.close()
5. NO HALLUCINATION. If unsure of science, state assumption."""

UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Number Bases", "Integers"], "S2": ["Patterns", "Bearings"], "S3": ["Quadratics", "Matrices"], "S4": ["Functions", "3D Geometry", "Statistics"], "S5": ["Differentiation"], "S6": ["Differential Equations"]},
    "Physics": {"S1": ["Measurement", "Forces"], "S2": ["Light", "Thermal Physics", "Electricity I", "Waves I", "Sound"], "S3": ["Electricity II"], "S4": ["Electromagnetism"], "S5": ["Gravitation"], "S6": ["Electric Fields"]},
    "Chemistry": {"S1": ["States of Matter"], "S2": ["Acids Alkalis"], "S3": ["Bonding"], "S4": ["REDOX"], "S5": ["Energetics"], "S6": ["Electrochemistry"]},
    "Biology": {"S1": ["Cells"], "S2": ["Soil"], "S3": ["Respiration"], "S4": ["Coordination"], "S5": ["Cell Biology"], "S6": ["Hormones"]},
    "Geography": {"S1": ["Map Reading"], "S2": ["Rocks"], "S3": ["Industry"], "S4": ["Agriculture"], "S5": ["Geomorphology"], "S6": ["Regional Geography"]},
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
    "Physics": {"S1-S4": {"Ohm's Law": {"objective": "Verify V=IR"}, "Pendulum": {"objective": "Find g"}, "Refraction": {"objective": "Find n"}}, "S5-S6": {"RC": {"objective": "Find tau"}, "Youngs": {"objective": "Find Y"}}},
    "Chemistry": {"S1-S4": {"Separation": {"objective": "Separate"}, "Titration": {"objective": "Find conc"}}, "S5-S6": {"Rate": {"objective": "Temp"}, "Electrolysis": {"objective": "CuSO4"}}},
    "Biology": {"S1-S4": {"Microscope": {"objective": "Observe"}, "Food": {"objective": "Test"}, "Osmosis": {"objective": "Potato"}}, "S5-S6": {"Enzyme": {"objective": "pH"}, "Transpiration": {"objective": "Rate"}}}
}

def load_logs(): return json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []
def save_log(entry): logs = load_logs(); logs.append(entry); json.dump(logs, open(LOG_FILE,"w"))
def log_activity(user_type, action, details): save_log({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user_type, "action": action, "details": details})
def create_pdf(content, title):
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); p.setFont("Helvetica-Bold", 14); p.drawString(50,800,title); y=770; p.setFont("Helvetica", 10)
    for i,line in enumerate(content.split('\n')[:80]): p.drawString(50,y-(i*14),line[:95])
    p.save(); buffer.seek(0); return buffer
def call_groq(user_prompt, temp=0.2):
    try: res = client.chat.completions.create(model=AI_MODEL_LONG, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}], max_tokens=2500, temperature=temp); return res.choices[0].message.content
    except RateLimitError: res = client.chat.completions.create(model=AI_MODEL_FAST, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}], max_tokens=1500, temperature=temp); return res.choices[0].message.content

### RATE + RETRY ENGINE ###
def auto_render_pixel_diagram(topic, subject, level, attempt=1, feedback=""):
    safe_topic = re.sub(r'[^\w_]', '_', topic)
    fname = f"auto_diagram_{safe_topic}_v{attempt}.png"

    detail_weight = "CRITICAL EXAMINER DETAIL" if attempt > 1 else "STANDARD"
    prompt = f"""Generate ONLY executable python matplotlib code to draw '{topic}' for {level} {subject}.
    MODE: {detail_weight}
    REQUIREMENTS:
    1. plt.style.use('seaborn-v0_8-whitegrid')
    2. fig = plt.figure(figsize=(10,7), dpi=300)
    3. Use 3D projection if topic is 3D: from mpl_toolkits.mplot3d import Axes3D
    4. Add Title, Axis labels, Grid, Legend
    5. Add 3 numbered annotations: ax.text(x,y,'1. Crest', fontsize=12, weight='bold', bbox=dict(boxstyle='round', facecolor='yellow'))
    6. Add arrows with ax.annotate()
    7. Add caption at bottom: plt.figtext(0.5, 0.01, 'Formula:...', ha='center')
    8. MUST END: plt.savefig('{fname}', dpi=300, bbox_inches='tight'); plt.close()
    FEEDBACK TO FIX: {feedback}
    Return only code."""

    code = call_groq(prompt, temp=0.1 if attempt>1 else 0.2).replace("```python","").replace("```","")
    code = re.sub(r"plt\.savefig\('.*?\.png'", f"plt.savefig('{fname}'", code)

    try:
        exec_globals = {"plt": plt, "np": np}
        exec(code, exec_globals)
        if os.path.exists(fname):
            return {"status": "OK", "path": fname}
        else:
            return {"status": "ERROR", "msg": f"File not created", "code": code[:300]}
    except Exception as e:
        return {"status": "ERROR", "msg": str(e), "trace": traceback.format_exc()[:300]}

def batch_generate_diagrams(subject, level, topic_list):
    results = []
    progress = st.progress(0)
    for i, topic in enumerate(topic_list):
        st.write(f"Rendering {i+1}/{len(topic_list)}: {topic}")
        res = auto_render_pixel_diagram(topic, subject, level, attempt=1)
        results.append({"topic": topic, "res": res})
        progress.progress((i+1)/len(topic_list))
        time.sleep(1)
    return results

def display_diagram_with_rating(topic_data):
    topic = topic_data["topic"]
    res = topic_data["res"]

    if res["status"] == "OK":
        st.image(res["path"], caption=f"{topic}", use_container_width=True)
        with open(res["path"], "rb") as file: st.download_button("📥 Download", file, res["path"], key=res["path"])

        rating = st.slider(f"Rate quality of '{topic}'", 1, 5, 3, key=f"rate_{topic}")
        if st.button(f"Regenerate '{topic}' if rating < 3", key=f"regen_{topic}"):
            if rating < 3:
                st.info("CRITICAL MODE: Regenerating with higher detail...")
                feedback = "Previous diagram lacked detail, labels, 3D. Make it examiner standard with more annotations."
                new_res = auto_render_pixel_diagram(topic, "Physics", "S2", attempt=2, feedback=feedback)
                if new_res["status"] == "OK":
                    st.image(new_res["path"], caption=f"{topic} V2 - Improved")
                    with open(new_res["path"], "rb") as file: st.download_button("📥 Download V2", file, new_res["path"], key=new_res["path"])
    else:
        st.error(f"{topic} failed: {res['msg']}")
        with st.expander("Debug Code"):
            st.code(res.get("code",""))

def show_student_portal():
    st.header("📚 Student Portal - NCDC S1 to S6")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tab1, tab2, tab3 = st.tabs(["🔍 Smart Search", "📖 Learn", "🎨 Batch Diagram Generator"])

    with tab1:
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)])
        ask_q = st.text_area("Ask NCDC question")
        if st.button("Ask AI Brain") and ask_q:
            ans = call_groq(f"Answer with Ugandan examples: {ask_q} for {level} {subject}")
            st.markdown(ans)

    with tab2:
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="s2")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="l2")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject2][level2])
        if st.button("Teach Me"):
            raw = call_groq(f"Teach {topic2} with Ugandan examples for {level2} {subject2}")
            st.markdown(raw)

    with tab3:
        st.header("🎨 Batch Diagram Generator - RATE + RETRY")
        subject3 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="b3")
        level3 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="bL3")
        topic_list = st.multiselect("Select Topics", UNEB_CURRICULUM_MAP[subject3][level3], default=UNEB_CURRICULUM_MAP[subject3][level3][:1])

        if st.button("Generate Batch Diagrams", type="primary"):
            results = batch_generate_diagrams(subject3, level3, topic_list)
            st.success(f"Generated {len([r for r in results if r['res']['status']=='OK'])} diagrams")
            for r in results:
                display_diagram_with_rating(r)

def show_admin_portal():
    st.header("🏫 Admin Portal")
    if st.button("Logout"): st.session_state.clear(); st.rerun()

st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO - V3.7.9.2 RATE + RETRY")
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"])
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    if user_type == "Student" and password == STUDENT_PASSWORD: st.session_state["role"] = "Student"; st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD: st.session_state["role"] = "Admin"; st.rerun()

if st.session_state.get("role") == "Admin": show_admin_portal()
elif st.session_state.get("role") == "Student": show_student_portal()
