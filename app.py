import streamlit as st
import os, io, json, re, time, difflib, requests, random, hashlib, threading
from datetime import datetime
from groq import Groq, RateLimitError
from difflib import SequenceMatcher

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 PRO", page_icon="📚", layout="wide")
st.sidebar.caption("Build: V5.4.7-DIAGRAM-HOTFIX")

### KEEP RENDER AWAKE ###
def keep_alive():
    while True:
        time.sleep(840)
        try: requests.get(os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8501"))
        except: pass
threading.Thread(target=keep_alive, daemon=True).start()

### 1. AUTO CREATE FILES + FOLDERS ###
DATA_PATH = os.getenv("STREAMLIT_DATA_PATH", ".")
LOG_FILE = f"{DATA_PATH}/usage_log.json"
CACHE_FILE = f"{DATA_PATH}/ai_cache.json"
PARENTS_FILE = f"{DATA_PATH}/parents.json"

def save_db(file,data):
    with open(file,"w") as f: json.dump(data,f,indent=2)

for f, default in [(LOG_FILE, []), (CACHE_FILE, {}), (PARENTS_FILE, {})]:
    if not os.path.exists(f):
        save_db(f, default)

def sanitize(s): return re.sub(r'[^a-z0-9]', '', s.lower())

### 1B. DIAGRAM CACHE ###
DIAGRAM_CACHE = {}

### 2. TTL CACHE CLASS ###
class TTLSchoolCache:
    def __init__(self, ttl_seconds: int = 86400, similarity_threshold: float = 0.75):
        self.ttl = ttl_seconds
        self.threshold = similarity_threshold
        self.cache_file = CACHE_FILE
        self.cache = self.load_from_disk()

    def load_from_disk(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as f:
                data = json.load(f)
                now = time.time()
                clean_data = {k:v for k,v in data.items() if now < v["expires_at"]}
                if len(clean_data)!= len(data): self.save_to_disk(clean_data)
                return clean_data
        return {}

    def save_to_disk(self, data=None):
        if data is None: data = self.cache
        save_db(self.cache_file, data)

    def _clean_text(self, text: str) -> str:
        text = text.strip().lower()
        text = re.sub(r'[^a-z0-9\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text

    def set_answer(self, question: str, answer: str):
        clean_question = self._clean_text(question)
        expire_at = time.time() + self.ttl
        self.cache[clean_question] = {"answer": answer, "expires_at": expire_at, "original_q": question}
        self.save_to_disk()

    def get_answer(self, question: str) -> str:
        clean_question = self._clean_text(question)
        now = time.time()
        if clean_question in self.cache:
            item = self.cache[clean_question]
            if now < item["expires_at"]: return item["answer"]
            else: del self.cache[clean_question]
        best_match = None; best_score = 0; expired_keys = []
        for cached_q, item in self.cache.items():
            if now >= item["expires_at"]: expired_keys.append(cached_q); continue
            score = SequenceMatcher(None, clean_question, cached_q).ratio()
            if score > best_score: best_score = score; best_match = item
        for k in expired_keys: del self.cache[k]
        if best_match and best_score >= self.threshold: return best_match["answer"]
        self.save_to_disk(); return None

    def clear_cache(self): self.cache = {}; self.save_to_disk()
    def get_stats(self):
        now = time.time()
        active = len([v for v in self.cache.values() if now < v["expires_at"]])
        return {"total": len(self.cache), "active": active}

def get_complexity_instructions(level):
    n = int(level[1])
    if n <= 2: return "S1-S2 LOWER SECONDARY. Very simple language. Short sentences. Basic Ugandan examples."
    elif n <= 4: return "S3-S4 UPPER SECONDARY. Intermediate. Explain concepts and apply. Ugandan context."
    else: return "S5-S6 ADVANCED LEVEL. University prep. Deep analysis, derivations, detailed explanations, critical thinking."

ai_cache = TTLSchoolCache(ttl_seconds=86400)

### 3. SECRETS ###
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
STUDENT_PASSWORD = os.getenv("STUDENT_PASSWORD", "1234")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

if not GROQ_API_KEY:
    st.error("Missing GROQ_API_KEY. Go to Render > Environment")
    st.stop()

@st.cache_resource
def get_client(): return Groq(api_key=GROQ_API_KEY)
client = get_client()

OFFLINE_MODE = st.sidebar.toggle("🔌 OFFLINE MODE", value=False, key="toggle_offline")
if OFFLINE_MODE: st.sidebar.warning("OFFLINE MODE ON")

MASTER_SYSTEM_PROMPT = """You are DIGITAL UNEB TUTOR 2026 PRO. NCDC 2026 UGANDA CURRICULUM ONLY.
CORE RULES:
1. ALWAYS answer the question asked directly first. Be smart like ChatGPT/Meta AI.
2. ONLY use UNEB format SCENARIO, ITEM, TASK when the user asks for: 'exam', 'quiz', 'test', '50 questions', 'paper', 'bulk', 'marking guide'.
3. For normal questions like 'give 2 examples', 'explain', 'define': Give a direct, clear answer with Ugandan examples. NO SCENARIO.
4. S1-S2: Simple. S3-S4: Intermediate. S5-S6: Advanced, deep analysis.
5. Always use Ugandan context. Do not hallucinate. If unsure say 'I don't have that information'."""

CONTACT = "256751040731"
AI_MODEL_LONG = "llama-3.3-70b-versatile"
AI_MODEL_FAST = "llama-3.1-8b-instant"
st.sidebar.success(f"⚠️ DIGITAL UNEB TUTOR 2026 PRO V5.4.7\nNCDC 2026 LOCKED\n📞 {CONTACT}")

### 4. ALL 15 SUBJECTS NCDC S1-S6 ###
UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Sets","Number Bases","Integers"], "S2": ["Rates","Percentages","Algebra"], "S3": ["Quadratics","Trigonometry","Probability"], "S4": ["Functions","Vectors","Matrices"], "S5": ["Differentiation","Integration","Binomial"], "S6": ["Mechanics","Statistics III","Complex Numbers"]},
    "Physics": {"S1": ["Measurement","Forces","Energy"], "S2": ["Light I","Sound","Pressure"], "S3": ["Magnetism II","Electricity II","Heat"], "S4": ["Electronics","Waves II","Radioactivity"], "S5": ["Optics II","Current Electricity II","Gravitation"], "S6": ["Electric Fields","Magnetic Fields","Nuclear Physics"]},
    "Chemistry": {"S1": ["Atoms","Elements","Compounds"], "S2": ["Acids Alkalis","Salts","Air"], "S3": ["Bonding","Structure","Periodic Table"], "S4": ["REDOX","Energy Changes","Kinetics I"], "S5": ["Kinetics","Equilibrium II","Acids Bases II"], "S6": ["Electrochemistry","Organic II","Industrial Chemistry"]},
    "Biology": {"S1": ["Cells","Classification","Nutrition"], "S2": ["Respiration II","Excretion","Circulation"], "S3": ["Genetics I","Evolution","Ecology"], "S4": ["Photosynthesis","Hormones I","Reproduction"], "S5": ["Cell Biology","Genetics III","Microbiology"], "S6": ["Hormones II","Coordination","Biotechnology"]},
    "Agriculture": {"S1": ["Introduction","Soil Formation"], "S2": ["Soil Properties","Livestock"], "S3": ["Soil Conservation","Plant Nutrition"], "S4": ["Animal Health","Breeding"], "S5": ["Agribusiness","Farm Planning"], "S6": ["Research","Biotech Agriculture"]},
    "Geography": {"S1": ["Map Reading","Weather"], "S2": ["Vegetation","Soils"], "S3": ["Population","Settlement"], "S4": ["Industrialization","Trade"], "S5": ["Climatology","Geomorphology"], "S6": ["Regional Geography","Field Work"]},
    "History": {"S1": ["Sources of History","Early Man"], "S2": ["Kingdoms of Uganda","Colonialism"], "S3": ["WWI","Nationalism"], "S4": ["Decolonization","Cold War"], "S5": ["EA History","African Nationalism"], "S6": ["International Relations","Genocide"]},
    "Literature": {"S1": ["Oral Literature","Poetry"], "S2": ["Novels","Drama"], "S3": ["Prose","Literary Devices"], "S4": ["African Literature","World Literature"], "S5": ["Critical Analysis","Themes"], "S6": ["Research Project","Comparative Literature"]},
    "CRE": {"S1": ["God and Man","Bible"], "S2": ["Prophets","Jesus"], "S3": ["Church","Sacraments"], "S4": ["Christian Living","Social Issues"], "S5": ["Theology","Ethics"], "S6": ["World Religions","Christian Leadership"]},
    "ICT": {"S1": ["Computer Basics","Word"], "S2": ["Excel","Internet"], "S3": ["Database","Programming"], "S4": ["Web Design","Graphics"], "S5": ["Networking","Systems Analysis"], "S6": ["AI","Cyber Security"]},
    "Entrepreneurship": {"S1": ["Business Ideas","Resources"], "S2": ["Marketing","Finance"], "S3": ["Business Plan","Risk"], "S4": ["Management","Law"], "S5": ["Project","Investment"], "S6": ["Innovation","Global Trade"]},
    "Art": {"S1": ["Drawing","Color"], "S2": ["Painting","Craft"], "S3": ["Design","Sculpture"], "S4": ["Art History","Printmaking"], "S5": ["Advanced Drawing","Portfolio"], "S6": ["Exhibition","Art Business"]},
    "Music": {"S1": ["Notes","Rhythm"], "S2": ["Instruments","Songs"], "S3": ["Theory","Composition"], "S4": ["Music History","Performance"], "S5": ["Harmony","Arrangement"], "S6": ["Conducting","Music Technology"]},
    "Luganda": {"S1": ["Ebigambo","Ennukuta"], "S2": ["Ekitabo","Olulimi"], "S3": ["Ennono","Ebyafaayo"], "S4": ["Ebiwandiiko","Engero"], "S5": ["Okunoonyereza","Emboozi"], "S6": ["Olulimi Olugazi","Ebyobuwangwa"]},
    "Kiswahili": {"S1": ["Alfabeti","Maneno"], "S2": ["Sarufi","Kusoma"], "S3": ["Fasihi","Utungaji"], "S4": ["Riwaya","Michezo"], "S5": ["Uchambuzi","Insha"], "S6": ["Tafsiri","Mjadala"]}
}

### 5. ALL 10 PRACTICALS ###
PRACTICAL_DATABASE = {
    "Physics": {
        "S1-S4": {"Ohm's Law": {"objective": "Verify Ohm's Law V=IR"}, "Simple Pendulum": {"objective": "Determine acceleration due to gravity g"}},
        "S5-S6": {"RC Circuit": {"objective": "Find time constant of RC circuit"}, "Potentiometer": {"objective": "Compare emfs of two cells"}}
    },
    "Chemistry": {
        "S1-S4": {"Acid-Base Titration": {"objective": "Determine concentration of HCl"}, "Solubility": {"objective": "Investigate effect of temperature on solubility"}},
        "S5-S6": {"Rate of Reaction": {"objective": "Determine order of reaction"}, "Electrolysis": {"objective": "Verify Faraday's laws of electrolysis"}}
    },
    "Biology": {
        "S1-S4": {"Microscope Use": {"objective": "Observe plant and animal cells"}, "Food Tests": {"objective": "Test for starch, proteins, lipids, reducing sugars"}},
        "S5-S6": {"Enzyme Activity": {"objective": "Effect of pH and temperature on amylase"}, "Plasmolysis": {"objective": "Observe osmosis in onion epidermal cells"}}
    }
}

### 6. UTILS ###
def get_pandas(): import pandas as pd; return pd
def get_docx(): from docx import Document; return Document
def get_canvas(): from reportlab.pdfgen import canvas; from reportlab.lib.pagesizes import A4; return canvas, A4

def load_logs():
    with open(LOG_FILE) as f: return json.load(f)
def save_log(entry):
    logs = load_logs(); logs.append(entry); save_db(LOG_FILE, logs)

@st.cache_data
def generate_file_bytes(content, fmt):
    if fmt == "pdf": canvas, A4 = get_canvas(); buffer = io.BytesIO(); p = canvas(buffer, pagesize=A4); p.setFont("Helvetica", 10); [p.drawString(50,800-(i*14),line[:100]) for i,line in enumerate(content.split('\n')[:90])]; p.save(); buffer.seek(0); return buffer.getvalue()
    elif fmt == "excel": pd = get_pandas(); df = pd.DataFrame({"Content": content.split('\n')}); buffer = io.BytesIO(); df.to_excel(buffer, index=False, engine='openpyxl'); buffer.seek(0); return buffer.getvalue()
    elif fmt == "html": html = f"<html><body><pre>{content}</pre></body></html>"; return html.encode()
    elif fmt == "docx": Document = get_docx(); doc = Document(); doc.add_paragraph(content); buffer = io.BytesIO(); doc.save(buffer); buffer.seek(0); return buffer.getvalue()

def get_level_group(level): return "S1-S4" if int(level[1]) <= 4 else "S5-S6"
def get_mixed_topics(level, subject):
    level_num = int(level[1]); topics = []; weights = {level_num: 0.7}
    if level_num-1 >= 1: weights[level_num-1] = 0.2
    for l, w in weights.items():
        if f"S{l}" in UNEB_CURRICULUM_MAP[subject]:
            topics.extend(random.sample(UNEB_CURRICULUM_MAP[subject][f"S{l}"], min(1, len(UNEB_CURRICULUM_MAP[subject][f"S{l}"]))))
    return topics

def display_with_preview(content, name):
    edited = st.text_area("AI Preview - EDIT BEFORE DOWNLOAD", content, height=350, key=f"preview_{name}")
    cols = st.columns(4)
    for i, fmt in enumerate(["pdf","excel","html","docx"]):
        if cols[i].button(f"📥 {fmt.upper()}", key=f"btn_dl_{name}_{fmt}"):
            st.download_button(label=f"Download {fmt.upper()}", data=generate_file_bytes(edited, fmt), file_name=f"{name}.{fmt}", mime="application/octet-stream", key=f"dl_{name}_{fmt}_{hash(edited)}")

### 7. AI CALL + ADVANCED DIAGRAM ENGINE ###
def call_groq(user_prompt, level="S1", sample="", instructions="", force_format=False):
    complexity = get_complexity_instructions(level)
    anti_hallucination = "Stay strictly to NCDC UNEB syllabus for Uganda."
    format_instruction = "IMPORTANT: Use UNEB format with SCENARIO, ITEM, TASK." if force_format or any(word in user_prompt.lower() for word in ["exam", "quiz", "test", "50", "bulk", "paper"]) else ""
    full_instructions = f"{complexity}\n{anti_hallucination}\n{format_instruction}\n{instructions}"
    cache_key = user_prompt + sample + full_instructions + level + str(force_format)
    cached_response = ai_cache.get_answer(cache_key)
    if cached_response: st.info("⚡ Loaded from Local TTL Cache. 0 Tokens used."); return cached_response
    if OFFLINE_MODE: return "❌ OFFLINE MODE: This question not in cache. Go online once."
    full_prompt = f"{full_instructions}\nTEACHER SAMPLE:\n{sample}\n\nUSER QUESTION:\n{user_prompt}"
    placeholder = st.empty(); full_response = ""
    model_to_use = AI_MODEL_LONG if "Generate 50" in user_prompt else AI_MODEL_FAST
    try:
        stream = client.chat.completions.create(model=model_to_use, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":full_prompt}], max_tokens=2500, stream=True)
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content; placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)
    except Exception as e:
        st.error(f"AI Error: {e}")
        res = client.chat.completions.create(model=AI_MODEL_LONG, messages=[{"role":"system","content":MASTER_SYSTEM_PROMPT},{"role":"user","content":full_prompt}], max_tokens=3000)
        full_response = res.choices[0].message.content; st.markdown(full_response)
    ai_cache.set_answer(cache_key, full_response); st.success("✅ Saved to Local TTL Cache for 24hrs")
    return full_response

def parse_multiple_json(text):
    """Extract all JSON objects from text, even if concatenated"""
    text = re.sub(r'```json|```', '', text).strip()
    objs = []
    decoder = json.JSONDecoder()
    idx = 0
    while idx < len(text):
        try:
            obj, end = decoder.raw_decode(text[idx:])
            objs.append(obj)
            idx += end
        except:
            break
    return objs

def generate_diagram_ai(topic, subject, level):
    cache_key = f"diagram_{sanitize(topic)}_{subject}_{level}"
    if cache_key in DIAGRAM_CACHE: return DIAGRAM_CACHE[cache_key]

    prompt = f"""For NCDC Uganda {level} {subject} topic '{topic}', generate 2 to 3 relevant diagrams.
Return a JSON ARRAY of objects. Each object: {{"title": "...", "mermaid": "graph TD\\nA-->B", "ascii": "A -> B"}}
Rules: 
1. Mermaid must use proper labels. Use () for circles, [] for rectangles. No \n escapes.
2. ASCII must be neat, <15 lines, use | - + / \\ for lines.
3. Use Ugandan examples.
Return ONLY the JSON array. No other text."""

    diagram_json = call_groq(prompt, level, instructions="Output ONLY JSON array. No explanation.")
    diagrams = parse_multiple_json(diagram_json)

    if not diagrams:
        diagrams = [{"title": f"{topic} Overview", "ascii": f"{topic}\n [Part A]\n |\n [Part B]", "mermaid": f"graph TD\nA[{topic} Part A] --> B[{topic} Part B]"}]
    
    DIAGRAM_CACHE[cache_key] = diagrams
    return diagrams

def show_diagram(topic, subject, level): # FIXED: added topic param
    st.subheader(f"Diagrams: {topic}")
    with st.spinner("Generating diagrams with AI..."):
        diags = generate_diagram_ai(topic, subject, level)

    for i, diag in enumerate(diags):
        title = diag.get('title', f"{topic} Diagram {i+1}") # FIXED: no undefined topic
        st.markdown(f"### {i+1}. {title}")
        tab1, tab2 = st.tabs(["📊 Mermaid", "📝 ASCII"])
        with tab1:
            if diag.get("mermaid"):
                st.markdown(f"```mermaid\n{diag['mermaid']}\n```")
        with tab2:
            st.code(diag.get("ascii","No ASCII available"), language="text")
        st.divider()

### 8. STUDENT PORTAL ###
def show_student_portal():
    st.header("📚 Student Portal - SMART MODE")
    if st.button("Logout", key="btn_logout_student"): [st.session_state.pop(k) for k in list(st.session_state.keys())]; st.rerun()
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Smart Search", "📖 Learn Topic", "🧪 Practicals", "🖼️ Diagram Library"])

    with tab1:
        st.subheader("Ask the AI Anything")
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="s1_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="s1_level")
        difficulty = st.selectbox("Difficulty", ["Mixed","Easy","Moderate","Hard"], key="s1_diff")
        ask_q = st.text_area("Ask anything. Type 'diagram:Sets' to generate diagrams", key="s1_ask")
        if st.button("Ask AI", key="s1_btn") and ask_q:
            if ask_q.lower().startswith("diagram:"):
                topic = ask_q.split(":")[1].strip()
                show_diagram(topic, subject, level)
            else:
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
        elif mode == "Bulk Quiz" and st.button("Generate 50Q Exam", key="s2_btn_bulk"):
            topics = get_mixed_topics(level2, subject2); exam = call_groq(f"Generate 50 UNEB questions from: {topics}. Difficulty: {difficulty2}", level2, force_format=True)
            display_with_preview(exam, "BulkQuiz_s2")

    with tab3:
        st.subheader("🧪 Practical Experiments from DATABASE")
        subject3 = st.selectbox("Subject", list(PRACTICAL_DATABASE.keys()), key="s3_subj")
        level3 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="s3_level")
        group = get_level_group(level3); prac_list = list(PRACTICAL_DATABASE.get(subject3, {}).get(group, {}).keys())
        if not prac_list: st.warning("No practicals for this subject/level")
        topic3 = st.selectbox("Select Practical", prac_list, key="s3_topic") if prac_list else None
        if st.button("Generate Full Practical", key="s3_btn") and topic3:
            objective = PRACTICAL_DATABASE[subject3][group][topic3]["objective"]
            practical = call_groq(f"Generate complete UNEB practical for {topic3}. Objective: {objective}. Include apparatus, procedure, results table.", level3)
            display_with_preview(practical, f"Practical_{topic3}_s3")

    with tab4:
        st.subheader("🖼️ Diagram Library - AI Generated")
        subject4 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="s4_subj")
        level4 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="s4_level")
        topic4 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject4][level4], key="s4_topic")
        if st.button("Generate Diagrams for Topic", key="s4_btn"):
            show_diagram(topic4, subject4, level4)

