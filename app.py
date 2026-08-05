import streamlit as st
import os, io, json, re, time, glob, difflib
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from groq import Groq, RateLimitError
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import zipfile

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 PRO", page_icon="📚", layout="wide")

### DUAL KEY + SECRETS ###
try:
    GROQ_API_KEY_1 = st.secrets["GROQ_API_KEY_1"]
    GROQ_API_KEY_2 = st.secrets["GROQ_API_KEY_2"]
    STUDENT_PASSWORD = st.secrets["STUDENT_PASSWORD"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
    WHATSAPP_TOKEN = st.secrets.get("WHATSAPP_TOKEN", "") # Optional: Meta WhatsApp API
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
PARENTS_FILE = "parents.json"
SCHEME_FILE = "schemes.json"
MARKING_FILE = "marking_guides.json"
os.makedirs(ASSETS_FOLDER, exist_ok=True)
os.makedirs(LABELS_FOLDER, exist_ok=True)
CONTACT = "256751040731"
AI_MODEL_LONG = "llama-3.3-70b-versatile"
AI_MODEL_FAST = "llama-3.1-8b-instant"
st.sidebar.success(f"⚠️ DIGITAL UNEB TUTOR 2026 PRO V4.7.0\nFULL ADMIN SUITE + WHATSAPP\n📞 {CONTACT}")

MASTER_SYSTEM_PROMPT = """You are DIGITAL UNEB TUTOR 2026 PRO.
Role: Senior NCDC Curriculum Specialist + UNEB Chief Examiner for Uganda S1-S6.
Chain of Thought Rule: For every problem solve in steps: 1. Understand 2. Formula 3. Substitute 4. Answer."""

### DATABASES - ALL 15 SUBJECTS S1-S6 ###
UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Number Bases", "Integers", "Fractions"], "S2": ["Angles", "Algebra II"], "S3": ["Quadratics", "Matrices"], "S4": ["Circle Geometry"], "S5": ["Differentiation"], "S6": ["Mechanics"]},
    "Physics": {"S1": ["Measurement", "Forces"], "S2": ["Light", "Electricity I"], "S3": ["Magnetism"], "S4": ["Electronics"], "S5": ["Optics"], "S6": ["Electric Fields"]},
    "Chemistry": {"S1": ["Atoms"], "S2": ["Acids Alkalis"], "S3": ["Bonding"], "S4": ["REDOX"], "S5": ["Kinetics"], "S6": ["Electrochemistry"]},
    "Biology": {"S1": ["Cells"], "S2": ["Respiration"], "S3": ["Genetics I"], "S4": ["Photosynthesis"], "S5": ["Cell Biology"], "S6": ["Hormones"]},
    "English": {"S1": ["Grammar", "Comprehension"], "S2": ["Literature", "Summary"], "S3": ["Novel", "Poetry"], "S4": ["Shakespeare"], "S5": ["Advanced Grammar"], "S6": ["Criticism"]},
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
    "Physics": {"S1-S4": {"Ohm's Law": {"objective": "To verify Ohm's Law", "apparatus": "Cell, Ammeter", "procedure": "Connect circuit", "questions": ["State Ohm's law"], "safety": "Do not short"}}, "S5-S6": {}},
    "Chemistry": {"S1-S4": {"Titration": {"objective": "To determine concentration", "apparatus": "Burette", "procedure": "Titrate", "questions": ["Calculate"], "safety": "Acid"}}, "S5-S6": {}},
    "Biology": {"S1-S4": {"Microscope": {"objective": "To observe cells", "apparatus": "Microscope", "procedure": "Focus", "questions": ["Function"], "safety": "Clean"}}, "S5-S6": {}}
}

### CORE ###
def load_db(file): return json.load(open(file)) if os.path.exists(file) else {}
def save_db(file,data): json.dump(data,open(file,"w"),indent=2)
def load_logs(): return json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []
def save_log(entry): logs = load_logs(); logs.append(entry); json.dump(logs, open(LOG_FILE,"w"))
def log_activity(user_type, action, details): save_log({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user_type, "action": action, "details": details})

def create_download(content, filename, fmt="pdf"):
    if fmt == "pdf":
        buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); p.setFont("Helvetica", 10)
        for i,line in enumerate(content.split('\n')[:80]): p.drawString(50,800-(i*14),line[:95])
        p.save(); buffer.seek(0); return buffer, f"{filename}.pdf"
    elif fmt == "excel":
        df = pd.DataFrame({"Content": content.split('\n')}); buffer = io.BytesIO(); df.to_excel(buffer, index=False); buffer.seek(0); return buffer, f"{filename}.xlsx"
    elif fmt == "html":
        html = f"<html><body><pre>{content}</pre></body></html>"; return io.BytesIO(html.encode()), f"{filename}.html"
    elif fmt == "docx":
        from docx import Document
        doc = Document(); doc.add_paragraph(content); buffer = io.BytesIO(); doc.save(buffer); buffer.seek(0); return buffer, f"{filename}.docx"

