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

MASTER_SYSTEM_PROMPT = """You are DIGITAL UNEB TUTOR 2026 PRO - NCDC UGANDA EXAMINER.
CRITICAL RULES: 1. Use ONLY NCDC 2026 + Ugandan examples. 2. UNEB ITEM/TASK/SCENARIO format. 3. Diagrams: Title, Numbered labels 1.2.3., Arrows, DPI 300. 4. CODE MUST SAVE TO EXACT FILENAME PROVIDED. 5. NO HALLUCINATION."""

UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Number Bases", "Integers", "Fractions"], "S2": ["Patterns", "Bearings", "Angles"], "S3": ["Quadratics", "Matrices", "Probability"], "S4": ["Functions", "3D Geometry", "Statistics"], "S5": ["Differentiation", "Integration"], "S6": ["Differential Equations", "Mechanics"]},
    "Physics": {"S1": ["Measurement", "Forces", "Work Energy Power"], "S2": ["Light", "Thermal Physics", "Electricity I", "Waves I", "Sound"], "S3": ["Electricity II", "Magnetism"], "S4": ["Electromagnetism", "Electronics"], "S5": ["Gravitation", "Optics"], "S6": ["Electric Fields", "Magnetic Fields"]},
    "Chemistry": {"S1": ["States of Matter", "Mixtures"], "S2": ["Acids Alkalis", "Salts"], "S3": ["Bonding", "Stoichiometry"], "S4": ["REDOX", "Organic II"], "S5": ["Energetics", "Kinetics"], "S6": ["Electrochemistry", "Organic III"]},
    "Biology": {"S1": ["Cells", "Classification"], "S2": ["Soil", "Nutrition"], "S3": ["Respiration", "Genetics I"], "S4": ["Coordination", "Ecology"], "S5": ["Cell Biology", "Enzymes"], "S6": ["Hormones", "Biotechnology"]},
    "Geography": {"S1": ["Map Reading", "Weather"], "S2": ["Rocks", "Drainage"], "S3": ["Industry", "Trade"], "S4": ["Agriculture", "Mining"], "S5": ["Geomorphology"], "S6": ["Regional Geography"]},
    "History": {"S1": ["Early Man"], "S2": ["Kingdoms of Uganda"], "S3": ["Scramble for Africa"], "S4": ["Decolonization"], "S5": ["Political Developments"], "S6": ["Governance"]},
    "Agriculture": {"S1": ["Soil", "Crops"], "S2": ["Livestock"], "S3": ["Crop Production"], "S4": ["Farm Management"], "S5": ["Crop Science"], "S6": ["Agribusiness"]},
    "CRE": {"S1": ["God's Creation"], "S2": ["Moses"], "S3": ["Jesus Ministry"], "S4": ["Church"], "S5": ["Ethics"], "S6": ["Philosophy"]},
    "IRE": {"S1": ["Tawheed"], "S2": ["Quran"], "S3": ["Pillars"], "S4": ["Islamic History"], "S5": ["Fiqh"], "S6": ["Islamic Economics"]},
    "Commerce": {"S1": ["Business"], "S2": ["Money"], "S3": ["Organizations"], "S4": ["Insurance"], "S5": ["Public Finance"], "S6": ["International Trade"]},
    "Economics": {"S1": ["Basic Concepts"], "S2": ["Demand"], "S3": ["Production"], "S4": ["National Income"], "S5": ["Public Finance"], "S6": ["International Economics"]},
    "Literature": {"S1": ["Poetry"], "S2": ["Drama"], "S3": ["Shakespeare"], "S4": ["Themes"], "S5": ["Critical Analysis"], "S6": ["Comparative"]},
    "ICT": {"S1": ["Computer Basics"], "S2": ["Spreadsheet"], "S3": ["Programming"], "S4": ["Web Design"], "S5": ["Python"], "S6": ["AI"]},
    "Fine Art": {"S1": ["Drawing"], "S2": ["Painting"], "S3": ["Craft"], "S4": ["Art History"], "S5": ["Advanced Painting"], "S6": ["Exhibition"]}
}

PRACTICAL_DATABASE = {
    "Physics": {"S1-S4": {"Ohm's Law": {"objective": "Verify V=IR"}, "Simple Pendulum": {"objective": "Find g"}, "Refraction": {"objective": "Find n"}}, "S5-S6": {"RC Circuit": {"objective": "Find tau"}, "Young's Modulus": {"objective": "Find Y"}}},
    "Chemistry": {"S1-S4": {"Separation": {"objective": "Separate"}, "Titration": {"objective": "Find conc"}, "Oxygen": {"objective": "Prep O2"}}, "S5-S6": {"Rate": {"objective": "Effect temp"}, "Electrolysis": {"objective": "CuSO4"}}},
    "Biology": {"S1-S4": {"Microscope": {"objective": "Observe"}, "Food Tests": {"objective": "Test"}, "Osmosis": {"objective": "Potato"}}, "S5-S6": {"Enzyme": {"objective": "pH"}, "Transpiration": {"objective": "Rate"}}}
}

