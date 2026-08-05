import streamlit as st
import os, io, json, re, time, glob, difflib, requests
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from groq import Groq, RateLimitError
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 PRO", page_icon="📚", layout="wide")

### SECRETS + DUAL KEY ###
try:
    GROQ_API_KEY_1 = st.secrets["GROQ_API_KEY_1"]
    GROQ_API_KEY_2 = st.secrets["GROQ_API_KEY_2"]
    STUDENT_PASSWORD = st.secrets["STUDENT_PASSWORD"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
    WHATSAPP_TOKEN = st.secrets.get("WHATSAPP_TOKEN", "")
    WHATSAPP_PHONE_ID = st.secrets.get("WHATSAPP_PHONE_ID", "")
except:
    st.error("Set GROQ_API_KEY_1, GROQ_API_KEY_2, STUDENT_PASSWORD, ADMIN_PASSWORD in Streamlit secrets")
    st.stop()

if "current_key" not in st.session_state: st.session_state.current_key = 1
def get_client():
    key = GROQ_API_KEY_1 if st.session_state.current_key == 1 else GROQ_API_KEY_2
    return Groq(api_key=key)
client = get_client()

### FILES + FOLDERS ###
LOG_FILE = "usage_log.json"
ASSETS_FOLDER = "assets"
LABELS_FOLDER = "assets/labels"
PARENTS_FILE = "parents.json"
os.makedirs(ASSETS_FOLDER, exist_ok=True)
os.makedirs(LABELS_FOLDER, exist_ok=True)
CONTACT = "256751040731"
AI_MODEL_LONG = "llama-3.3-70b-versatile"
AI_MODEL_FAST = "llama-3.1-8b-instant"
st.sidebar.success(f"⚠️ DIGITAL UNEB TUTOR 2026 PRO V4.9.0\nSMART GPT-LIKE + NCDC 2026 LOCKED\n📞 {CONTACT}")

### NEW SMART SYSTEM PROMPT - GPT LIKE + UNEB + LEVEL AWARE ###
MASTER_SYSTEM_PROMPT = """You are DIGITAL UNEB TUTOR 2026 PRO. You are a Smart AI Tutor like ChatGPT, but 100% locked to Uganda NCDC 2026 Curriculum and UNEB standards.

CORE IDENTITY:
1. You answer EVERY question specifically to what the student wants. Be direct, helpful, and smart like ChatGPT.
2. You are NCDC 2026 LOCKED. Do not answer anything outside the Uganda S1-S6 NCDC 2026 syllabus. If asked outside, say: "That topic is not in NCDC 2026. Let me teach you a related NCDC topic instead."
3. You are LEVEL AWARE. Detect if student is S1-S4 Lower Secondary or S5-S6 Advanced. Adjust depth automatically.

RESPONSE FORMAT RULES:
For S1-S4 LOWER SECONDARY:
- Use simple English. Ugandan examples. Market, boda, school, farm examples.
- Depth: Basic but clear. Step by step.
- Always start with: "UGANDAN SCENARIO:" then a real life Uganda example to explain.
- Then: "ITEM:" - UNEB style question
- Then: "TASK:" - What the student must do
- Then: "EXPLANATION:" Step by step

For S5-S6 ADVANCED LEVEL:
- Use deeper explanations, formulas, derivations, analysis.
- Depth: University foundation level but still NCDC 2026.
- Still use: "UGANDAN SCENARIO:" but make it A-level context. Example: Factory in Namanve, Research, Engineering.
- Then: "ITEM:" Complex UNEB A-Level style
- Then: "TASK:"
- Then: "DETAILED SOLUTION:" With Chain of Thought: 1.Understand 2.Formula 3.Substitute 4.Answer

GLOBAL RULES:
1. Every answer must have a Ugandan scenario first so students understand.
2. Never hallucinate topics not in NCDC 2026.
3. Be smart, conversational, and specific like ChatGPT. Don't be robotic.
4. If student asks "explain simply" → give S1-S4 style. If "explain deeply" → give S5-S6 style.
5. Cover ALL 15 SUBJECTS: Maths, Physics, Chemistry, Biology, English, ICT, Geography, History, CRE, IRE, Literature, Commerce, Economics, Agriculture, Art."""

### FULL DATABASE - 15 SUBJECTS S1-S6 ###
UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Number Bases", "Integers", "Fractions", "Cartesian Coordinates", "Percentages", "Algebra I"], "S2": ["Patterns", "Bearings", "Angles", "Algebra II", "Sets", "Rates"], "S3": ["Quadratics", "Matrices", "Probability", "Vectors", "Similarity", "Trigonometry I"], "S4": ["Functions", "3D Geometry", "Statistics", "Circle Geometry", "Binomials"], "S5": ["Differentiation", "Integration", "Permutations", "Complex Numbers"], "S6": ["Differential Equations", "Mechanics", "Statistics II", "Linear Programming"]},
    "Physics": {"S1": ["Measurement", "Forces", "Work Energy Power", "Density", "Pressure"], "S2": ["Light", "Thermal Physics", "Electricity I", "Waves I", "Sound"], "S3": ["Electricity II", "Magnetism", "Waves II", "Atomic Physics"], "S4": ["Electromagnetism", "Electronics", "Radioactivity", "Astrophysics"], "S5": ["Gravitation", "Optics", "Fluid Mechanics", "Thermal Physics II"], "S6": ["Electric Fields", "Magnetic Fields", "Nuclear Physics", "Quantum Physics"]},
    "Chemistry": {"S1": ["States of Matter", "Mixtures", "Atoms", "Compounds"], "S2": ["Acids Alkalis", "Salts", "Air", "Water"], "S3": ["Bonding", "Stoichiometry", "Electrolysis", "Energy Changes"], "S4": ["REDOX", "Organic II", "Rate of Reaction", "Equilibrium I"], "S5": ["Energetics", "Kinetics", "Equilibrium II", "Acids and Bases"], "S6": ["Electrochemistry", "Organic III", "Industrial Chemistry"]},
    "Biology": {"S1": ["Cells", "Classification", "Nutrition in Plants", "Diversity"], "S2": ["Soil", "Nutrition in Animals", "Respiration", "Excretion"], "S3": ["Respiration", "Genetics I", "Reproduction", "Growth"], "S4": ["Coordination", "Ecology", "Photosynthesis", "Transport"], "S5": ["Cell Biology", "Enzymes", "Genetics II", "Microbiology"], "S6": ["Hormones", "Biotechnology", "Evolution", "Ecosystems"]},
    "English": {"S1": ["Grammar", "Comprehension", "Composition", "Parts of Speech"], "S2": ["Literature", "Summary", "Letter Writing", "Punctuation"], "S3": ["Novel", "Poetry", "Oral Skills", "Essay Writing"], "S4": ["Shakespeare", "Functional Writing", "Report Writing"], "S5": ["Advanced Grammar", "Literary Devices"], "S6": ["Literary Appreciation", "Criticism"]},
    "ICT": {"S1": ["Computer Basics","Hardware"],"S2": ["Word Processing","Spreadsheets"],"S3": ["Databases","Presentations"],"S4": ["Internet","Graphics"],"S5": ["Programming Python"],"S6": ["Web Design","Networks"]},
    "Geography": {"S1": ["Map Reading","Vegetation"],"S2": ["Climate","Soils"],"S3": ["Rivers","Lakes"],"S4": ["Population","Urbanization"],"S5": ["Industries","Mining"],"S6": ["GIS","Tourism"]},
    "History": {"S1": ["Early Man","Stone Age"],"S2": ["Kingdoms","Trade"],"S3": ["Colonialism","Scramble"],"S4": ["Independence","Governments"],"S5": ["World Wars","UNO"],"S6": ["Cold War","Decolonization"]},
    "CRE": {"S1": ["Creation","Fall"],"S2": ["Prophets","Covenants"],"S3": ["Jesus","Parables"],"S4": ["Church","Sacraments"],"S5": ["Ethics","Social Justice"],"S6": ["Comparative","World Religions"]},
    "IRE": {"S1": ["Tawheed","Prophets"],"S2": ["Quran","Hadith"],"S3": ["Fiqh","Pillars"],"S4": ["History","Sirah"],"S5": ["Islamic Law"],"S6": ["Comparative Religion"]},
    "Literature": {"S1": ["Poetry","Prose"],"S2": ["Drama","Novel"],"S3": ["African Literature"],"S4": ["Shakespeare","Essays"],"S5": ["Literary Devices"],"S6": ["Criticism"]},
    "Commerce": {"S1": ["Business","Trade"],"S2": ["Banking","Insurance"],"S3": ["Marketing","Advertising"],"S4": ["Entrepreneurship"],"S5": ["Finance"],"S6": ["Business Law"]},
    "Economics": {"S1": ["Scarcity","Needs"],"S2": ["Demand","Supply"],"S3": ["Money","Banking"],"S4": ["Trade","Taxation"],"S5": ["National Income"],"S6": ["Development","International Trade"]},
    "Agriculture": {"S1": ["Soil","Crops"],"S2": ["Livestock","Tools"],"S3": ["Crop Production"],"S4": ["Animal Health"],"S5": ["Records","Marketing"],"S6": ["Agribusiness"]},
    "Art": {"S1": ["Drawing","Color"],"S2": ["Painting","Design"],"S3": ["Sculpture","Craft"],"S4": ["Graphics","Textiles"],"S5": ["Photography"],"S6": ["Art History"]}
}

