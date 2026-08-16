from difflib import SequenceMatcher
import streamlit as st
import os, io, json, re, time, requests, random, threading
from datetime import datetime
from groq import Groq, RateLimitError
import logging
logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 PRO", page_icon="📚", layout="wide")
st.sidebar.caption("Build: V6.0.2-DEMO | NCDC COMPLIANT")

### KEEP RENDER AWAKE ###
def keep_alive():
    while True:
        time.sleep(840)
        try:
            requests.get(os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8501"), timeout=5)
        except:
            pass
threading.Thread(target=keep_alive, daemon=True).start()

### 1. AUTO CREATE FILES + FOLDERS ###
DATA_PATH = os.getenv("STREAMLIT_DATA_PATH", ".")
LOG_FILE = f"{DATA_PATH}/usage_log.json"
CACHE_FILE = f"{DATA_PATH}/ai_cache.json"
VECTOR_FILE = f"{DATA_PATH}/vector_index.faiss"
DOCS_FILE = f"{DATA_PATH}/vector_docs.json"
CURRICULUM_SETTINGS_FILE = f"{DATA_PATH}/teacher_settings.json"

def save_db(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def load_db(file, default):
    if not os.path.exists(file):
        save_db(file, default)
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        save_db(file, default)
        return default

for f, default in [(LOG_FILE, []), (CACHE_FILE, {}), (DOCS_FILE, []), (CURRICULUM_SETTINGS_FILE, {})]:
    load_db(f, default)

DIAGRAM_CACHE = {}

### 2. TTL CACHE CLASS ###
class TTLSchoolCache:
    def __init__(self, ttl_seconds: int = 86400, similarity_threshold: float = 0.75):
        self.ttl = ttl_seconds
        self.threshold = similarity_threshold
        self.cache_file = CACHE_FILE
        self.cache = self.load_from_disk()

    def load_from_disk(self):
        data = load_db(self.cache_file, {})
        now = time.time()
        clean_data = {k: v for k, v in data.items() if now < v["expires_at"]}
        if len(clean_data)!= len(data):
            self.save_to_disk(clean_data)
        return clean_data

    def save_to_disk(self, data=None):
        if data is None:
            data = self.cache
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
            if now < item["expires_at"]:
                return item["answer"]
            else:
                del self.cache[clean_question]

        best_match = None
        best_score = 0
        expired_keys = []
        for cached_q, item in self.cache.items():
            if now >= item["expires_at"]:
                expired_keys.append(cached_q)
                continue
            score = SequenceMatcher(None, clean_question, cached_q).ratio()
            if score > best_score:
                best_score = score
                best_match = item

        for k in expired_keys:
            del self.cache[k]

        if best_match and best_score >= self.threshold:
            return best_match["answer"]
        self.save_to_disk()
        return None

    def clear_cache(self):
        self.cache = {}
        self.save_to_disk()

    def get_stats(self):
        now = time.time()
        active = len([v for v in self.cache.values() if now < v["expires_at"]])
        return {"total": len(self.cache), "active": active}

def get_complexity_instructions(level):
    n = int(level[1])
    if n <= 2:
        return "S1-S2: Simple. Short. Ugandan examples."
    elif n <= 4:
        return "S3-S4: Intermediate. Explain + apply. Ugandan context."
    else:
        return "S5-S6: Advanced. Deep analysis. Derivations."

ai_cache = TTLSchoolCache(ttl_seconds=86400)

### 3. SECRETS ###
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
STUDENT_PASSWORD = os.getenv("STUDENT_PASSWORD", "1234")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
if not GROQ_API_KEY:
    st.error("Missing GROQ_API_KEY. Go to Render > Environment")
    st.stop()

@st.cache_resource
def get_client():
    return Groq(api_key=GROQ_API_KEY)

client = get_client()
OFFLINE_MODE = st.sidebar.toggle("🔌 OFFLINE MODE", value=False, key="toggle_offline")
if OFFLINE_MODE:
    st.sidebar.warning("OFFLINE MODE ON - RAG + CACHE ONLY")

MASTER_SYSTEM_PROMPT = """You are DIGITAL UNEB TUTOR 2026 PRO. NCDC 2026 UGANDA CURRICULUM ONLY. CITE YOUR SOURCES FROM UPLOADED TEACHER NOTES IF USED."""
CONTACT = "256751040731"
AI_MODEL_LONG = "llama-3.3-70b-versatile"
AI_MODEL_FAST = "llama-3.1-8b-instant"
st.sidebar.success(f"⚠️ DIGITAL UNEB TUTOR 2026 PRO V6.0.2\n📞 {CONTACT}")

### 4. ALL 15 SUBJECTS NCDC S1-S6 ###
UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Sets","Number Bases","Integers","Fractions","Decimals"], "S2": ["Rates","Percentages","Algebra","Equations","Geometry"], "S3": ["Quadratics","Trigonometry","Probability","Statistics I","Vectors"], "S4": ["Functions","Matrices","Sequences","Logarithms","Circle Geometry"], "S5": ["Differentiation","Integration","Binomial","Complex Numbers","Mechanics I"], "S6": ["Mechanics II","Statistics III","Probability II","Linear Programming","Vectors II"]},
    "Physics": {"S1": ["Measurement","Forces","Energy","Heat","Light I"], "S2": ["Sound","Pressure","Magnetism I","Electricity I","Waves I"], "S3": ["Magnetism II","Electricity II","Heat II","Optics I","Modern Physics I"], "S4": ["Electronics","Waves II","Radioactivity","Mechanics","Thermal Physics"], "S5": ["Optics II","Current Electricity II","Gravitation","Fields","Nuclear Physics I"], "S6": ["Electric Fields","Magnetic Fields","Electromagnetic Induction","Nuclear Physics II","Electronics II"]},
    "Chemistry": {"S1": ["Atoms","Elements","Compounds","Mixtures","Air"], "S2": ["Acids Alkalis","Salts","Water","Metals","Non-Metals"], "S3": ["Bonding","Structure","Periodic Table","Kinetics I","Organic I"], "S4": ["REDOX","Energy Changes","Kinetics II","Equilibrium I","Acids Bases I"], "S5": ["Kinetics III","Equilibrium II","Acids Bases II","Electrochemistry I","Organic II"], "S6": ["Electrochemistry II","Organic III","Industrial Chemistry","Environmental Chemistry","Analytical Chemistry"]},
    "Biology": {"S1": ["Cells","Classification","Nutrition","Respiration I","Ecology I"], "S2": ["Respiration II","Excretion","Circulation","Support","Reproduction I"], "S3": ["Genetics I","Evolution","Ecology II","Diversity","Physiology I"], "S4": ["Photosynthesis","Hormones I","Reproduction II","Growth","Physiology II"], "S5": ["Cell Biology","Genetics III","Microbiology","Biotechnology I","Ecology III"], "S6": ["Hormones II","Coordination","Biotechnology II","Genetics IV","Applied Biology"]},
    "Agriculture": {"S1": ["Introduction","Soil Formation","Farm Tools","Crops","Livestock Basics"], "S2": ["Soil Properties","Crop Production","Animal Nutrition","Pests","Farm Records"], "S3": ["Soil Conservation","Plant Nutrition","Animal Health","Breeding","Agroforestry"], "S4": ["Crop Protection","Animal Diseases","Farm Structures","Irrigation","Farm Management"], "S5": ["Agribusiness","Farm Planning","Soil Science","Animal Production","Crop Science"], "S6": ["Research Methods","Biotech Agriculture","Agricultural Economics","Extension","Project"]},
    "Geography": {"S1": ["Map Reading","Weather","Climate","Vegetation","Rocks"], "S2": ["Soils","Drainage","Population","Settlement","Transport"], "S3": ["Industry","Trade","Tourism","Environmental Issues","Field Work I"], "S4": ["Industrialization","Trade","Settlement Patterns","Population Structure","GIS"], "S5": ["Climatology","Geomorphology","Hydrology","Biogeography","Regional Geography I"], "S6": ["Regional Geography II","Economic Geography","Political Geography","Research Methods","Field Work II"]},
    "History": {"S1": ["Sources of History","Early Man","Ancient Civilizations","Iron Age","Bantu Migrations"], "S2": ["Kingdoms of Uganda","Colonialism","Resistance","Missionaries","Trade"], "S3": ["WWI","WWII","Nationalism","Decolonization","Cold War"], "S4": ["UN","OAU","East African Community","Post-Colonial Africa","Human Rights"], "S5": ["EA History","African Nationalism","Pan-Africanism","Economic History","Political History"], "S6": ["International Relations","Genocide","Globalization","Democracy","Contemporary Issues"]},
    "Literature": {"S1": ["Oral Literature","Poetry","Prose","Drama","Literary Terms"], "S2": ["Novels","Plays","Poems","Themes","Characters"], "S3": ["Prose","Literary Devices","Style","Setting","Plot"], "S4": ["African Literature","World Literature","Critical Analysis","Themes","Style"], "S5": ["Critical Analysis","Themes","Style","Language","Context"], "S6": ["Research Project","Comparative Literature","Literary Criticism","Advanced Drama","Advanced Poetry"]},
    "CRE": {"S1": ["God and Man","Bible","Creation","Sin","Salvation"], "S2": ["Prophets","Jesus","Parables","Miracles","Disciples"], "S3": ["Church","Sacraments","Prayer","Christian Living","Community"], "S4": ["Christian Living","Social Issues","Ethics","Leadership","Service"], "S5": ["Theology","Ethics","World Religions","Christian Doctrine","Biblical Studies"], "S6": ["World Religions","Christian Leadership","Pastoral Care","Mission","Contemporary Theology"]},
    "ICT": {"S1": ["Computer Basics","Word","Keyboard","Mouse","Internet Basics"], "S2": ["Excel","Internet","Email","PowerPoint","File Management"], "S3": ["Database","Programming","Algorithms","Flowcharts","Web Basics"], "S4": ["Web Design","Graphics","Multimedia","Networking","Security"], "S5": ["Networking","Systems Analysis","Database Design","Programming II","Web Development"], "S6": ["AI","Cyber Security","Software Engineering","Data Science","Project"]},
    "Entrepreneurship": {"S1": ["Business Ideas","Resources","Market","Money","Saving"], "S2": ["Marketing","Finance","Business Plan","Risk","Customers"], "S3": ["Business Plan","Risk","Management","Law","Records"], "S4": ["Management","Law","Tax","Insurance","Growth"], "S5": ["Project","Investment","Business Growth","Innovation","Global Trade"], "S6": ["Innovation","Global Trade","Business Strategy","Leadership","Case Studies"]},
    "Art": {"S1": ["Drawing","Color","Shapes","Lines","Composition"], "S2": ["Painting","Craft","Design","Patterns","Texture"], "S3": ["Design","Sculpture","Printmaking","Art History","Critique"], "S4": ["Art History","Printmaking","Advanced Design","Portfolio","Exhibition"], "S5": ["Advanced Drawing","Portfolio","Art Theory","Contemporary Art","Project"], "S6": ["Exhibition","Art Business","Curating","Art Criticism","Final Project"]},
    "Music": {"S1": ["Notes","Rhythm","Instruments","Songs","Listening"], "S2": ["Instruments","Songs","Theory","Composition","Performance"], "S3": ["Theory","Composition","Music History","Ensemble","Arrangement"], "S4": ["Music History","Performance","Harmony","Conducting","Technology"], "S5": ["Harmony","Arrangement","Composition II","Musicology","Performance II"], "S6": ["Conducting","Music Technology","Composition III","Music Business","Recital"]},
    "Luganda": {"S1": ["Ebigambo","Ennukuta","Ennongo","Emiramwa","Ebiwandiiko"], "S2": ["Ekitabo","Olulimi","Ennono","Emboozi","Ebyafaayo"], "S3": ["Ennono","Ebyafaayo","Olulimi","Ebiwandiiko","Okwogerera"], "S4": ["Ebiwandiiko","Engero","Enkola","Olulimi Olugazi","Ebyobuwangwa"], "S5": ["Okunoonyereza","Emboozi","Ebyafaayo","Olulimi","Ebiwandiiko"], "S6": ["Olulimi Olugazi","Ebyobuwangwa","Okutunga","Okulongoosa","Omulimu"]},
    "Kiswahili": {"S1": ["Alfabeti","Maneno","Sentensi","Kusoma","Kuandika"], "S2": ["Sarufi","Kusoma","Kusikia","Kuongea","Utungaji"], "S3": ["Fasihi","Utungaji","Insha","Barua","Ripoti"], "S4": ["Riwaya","Michezo","Ushairi","Maqala","Hotuba"], "S5": ["Uchambuzi","Insha","Tafsiri","Utafiti","Fasihi"], "S6": ["Tafsiri","Mjadala","Uchambuzi wa Kina","Uandishi wa Kitaaluma","Mradi"]}
}

### 5. ALL 10 PRACTICALS ###
PRACTICAL_DATABASE = {
    "Physics": {"S1-S4": {"Ohm's Law": {"objective": "Verify Ohm's Law V=IR"}, "Simple Pendulum": {"objective": "Determine acceleration due to gravity g"}}, "S5-S6": {"RC Circuit": {"objective": "Find time constant of RC circuit"}, "Potentiometer": {"objective": "Compare emfs of two cells"}, "Wheatstone Bridge": {"objective": "Determine unknown resistance"}}},
    "Chemistry": {"S1-S4": {"Acid-Base Titration": {"objective": "Determine concentration of HCl"}, "Solubility": {"objective": "Investigate effect of temperature on solubility"}}, "S5-S6": {"Rate of Reaction": {"objective": "Determine order of reaction"}, "Electrolysis": {"objective": "Verify Faraday's laws"}, "Organic Prep": {"objective": "Prepare ethanoic acid"}}},
    "Biology": {"S1-S4": {"Microscope Use": {"objective": "Observe plant and animal cells"}, "Food Tests": {"objective": "Test for starch, proteins, lipids, reducing sugars"}}, "S5-S6": {"Enzyme Activity": {"objective": "Effect of pH and temperature on amylase"}, "Plasmolysis": {"objective": "Observe osmosis in onion epidermal cells"}, "Chromatography": {"objective": "Separate plant pigments"}}},
    "Agriculture": {"S1-S4": {"Soil pH Test": {"objective": "Determine soil pH using indicator"}, "Seed Germination": {"objective": "Test germination percentage"}}, "S5-S6": {"Feed Formulation": {"objective": "Formulate poultry feed"}, "Farm Budget": {"objective": "Prepare farm enterprise budget"}}}
}

### 6. LAZY RAG + VECTOR DB CLASS ###
VECTOR_READY = False
faiss = None
embedding_model = None

def load_vector_tools():
    global faiss, embedding_model
    if faiss is None:
        try:
            import faiss as _faiss
            from sentence_transformers import SentenceTransformer
            faiss = _faiss
            embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            return True
        except Exception as e:
            st.sidebar.error(f"RAG Disabled: {e}")
            return False
    return True

class VectorRAG:
    def __init__(self):
        self.index = None
        self.docs = []
        self.load()

    def load(self):
        if os.path.exists(VECTOR_FILE) and os.path.exists(DOCS_FILE):
            if load_vector_tools():
                self.index = faiss.read_index(VECTOR_FILE)
            self.docs = load_db(DOCS_FILE, [])

    def save(self):
        if self.index and faiss:
            faiss.write_index(self.index, VECTOR_FILE)
        save_db(DOCS_FILE, self.docs)

    def add_documents(self, texts):
        if not load_vector_tools():
            return
        embeddings = embedding_model.encode(texts, convert_to_numpy=True)
        if self.index is None:
            self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)
        self.docs.extend(texts)
        self.save()

    def search(self, query, k=3):
        if not load_vector_tools() or not self.index:
            return []
        q_emb = embedding_model.encode([query], convert_to_numpy=True)
        D, I = self.index.search(q_emb, min(k, len(self.docs)))
        return [self.docs[i] for i in I[0]]

