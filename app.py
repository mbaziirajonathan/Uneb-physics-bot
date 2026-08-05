import streamlit as st
import os, io, json, re, time, glob, difflib, requests, random, hashlib, threading
from datetime import datetime
from groq import Groq, RateLimitError

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 PRO", page_icon="📚", layout="wide")
st.sidebar.caption("Build: V5.2.8-FULL-RESTORED-FAST")

### KEEP RENDER AWAKE ###
def keep_alive():
    while True:
        time.sleep(840) # 14 minutes
        try: requests.get(os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8501"))
        except: pass
threading.Thread(target=keep_alive, daemon=True).start()

### 1. AUTO CREATE FILES + FOLDERS ###
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

### 2. SECRETS - RENDER ONLY ###
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
STUDENT_PASSWORD = os.getenv("STUDENT_PASSWORD", "1234")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")

if not GROQ_API_KEY:
    st.error("Missing GROQ_API_KEY. Go to Render > Environment > Add Environment Variable")
    st.stop()

@st.cache_resource
def get_client(): return Groq(api_key=GROQ_API_KEY)
client = get_client()

OFFLINE_MODE = st.sidebar.toggle("🔌 OFFLINE MODE", value=False, key="toggle_offline")
if OFFLINE_MODE: st.sidebar.warning("OFFLINE MODE ON")

def load_cache():
    with open(CACHE_FILE) as f: return json.load(f)
def save_cache(cache):
    with open(CACHE_FILE,"w") as f: json.dump(cache, f, indent=2)
def get_cache_key(prompt, level): return hashlib.md5((prompt + level).encode()).hexdigest()

CONTACT = "256751040731"
AI_MODEL_LONG = "llama-3.3-70b-versatile"
AI_MODEL_FAST = "llama-3.1-8b-instant"
st.sidebar.success(f"⚠️ DIGITAL UNEB TUTOR 2026 PRO V5.2.8\nFULL CURRICULUM RESTORED\n📞 {CONTACT}")

MASTER_SYSTEM_PROMPT = """You are DIGITAL UNEB TUTOR 2026 PRO. AI ASSISTANT ONLY. Follow teacher sample + instructions. NCDC 2026 LOCKED. S1-S4 Simple. S5-S6 Deep. UGANDAN SCENARIO first. Use UNEB format: SCENARIO, ITEM, TASK for questions. Do not hallucinate facts. If unsure, say you don't know."""

### 3. FULL UNEB CURRICULUM RESTORED S1-S6 ###
UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Number Bases", "Fractions", "Decimals", "Integers", "Rates", "Algebra"], "S2": ["Angles", "Bearings", "Similarity", "Linear Equations", "Statistics"], "S3": ["Quadratics", "Trigonometry", "Matrices", "Sequences", "Probability"], "S4": ["Functions", "Calculus Intro", "Vectors", "Statistics II", "Financial Math"], "S5": ["Differentiation", "Integration", "Binomial", "Permutations", "Probability Dist"], "S6": ["Mechanics", "Statistics III", "Complex Numbers", "Linear Programming", "Differential Equations"]},
    "Physics": {"S1": ["Measurement", "Forces", "Energy", "Heat", "Waves"], "S2": ["Light", "Sound", "Electricity I", "Magnetism I", "Density"], "S3": ["Magnetism", "Electricity II", "Radioactivity", "Energy Sources", "Pressure"], "S4": ["Electronics", "Waves II", "Atomic Physics", "Statics", "Dynamics"], "S5": ["Optics", "Current Electricity", "EM Waves", "Fields", "SHM"], "S6": ["Electric Fields", "Magnetic Fields", "Quantum Physics", "Nuclear Physics", "Astrophysics"]},
    "Chemistry": {"S1": ["Atoms", "Elements", "Compounds", "Mixtures", "Air"], "S2": ["Acids Alkalis", "Salts", "Oxygen", "Hydrogen", "Water"], "S3": ["Bonding", "Structure", "Periodic Table", "Metals", "Non-Metals"], "S4": ["REDOX", "Energy Changes", "Rate of Reaction", "Equilibrium", "Organic Intro"], "S5": ["Kinetics", "Equilibrium II", "Energetics", "Organic Chemistry I", "Analytical"], "S6": ["Electrochemistry", "Organic II", "Polymers", "Biochemistry", "Industrial Chemistry"]},
    "Biology": {"S1": ["Cells", "Classification", "Nutrition", "Respiration", "Transport"], "S2": ["Respiration", "Excretion", "Reproduction I", "Ecology I", "Diversity"], "S3": ["Genetics I", "Evolution", "Ecology II", "Physiology", "Health"], "S4": ["Photosynthesis", "Hormones", "Reproduction II", "Genetics II", "Biotechnology"], "S5": ["Cell Biology", "Genetics III", "Physiology II", "Ecology III", "Microbiology"], "S6": ["Hormones II", "Coordination", "Genetics IV", "Evolution II", "Environmental Biology"]},
    "English": {"S1": ["Grammar", "Composition", "Comprehension", "Oral Literature", "Vocabulary"], "S2": ["Literature", "Poetry", "Drama", "Novel", "Summary"], "S3": ["Novel", "Play", "Poetry Anthology", "Grammar II", "Writing Skills"], "S4": ["Shakespeare", "African Literature", "Grammar III", "Oral Skills", "Literary Devices"], "S5": ["Advanced Grammar", "Criticism", "Drama Analysis", "Novel Analysis", "Poetry Analysis"], "S6": ["Criticism II", "Comparative Literature", "Research", "Advanced Composition", "Oral Literature II"]},
    "ICT": {"S1": ["Computer Basics", "Hardware", "Software", "OS", "Applications"], "S2": ["Word Processing", "Spreadsheets", "Presentation", "Internet Basics", "Safety"], "S3": ["Databases", "Networking", "Graphics", "Programming Intro", "Web Basics"], "S4": ["Internet", "Multimedia", "Programming Python", "Database Design", "E-Commerce"], "S5": ["Programming Python", "Data Structures", "Web Design", "Mobile Apps", "AI Intro"], "S6": ["Web Design", "Database Systems", "System Analysis", "Networking II", "Project"]},
    "Geography": {"S1": ["Map Reading", "Weather", "Climate", "Vegetation", "Population"], "S2": ["Climate", "Soils", "Rivers", "Lakes", "Landforms"], "S3": ["Rivers", "Weathering", "Mass Wasting", "Glaciation", "Coasts"], "S4": ["Population", "Settlement", "Agriculture", "Industry", "Trade"], "S5": ["Industries", "Transport", "Tourism", "Energy", "Urbanization"], "S6": ["GIS", "Remote Sensing", "Development", "Environment", "Fieldwork"]},
    "History": {"S1": ["Early Man", "Stone Age", "Iron Age", "Kingdoms Intro", "Trade"], "S2": ["Kingdoms", "Buganda", "Bunyoro", "Migration", "Islam"], "S3": ["Colonialism", "Scramble", "Resistance", "Colonial Economy", "Social Services"], "S4": ["Independence", "Political Parties", "Nationalism", "Constitutions", "Post Independence"], "S5": ["World Wars", "UN", "Cold War", "Decolonization", "Regional Organizations"], "S6": ["Cold War", "Middle East", "China", "Africa Since 1960", "Globalization"]},
    "CRE": {"S1": ["Creation", "Fall", "Abraham", "Moses", "Exodus"], "S2": ["Prophets", "Kings", "Exile", "Return", "Jesus Birth"], "S3": ["Jesus Ministry", "Parables", "Miracles", "Disciples", "Teachings"], "S4": ["Church", "Early Church", "Paul", "Letters", "Christian Living"], "S5": ["Ethics", "Human Sexuality", "Marriage", "Work", "Law"], "S6": ["Comparative Religion", "Islam", "African Religion", "Secularism", "Apologetics"]},
    "IRE": {"S1": ["Tawheed", "Prophets", "Quran", "Pillars", "Akhlak"], "S2": ["Quran", "Hadith", "Sunnah", "Fiqh Basics", "History"], "S3": ["Fiqh", "Ibada", "Muamalat", "Family", "Ethics"], "S4": ["History", "Khulafa", "Islam in Africa", "Sects", "Jihad"], "S5": ["Islamic Law", "Economics", "Politics", "Education", "Women"], "S6": ["Comparative Religion", "Dawah", "Modern Issues", "Ijtihad", "Islam and Science"]},
    "Literature": {"S1": ["Poetry", "Prose", "Drama", "Oral Lit", "Figures"], "S2": ["Drama", "Novel", "Poetry", "Themes", "Characters"], "S3": ["African Literature", "Novel", "Play", "Poetry", "Setting"], "S4": ["Shakespeare", "Modern Drama", "African Novel", "Poetry", "Criticism"], "S5": ["Literary Devices", "Themes", "Style", "Context", "Analysis"], "S6": ["Criticism", "Theory", "Comparative", "Research", "Seminar"]},
    "Commerce": {"S1": ["Business", "Types", "Trade", "Money", "Banking"], "S2": ["Banking", "Insurance", "Communication", "Transport", "Warehousing"], "S3": ["Marketing", "Advertising", "Consumer", "Law", "Tourism"], "S4": ["Entrepreneurship", "Business Plan", "Finance", "Records", "Tax"], "S5": ["Finance", "Investment", "Stock Exchange", "International Trade", "Business Law"], "S6": ["Business Law", "Management", "HR", "Operations", "Strategic Planning"]},
    "Economics": {"S1": ["Scarcity", "Choice", "Production", "Resources", "Goods"], "S2": ["Demand", "Supply", "Price", "Market", "Competition"], "S3": ["Money", "Banking", "Inflation", "Unemployment", "Government"], "S4": ["Trade", "Balance of Payments", "Exchange Rate", "Economic Systems", "Development"], "S5": ["National Income", "Consumption", "Investment", "Fiscal Policy", "Monetary Policy"], "S6": ["Development", "Planning", "International Economics", "Economic Growth", "Uganda Economy"]},
    "Agriculture": {"S1": ["Soil", "Tools", "Crops", "Animals", "Farm Records"], "S2": ["Livestock", "Poultry", "Feeds", "Housing", "Health"], "S3": ["Crop Production", "Planting", "Weeding", "Harvesting", "Storage"], "S4": ["Animal Health", "Breeding", "Nutrition", "Diseases", "Parasites"], "S5": ["Records", "Marketing", "Cooperatives", "Farm Planning", "Irrigation"], "S6": ["Agribusiness", "Processing", "Value Addition", "Policy", "Research"]},
    "Art": {"S1": ["Drawing", "Shading", "Color", "Design", "Craft"], "S2": ["Painting", "Printing", "Weaving", "Pottery", "Composition"], "S3": ["Sculpture", "Carving", "Modelling", "Graphics", "Lettering"], "S4": ["Graphics", "Advertisement", "Layout", "Photography", "Design"], "S5": ["Photography", "Cinematography", "Digital Art", "Exhibition", "Critique"], "S6": ["Art History", "African Art", "Western Art", "Contemporary", "Project"]}
}

