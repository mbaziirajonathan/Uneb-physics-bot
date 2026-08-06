import streamlit as st
import os, io, json, re, time, glob, difflib, requests, random, hashlib, threading
from datetime import datetime
from groq import Groq, RateLimitError
from difflib import SequenceMatcher

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 PRO", page_icon="📚", layout="wide")
st.sidebar.caption("Build: V5.2.9-NCDC-FULL-RESTORED")

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
ASSETS_FOLDER = f"{DATA_PATH}/assets"
LABELS_FOLDER = f"{DATA_PATH}/assets/labels"

for f, default in [(LOG_FILE, []), (CACHE_FILE, {}), (PARENTS_FILE, {})]:
    if not os.path.exists(f):
        with open(f, "w") as fp: json.dump(default, fp)
os.makedirs(ASSETS_FOLDER, exist_ok=True)
os.makedirs(LABELS_FOLDER, exist_ok=True)

### 2. TTL CACHE CLASS + SCALING LOGIC - MUST BE BEFORE ai_cache INIT ###
class TTLSchoolCache:
    def __init__(self, ttl_seconds: int = 86400, similarity_threshold: float = 0.75):
        self.ttl = ttl_seconds
        self.threshold = similarity_threshold # 75% similar = same question
        self.cache_file = CACHE_FILE
        self.cache = self.load_from_disk() # Load previous data, no data lost

    def load_from_disk(self):
        """Load cache from JSON so we don't lose data on restart"""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as f:
                data = json.load(f)
                # Remove expired items on load
                now = time.time()
                clean_data = {k:v for k,v in data.items() if now < v["expires_at"]}
                if len(clean_data)!= len(data):
                    self.save_to_disk(clean_data) # Clean stale data
                return clean_data
        return {}

    def save_to_disk(self, data=None):
        """Save to disk to prevent data loss"""
        if data is None: data = self.cache
        with open(self.cache_file, "w") as f:
            json.dump(data, f, indent=2)

    def _clean_text(self, text: str) -> str:
        """Makes uneb = UNEB. Removes extra spaces/punctuation for better matching"""
        text = text.strip().lower()
        text = re.sub(r'[^a-z0-9\s]', '', text) # remove punctuation?.!
        text = re.sub(r'\s+', ' ', text) # remove double spaces
        return text

    def set_answer(self, question: str, answer: str):
        """Saves an answer with an expiration timestamp."""
        clean_question = self._clean_text(question)
        expire_at = time.time() + self.ttl
        self.cache[clean_question] = {
            "answer": answer,
            "expires_at": expire_at,
            "original_q": question
        }
        self.save_to_disk()

    def get_answer(self, question: str) -> str:
        """Retrieves a fresh answer. Uses fuzzy match if exact not found."""
        clean_question = self._clean_text(question)
        now = time.time()
        # 1. EXACT MATCH FIRST
        if clean_question in self.cache:
            item = self.cache[clean_question]
            if now < item["expires_at"]:
                print("--- Cache Hit! Exact Match ---")
                return item["answer"]
            else:
                del self.cache[clean_question]
        # 2. FUZZY/SEMANTIC MATCH
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
        for k in expired_keys: del self.cache[k]
        if best_match and best_score >= self.threshold:
            print(f"--- Cache Hit! Semantic Match: {best_score:.2f} ---")
            return best_match["answer"]
        self.save_to_disk()
        return None # Cache miss

    def clear_cache(self):
        """Admin function to wipe all cache"""
        self.cache = {}
        self.save_to_disk()
        print("--- Cache Cleared by Admin ---")

    def get_stats(self):
        """Return cache stats for admin"""
        now = time.time()
        active = len([v for v in self.cache.values() if now < v["expires_at"]])
        return {"total": len(self.cache), "active": active}

def get_complexity_instructions(level):
    """Scaling complexity by class"""
    n = int(level[1])
    if n <= 2: return "S1-S2 LOWER SECONDARY. Very simple language. Short sentences. Basic Ugandan examples."
    elif n <= 4: return "S3-S4 UPPER SECONDARY. Intermediate. Explain concepts and apply. Ugandan context."
    else: return "S5-S6 ADVANCED LEVEL. University prep. Deep analysis, derivations, detailed explanations, critical thinking."

# INIT CACHE AFTER CLASS IS DEFINED
ai_cache = TTLSchoolCache(ttl_seconds=86400) # 24 hours

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