### FULL PRACTICAL DATABASE S1-S6 ###
PRACTICAL_DATABASE = {
    "Physics": {"S1-S4": {"Ohm's Law": {"objective": "To verify Ohm's Law V=IR", "apparatus": "Cell, Ammeter, Voltmeter, Rheostat", "procedure": "Connect circuit, vary rheostat, record V and I.", "questions": ["State Ohm's law"], "safety": "Do not short circuit"}, "Simple Pendulum": {"objective": "To determine g", "apparatus": "Bob, String, Stopwatch", "procedure": "Time 20 oscillations", "questions": ["What affects period"], "safety": "Secure support"}}, "S5-S6": {"RC Circuit": {"objective": "To determine time constant", "apparatus": "Capacitor, Resistor", "procedure": "Charge and discharge", "questions": ["Define tau"], "safety": "Discharge capacitor"}}},
    "Chemistry": {"S1-S4": {"Titration": {"objective": "To determine concentration of NaOH", "apparatus": "Burette, Pipette", "procedure": "Titrate with base", "questions": ["Calculate molarity"], "safety": "Acid burns"}, "Separation of Mixtures": {"objective": "To separate sand and salt", "apparatus": "Beaker, Filter paper", "procedure": "Dissolve, Filter, Evaporate", "questions": ["Name methods"], "safety": "Wear goggles"}}, "S5-S6": {"Rate of Reaction": {"objective": "Effect of temperature", "apparatus": "Mg, HCl", "procedure": "Time gas produced", "questions": ["Plot graph"], "safety": "HCl fumes"}}},
    "Biology": {"S1-S4": {"Use of Microscope": {"objective": "To observe cells", "apparatus": "Microscope, Slide", "procedure": "Place specimen, Focus", "questions": ["Function of nucleus"], "safety": "Clean lens"}, "Food Tests": {"objective": "To test for nutrients", "apparatus": "Iodine, Benedict's", "procedure": "Add reagents", "questions": ["Test for protein"], "safety": "Do not taste"}}, "S5-S6": {"Enzyme Action": {"objective": "Effect of pH on amylase", "apparatus": "Amylase, Starch", "procedure": "Mix at different pH", "questions": ["Optimum pH"], "safety": "Sterile"}}}
}

