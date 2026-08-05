import streamlit as st
import os, io, json, re, time, glob, difflib, requests, random, hashlib
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from groq import Groq, RateLimitError
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import fitz # PyMuPDF

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 PRO", page_icon="📚", layout="wide")

### 1. AUTO CREATE FILES + FOLDERS - PREVENTS BOOT CRASH + RENDER DISK ###
DATA_PATH = os.getenv("STREAMLIT_DATA_PATH", ".")
LOG_FILE = f"{DATA_PATH}/usage_log.json"
CACHE_FILE = f"{DATA_PATH}/ai_cache.json"
PARENTS_FILE = f"{DATA_PATH}/parents.json"
ASSETS_FOLDER = f"{DATA_PATH}/assets"
LABELS_FOLDER = f"{DATA_PATH}/assets/labels"

for f, default in [(LOG_FILE, []), (CACHE_FILE, {}), (PARENTS_FILE, {})]:
    if not os.path.exists(f):
        with open(f, "w") as fp: json.dump(default, fp)

os.makedirs(ASSETS_FOLDER, exist_ok=True)
os.makedirs(LABELS_FOLDER, exist_ok=True)

### 2. SECRETS + SINGLE KEY ONLY ### [RENDER ONLY - NO st.secrets]
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
STUDENT_PASSWORD = os.getenv("STUDENT_PASSWORD", "1234")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")

if not GROQ_API_KEY:
    st.error("Missing GROQ_API_KEY. Go to Render > Environment > Add Environment Variable")
    st.stop()

@st.cache_resource
def get_client():
    if not GROQ_API_KEY:
        st.stop()
    return Groq(api_key=GROQ_API_KEY)
client = get_client()

### 3. OFFLINE + CACHE SYSTEM ###
OFFLINE_MODE = st.sidebar.toggle("🔌 OFFLINE MODE - No Internet, No Tokens", value=False)
if OFFLINE_MODE:
    st.sidebar.warning("OFFLINE MODE ON. Using local cache only. No API calls.")

def load_cache():
    with open(CACHE_FILE) as f: return json.load(f)
def save_cache(cache):
    with open(CACHE_FILE,"w") as f: json.dump(cache, f, indent=2)

def get_cache_key(prompt, level):
    return hashlib.md5((prompt + level).encode()).hexdigest()

### 4. YOUR DATABASES - RESTORED ###
CONTACT = "256751040731"
AI_MODEL_LONG = "llama-3.3-70b-versatile"
AI_MODEL_FAST = "llama-3.1-8b-instant"
st.sidebar.success(f"⚠️ DIGITAL UNEB TUTOR 2026 PRO V5.2.6\nSINGLE KEY MODE\n📞 {CONTACT}")

MASTER_SYSTEM_PROMPT = """You are DIGITAL UNEB TUTOR 2026 PRO. AI ASSISTANT ONLY. Follow teacher sample + instructions. NCDC 2026 LOCKED. S1-S4 Simple. S5-S6 Deep. UGANDAN SCENARIO first. Use UNEB format: SCENARIO, ITEM, TASK for questions. Do not hallucinate facts. If unsure, say you don't know."""

UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Number Bases"], "S2": ["Angles"], "S3": ["Quadratics"], "S4": ["Functions"], "S5": ["Differentiation"], "S6": ["Mechanics"]},
    "Physics": {"S1": ["Measurement"], "S2": ["Light"], "S3": ["Magnetism"], "S4": ["Electronics"], "S5": ["Optics"], "S6": ["Electric Fields"]},
    "Chemistry": {"S1": ["Atoms"], "S2": ["Acids Alkalis"], "S3": ["Bonding"], "S4": ["REDOX"], "S5": ["Kinetics"], "S6": ["Electrochemistry"]},
    "Biology": {"S1": ["Cells"], "S2": ["Respiration"], "S3": ["Genetics I"], "S4": ["Photosynthesis"], "S5": ["Cell Biology"], "S6": ["Hormones"]},
    "English": {"S1": ["Grammar"], "S2": ["Literature"], "S3": ["Novel"], "S4": ["Shakespeare"], "S5": ["Advanced Grammar"], "S6": ["Criticism"]},
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
    "Physics": {"S1-S4": {"Ohm's Law": {"objective": "Verify V=IR"}}, "S5-S6": {"RC Circuit": {"objective": "Find tau"}}},
    "Chemistry": {"S1-S4": {"Titration": {"objective": "Find concentration"}}, "S5-S6": {"Rate": {"objective": "Effect of temp"}}},
    "Biology": {"S1-S4": {"Microscope": {"objective": "Observe cells"}}, "S5-S6": {"Enzyme": {"objective": "Effect of pH"}}}
}