def load_logs(): return json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []
def save_log(entry): logs = load_logs(); logs.append(entry); json.dump(logs, open(LOG_FILE,"w"))
def log_activity(user_type, action, details): save_log({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user_type, "action": action, "details": details})
def create_pdf(content, title):
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); p.setFont("Helvetica-Bold", 14); p.drawString(50,800,title); y=770; p.setFont("Helvetica", 10)
    for i,line in enumerate(content.split('\n')[:80]): p.drawString(50,y-(i*14),line[:95])
    p.save(); buffer.seek(0); return buffer
def call_groq(user_prompt):
    try: res = client.chat.completions.create(model=AI_MODEL_LONG, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}], max_tokens=2000, temperature=0.2); return res.choices[0].message.content
    except RateLimitError: res = client.chat.completions.create(model=AI_MODEL_FAST, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}], max_tokens=1500, temperature=0.2); return res.choices[0].message.content

### DEBUG AUTO-RENDER ENGINE ###
def auto_render_pixel_diagram(topic, subject, level):
    safe_topic = re.sub(r'[^\w_]', '_', topic) # Remove spaces/special chars
    fname = f"auto_diagram_{safe_topic}.png"

    prompt = f"""Generate ONLY executable python matplotlib code to draw '{topic}' for {level} {subject}.
    RULES:
    1. Use plt.figure(figsize=(8,6))
    2. Add plt.title('Title'), plt.xlabel(), plt.ylabel(), legend if needed
    3. Add 3 numbered text labels with plt.text(x,y,'1. Label',weight='bold')
    4. MUST END WITH: plt.savefig('{fname}', dpi=200, bbox_inches='tight'); plt.close()
    5. NO plt.show()
    Return only code."""

    code = call_groq(prompt).replace("```python","").replace("```","")

    # Force correct filename in case AI hallucinates
    code = re.sub(r"plt\.savefig\('.*?\.png'", f"plt.savefig('{fname}'", code)

    try:
        exec_globals = {"plt": plt, "np": np}
        exec(code, exec_globals)

        if os.path.exists(fname):
            return {"status": "OK", "path": fname, "code": code[:100]}
        else:
            return {"status": "ERROR", "msg": f"File {fname} not created", "code": code[:200]}
    except Exception as e:
        return {"status": "ERROR", "msg": str(e), "trace": traceback.format_exc()[:300]}

def batch_generate_diagrams(subject, level, topic_list):
    results = []
    errors = []
    progress = st.progress(0)

    for i, topic in enumerate(topic_list):
        st.write(f"Rendering {i+1}/{len(topic_list)}: {topic}")
        res = auto_render_pixel_diagram(topic, subject, level)

        if res["status"] == "OK":
            results.append({"topic": topic, "path": res["path"]})
        else:
            errors.append(f"{topic}: {res['msg']}")
            with st.expander(f"Debug: {topic} failed"):
                st.code(res.get("code",""), language="python")
                st.text(res.get("trace",""))

        progress.progress((i+1)/len(topic_list))
        time.sleep(1.5) # Prevent rate limit

    return results, errors

def generate_practical(subject, level, prac_name):
    level_group = "S1-S4" if int(level[1]) <= 4 else "S5-S6"
    data = PRACTICAL_DATABASE.get(subject,{}).get(level_group,{}).get(prac_name,{})
    if not data: return "Practical not in NCDC database"
    prompt = f"Expand this NCDC practical into full UNEB report for {subject} {level} Ugandan context: {data}"
    return call_groq(prompt)

def generate_uneb_item_task(subject, level, topic):
    prompt = f"Generate 1 UNEB ITEM/TASK/SCENARIO for {level} {subject} topic: {topic}. Use Ugandan context. Provide scenario, task, marking guide."
    return call_groq(prompt)

def display_with_pdf(content, name):
    st.markdown(content)
    for f in re.findall(r'\$(.*?)\$', content): st.latex(f)
    pdf = create_pdf(content, name); st.download_button("📥 Download PDF", pdf, f"{name}.pdf", key=f"dl_{name}_{time.time()}")