### 4. FULL PRACTICALS DATABASE RESTORED S1-S6 ###
PRACTICAL_DATABASE = {
    "Physics": {
        "S1-S4": {"Ohm's Law": {"objective": "Verify Ohm's Law V=IR"}, "Simple Pendulum": {"objective": "Determine g"}, "Refraction": {"objective": "Find refractive index"}, "Hooke's Law": {"objective": "Verify Hooke's Law"}, "Density": {"objective": "Find density of solid"}},
        "S5-S6": {"RC Circuit": {"objective": "Find time constant"}, "Wheatstone Bridge": {"objective": "Find unknown resistance"}, "Photoelectric Effect": {"objective": "Find Planck's constant"}, "Spectrometer": {"objective": "Determine wavelength"}, "Capacitance": {"objective": "Find capacitance"}}
    },
    "Chemistry": {
        "S1-S4": {"Titration": {"objective": "Find concentration of acid"}, "Solubility": {"objective": "Effect of temperature on solubility"}, "Gas Laws": {"objective": "Verify Boyle's Law"}, "Reactions": {"objective": "Rate of reaction"}, "Salts": {"objective": "Identify cations and anions"}},
        "S5-S6": {"Rate of Reaction": {"objective": "Effect of concentration and temperature"}, "Electrolysis": {"objective": "Faraday's Laws"}, "Organic Prep": {"objective": "Prepare Ethyl Ethanoate"}, "Enthalpy": {"objective": "Heat of neutralization"}, "Redox Titration": {"objective": "Determine molarity"}}
    },
    "Biology": {
        "S1-S4": {"Microscope": {"objective": "Observe plant and animal cells"}, "Food Tests": {"objective": "Test for starch, protein, fats"}, "Transpiration": {"objective": "Measure rate of transpiration"}, "Germination": {"objective": "Effect of light on germination"}, "Photosynthesis": {"objective": "Test for starch production"}},
        "S5-S6": {"Enzyme Activity": {"objective": "Effect of pH and temperature"}, "Osmosis": {"objective": "Water potential in plant tissue"}, "DNA Extraction": {"objective": "Extract DNA from onion"}, "Population Study": {"objective": "Quadrat sampling"}, "Blood Smear": {"objective": "Observe blood cells"}}
    }
}