### 5. CORE FUNCTIONS ###
def load_db(file):
    with open(file) as f: return json.load(f)
def save_db(file,data):
    with open(file,"w") as f: json.dump(data,f,indent=2)
def load_logs():
    with open(LOG_FILE) as f: return json.load(f)
def save_log(entry):
    logs = load_logs(); logs.append(entry); save_db(LOG_FILE, logs)

def read_uploaded_file(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in doc])
    elif uploaded_file.name.endswith(".docx"):
        from docx import Document
        doc = Document(uploaded_file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif uploaded_file.name.endswith(".txt"):
        return uploaded_file.read().decode()
    return ""

def create_download(content, filename, fmt="pdf"):
    if fmt == "pdf":
        buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); p.setFont("Helvetica", 10)
        for i,line in enumerate(content.split('\n')[:90]): p.drawString(50,800-(i*14),line[:100])
        p.save(); buffer.seek(0); return buffer, f"{filename}.pdf"
    elif fmt == "excel":
        df = pd.DataFrame({"Content": content.split('\n')}); buffer = io.BytesIO(); df.to_excel(buffer, index=False, engine='openpyxl'); buffer.seek(0); return buffer, f"{filename}.xlsx"
    elif fmt == "html":
        html = f"<html><body><pre>{content}</pre></body></html>"; return io.BytesIO(html.encode()), f"{filename}.html"
    elif fmt == "docx":
        from docx import Document
        doc = Document(); doc.add_paragraph(content); buffer = io.BytesIO(); doc.save(buffer); buffer.seek(0); return buffer, f"{filename}.docx"

def get_level_group(level):
    n = int(level[1])
    return "S1-S4" if n <= 4 else "S5-S6"

def get_mixed_topics(level, subject):
    level_num = int(level[1])
    topics = []; weights = {level_num: 0.7}
    if level_num-1 >= 1: weights[level_num-1] = 0.2
    if level_num-2 >= 1: weights[level_num-2] = 0.1
    for l, w in weights.items():
        l_str = f"S{l}"
        all_topics = UNEB_CURRICULUM_MAP[subject][l_str]
        num_topics = max(1, int(len(all_topics) * w))
        topics.extend(random.sample(all_topics, min(num_topics, len(all_topics))))
    return topics