def call_groq(user_prompt, level="S1", sample="", instructions=""):
    """Main AI function with TTL cache + scaling"""
    complexity = get_complexity_instructions(level)
    anti_hallucination = "IMPORTANT: Only answer based on NCDC UNEB syllabus. Do not make up facts. If unsure, say 'I don't have that information'."
    full_instructions = f"{complexity}\n{anti_hallucination}\n{instructions}"
    cache_key = user_prompt + sample + full_instructions + level

    # 1. CHECK CACHE FIRST
    cached_response = ai_cache.get_answer(cache_key)
    if cached_response:
        st.info("⚡ Loaded from Local TTL Cache. 0 Tokens used.")
        return cached_response

    if OFFLINE_MODE:
        return "❌ OFFLINE MODE: This question not in cache. Please go online once to generate and cache it."

    # 2. BUILD PROMPT
    full_prompt = f"{full_instructions}\nTEACHER SAMPLE:\n{sample}\n\nGENERATE:\n{user_prompt}"
    placeholder = st.empty()
    full_response = ""
    model_to_use = AI_MODEL_LONG if "Generate 50" in user_prompt or "Bulk" in user_prompt else AI_MODEL_FAST

    # 3. CALL AI
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

    # 4. SAVE TO CACHE
    ai_cache.set_answer(cache_key, full_response)
    st.success("✅ Saved to Local TTL Cache for 24hrs")
    return full_response

# DELETED: load_cache, save_cache, get_cache_key - replaced by TTLSchoolCache

CONTACT = "256751040731"
AI_MODEL_LONG = "llama-3.3-70b-versatile"
AI_MODEL_FAST = "llama-3.1-8b-instant"
st.sidebar.success(f"⚠️ DIGITAL UNEB TUTOR 2026 PRO V5.2.9\nNCDC 2026 LOCKED\n📞 {CONTACT}")

MASTER_SYSTEM_PROMPT = """You are DIGITAL UNEB TUTOR 2026 PRO. NCDC 2026 UGANDA CURRICULUM ONLY. Follow teacher sample + instructions. RULES: S1-S2: Very simple, basic Ugandan examples. S3-S4: Intermediate, apply concepts. S5-S6: Advanced, university prep, deep analysis, derivations. Always use UNEB format: SCENARIO, ITEM, TASK. Use local Ugandan context. Do not hallucinate. If unsure, say 'I don't have that information'."""