### 9. ADMIN PORTAL ###
def show_admin_portal():
    st.header("🏫 Admin Portal - TEACHER DRIVEN AI")
    if st.button("Logout", key="btn_logout_admin"): [st.session_state.pop(k) for k in list(st.session_state.keys())]; st.rerun()
    tabs = st.tabs(["📊 Analytics","📖 Curriculum Editor","🧪 Practicals Editor","📤 Exam Generator"])

    with tabs[0]:
        st.subheader("📊 Usage Analytics + Cache Control")
        pd = get_pandas(); logs = load_logs(); stats = ai_cache.get_stats()
        col1, col2 = st.columns(2)
        col1.metric("Total Actions", len(logs)); col2.metric("Cache Entries", stats['total'])
        if st.button("Clear Entire AI Cache", type="primary"): ai_cache.clear_cache(); DIAGRAM_CACHE.clear(); st.success("✅ Cache Cleared!"); st.rerun()

    with tabs[1]:
        st.subheader("📖 NCDC Curriculum Editor")
        edit_subj = st.selectbox("Pick Subject", list(UNEB_CURRICULUM_MAP.keys()), key="admin_edit_subj")
        st.json(UNEB_CURRICULUM_MAP[edit_subj])

    with tabs[2]:
        st.subheader("🧪 Practicals Database")
        st.json(PRACTICAL_DATABASE)

    with tabs[3]: st.subheader("📤 Bulk Exam Generator"); st.info("Coming Soon")

### 10. LOGIN ###
st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO - V5.4.7")
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"], key="radio_login")
password = st.sidebar.text_input("Password", type="password", key="input_password")

if st.sidebar.button("Login", key="btn_login"):
    if user_type == "Student" and password == STUDENT_PASSWORD:
        st.session_state["role"] = "Student"; save_log({"time": str(datetime.now()), "user": "Student", "action": "Login"}); st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD:
        st.session_state["role"] = "Admin"; save_log({"time": str(datetime.now()), "user": "Admin", "action": "Login"}); st.rerun()
    elif password: st.sidebar.error("Wrong password")

if st.session_state.get("role") == "Admin": show_admin_portal()
elif st.session_state.get("role") == "Student": show_student_portal()
else: st.info("Please login to continue")