vector_rag = VectorRAG()
st.sidebar.info(f"Build: V6.0.2 | VDB Chunks: {len(vector_rag.docs)}")

def chunk_text(text, chunk_size=500):
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current = ""
    for s in sentences:
        if len(current) + len(s) < chunk_size:
            current += s + " "
        else:
            chunks.append(current)
            current = s
    if current:
        chunks.append(current)
    return chunks

def render_upload_download(key_prefix="default"):
    st.subheader("📤 Upload & 📥 Download")
    uploaded_file = st.file_uploader("Upload PDF/DOCX/TXT to add to VDB", type=["pdf", "docx", "txt"], key=f"uploader_{key_prefix}")
    if uploaded_file:
        text = ""
        try:
            if uploaded_file.name.endswith(".pdf"):
                from pypdf import PdfReader
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    text += page.extract_text() or ""
            elif uploaded_file.name.endswith(".docx"):
                from docx import Document
                doc = Document(uploaded_file)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            else:
                text = uploaded_file.getvalue().decode("utf-8")
        except Exception as e:
            st.error(f"File Read Error: {e}")
            return

        if not text.strip():
            st.warning("File is empty")
            return

        chunks = chunk_text(text)
        if st.button(f"Add {len(chunks)} Chunks to Vector DB", key=f"add_vdb_btn_{key_prefix}"):
            if load_vector_tools():
                vector_rag.add_documents(chunks)
                st.success(f"Added {len(chunks)} chunks to RAG! ✅")
            else:
                st.error("RAG tools failed to load")