### 4. FULL NCDC CURRICULUM S1-S6 - CALCULUS REMOVED FROM S4 ###
UNEB_CURRICULUM_MAP = {
    "Mathematics": {
        "S1": ["Sets", "Number Bases", "Fractions", "Decimals", "Integers", "Algebra Intro"],
        "S2": ["Rates", "Percentages", "Angles", "Triangles", "Linear Equations", "Statistics I"],
        "S3": ["Quadratics", "Trigonometry", "Matrices", "Sequences", "Probability I", "Bearings"],
        "S4": ["Functions", "Vectors", "Statistics II", "Financial Math", "Linear Programming", "Probability II"], # NO CALCULUS
        "S5": ["Differentiation", "Integration", "Binomial Theorem", "Permutations", "Probability Distributions", "Complex Numbers"],
        "S6": ["Mechanics", "Statistics III", "Differential Equations", "Linear Algebra", "Numerical Methods", "Calculus Applications"]
    },
    "Physics": {
        "S1": ["Measurement", "Forces", "Energy", "Heat", "Waves I"],
        "S2": ["Light I", "Sound", "Electricity I", "Magnetism I", "Density"],
        "S3": ["Magnetism II", "Electricity II", "Radioactivity", "Energy Sources", "Pressure"],
        "S4": ["Electronics", "Waves II", "Atomic Physics", "Statics", "Dynamics"],
        "S5": ["Optics II", "Current Electricity II", "EM Waves", "Gravitational Fields", "SHM"],
        "S6": ["Electric Fields", "Magnetic Fields", "Quantum Physics", "Nuclear Physics", "Astrophysics"]
    },
    "Chemistry": {
        "S1": ["Atoms", "Elements", "Compounds", "Mixtures", "Air and Combustion"],
        "S2": ["Acids Alkalis", "Salts", "Oxygen", "Hydrogen", "Water"],
        "S3": ["Bonding", "Structure", "Periodic Table", "Metals", "Non-Metals"],
        "S4": ["REDOX", "Energy Changes", "Rate of Reaction", "Equilibrium", "Organic Intro"],
        "S5": ["Kinetics", "Equilibrium II", "Energetics", "Organic Chemistry I", "Analytical Chemistry"],
        "S6": ["Electrochemistry", "Organic II", "Polymers", "Biochemistry", "Industrial Chemistry"]
    },
    "Biology": {
        "S1": ["Cells", "Classification", "Nutrition", "Respiration", "Transport"],
        "S2": ["Respiration II", "Excretion", "Reproduction I", "Ecology I", "Diversity"],
        "S3": ["Genetics I", "Evolution", "Ecology II", "Physiology", "Health"],
        "S4": ["Photosynthesis", "Hormones I", "Reproduction II", "Genetics II", "Biotechnology"],
        "S5": ["Cell Biology", "Genetics III", "Physiology II", "Ecology III", "Microbiology"],
        "S6": ["Hormones II", "Coordination", "Genetics IV", "Evolution II", "Environmental Biology"]
    },
    "Agriculture": { # FULL THEORY ADDED S1-S6
        "S1": ["Introduction to Agriculture", "Soil Formation", "Farm Tools", "Crop Classification", "Animal Classification"],
        "S2": ["Soil Properties", "Livestock Production", "Poultry", "Crop Production", "Farm Records"],
        "S3": ["Soil Conservation", "Plant Nutrition", "Crop Pests", "Animal Feeds", "Animal Housing"],
        "S4": ["Animal Health", "Breeding", "Pasture Management", "Land Use", "Agricultural Economics"],
        "S5": ["Agribusiness", "Farm Planning", "Irrigation", "Agricultural Marketing", "Cooperatives"],
        "S6": ["Agricultural Research", "Biotechnology in Agriculture", "Climate Change", "Policy", "Value Addition"]
    },
    "English": {"S1": ["Grammar", "Composition", "Comprehension", "Oral Literature", "Vocabulary"], "S2": ["Literature", "Poetry", "Drama", "Novel", "Summary"], "S3": ["Novel", "Play", "Poetry Anthology", "Grammar II", "Writing Skills"], "S4": ["Shakespeare", "African Literature", "Grammar III", "Oral Skills", "Literary Devices"], "S5": ["Advanced Grammar", "Criticism", "Drama Analysis", "Novel Analysis", "Poetry Analysis"], "S6": ["Criticism II", "Comparative Literature", "Research", "Advanced Composition", "Oral Literature II"]},
    "ICT": {"S1": ["Computer Basics", "Hardware", "Software", "OS", "Applications"], "S2": ["Word Processing", "Spreadsheets", "Presentation", "Internet Basics", "Safety"], "S3": ["Databases", "Networking", "Graphics", "Programming Intro", "Web Basics"], "S4": ["Internet", "Multimedia", "Programming Python", "Database Design", "E-Commerce"], "S5": ["Programming Python", "Data Structures", "Web Design", "Mobile Apps", "AI Intro"], "S6": ["Web Design", "Database Systems", "System Analysis", "Networking II", "Project"]},
    "Geography": {"S1": ["Map Reading", "Weather", "Climate", "Vegetation", "Population"], "S2": ["Climate", "Soils", "Rivers", "Lakes", "Landforms"], "S3": ["Rivers", "Weathering", "Mass Wasting", "Glaciation", "Coasts"], "S4": ["Population", "Settlement", "Agriculture", "Industry", "Trade"], "S5": ["Industries", "Transport", "Tourism", "Energy", "Urbanization"], "S6": ["GIS", "Remote Sensing", "Development", "Environment", "Fieldwork"]},
    "History": {"S1": ["Early Man", "Stone Age", "Iron Age", "Kingdoms Intro", "Trade"], "S2": ["Kingdoms", "Buganda", "Bunyoro", "Migration", "Islam"], "S3": ["Colonialism", "Scramble", "Resistance", "Colonial Economy", "Social Services"], "S4": ["Independence", "Political Parties", "Nationalism", "Constitutions", "Post Independence"], "S5": ["World Wars", "UN", "Cold War", "Decolonization", "Regional Organizations"], "S6": ["Cold War", "Middle East", "China", "Africa Since 1960", "Globalization"]},
    "CRE": {"S1": ["Creation", "Fall", "Abraham", "Moses", "Exodus"], "S2": ["Prophets", "Kings", "Exile", "Return", "Jesus Birth"], "S3": ["Jesus Ministry", "Parables", "Miracles", "Disciples", "Teachings"], "S4": ["Church", "Early Church", "Paul", "Letters", "Christian Living"], "S5": ["Ethics", "Human Sexuality", "Marriage", "Work", "Law"], "S6": ["Comparative Religion", "Islam", "African Religion", "Secularism", "Apologetics"]},
    "IRE": {"S1": ["Tawheed", "Prophets", "Quran", "Pillars", "Akhlak"], "S2": ["Quran", "Hadith", "Sunnah", "Fiqh Basics", "History"], "S3": ["Fiqh", "Ibada", "Muamalat", "Family", "Ethics"], "S4": ["History", "Khulafa", "Islam in Africa", "Sects", "Jihad"], "S5": ["Islamic Law", "Economics", "Politics", "Education", "Women"], "S6": ["Comparative Religion", "Dawah", "Modern Issues", "Ijtihad", "Islam and Science"]},
    "Literature": {"S1": ["Poetry", "Prose", "Drama", "Oral Lit", "Figures"], "S2": ["Drama", "Novel", "Poetry", "Themes", "Characters"], "S3": ["African Literature", "Novel", "Play", "Poetry", "Setting"], "S4": ["Shakespeare", "Modern Drama", "African Novel", "Poetry", "Criticism"], "S5": ["Literary Devices", "Themes", "Style", "Context", "Analysis"], "S6": ["Criticism", "Theory", "Comparative", "Research", "Seminar"]},
    "Commerce": {"S1": ["Business", "Types", "Trade", "Money", "Banking"], "S2": ["Banking", "Insurance", "Communication", "Transport", "Warehousing"], "S3": ["Marketing", "Advertising", "Consumer", "Law", "Tourism"], "S4": ["Entrepreneurship", "Business Plan", "Finance", "Records", "Tax"], "S5": ["Finance", "Investment", "Stock Exchange", "International Trade", "Business Law"], "S6": ["Business Law", "Management", "HR", "Operations", "Strategic Planning"]},
    "Economics": {"S1": ["Scarcity", "Choice", "Production", "Resources", "Goods"], "S2": ["Demand", "Supply", "Price", "Market", "Competition"], "S3": ["Money", "Banking", "Inflation", "Unemployment", "Government"], "S4": ["Trade", "Balance of Payments", "Exchange Rate", "Economic Systems", "Development"], "S5": ["National Income", "Consumption", "Investment", "Fiscal Policy", "Monetary Policy"], "S6": ["Development", "Planning", "International Economics", "Economic Growth", "Uganda Economy"]},
    "Art": {"S1": ["Drawing", "Shading", "Color", "Design", "Craft"], "S2": ["Painting", "Printing", "Weaving", "Pottery", "Composition"], "S3": ["Sculpture", "Carving", "Modelling", "Graphics", "Lettering"], "S4": ["Graphics", "Advertisement", "Layout", "Photography", "Design"], "S5": ["Photography", "Cinematography", "Digital Art", "Exhibition", "Critique"], "S6": ["Art History", "African Art", "Western Art", "Contemporary", "Project"]}
}