### 6. SMART CALL WITH CACHE + NO HALLUCINATION GUARD ###
def call_groq(user_prompt, level="S1", sample="", instructions=""):
    cache = load_cache()
    key = get_cache_key(user_prompt + sample + instructions, level)

    if key in cache:
        st.info("⚡ Loaded from Local Cache. 0 Tokens used.")
        return cache[key]

    if OFFLINE_MODE:
        return "❌ OFFLINE MODE: This question not in cache. Please go online once to generate and cache it."

    level_instruction = "LOWER SECONDARY S1-S4. Simple, Ugandan examples." if int(level[1]) <=4 else "ADVANCED S5-S6. Deep, detailed."
    anti_hallucination = "IMPORTANT: Only answer based on UNEB syllabus and facts. If you don't know, say 'I don't have that information'. Do not make up formulas or data."
    full_prompt = f"{level_instruction}\n{anti_hallucination}\nTEACHER SAMPLE:\n{sample}\nTEACHER INSTRUCTIONS: {instructions}\n\nGENERATE:\n{user_prompt}"

    try:
        res = client.chat.completions.create(model=AI_MODEL_LONG, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":full_prompt}], max_tokens=4000)
        answer = res.choices[0].message.content
    except RateLimitError:
        st.warning("Rate limited. Switching to fast model.")
        res = client.chat.completions.create(model=AI_MODEL_FAST, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":full_prompt}], max_tokens=2000)
        answer = res.choices[0].message.content
    except Exception as e:
        return f"Error calling Groq: {e}"

    cache[key] = answer
    save_cache(cache)
    st.success("✅ Saved to Local Cache for next time")
    return answer

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

def display_image_with_zoom(img_path):
    img = Image.open(img_path)
    zoom = st.slider("Zoom %", 50, 200, 100, key=f"zoom_{img_path}")
    width = int(img.width * zoom / 100)
    st.image(img.resize((width, int(img.height * zoom / 100))))

def display_with_preview(content, name):
    edited = st.text_area("AI Preview - EDIT BEFORE DOWNLOAD", content, height=350, key=f"preview_{name}")
    cols = st.columns(4)
    formats = ["pdf","excel","html","docx"]
    for i, fmt in enumerate(formats):
        buf, fname = create_download(edited, name, fmt)
        cols[i].download_button(f"📥 {fmt.upper()}", buf, fname, key=f"{name}_{fmt}_{time.time()}")

def teacher_input_section(tab_name):
    st.info(f"🤖 AI Assistant Mode: Upload sample. Type instructions. AI follows.")
    col1, col2 = st.columns(2)
    with col1: sample_file = st.file_uploader(f"Upload Sample for {tab_name}", type=["pdf","docx","txt"], key=f"sample_{tab_name}")
    with col2: instructions = st.text_area(f"Teacher Instructions for {tab_name}", key=f"instr_{tab_name}")
    sample_text = read_uploaded_file(sample_file) if sample_file else ""
    return sample_text, instructions

 ### 7. STUDENT PORTAL - ALL KEYS ADDED ###
def show_student_portal():
    st.header("📚 Student Portal - SMART MODE")
    if st.button("Logout", key="btn_logout_student"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Smart Search", "📖 Learn Topic", "🧪 Practicals", "🖼️ Diagram Library"])

    with tab1: # SMART SEARCH
        st.subheader("Ask the AI Anything")
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="tab1_subject")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="tab1_level")
        difficulty = st.selectbox("Difficulty", ["Mixed","Easy","Moderate","Hard"], key="tab1_difficulty")
        ask_q = st.text_area("Ask anything", key="tab1_ask")
        if st.button("Ask AI", key="tab1_btn") and ask_q:
            ans = call_groq(f"Difficulty: {difficulty}. {ask_q}", level)
            display_with_preview(ans, "Answer_tab1")

    with tab2: # LEARN TOPIC
        st.subheader("Generate Content for a Topic")
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="tab2_subject")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="tab2_level")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject2][level2], key="tab2_topic")
        mode = st.radio("Mode", ["Theory","AOI","Practicals","Quiz","Bulk Quiz"], key="tab2_mode")
        difficulty2 = st.selectbox("Difficulty", ["Mixed","Easy","Moderate","Hard"], key="tab2_difficulty")

        if mode == "Theory" and st.button("Generate Notes", key="tab2_btn_notes"):
            notes = call_groq(f"Generate detailed notes on {topic2} for {level2} {subject2}. Difficulty: {difficulty2}", level2)
            display_with_preview(notes, "Notes_tab2")
        elif mode == "AOI" and st.button("Generate AOI Questions", key="tab2_btn_aoi"):
            aoi = call_groq(f"Generate 5 Areas Of Interaction questions on {topic2} for {level2} {subject2}", level2)
            display_with_preview(aoi, "AOI_tab2")
        elif mode == "Practicals" and st.button("Generate Practical", key="tab2_btn_prac"):
            group = get_level_group(level2)
            prac_db = PRACTICAL_DATABASE.get(subject2, {}).get(group, {})
            prac_name = list(prac_db.keys())[0] if prac_db else topic2
            objective = prac_db.get(prac_name, {}).get("objective", "")
            prac = call_groq(f"Generate UNEB practical experiment: {prac_name}. Objective: {objective}. Include: Aim, Apparatus, Procedure, Observations, Conclusion for {level2} {subject2}", level2)
            display_with_preview(prac, f"Practical_{prac_name}_tab2")
        elif mode == "Quiz" and st.button("Generate Quiz", key="tab2_btn_quiz"):
            topics = get_mixed_topics(level2, subject2)
            quiz = call_groq(f"Generate 10 UNEB questions from: {topics}. Difficulty: {difficulty2}", level2)
            display_with_preview(quiz, "Quiz_tab2")
        elif mode == "Bulk Quiz" and st.button("Generate 50Q Exam", key="tab2_btn_bulk"):
            topics = get_mixed_topics(level2, subject2)
            exam = call_groq(f"Generate 50 UNEB questions from: {topics}. Difficulty: {difficulty2}. Use SCENARIO, ITEM, TASK format.", level2)
            display_with_preview(exam, "BulkQuiz_tab2")

    with tab3: # PRACTICALS
        st.subheader("🧪 Practical Experiments from DATABASE")
        subject3 = st.selectbox("Subject", list(PRACTICAL_DATABASE.keys()), key="tab3_subject")
        level3 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="tab3_level")
        group = get_level_group(level3)
        prac_list = list(PRACTICAL_DATABASE.get(subject3, {}).get(group, {}).keys())
        if not prac_list:
            st.warning("No practicals in database for this level")
            topic3 = None
        else:
            topic3 = st.selectbox("Select Practical", prac_list, key="tab3_topic")
        if st.button("Generate Full Practical", key="tab3_btn") and topic3:
            objective = PRACTICAL_DATABASE[subject3][group][topic3]["objective"]
            practical = call_groq(f"Generate complete UNEB practical for {topic3}. Objective: {objective}. Include: Title, Aim, Materials, Procedure, Data Table, Questions, Conclusion. Ugandan context.", level3)
            display_with_preview(practical, f"Practical_{topic3}_tab3")

    with tab4: # DIAGRAM LIBRARY
        st.subheader("View Diagrams")
        subject4 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="tab4_subject")
        level4 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="tab4_level")
        topic4 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject4][level4], key="tab4_topic")
        if st.button("Load Diagram", key="tab4_btn"):
            img_path,_ = find_asset_strict(level4, subject4, topic4)
            if img_path: display_image_with_zoom(img_path)
            else: st.error("No diagram uploaded for this topic")