### 5. LAZY IMPORTS FOR SPEED ###
def get_pandas(): import pandas as pd; return pd
def get_pil(): from PIL import Image; return Image
def get_plt(): import matplotlib.pyplot as plt; return plt
def get_fitz(): import fitz; return fitz
def get_docx(): from docx import Document; return Document
def get_canvas(): from reportlab.pdfgen import canvas; from reportlab.lib.pagesizes import A4; return canvas, A4

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
        fitz = get_fitz(); doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in doc])
    elif uploaded_file.name.endswith(".docx"):
        Document = get_docx(); doc = Document(uploaded_file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif uploaded_file.name.endswith(".txt"):
        return uploaded_file.read().decode()
    return ""

@st.cache_data
def generate_file_bytes(content, fmt):
    if fmt == "pdf":
        canvas, A4 = get_canvas(); buffer = io.BytesIO(); p = canvas(buffer, pagesize=A4); p.setFont("Helvetica", 10)
        for i,line in enumerate(content.split('\n')[:90]): p.drawString(50,800-(i*14),line[:100])
        p.save(); buffer.seek(0); return buffer.getvalue()
    elif fmt == "excel":
        pd = get_pandas(); df = pd.DataFrame({"Content": content.split('\n')}); buffer = io.BytesIO(); df.to_excel(buffer, index=False, engine='openpyxl'); buffer.seek(0); return buffer.getvalue()
    elif fmt == "html":
        html = f"<html><body><pre>{content}</pre></body></html>"; return html.encode()
    elif fmt == "docx":
        Document = get_docx(); doc = Document(); doc.add_paragraph(content); buffer = io.BytesIO(); doc.save(buffer); buffer.seek(0); return buffer.getvalue()

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

### 6. FAST AI WITH SMART MODEL ROUTING ###
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

    placeholder = st.empty()
    full_response = ""
    # SMART ROUTING: 70B only for bulk/50Q
    model_to_use = AI_MODEL_LONG if "Generate 50" in user_prompt or "Bulk" in user_prompt else AI_MODEL_FAST
    try:
        stream = client.chat.completions.create(model=model_to_use, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":full_prompt}], max_tokens=2500, stream=True)
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)
    except Exception as e:
        st.warning(f"Fast model failed. Trying 70B: {e}")
        res = client.chat.completions.create(model=AI_MODEL_LONG, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":full_prompt}], max_tokens=3000)
        full_response = res.choices[0].message.content
        st.markdown(full_response)

    cache[key] = full_response
    save_cache(cache)
    st.success("✅ Saved to Local Cache for next time")
    return full_response

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
    Image = get_pil(); img = Image.open(img_path)
    zoom = st.slider("Zoom %", 50, 200, 100, key=f"zoom_{img_path}_{time.time()}")
    width = int(img.width * zoom / 100)
    st.image(img.resize((width, int(img.height * zoom / 100))))
def display_with_preview(content, name):
    edited = st.text_area("AI Preview - EDIT BEFORE DOWNLOAD", content, height=350, key=f"preview_{name}")
    cols = st.columns(4)
    formats = ["pdf","excel","html","docx"]
    for i, fmt in enumerate(formats):
        if cols[i].button(f"📥 {fmt.upper()}", key=f"btn_dl_{name}_{fmt}"):
            data = generate_file_bytes(edited, fmt)
            st.download_button(label=f"Click to download {fmt.upper()}", data=data, file_name=f"{name}.{fmt}", mime="application/octet-stream", key=f"dl_{name}_{fmt}_{hash(data)}")

def teacher_input_section(tab_name):
    st.info(f"🤖 AI Assistant Mode: Upload sample. Type instructions. AI follows.")
    col1, col2 = st.columns(2)
    with col1: sample_file = st.file_uploader(f"Upload Sample for {tab_name}", type=["pdf","docx","txt"], key=f"sample_{tab_name}")
    with col2: instructions = st.text_area(f"Teacher Instructions for {tab_name}", key=f"instr_{tab_name}")
    sample_text = read_uploaded_file(sample_file) if sample_file else ""
    return sample_text, instructions

### 7. STUDENT PORTAL - ALL KEYS UNIQUE ###
def show_student_portal():
    st.header("📚 Student Portal - SMART MODE")
    if st.button("Logout", key="btn_logout_student"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Smart Search", "📖 Learn Topic", "🧪 Practicals", "🖼️ Diagram Library"])

    with tab1:
        st.subheader("Ask the AI Anything")
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="s1_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="s1_level")
        difficulty = st.selectbox("Difficulty", ["Mixed","Easy","Moderate","Hard"], key="s1_diff")
        ask_q = st.text_area("Ask anything", key="s1_ask")
        if st.button("Ask AI", key="s1_btn") and ask_q:
            ans = call_groq(f"Difficulty: {difficulty}. {ask_q}", level)
            display_with_preview(ans, "Answer_s1")

    with tab2:
        st.subheader("Generate Content for a Topic")
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="s2_subj")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="s2_level")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject2][level2], key="s2_topic")
        mode = st.radio("Mode", ["Theory","AOI","Practicals","Quiz","Bulk Quiz"], key="s2_mode")
        difficulty2 = st.selectbox("Difficulty", ["Mixed","Easy","Moderate","Hard"], key="s2_diff")
        if mode == "Theory" and st.button("Generate Notes", key="s2_btn_notes"):
            notes = call_groq(f"Generate detailed notes on {topic2} for {level2} {subject2}. Difficulty: {difficulty2}", level2)
            display_with_preview(notes, "Notes_s2")
        elif mode == "AOI" and st.button("Generate AOI Questions", key="s2_btn_aoi"):
            aoi = call_groq(f"Generate 5 Areas Of Interaction questions on {topic2} for {level2} {subject2}", level2)
            display_with_preview(aoi, "AOI_s2")
        elif mode == "Practicals" and st.button("Generate Practical", key="s2_btn_prac"):
            group = get_level_group(level2); prac_db = PRACTICAL_DATABASE.get(subject2, {}).get(group, {})
            prac_name = list(prac_db.keys())[0] if prac_db else topic2; objective = prac_db.get(prac_name, {}).get("objective", "")
            prac = call_groq(f"Generate UNEB practical experiment: {prac_name}. Objective: {objective}. Include: Aim, Apparatus, Procedure, Observations, Conclusion for {level2} {subject2}", level2)
            display_with_preview(prac, f"Practical_{prac_name}_s2")
        elif mode == "Quiz" and st.button("Generate Quiz", key="s2_btn_quiz"):
            topics = get_mixed_topics(level2, subject2); quiz = call_groq(f"Generate 10 UNEB questions from: {topics}. Difficulty: {difficulty2}", level2)
            display_with_preview(quiz, "Quiz_s2")
        elif mode == "Bulk Quiz" and st.button("Generate 50Q Exam", key="s2_btn_bulk"):
            topics = get_mixed_topics(level2, subject2); exam = call_groq(f"Generate 50 UNEB questions from: {topics}. Difficulty: {difficulty2}. Use SCENARIO, ITEM, TASK format.", level2)
            display_with_preview(exam, "BulkQuiz_s2")

    with tab3:
        st.subheader("🧪 Practical Experiments from DATABASE")
        subject3 = st.selectbox("Subject", list(PRACTICAL_DATABASE.keys()), key="s3_subj")
        level3 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="s3_level")
        group = get_level_group(level3); prac_list = list(PRACTICAL_DATABASE.get(subject3, {}).get(group, {}).keys())
        if not prac_list: st.warning("No practicals in database for this level"); topic3 = None
        else: topic3 = st.selectbox("Select Practical", prac_list, key="s3_topic")
        if st.button("Generate Full Practical", key="s3_btn") and topic3:
            objective = PRACTICAL_DATABASE[subject3][group][topic3]["objective"]
            practical = call_groq(f"Generate complete UNEB practical for {topic3}. Objective: {objective}. Include: Title, Aim, Materials, Procedure, Data Table, Questions, Conclusion. Ugandan context.", level3)
            display_with_preview(practical, f"Practical_{topic3}_s3")

    with tab4:
        st.subheader("View Diagrams")
        subject4 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="s4_subj")
        level4 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="s4_level")
        topic4 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject4][level4], key="s4_topic")
        if st.button("Load Diagram", key="s4_btn"):
            img_path,_ = find_asset_strict(level4, subject4, topic4)
            if img_path: display_image_with_zoom(img_path)
            else: st.error("No diagram uploaded for this topic")

### 8. ADMIN PORTAL ###
def show_admin_portal():
    st.header("🏫 Admin Portal - TEACHER DRIVEN AI")
    if st.button("Logout", key="btn_logout_admin"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
    tabs = st.tabs(["📊 Analytics","📖 Curriculum","✏️ Labels","📤 Exam Generator","📈 Performance","📱 WhatsApp","📑 MOES","📝 Marking","📅 SOW","🏆 Report Cards"])
    with tabs[0]: st.dataframe(pd.DataFrame(load_logs()))

st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO - V5.2.8")
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"], key="radio_login")
password = st.sidebar.text_input("Password", type="password", key="input_password")
if st.sidebar.button("Login", key="btn_login"):
    if user_type == "Student" and password == STUDENT_PASSWORD: st.session_state["role"] = "Student"; st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD: st.session_state["role"] = "Admin"; st.rerun()
    elif password: st.sidebar.error("Wrong password")

if st.session_state.get("role") == "Admin": show_admin_portal()
elif st.session_state.get("role") == "Student": show_student_portal()
else: st.info("Please login")