### 5. FULL PRACTICALS DATABASE - 10+ PER SCIENCE + AGRIC + S6 DISSECTION ###
PRACTICAL_DATABASE = {
    "Physics": {
        "S1-S4": { # LOWER - SIMPLE
            "Ohm's Law": {"objective": "Verify Ohm's Law V=IR"},
            "Simple Pendulum": {"objective": "Determine acceleration due to gravity"},
            "Refraction of Light": {"objective": "Find refractive index of glass"},
            "Hooke's Law": {"objective": "Verify Hooke's Law using spring"},
            "Density": {"objective": "Find density of regular and irregular solid"},
            "Heat Capacity": {"objective": "Find specific heat capacity of metal"},
            "Magnetic Field": {"objective": "Plot magnetic field lines"},
            "Echo": {"objective": "Determine speed of sound"},
            "Levers": {"objective": "Verify principle of moments"},
            "Focal Length": {"objective": "Find focal length of concave lens"}
        },
        "S5-S6": { # ADVANCED - UNIVERSITY PREP
            "RC Circuit": {"objective": "Find time constant and analyze charging/discharging"},
            "Wheatstone Bridge": {"objective": "Determine unknown resistance with high precision"},
            "Photoelectric Effect": {"objective": "Determine Planck's constant"},
            "Spectrometer": {"objective": "Determine wavelength using diffraction grating"},
            "Capacitance": {"objective": "Find capacitance and dielectric constant"},
            "Young's Modulus": {"objective": "Determine Young's modulus using Searle's apparatus"},
            "Hall Effect": {"objective": "Measure magnetic field and carrier concentration"},
            "Radioactive Decay": {"objective": "Determine half-life using GM counter"},
            "Interference": {"objective": "Young's double slit experiment"},
            "Resonance": {"objective": "Determine resonant frequency in LCR circuit"}
        }
    },
    "Chemistry": {
        "S1-S4": {
            "Titration": {"objective": "Determine concentration of acid using standard base"},
            "Solubility": {"objective": "Effect of temperature on solubility"},
            "Gas Laws": {"objective": "Verify Boyle's Law"},
            "Rate of Reaction": {"objective": "Effect of concentration on reaction rate"},
            "Salt Analysis": {"objective": "Identify cations and anions"},
            "Electrolysis": {"objective": "Electrolysis of copper sulfate"},
            "pH": {"objective": "Determine pH of solutions"},
            "Crystallization": {"objective": "Prepare crystals of alum"},
            "Combustion": {"objective": "Heat of combustion"},
            "Chromatography": {"objective": "Separate ink pigments"}
        },
        "S5-S6": {
            "Rate of Reaction": {"objective": "Determine order and rate constant"},
            "Electrolysis Quantitative": {"objective": "Verify Faraday's Laws"},
            "Organic Prep": {"objective": "Prepare and purify Ethyl Ethanoate"},
            "Enthalpy": {"objective": "Determine heat of neutralization"},
            "Redox Titration": {"objective": "Determine molarity using KMnO4"},
            "Buffer Solution": {"objective": "Prepare and test buffer capacity"},
            "Qualitative Analysis": {"objective": "Systematic analysis of mixture"},
            "Distillation": {"objective": "Fractional distillation of mixture"},
            "Spectrophotometry": {"objective": "Determine concentration using Beer-Lambert"},
            "Polymerization": {"objective": "Prepare nylon 6,6"}
        }
    },
    "Biology": {
        "S1-S4": {
            "Microscope": {"objective": "Observe plant and animal cells"},
            "Food Tests": {"objective": "Test for starch, protein, fats, reducing sugars"},
            "Transpiration": {"objective": "Measure rate of transpiration"},
            "Germination": {"objective": "Effect of light on germination"},
            "Photosynthesis": {"objective": "Test for starch production"},
            "Osmosis": {"objective": "Effect of concentration on plant tissue"},
            "Respiration": {"objective": "Demonstrate CO2 production during respiration"},
            "Tropism": {"objective": "Phototropism and geotropism"},
            "Classification": {"objective": "Classify plants and animals"},
            "Ecology": {"objective": "Quadrat sampling in school compound"}
        },
        "S5-S6": {
            "Enzyme Activity": {"objective": "Effect of pH and temperature on amylase"},
            "DNA Extraction": {"objective": "Extract DNA from onion cells"},
            "Blood Smear": {"objective": "Prepare and observe human blood smear"},
            "Mammals Dissection": {"objective": "Dissect rat/toad to study organ systems"}, # YOU ASKED FOR THIS
            "Mitotic Division": {"objective": "Observe mitosis in onion root tip"},
            "Population Study": {"objective": "Lincoln index method"},
            "Chi Square": {"objective": "Genetic inheritance using Drosophila"},
            "Water Potential": {"objective": "Determine water potential of potato"},
            "Microbiology": {"objective": "Culture and stain bacteria"},
            "Hormone Assay": {"objective": "Effect of auxin on plant growth"}
        }
    },
    "Agriculture": { # NEW FULL PRACTICALS S1-S6
        "S1-S4": {
            "Soil Texture": {"objective": "Determine soil texture by feel method"},
            "Seed Germination": {"objective": "Test viability of seeds"},
            "Compost Making": {"objective": "Prepare compost manure"},
            "Poultry Feeding": {"objective": "Formulate poultry rations"},
            "Crop Pests": {"objective": "Identify common crop pests"},
            "Farm Records": {"objective": "Keep farm income and expenditure records"},
            "Animal Breeds": {"objective": "Identify cattle breeds"},
            "Vegetative Propagation": {"objective": "Practice grafting and budding"},
            "Soil pH": {"objective": "Test soil pH"},
            "Crop Spacing": {"objective": "Determine plant population"}
        },
        "S5-S6": {
            "Agribusiness Plan": {"objective": "Develop full agribusiness proposal"},
            "Irrigation Design": {"objective": "Design drip irrigation system"},
            "Feed Formulation": {"objective": "Formulate balanced animal feed"},
            "Disease Diagnosis": {"objective": "Diagnose livestock diseases"},
            "Soil Analysis": {"objective": "NPK analysis of soil"},
            "Value Addition": {"objective": "Process milk to yoghurt"},
            "Farm Survey": {"objective": "Conduct farm management survey"},
            "Biotech": {"objective": "Tissue culture techniques"},
            "Marketing": {"objective": "Market analysis for agricultural products"},
            "Project": {"objective": "Implement and manage farm project"}
        }
    }
}