### 8. UTILS + DOWNLOADS ###
def get_pandas():
    import pandas as pd
    return pd

def get_docx():
    from docx import Document
    return Document

def get_canvas():
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    return canvas, A4

def load_logs():
    return load_db(LOG_FILE, [])

def save_log(entry):
    logs = load_logs()
    logs.append(entry)
    save_db(LOG_FILE, logs)

def load_teacher_settings():
    return load_db(CURRICULUM_SETTINGS_FILE, {})

def save_teacher_settings(data):
    save_db(CURRICULUM_SETTINGS_FILE, data)

def download_all_formats(content, name):
    cols = st.columns(5)
    formats = ["pdf","excel","docx","txt","gsheet"]
    for i, fmt in enumerate(formats):
        if cols[i].button(f"📥 {fmt.upper()}", key=f"btn_dl_{name}_{fmt}"):
            if fmt == "gsheet":
                st.info("To enable Google Sheets: Add GSPREAD_CREDENTIALS to Render Env")
            else:
                st.download_button(
                    label=f"Download {fmt.upper()}",
                    data=generate_file_bytes(content, fmt),
                    file_name=f"{name}.{fmt}",
                    mime="application/octet-stream",
                    key=f"dl_{name}_{fmt}_{hash(content)}"
                )

@st.cache_data
def generate_file_bytes(content, fmt):
    if fmt == "pdf":
        canvas, A4 = get_canvas()
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        p.setFont("Helvetica", 10)
        for i, line in enumerate(content.split('\n')[:90]):
            p.drawString(50, 800-(i*14), line[:100])
        p.save()
        buffer.seek(0)
        return buffer.getvalue()
    elif fmt == "excel":
        pd = get_pandas()
        df = pd.DataFrame({"Content": content.split('\n')})
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)
        return buffer.getvalue()
    elif fmt == "txt":
        return content.encode()
    elif fmt == "docx":
        Document = get_docx()
        doc = Document()
        doc.add_paragraph(content)
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()