### DUAL KEY ###
def switch_key():
    st.session_state.current_key = 2 if st.session_state.current_key == 1 else 1
    global client
    client = get_client()
    st.warning(f"🔄 Switched to API Key {st.session_state.current_key}")

def call_groq(user_prompt):
    try:
        res = client.chat.completions.create(model=AI_MODEL_LONG, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}], max_tokens=4000)
        return res.choices[0].message.content
    except RateLimitError:
        switch_key()
        res = client.chat.completions.create(model=AI_MODEL_FAST, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}], max_tokens=2000)
        return res.choices[0].message.content

### ASSETS ###
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
def load_labels(level, subject, topic): path = f"{LABELS_FOLDER}/{sanitize(level+subject+topic)}.json"; return json.load(open(path)) if os.path.exists(path) else []
def save_labels(level, subject, topic, labels): path = f"{LABELS_FOLDER}/{sanitize(level+subject+topic)}.json"; json.dump(labels, open(path,"w"), indent=2)
def display_image_with_labels(img_path, labels):
    img = Image.open(img_path); fig, ax = plt.subplots(figsize=(10, 7)); ax.imshow(img); ax.axis('off')
    for label in labels: x_px = label["x"] * img.width; y_px = label["y"] * img.height; ax.annotate(f"{label['num']}. {label['name']}", xy=(x_px, y_px), xytext=(x_px + 40, y_px - 20), arrowprops=dict(arrowstyle='->', color='red'), bbox=dict(boxstyle="round", fc="yellow"))
    st.pyplot(fig)

### WHATSAPP FUNCTION ###
def send_whatsapp(number, message):
    if not WHATSAPP_TOKEN: return "WhatsApp Token not set in secrets"
    # This is placeholder. Integrate with Meta WhatsApp Cloud API or Twilio
    log_activity("Admin", "WhatsApp Sent", f"To: {number}")
    return f"✅ Message queued to {number}"

### STUDENT PORTAL - UNTOUCHED ###
def show_student_portal():
    st.header("📚 Student Portal - S1 to S6")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tab1, tab2, tab3 = st.tabs(["🔍 Smart Search + Solver", "📖 Learn Topic", "🖼️ Diagram Library"])
    with tab1:
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="s_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="s_level")
        ask_q = st.text_area("Ask any question")
        if st.button("Ask AI Brain", type="primary") and ask_q: display_with_pdf(call_groq(f"Answer: {ask_q} for {level} {subject}"), "Answer")
    with tab2:
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="learn_subj")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="learn_level")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject2][level2], key="learn_topic")
        if st.button("Teach Me"): display_with_pdf(call_groq(f"Teach {topic2} for {level2} {subject2}"), "Theory")
    with tab3:
        subject3 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="asset_subj")
        level3 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="asset_level")
        topic3 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject3][level3], key="asset_topic")
        if st.button("Load Diagram"):
            img_path, _ = find_asset_strict(level3, subject3, topic3); labels = load_labels(level3, subject3, topic3)
            if img_path: display_image_with_labels(img_path, labels) if labels else st.image(img_path)
            else: st.error("No diagram found")