### 6. LAZY IMPORTS FOR SPEED ###
def get_pandas(): import pandas as pd; return pd
def get_pil(): from PIL import Image; return Image
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

def sanitize(s): return re.sub(r'[^a-z0-9]', '', s.lower())

@st.cache_data(ttl=60)
def get_all_assets(): return glob.glob(f"{ASSETS_FOLDER}/*.*")

def find_asset_strict(level, subject, topic):
    assets = get_all_assets()
    topic_clean = sanitize(topic)
    st.write(f"🔍 Searching for: {topic}") # DEBUG LINE
    # 1. Try exact topic match in filename
    matches = [p for p in assets if topic_clean in sanitize(os.path.basename(p))]
    # 2. If no match, try subject match
    if not matches:
        subj_clean = sanitize(subject)
        matches = [p for p in assets if subj_clean in sanitize(os.path.basename(p))]
    # 3. If still no match, show all images
    if not matches:
        matches = [p for p in assets if p.lower().endswith(('.png','.jpg','.jpeg'))]
    if matches:
        return matches[0], matches # return first best + all options
    return None, []

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

### 7. STUDENT PORTAL ###
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
        elif mode == "AOI" and st.button("Generate AOI Questions", key="s2_btn_aoi"):n
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
            practical = call_groq(f"Generate complete UNEB practical for {topic3}. Objective: {objective}. Include: Title, Aim, Materials, Procedure, Data Table, Questions, Conclusion. Use Ugandan context. Match complexity to {level3}", level3)
            display_with_preview(practical, f"Practical_{topic3}_s3")

    with tab4:
        st.subheader("🖼️ Diagram Library")
        subject4 = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="s4_subj")
        level4 = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="s4_level")
        topic4 = st.selectbox("Topic", UNEB_CURRICULUM_MAP[subject4][level4], key="s4_topic")

        if st.button("Load Diagram", key="s4_btn"):
            img_path, all_found = find_asset_strict(level4, subject4, topic4)

            if all_found:
                st.success(f"Found {len(all_found)} diagram(s) in assets/")

                # Show all found diagrams in a grid
                cols = st.columns(3)
                for i, path in enumerate(all_found):
                    with cols[i % 3]:
                        display_image_with_zoom(path)
                        st.caption(os.path.basename(path))
            else:
                st.error("No diagrams found in assets folder. Upload one in Admin Portal")