### 8. ADMIN PORTAL ###
def show_admin_portal():
    st.header("🏫 Admin Portal - TEACHER DRIVEN AI")
    if st.button("Logout"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
    tabs = st.tabs(["📊 Analytics","📖 Curriculum","✏️ Labels","📤 Exam Generator","📈 Performance","📱 WhatsApp","📑 MOES","📝 Marking","📅 SOW","🏆 Report Cards"])

    with tabs[0]: st.dataframe(pd.DataFrame(load_logs()))
    with tabs[1]:
        sample, instr = teacher_input_section("Curriculum")
        subj = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)])
        if st.button("Generate Curriculum Doc"):
            out = call_groq(f"Generate curriculum document for {level} {subj}", level, sample, instr)
            display_with_preview(out, "Curriculum")

    with tabs[2]:
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="a1")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="a2")
        topic = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject][level])
        uploaded = st.file_uploader("Upload PNG Diagram")
        if uploaded:
            with open(f"{ASSETS_FOLDER}/{level} {subject} {topic}.png","wb") as f: f.write(uploaded.getbuffer())
            st.success("Uploaded")

    with tabs[3]:
        sample, instr = teacher_input_section("Exam")
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="ex_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="ex_level")
        num_q = st.slider("Number of Questions", 10, 50, 50)
        difficulty = st.selectbox("Difficulty Mix", ["Mixed","Easy","Moderate","Hard"])
        if st.button("Generate Exam"):
            topics = get_mixed_topics(level, subject)
            prompt = f"Generate {num_q} UNEB exam questions for {level} {subject}. Topics: {topics}. Difficulty: {difficulty}. Use SCENARIO, ITEM, TASK."
            exam = call_groq(prompt, level, sample, instr)
            display_with_preview(exam, f"{level}_{subject}_Exam")

    with tabs[4]:
        sample, instr = teacher_input_section("Performance Report")
        uploaded = st.file_uploader("Upload Results CSV: Name,Subject,Score,Term", type="csv")
        if uploaded:
            df=pd.read_csv(uploaded)
            st.dataframe(df)
            st.bar_chart(df.groupby("Subject")["Score"].mean())
            if st.button("Generate Performance Report"):
                data_summary = df.describe().to_string()
                report = call_groq(f"Generate performance analysis report. Data: {data_summary}", "S4", sample, instr)
                display_with_preview(report, "Performance_Report")

    with tabs[5]:
        parents = load_db(PARENTS_FILE)
        name = st.text_input("Student Name"); number = st.text_input("Number +256")
        if st.button("Save"): parents[name]=number; save_db(PARENTS_FILE, parents); st.success("Saved")
        msg = st.text_area("Message")
        if st.button("Send"): st.warning("WhatsApp needs internet. Disabled in Offline Mode" if OFFLINE_MODE else "Send logic here")

    with tabs[6]:
        sample, instr = teacher_input_section("MOES")
        if st.button("Generate MOES Report"):
            report = call_groq("Generate MOES termly report", "S4", sample, instr)
            display_with_preview(report, "MOES")

    with tabs[7]:
        sample, instr = teacher_input_section("Marking Guide")
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="m1")
        ans = st.text_area("Paste Student Answer")
        if st.button("Mark"):
            marked = call_groq(f"Mark this answer for {subject}. Give marks and feedback. Be accurate.", "S4", sample, instr)
            st.markdown(marked)

    with tabs[8]:
        sample, instr = teacher_input_section("SOW")
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="sow1")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="sow2")
        if st.button("Generate SOW"):
            sow = call_groq(f"Generate SOW + 12 lesson plans for {level} {subject}", level, sample, instr)
            display_with_preview(sow, "SOW")

    with tabs[9]:
        sample, instr = teacher_input_section("Report Card")
        uploaded = st.file_uploader("Upload Results CSV: Name,Subject,Score,Grade,Remarks", type="csv", key="rc")
        if uploaded:
            df = pd.read_csv(uploaded)
            st.dataframe(df)
            for student in df["Name"].unique():
                s_df = df[df["Name"]==student]
                data = s_df.to_string()
                if st.button(f"Generate Report for {student}", key=f"btn_{student}"):
                    report_text = call_groq(f"Generate report card for {student}. Data: {data}", "S4", sample, instr)
                    st.text_area(f"Preview {student}", report_text, height=300, key=f"prev_{student}")
                    buf,fname = create_download(report_text, f"Report_{student}", "pdf")
                    st.download_button(f"Download {student}", buf, fname, key=f"dl{student}")

### 9. MAIN APP ###
st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO - V5.2.6")
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"])
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    if user_type == "Student" and password == STUDENT_PASSWORD: st.session_state["role"] = "Student"; st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD: st.session_state["role"] = "Admin"; st.rerun()
    elif password: st.sidebar.error("Wrong password")

if st.session_state.get("role") == "Admin": show_admin_portal()
elif st.session_state.get("role") == "Student": show_student_portal()
else: st.info("Please login")