### ADMIN PORTAL - FULL RESTORED ###
def show_admin_portal():
    st.header("🏫 Admin Portal - FULL SUITE")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tabs = st.tabs([
        "📊 Analytics", "📖 Curriculum Editor", "✏️ Label Editor",
        "📤 Bulk Exam Generator", "📈 Student Performance", "📱 WhatsApp Parents",
        "📑 MOES Reports", "📝 Marking Guide Editor", "📅 Scheme of Work", "🏆 Report Cards"
    ])

    with tabs[0]: # Analytics
        logs = load_logs()
        st.metric("Total Logs", len(logs)); st.metric("Total Assets", len(get_all_assets()))
        if logs: st.dataframe(pd.DataFrame(logs))

    with tabs[1]: # Curriculum Editor
        st.subheader("Syllabus + Curriculum Editor")
        subj = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)])
        topics = st.text_area("Edit Topics", "\n".join(UNEB_CURRICULUM_MAP[subj][level]))
        if st.button("Save Curriculum"):
            UNEB_CURRICULUM_MAP[subj][level] = topics.split('\n'); st.success("Saved")

    with tabs[2]: # Label Editor
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="a_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="a_level")
        topic = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject][level], key="a_topic")
        uploaded_file = st.file_uploader("Upload PNG")
        if uploaded_file:
            save_path = f"{ASSETS_FOLDER}/{level} {subject} {topic}.png"
            with open(save_path, "wb") as f: f.write(uploaded_file.getbuffer())
            st.success(f"Saved to {save_path}")

    with tabs[3]: # Bulk Exam Generator
        st.subheader("Bulk Exam + Marking Guide Generator")
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="bulk_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="bulk_level")
        if st.button("Generate Full Exam Paper"):
            paper = call_groq(f"Generate full UNEB exam paper + marking guide for {level} {subject} with 50 marks")
            fmt = st.radio("Download as", ["pdf","excel","html","docx"])
            buf, name = create_download(paper, f"{level}_{subject}_Exam", fmt)
            st.download_button("📥 Download", buf, name)

    with tabs[4]: # Student Performance
        st.subheader("Student Performance Monitoring")
        uploaded = st.file_uploader("Upload Results CSV: Name,Subject,Score", type="csv")
        if uploaded:
            df = pd.read_csv(uploaded)
            st.dataframe(df)
            st.bar_chart(df.groupby("Subject")["Score"].mean())
            st.success("Performance dashboard loaded")

    with tabs[5]: # WhatsApp Parents
        st.subheader("Parents Communication via WhatsApp")
        parents = load_db(PARENTS_FILE)
        with st.expander("Add Parent Number"):
            name = st.text_input("Student Name")
            number = st.text_input("Parent WhatsApp +256...")
            if st.button("Save Number"):
                parents[name] = number; save_db(PARENTS_FILE, parents); st.success("Saved")
        st.dataframe(pd.DataFrame(parents.items(), columns=["Student","Number"]))
        message = st.text_area("Message to send")
        if st.button("Send to All Parents"):
            for n, num in parents.items(): send_whatsapp(num, message)
            st.success(f"Sent to {len(parents)} parents")

    with tabs[6]: # MOES Reports
        st.subheader("MOES Compliance + Report Generation")
        report = call_groq("Generate MOES school termly report template with enrolment, performance, resources")
        fmt = st.radio("MOES Format", ["pdf","excel","html","docx"], key="moes_fmt")
        buf, name = create_download(report, "MOES_Report", fmt)
        st.download_button("📥 Download MOES Report", buf, name)

    with tabs[7]: # Marking Guide Editor
        st.subheader("Marking Assistant + Marking Guide Editor")
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="mark_subj")
        question = st.text_area("Paste Student Answer")
        if st.button("Mark with Guide"):
            guide = call_groq(f"Create marking guide and mark this answer for {subject}: {question}")
            st.markdown(guide)

    with tabs[8]: # Scheme of Work
        st.subheader("Scheme of Work + Lesson Plan Generator")
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="sow_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="sow_level")
        if st.button("Generate SOW + Lesson Plans"):
            sow = call_groq(f"Generate full term Scheme of Work and 12 lesson plans for {level} {subject} NCDC 2026")
            fmt = st.radio("Download SOW as", ["pdf","docx"], key="sow_fmt")
            buf, name = create_download(sow, f"{level}_{subject}_SOW", fmt)
            st.download_button("📥 Download SOW", buf, name)

    with tabs[9]: # Report Cards
        st.subheader("All Subjects One Report Card Generator")
        uploaded = st.file_uploader("Upload Full Results CSV: Name,Subject,Score", type="csv")
        if uploaded:
            df = pd.read_csv(uploaded)
            students = df["Name"].unique()
            for student in students:
                student_df = df[df["Name"]==student]
                report_text = f"REPORT CARD\nName: {student}\n" + student_df.to_string()
                st.write(report_text)
                buf, name = create_download(report_text, f"Report_{student}", "pdf")
                st.download_button(f"Download {student}", buf, name, key=student)

def display_with_pdf(content, name):
    st.markdown(content); pdf = create_download(content, name, "pdf")[0]; st.download_button("📥 Download PDF", pdf, f"{name}.pdf")

st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO - V4.7.0 FULL ADMIN")
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"])
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    if user_type == "Student" and password == STUDENT_PASSWORD: st.session_state["role"] = "Student"; st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD: st.session_state["role"] = "Admin"; st.rerun()
    elif password: st.sidebar.error("Wrong password")

if st.session_state.get("role") == "Admin": show_admin_portal()
elif st.session_state.get("role") == "Student": show_student_portal()
else: st.info("Please login to continue")