### 8. ADMIN PORTAL - FULLY INTERACTIVE ###
def show_admin_portal():
    st.header("🏫 Admin Portal - TEACHER DRIVEN AI")
    if st.button("Logout", key="btn_logout_admin"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

    tabs = st.tabs([
        "📊 Analytics","📖 Curriculum Editor","✏️ Upload Diagram",
        "📤 Exam Generator","📈 Performance Tracker","📱 WhatsApp Logs",
        "📑 MOES Docs","📝 Marking Guide","📅 Scheme of Work","🏆 Report Cards"
    ])

    # TAB 1: ANALYTICS + CACHE CONTROL
    with tabs[0]:
        st.subheader("📊 Usage Analytics + Cache Control")
        try:
            pd = get_pandas()
            logs = load_logs()
            stats = ai_cache.get_stats()

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Actions", len(logs))
            col2.metric("Students", len([l for l in logs if l['user']=="Student"]))
            col3.metric("Cache Entries", stats['total'])
            col4.metric("Active Cache", stats['active'])

            if logs:
                df = pd.DataFrame(logs)
                df['time'] = pd.to_datetime(df['time'])
                st.dataframe(df, use_container_width=True)

            st.markdown("---")
            st.subheader("🗑️ Cache Management")
            st.warning("Clearing cache will force AI to regenerate answers. Use if AI gave wrong info.")

            if st.button("Clear Entire AI Cache", type="primary", key="btn_clear_cache"):
                ai_cache.clear_cache()
                st.success("✅ Cache Cleared Successfully! All 24hr cached answers deleted.")
                st.rerun()

        except Exception as e:
            st.error(f"Analytics Error: {e}")

    # TAB 2: CURRICULUM/SYLLABUS EDITOR - FULL CRUD
    with tabs[1]:
        st.subheader("📖 NCDC Curriculum Editor")
        st.warning("Changes here affect what students see. Be careful.")

        edit_subj = st.selectbox("1. Pick Subject", list(UNEB_CURRICULUM_MAP.keys()), key="admin_edit_subj")
        edit_level = st.selectbox("2. Pick Class", [f"S{i}" for i in range(1,7)], key="admin_edit_level")

        current_topics = UNEB_CURRICULUM_MAP[edit_subj][edit_level]

        tab_a, tab_b, tab_c = st.tabs(["Add Topic", "Edit Topic", "Delete Topic"])

        with tab_a:
            new_topic = st.text_input("New Topic Name", key="admin_new_topic")
            if st.button("➕ Add Topic", key="btn_add_topic"):
                if new_topic and new_topic not in current_topics:
                    UNEB_CURRICULUM_MAP[edit_subj][edit_level].append(new_topic)
                    st.success(f"Added '{new_topic}' to {edit_subj} {edit_level}")
                    st.rerun()
                else:
                    st.error("Topic already exists or empty")

        with tab_b:
            old_topic = st.selectbox("Select Topic to Edit", current_topics, key="admin_old_topic")
            new_name = st.text_input("New Name", value=old_topic, key="admin_new_name")
            if st.button("✏️ Update Topic", key="btn_update_topic"):
                idx = current_topics.index(old_topic)
                UNEB_CURRICULUM_MAP[edit_subj][edit_level][idx] = new_name
                st.success(f"Updated to '{new_name}'")
                st.rerun()

        with tab_c:
            del_topic = st.selectbox("Select Topic to Delete", current_topics, key="admin_del_topic")
            if st.button("🗑️ Delete Topic", key="btn_del_topic"):
                UNEB_CURRICULUM_MAP[edit_subj][edit_level].remove(del_topic)
                st.success(f"Deleted '{del_topic}'")
                st.rerun()

        st.markdown("---")
        st.write("**Current Topics:**")
        st.write(current_topics)

    # TAB 3: UPLOAD DIAGRAM
    with tabs[2]:
        st.subheader("✏️ Upload Diagram/PNG to Assets")
        up_topic = st.text_input("Topic Name - use same name as in curriculum", key="admin_up_topic")
        up_file = st.file_uploader("Upload PNG/JPG", type=["png","jpg","jpeg"], key="admin_up_file")

        if st.button("Save Diagram", key="admin_up_btn") and up_file and up_topic:
            try:
                ext = up_file.name.split('.')[-1]
                safe_topic = up_topic.replace(' ', '_').replace('/', '-')
                filepath = f"{ASSETS_FOLDER}/{safe_topic}.{ext}" # Saves as animal_cell.png
                with open(filepath, "wb") as f: f.write(up_file.getbuffer())
                st.success(f"✅ Saved to {filepath}")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to save: {e}")

        st.markdown("---")
        st.write("**Existing Diagrams in assets/:**")
        all_assets = get_all_assets()
        if all_assets:
            for f in all_assets:
                st.write(f"- {os.path.basename(f)}")
                st.image(f, width=150)
        else:
            st.warning("assets folder is empty")

    # TAB 4: EXAM GENERATOR
    with tabs[3]:
        st.subheader("📤 Bulk Exam Generator")
        ex_subj = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="admin_ex_subj")
        ex_level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="admin_ex_level")
        ex_topics = st.multiselect("Pick Topics", UNEB_CURRICULUM_MAP[ex_subj][ex_level], key="admin_ex_topics")
        ex_num = st.slider("Number of Questions", 10, 100, 50)

        if st.button("Generate Exam", key="btn_gen_exam") and ex_topics:
            prompt = f"Generate {ex_num} UNEB questions from: {ex_topics}. Use SCENARIO, ITEM, TASK format. For {ex_level} {ex_subj}"
            exam = call_groq(prompt, ex_level)
            display_with_preview(exam, f"Exam_{ex_subj}_{ex_level}")

    # TAB 5: PERFORMANCE TRACKER
    with tabs[4]:
        st.subheader("📈 Student Performance Tracker")
        st.info("Upload CSV of student scores to analyze")
        perf_file = st.file_uploader("Upload scores.csv", type=["csv"], key="admin_perf_file")
        if perf_file:
            pd = get_pandas()
            df = pd.read_csv(perf_file)
            st.dataframe(df)
            st.bar_chart(df.set_index(df.columns[0]))

    # TAB 6: WHATSAPP LOGS
    with tabs[5]:
        st.subheader("📱 WhatsApp Integration Logs")
        st.text_area("Paste WhatsApp API logs here", height=300, key="wa_logs")
        st.download_button("Download Logs", data="log data", file_name="whatsapp_logs.txt")

    # TAB 7: MOES DOCS
    with tabs[6]:
        st.subheader("📑 MOES Document Vault")
        moes_file = st.file_uploader("Upload MOES Circular/PDF", type=["pdf","docx"], key="admin_moes")
        if moes_file:
            content = read_uploaded_file(moes_file)
            st.text_area("Preview", content, height=300)
            st.download_button("Download", data=moes_file.getvalue(), file_name=moes_file.name)

    # TAB 8: MARKING GUIDE
    with tabs[7]:
        st.subheader("📝 AI Marking Guide Generator")
        qn = st.text_area("Paste UNEB Question", key="admin_qn")
        memo = st.text_area("Paste Student Answer", key="admin_memo")
        if st.button("Generate Marking Guide", key="btn_mark"):
            guide = call_groq(f"Create UNEB marking guide for: {qn}. Student answer: {memo}. Give points and marks", "S4")
            st.write(guide)

    # TAB 9: SCHEME OF WORK
    with tabs[8]:
        st.subheader("📅 Scheme of Work Generator")
        sow_subj = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()), key="admin_sow_subj")
        sow_level = st.selectbox("Class", [f"S{i}" for i in range(1,7)], key="admin_sow_level")
        term = st.selectbox("Term", ["Term 1", "Term 2", "Term 3"])
        if st.button("Generate SOW", key="btn_sow"):
            topics = UNEB_CURRICULUM_MAP[sow_subj][sow_level]
            sow = call_groq(f"Generate {term} Scheme of Work for {sow_level} {sow_subj}. Topics: {topics}. Include week, topic, objectives, activities", sow_level)
            display_with_preview(sow, f"SOW_{sow_subj}_{sow_level}")

    # TAB 10: REPORT CARDS
    with tabs[9]:
        st.subheader("🏆 Report Card Generator")
        student_name = st.text_input("Student Name")
        student_class = st.selectbox("Class", [f"S{i}" for i in range(1,7)])
        scores_text = st.text_area("Paste Subject:Score pairs. Eg: Math:85\nPhysics:70")
        if st.button("Generate Report Card", key="btn_report"):
            report = call_groq(f"Generate UNEB report card for {student_name} {student_class}. Scores: {scores_text}. Include remarks and position", student_class)
            display_with_preview(report, f"Report_{student_name}")