def get_level_group(level):
    return "S1-S4" if int(level[1]) <= 4 else "S5-S6"

def get_mixed_topics(level, subject):
    settings = load_teacher_settings()
    saved = settings.get(f"{subject}_{level}", [])
    if saved:
        return saved
    level_num = int(level[1])
    topics = []
    weights = {level_num: 0.7}
    if level_num-1 >= 1:
        weights[level_num-1] = 0.2
    for l, w in weights.items():
        if f"S{l}" in UNEB_CURRICULUM_MAP.get(subject, {}):
            topics.extend(random.sample(UNEB_CURRICULUM_MAP[subject][f"S{l}"], min(2, len(UNEB_CURRICULUM_MAP[subject][f"S{l}"]))))
    return topics

def display_with_preview(content, name, sources=[]):
    if sources:
        st.info(f"📚 Sourced from your uploaded notes: {len(sources)} chunks")
    edited = st.text_area("AI Preview - EDIT BEFORE DOWNLOAD", content, height=350, key=f"preview_{name}")
    download_all_formats(edited, name)

### 9. SMART TOKEN MINIMIZER + RAG CITATION ###
def get_conversation_context():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    return st.session_state.chat_history[-4:]

def compress_prompt(prompt):
    return re.sub(r'\s+', ' ', prompt).strip()[:2000]