### CORE FUNCTIONS ###
def load_db(file): return json.load(open(file)) if os.path.exists(file) else {}
def save_db(file,data): json.dump(data,open(file,"w"),indent=2)
def load_logs(): return json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []
def save_log(entry): logs = load_logs(); logs.append(entry); json.dump(logs, open(LOG_FILE,"w"))
def log_activity(user_type, action, details): save_log({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user_type, "action": action, "details": details})

def create_download(content, filename, fmt="pdf"):
    if fmt == "pdf":
        buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); p.setFont("Helvetica", 10)
        for i,line in enumerate(content.split('\n')[:90]): p.drawString(50,800-(i*14),line[:100])
        p.save(); buffer.seek(0); return buffer, f"{filename}.pdf"
    elif fmt == "excel":
        df = pd.DataFrame({"Content": content.split('\n')}); buffer = io.BytesIO(); df.to_excel(buffer, index=False); buffer.seek(0); return buffer, f"{filename}.xlsx"
    elif fmt == "html":
        html = f"<html><body><pre>{content}</pre></body></html>"; return io.BytesIO(html.encode()), f"{filename}.html"
    elif fmt == "docx":
        try:
            from docx import Document
            doc = Document(); doc.add_paragraph(content); buffer = io.BytesIO(); doc.save(buffer); buffer.seek(0); return buffer, f"{filename}.docx"
        except: return create_download(content, filename, "pdf")