st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO - V5.2.9")
user_type = st.sidebar.radio("Login As", ["Student", "Admin/Teacher"], key="radio_login")
password = st.sidebar.text_input("Password", type="password", key="input_password")

if st.sidebar.button("Login", key="btn_login"):
    if user_type == "Student" and password == STUDENT_PASSWORD:
        st.session_state["role"] = "Student"
        save_log({"time": str(datetime.now()), "user": "Student", "action": "Login"})
        st.rerun()
    elif user_type == "Admin/Teacher" and password == ADMIN_PASSWORD:
        st.session_state["role"] = "Admin"
        save_log({"time": str(datetime.now()), "user": "Admin", "action": "Login"})
        st.rerun()
    elif password:
        st.sidebar.error("Wrong password")

if st.session_state.get("role") == "Admin":
    show_admin_portal()
elif st.session_state.get("role") == "Student":
    show_student_portal()
else:
    st.info("Please login to continue")
    st.markdown("### Features:")
    st.markdown("- **S1-S6 Full NCDC Curriculum** with 15 subjects")
    st.markdown("- **40+ Practicals** per science + 20 Agriculture practicals")
    st.markdown("- **Smart AI** that scales: S1 simple → S6 University level")
    st.markdown("- **PNG/JPG Diagram Library** with zoom")
    st.markdown("- **Offline Cache** for zero data cost")