def search_notes(query):
    return vector_rag.search(query, k=3)

def get_cached_answer(query):
    return ai_cache.get_answer(query)

TOOLS = [{"type": "function", "function": {"name": "search_notes", "description": "Search NCDC notes vector database", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}}]

def call_groq(user_prompt, level="S1", instructions="", force_format=False):
    complexity = get_complexity_instructions(level)
    format_instruction = "Use SCENARIO/ITEM/TASK FORMAT with headers." if force_format or any(word in user_prompt.lower() for word in ["exam", "quiz", "test", "50", "bulk", "paper"]) else ""
    full_instructions = f"{complexity}\n{format_instruction}\n{instructions}"

    cached = get_cached_answer(user_prompt)
    if cached:
        st.info("⚡ Cache Hit. 0 Tokens used.")
        return cached, []

    rag_context = search_notes(user_prompt)
    st.sidebar.caption(f"RAG hits: {len(rag_context)} | Prompt len: {len(user_prompt)}")

    if rag_context and OFFLINE_MODE:
        return f"📚 OFFLINE RAG MODE:\n{chr(10).join(rag_context[:3])}", rag_context
    if OFFLINE_MODE:
        return "❌ OFFLINE: Not in cache/vector. Go online.", []

    context_history = get_conversation_context()
    messages = [{"role":"system","content":MASTER_SYSTEM_PROMPT + "\n" + full_instructions}]
    messages.extend(context_history)
    messages.append({"role":"user","content":compress_prompt(user_prompt)})

    if rag_context:
        messages.append({"role":"system","content":f"CONTEXT FROM TEACHER'S UPLOADED NOTES - CITE THIS: {chr(10).join(rag_context[:3])}"})

    model_to_use = AI_MODEL_FAST if len(user_prompt) < 100 else AI_MODEL_LONG
    placeholder = st.empty()
    full_response = ""

    try:
        with st.spinner(f"Thinking with {model_to_use}..."):
            response = client.chat.completions.create(
                model=model_to_use,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                max_tokens=2000,
                temperature=0.3
            )
            msg = response.choices[0].message

            if msg.tool_calls:
                for tool_call in msg.tool_calls:
                    if tool_call.function.name == "search_notes":
                        args = json.loads(tool_call.function.arguments)
                        st.sidebar.info(f"AI called tool: search_notes('{args['query']}')")
                        tool_result = search_notes(args["query"])
                        messages.append({"role":"tool","content":str(tool_result),"tool_call_id":tool_call.id})

                response = client.chat.completions.create(model=model_to_use, messages=messages, max_tokens=2000)
                full_response = response.choices[0].message.content
            else:
                full_response = msg.content

        placeholder.markdown(full_response)

    except RateLimitError:
        st.error("Groq Rate Limit. Try again in 10s")
        full_response = "Rate limit error."
    except Exception as e:
        st.error(f"AI Error: {e}")
        full_response = "Error. Try again."

    st.session_state.chat_history.append({"role":"user","content":user_prompt})
    st.session_state.chat_history.append({"role":"assistant","content":full_response})

    if len(st.session_state.chat_history) > 8:
        st.session_state.chat_history = st.session_state.chat_history[-8:]

    ai_cache.set_answer(user_prompt, full_response)
    st.success("✅ Saved to Cache for 24hrs")
    save_log({"time": str(datetime.now()), "user": st.session_state.get("role"), "action": "AI Query", "prompt": user_prompt[:50]})
    return full_response, rag_context