### DUAL KEY ###
def switch_key():
    st.session_state.current_key = 2 if st.session_state.current_key == 1 else 1
    global client
    client = get_client()
    st.warning(f"🔄 Switched to API Key {st.session_state.current_key}")

def call_groq(user_prompt, level="S1"):
    level_instruction = "This is a LOWER SECONDARY S1-S4 student. Use simple Ugandan examples." if int(level[1]) <=4 else "This is an ADVANCED LEVEL S5-S6 student. Give deep detailed explanations."
    full_prompt = f"{level_instruction}\n\nStudent Question: {user_prompt}"
    try:
        res = client.chat.completions.create(model=AI_MODEL_LONG, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":full_prompt}], max_tokens=4000, temperature=0.7)
        return res.choices[0].message.content
    except RateLimitError:
        switch_key()
        res = client.chat.completions.create(model=AI_MODEL_FAST, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":full_prompt}], max_tokens=2000)
        return res.choices[0].message.content

### ASSETS ENGINE ###
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
    for label in labels: x_px = label["x"] * img.width; y_px = label["y"] * img.height; ax.annotate(f"{label['num']}. {label['name']}", xy=(x_px, y_px), xytext=(x_px + 40, y_px - 20), arrowprops=dict(arrowstyle='->', color='red', lw=2), bbox=dict(boxstyle="round", fc="yellow", alpha=0.9))
    st.pyplot(fig)

def generate_practical(subject, level, prac_name):
    level_group = "S1-S4" if int(level[1]) <= 4 else "S5-S6"
    data = PRACTICAL_DATABASE.get(subject,{}).get(level_group,{}).get(prac_name,{})
    if not data: return "Practical not found in database"
    prompt = f"Expand this NCDC practical into full UNEB report format: {data} for {subject} {level}"
    return call_groq(prompt, level)

def display_with_pdf(content, name):
    st.markdown(content)
    for f in re.findall(r'\$(.*?)\$', content): st.latex(f)
    buf, fname = create_download(content, name, "pdf"); st.download_button("📥 Download PDF", buf, fname, key=f"dl_{name}_{time.time()}")

### WHATSAPP SEND ###
def send_whatsapp(number, message):
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID: return "Set WHATSAPP_TOKEN and WHATSAPP_PHONE_ID in secrets"
    url = f"https://graph.facebook.com/v20.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": number, "type": "text", "text": {"body": message}}
    try:
        r = requests.post(url, headers=headers, json=data)
        log_activity("Admin", "WhatsApp Sent", f"To: {number}")
        return "✅ Sent" if r.status_code == 200 else f"❌ Error: {r.text}"
    except: return "❌ Failed to send"

### STUDENT PORTAL - FULL 3 TABS RESTORED ###
def show_student_portal():
    st.header("📚 Student Portal - S1 to S6 - SMART GPT-LIKE TUTOR")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tab1, tab2, tab3 = st.tabs(["🔍 Smart Search + Solver", "📖 Learn Topic", "🖼️ Diagram Library"])

    with tab1:
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="search_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="search_level")
        ask_q = st.text_area("Ask me anything. I will use Ugandan examples.")
        if st.button("Ask AI Brain", type="primary") and ask_q:
            log_activity("Student", "Ask Question", ask_q)
            ans = call_groq(ask_q, level)
            display_with_pdf(ans, "Answer")

    with tab2:
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="learn_subj")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="learn_level")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject2][level2], key="learn_topic")
        mode = st.radio("Mode", ["📖 Theory", "🧠 AOI", "🧪 Practicals Lab", "📝 UNEB Quiz Mode", "📚 Bulk Revision"])

        if mode == "📖 Theory" and st.button("Teach Me"):
            raw = call_groq(f"Teach me {topic2} with Ugandan scenario first", level2)
            display_with_pdf(raw, "Theory")
        elif mode == "🧠 AOI" and st.button("Generate Activity of Integration"):
            aoi = call_groq(f"Generate NCDC Activity of Integration for {level2} {subject2} topic: {topic2}. Start with Ugandan scenario", level2)
            display_with_pdf(aoi, "AOI")
        elif mode == "🧪 Practicals Lab":
            level_group = "S1-S4" if int(level2[1]) <= 4 else "S5-S6"
            prac_list = list(PRACTICAL_DATABASE.get(subject2,{}).get(level_group,{}).keys())
            if not prac_list: prac_list = ["No practicals in DB for this subject"]
            prac = st.selectbox("Select Practical", prac_list)
            if st.button("Generate Practical"):
                report = generate_practical(subject2,level2,prac)
                display_with_pdf(report, "Practical")
        elif mode == "📝 UNEB Quiz Mode" and st.button("Generate Quiz"):
            quiz = call_groq(f"Generate 10 UNEB ITEM, TASK, SCENARIO questions with answers on {topic2} for {level2} {subject2}", level2)
            display_with_pdf(quiz, "Quiz")
        elif mode == "📚 Bulk Revision" and st.button("Generate Revision"):
            rev = call_groq(f"Generate full revision notes + 20 questions for {topic2} {level2} {subject2} with Ugandan examples", level2)
            display_with_pdf(rev, "Revision")

    with tab3:
        st.header("🖼️ Diagram Library - Assets Only")
        subject3 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="asset_subj")
        level3 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="asset_level")
        topic3 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject3][level3], key="asset_topic")
        if st.button("Load Diagram", type="primary"):
            log_activity("Student", "Load Diagram", f"{level3}_{subject3}_{topic3}")
            img_path, candidates = find_asset_strict(level3, subject3, topic3)
            labels = load_labels(level3, subject3, topic3)
            if img_path:
                st.success(f"✅ Found: {os.path.basename(img_path)}")
                display_image_with_labels(img_path, labels) if labels else st.image(img_path, use_container_width=True)
                with open(img_path, "rb") as file: st.download_button("📥 Download PNG", file, f"{topic3}.png")
            else:
                st.error(f"❌ No diagram found for {level3} {subject3} - {topic3}")