### PORTALS ###
def show_student_portal():
    st.header("📚 Student Portal - NCDC S1 to S6 - 14 SUBJECTS")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Smart Search", "📖 Learn Topic", "🎨 Batch Diagram Generator", "📝 UNEB ITEM/TASK"])

    with tab1:
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="search_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="search_level")
        ask_q = st.text_area("Ask any NCDC question")
        if st.button("Ask AI Brain", type="primary") and ask_q:
            log_activity("Student", "Ask Question", ask_q)
            ans = call_groq(f"Answer with Ugandan examples: {ask_q} for {level} {subject}")
            display_with_pdf(ans, "Answer")

    with tab2:
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="learn_subj")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="learn_level")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject2][level2], key="learn_topic")
        mode = st.radio("Mode", ["📖 Theory", "🧠 AOI", "🧪 Practicals Lab", "📚 Bulk Revision"])

        if mode == "📖 Theory" and st.button("Teach Me"):
            raw = call_groq(f"Teach {topic2} with Ugandan examples for {level2} {subject2}")
            display_with_pdf(raw, "Theory")
        elif mode == "🧠 AOI" and st.button("Generate AOI"):
            aoi = call_groq(f"Generate NCDC Activity of Integration for {level2} {subject2} topic: {topic2}")
            display_with_pdf(aoi, "AOI")
        elif mode == "🧪 Practicals Lab":
            if subject2 in PRACTICAL_DATABASE:
                prac_list = list(PRACTICAL_DATABASE.get(subject2,{}).get("S1-S4",{}).keys()) if int(level2[1])<=4 else list(PRACTICAL_DATABASE.get(subject2,{}).get("S5-S6",{}).keys())
            else: prac_list = ["No practicals"]
            prac = st.selectbox("Select Practical", prac_list)
            if st.button("Generate Practical"):
                report = generate_practical(subject2,level2,prac)
                display_with_pdf(report, "Practical")
        elif mode == "📚 Bulk Revision" and st.button("Generate Revision"):
            rev = call_groq(f"Generate NCDC revision + 20 Ugandan questions for {topic2} {level2} {subject2}")
            display_with_pdf(rev, "Revision")

    with tab3:
        st.header("🎨 Batch Diagram Generator - DEBUG MODE")
        subject3 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="batch_subj")
        level3 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="batch_level")

        col1, col2 = st.columns(2)
        with col1:
            mode = st.radio("Batch Mode", ["1 Topic", "All Topics in Class", "Selected Topics"])
        with col2:
            if mode == "1 Topic":
                topic_list = [st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject3][level3])]
            elif mode == "All Topics in Class":
                topic_list = UNEB_CURRICULUM_MAP[subject3][level3]
                st.info(f"Will generate {len(topic_list)} diagrams")
            else:
                topic_list = st.multiselect("Select Topics", UNEB_CURRICULUM_MAP[subject3][level3])

        if st.button("Generate Batch Diagrams", type="primary"):
            log_activity("Student", "Batch Generate", f"{subject3} {level3}")
            results, errors = batch_generate_diagrams(subject3, level3, topic_list)

            st.success(f"Generated {len(results)} diagrams")
            if errors:
                st.error(f"Failed {len(errors)} diagrams")
                for e in errors: st.write(e)

            for r in results:
                st.image(r["path"], caption=f"{r['topic']}", use_container_width=True)
                with open(r["path"], "rb") as file: st.download_button("📥 Download", file, r["path"], key=r["path"])

    with tab4:
        st.header("📝 UNEB ITEM/TASK/SCENARIO GENERATOR")
        subject4 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="item_subj")
        level4 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="item_level")
        topic4 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject4][level4], key="item_topic")
        if st.button("Generate UNEB ITEM/TASK", type="primary"):
            item = generate_uneb_item_task(subject4, level4, topic4)
            display_with_pdf(item, "UNEB_ITEM")

def show_admin_portal():
    st.header("🏫 Admin Portal - NCDC MANAGER")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tab1, tab2 = st.tabs(["📊 Analytics", "📖 Curriculum Manager"])
    with tab1:
        logs = load_logs()
        st.metric("Total Logs", len(logs))
        if logs: st.dataframe(pd.DataFrame(logs))
    with tab2:
        st.subheader("14 NCDC Subjects")
        subj = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)])
        st.write(UNEB_CURRICULUM_MAP[subj][level])

st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO - V3.7.9.1 DEBUG MODE")
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"])
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    if user_type == "Student" and password == STUDENT_PASSWORD: st.session_state["role"] = "Student"; st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD: st.session_state["role"] = "Admin"; st.rerun()
    elif password: st.sidebar.error("Wrong password")

if st.session_state.get("role") == "Admin": show_admin_portal()
elif st.session_state.get("role") == "Student": show_student_portal()
else: st.info("Please login to continue")