### 10. STUDENT PORTAL ###
def show_student_portal():
    st.header("📚 Student Portal - SMART MODE")
    if st.button("Logout", key="btn_logout_student"):
        for k in list(st.session_state.keys()):
            st.session_state.pop(k)
        st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Smart Search", "📖 Learn Topic", "🧪 Practicals", "🖼️ Diagram Library"])

    with tab1:
        st.subheader("Ask the AI Anything")
        render_upload_download("student1")
        subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="s1_subj")
        level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="s1_level")
        ask_q = st.text_area("Ask anything", key="s1_ask")
        if st.button("Ask AI", key="s1_btn") and ask_q:
            ans, sources = call_groq(ask_q, level)
            display_with_preview(ans, "Answer_s1", sources)

    with tab2:
        st.subheader("Generate Content")
        render_upload_download("student2")
        subject2 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="s2_subj")
        level2 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="s2_level")
        topic2 = st.selectbox("Topic", UNEB_CURRICULUM_MAP.get(subject2, {}).get(level2, []), key="s2_topic")
        if st.button("Generate Notes", key="s2_btn_notes"):
            notes, sources = call_groq(f"Notes on {topic2} for {level2} {subject2}.", level2)
            display_with_preview(notes, "Notes_s2", sources)

    with tab3:
        st.subheader("🧪 Practicals")
        render_upload_download("student3")
        subject3 = st.selectbox("Subject", list(PRACTICAL_DATABASE.keys()), key="s3_subj")
        level3 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="s3_level")
        group = get_level_group(level3)
        prac_list = list(PRACTICAL_DATABASE.get(subject3, {}).get(group, {}).keys())
        topic3 = st.selectbox("Select Practical", prac_list, key="s3_topic") if prac_list else None
        if st.button("Generate Full Practical", key="s3_btn") and topic3:
            objective = PRACTICAL_DATABASE[subject3][group][topic3]["objective"]
            practical, sources = call_groq(f"Full UNEB practical for {topic3}. {objective}. Apparatus, procedure, table, safety, Uganda.", level3)
            display_with_preview(practical, f"Practical_{topic3}_s3", sources)

    with tab4:
        st.subheader("🖼️ Diagram Library")
        render_upload_download("student4")
        subject4 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="s4_subj")
        level4 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="s4_level")
        topic4 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject4][level4], key="s4_topic")
        if st.button("Generate Diagrams", key="s4_btn"):
            prompt = f"For NCDC {level4} {subject4} '{topic4}', generate 2 JSON diagrams with title,mermaid,ascii. Ugandan examples."
            result, sources = call_groq(prompt, level4)
            display_with_preview(result, f"Diagram_{topic4}", sources)