### ADMIN PORTAL - 10 TABS FULL RESTORED ###
def show_admin_portal():
    st.header("🏫 Admin Portal - FULL SUITE")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tabs = st.tabs([
        "📊 Analytics", "📖 Curriculum Editor", "✏️ Label Editor",
        "📤 Bulk Exam Generator", "📈 Student Performance", "📱 WhatsApp Parents",
        "📑 MOES Reports", "📝 Marking Guide", "📅 Scheme of Work", "🏆 Report Cards"
    ])

    with tabs[0]:
        logs = load_logs()
        st.metric("Total Logs", len(logs)); st.metric("Total Assets", len(get_all_assets()))
        if logs: st.dataframe(pd.DataFrame(logs))

    with tabs[1]:
        st.subheader("Syllabus + Curriculum Editor")
        subj = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)])
        topics = st.text_area("Edit Topics", "\n".join(UNEB_CURRICULUM_MAP[subj][level]))
        if st.button("Save Curriculum"): UNEB_CURRICULUM_MAP[subj][level] = topics.split('\n'); st.success("Saved")

    with tabs[2]:
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="a_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="a_level")
        topic = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject][level], key="a_topic")
        uploaded_file = st.file_uploader("Upload PNG")
        if uploaded_file:
            save_path = f"{ASSETS_FOLDER}/{level} {subject} {topic}.png"
            with open(save_path, "wb") as f: f.write(uploaded_file.getbuffer())
            st.success(f"Saved to {save_path}")

    with tabs[3]:
        st.subheader("Bulk Exam + Marking Guide Generator")
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="bulk_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="bulk_level")
        if st.button("Generate Full Exam Paper"):
            paper = call_groq(f"Generate full UNEB exam paper with SCENARIO, ITEM, TASK format + marking guide for {level} {subject}", level)
            fmt = st.radio("Download as", ["pdf","excel","html","docx"])
            buf, name = create_download(paper, f"{level}_{subject}_Exam", fmt)
            st.download_button("📥 Download", buf, name)

    with tabs[4]:
        st.subheader("Student Performance Monitoring")
        uploaded = st.file_uploader("Upload Results CSV: Name,Subject,Score", type="csv")
        if uploaded:
            df = pd.read_csv(uploaded); st.dataframe(df); st.bar_chart(df.groupby("Subject")["Score"].mean())

    with tabs[5]:
        st.subheader("Parents Communication via WhatsApp")
        parents = load_db(PARENTS_FILE)
        with st.expander("Add Parent Number"):
            name = st.text_input("Student Name")
            number = st.text_input("Parent WhatsApp +256...")
            if st.button("Save Number"): parents[name] = number; save_db(PARENTS_FILE, parents); st.success("Saved")
        st.dataframe(pd.DataFrame(parents.items(), columns=["Student","Number"]))
        message = st.text_area("Message to send")
        if st.button("Send to All Parents"):
            for n, num in parents.items(): st.write(send_whatsapp(num, message))

    with tabs[6]:
        st.subheader("MOES Compliance + Report Generation")
        report = call_groq("Generate MOES school termly report template", "S4")
        fmt = st.radio("MOES Format", ["pdf","excel","html","docx"], key="moes_fmt")
        buf, name = create_download(report, "MOES_Report", fmt)
        st.download_button("📥 Download MOES Report", buf, name)

    with tabs[7]:
        st.subheader("Marking Assistant + Marking Guide Editor")
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="mark_subj")
        question = st.text_area("Paste Student Answer")
        if st.button("Mark with Guide"):
            guide = call_groq(f"Mark this answer and give feedback for {subject}: {question}", "S4")
            st.markdown(guide)

    with tabs[8]:
        st.subheader("Scheme of Work + Lesson Plan Generator")
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="sow_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="sow_level")
        if st.button("Generate SOW + Lesson Plans"):
            sow = call_groq(f"Generate full term Scheme of Work and 12 lesson plans for {level} {subject} NCDC 2026", level)
            buf, name = create_download(sow, f"{level}_{subject}_SOW", "pdf")
            st.download_button("📥 Download SOW", buf, name)

    with tabs[9]:
        st.subheader("All Subjects One Report Card Generator")
        uploaded = st.file_uploader("Upload Full Results CSV: Name,Subject,Score", type="csv")
        if uploaded:
            df = pd.read_csv(uploaded)
            for student in df["Name"].unique():
                student_df = df[df["Name"]==student]
                report_text = f"REPORT CARD\nName: {student}\n" + student_df.to_string()
                buf, name = create_download(report_text, f"Report_{student}", "pdf")
                st.download_button(f"Download {student}", buf, name, key=student)

st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO - V4.9.0 SMART")
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"])
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    if user_type == "Student" and password == STUDENT_PASSWORD: st.session_state["role"] = "Student"; st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD: st.session_state["role"] = "Admin"; st.rerun()
    elif password: st.sidebar.error("Wrong password")

if st.session_state.get("role") == "Admin": show_admin_portal()
elif st.session_state.get("role") == "Student": show_student_portal()
else: st.info("Please login to continue")