### 11. ADMIN PORTAL - 7 TABS ###
def show_admin_portal():
    st.header("🏫 Admin Portal")
    if st.button("Logout", key="btn_logout_admin"):
        for k in list(st.session_state.keys()):
            st.session_state.pop(k)
        st.rerun()

    tabs = st.tabs(["📊 Analytics","📖 Curriculum","🧪 Practicals","📤 Bulk Exam","📚 RAG KB","📝 Lesson/Scheme","📄 MOES Reports"])

    with tabs[0]:
        st.subheader("📊 Analytics")
        render_upload_download("admin1")
        pd = get_pandas()
        logs = load_logs()
        stats = ai_cache.get_stats()
        col1, col2, col3 = st.columns(3)
        col1.metric("Actions", len(logs))
        col2.metric("Cache", stats['total'])
        col3.metric("VDB Chunks", len(vector_rag.docs))

        if st.button("Clear Cache"):
            ai_cache.clear_cache()
            DIAGRAM_CACHE.clear()
            st.success("Cleared!")
            st.rerun()

        st.download_button(
            "📥 Download VDB Backup",
            data=open(VECTOR_FILE,"rb").read() if os.path.exists(VECTOR_FILE) else b"",
            file_name="vector_index.faiss"
        )

        uploaded_vdb = st.file_uploader("Restore VDB", type=["faiss"], key="restore_vdb")
        if uploaded_vdb:
            open(VECTOR_FILE,"wb").write(uploaded_vdb.read())
            st.success("VDB Restored. Refresh page")

        if logs:
            st.dataframe(pd.DataFrame(logs[-20:]))

    with tabs[1]:
        st.subheader("📖 Teacher Curriculum Settings")
        render_upload_download("admin2")
        settings = load_teacher_settings()
        subject = st.selectbox("Pick Subject", list(UNEB_CURRICULUM_MAP.keys()), key="set_subj")
        level = st.selectbox("Pick Class", [f"S{i}" for i in range(1,7)], key="set_level")
        topics = st.multiselect(
            "Select Topics to Teach This Term",
            UNEB_CURRICULUM_MAP.get(subject, {}).get(level, []),
            default=settings.get(f"{subject}_{level}", [])
        )
        if st.button("Save Curriculum Settings"):
            settings[f"{subject}_{level}"] = topics
            save_teacher_settings(settings)
            st.success("Saved! Bulk exams will now use these topics")

    with tabs[2]:
        st.subheader("🧪 Practicals")
        render_upload_download("admin3")
        st.json(PRACTICAL_DATABASE)

    with tabs[3]:
        st.subheader("📤 Bulk Exam Generator")
        render_upload_download("admin4")
        settings = load_teacher_settings()
        b_subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="bulk_subj")
        b_level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="bulk_level")
        default_topics = settings.get(f"{b_subject}_{b_level}", get_mixed_topics(b_level, b_subject))
        topics = st.multiselect(
            "Topics from Your Curriculum Settings",
            UNEB_CURRICULUM_MAP.get(b_subject, {}).get(b_level, []),
            default=default_topics
        )
        num_q = st.slider("Number of Questions", 10, 100, 50)
        if st.button("Generate Exam"):
            paper, sources = call_groq(f"Generate {num_q} UNEB Qs from: {topics}. Include marking guide. Use teacher curriculum.", b_level, force_format=True)
            display_with_preview(paper, f"Bulk_{b_subject}_{b_level}", sources)

    with tabs[4]:
        st.subheader("📚 Vector DB Management")
        st.caption(f"Total chunks in DB: {len(vector_rag.docs)}")
        render_upload_download("admin5")
        if st.button("Reset Vector DB"):
            vector_rag.index = None
            vector_rag.docs = []
            vector_rag.save()
            st.success("Reset done")

    with tabs[5]:
        st.subheader("📝 Lesson Plan & Scheme of Work")
        render_upload_download("admin6")

        col1, col2 = st.columns(2)
        with col1:
            subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="ls_subj")
        with col2:
            level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="ls_level")

        topic = st.selectbox("Topic", UNEB_CURRICULUM_MAP.get(subject, {}).get(level, []), key="ls_topic")

        mode = st.radio("Generate", ["Lesson Plan 40min", "Scheme of Work Term"], horizontal=True, key="ls_mode")

        duration = st.selectbox("Duration", ["40 Minutes", "80 Minutes Double"], key="ls_duration") if mode == "Lesson Plan 40min" else None
        term = st.selectbox("Term", ["Term 1", "Term 2", "Term 3"], key="ls_term") if mode == "Scheme of Work Term" else None

        if st.button("Generate", key="btn_generate_ls"):
            if mode == "Lesson Plan 40min":
                prompt = f"""Generate a detailed NCDC {level} {subject} Lesson Plan for '{topic}'.
                Duration: {duration}
                Include: Topic, Objectives, Materials, Introduction, Lesson Development, Activities, Ugandan Examples, Assessment, Reflection. Use teacher notes if available."""
            else:
                prompt = f"""Generate a full NCDC {level} {subject} Scheme of Work for {term} 2026.
                Focus Topic: {topic}
                Include: Week, Topic, Sub-Topic, Objectives, Teaching Aids, Methods, References, Remarks. Use teacher curriculum settings."""

            result, sources = call_groq(prompt, level)
            display_with_preview(result, f"{mode}_{topic}_{level}", sources)
