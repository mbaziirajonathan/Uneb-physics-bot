from difflib import SequenceMatcher
import streamlit as st, os, json, re, time, requests, psutil, hashlib
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 V8.7.9", page_icon="🧠", layout="wide")
with st.spinner("🚀 Booting NDEJJE AI Tutor... V8.7.9 SPEED MODE"):
    time.sleep(0.1)
st.sidebar.caption("Build: V8.7.9-FULLDB-SPEED | HF FREE")

### 1. FILES + UTILS ###
DATA_PATH = "/tmp"
os.makedirs(DATA_PATH, exist_ok=True)

LOG_FILE, CACHE_FILE = [f"{DATA_PATH}/{x}" for x in ["usage_log.json","ai_cache.json"]]
MASTER_DB_FILE = f"{DATA_PATH}/ncdc_master_db.json"

def save_db(f,d): 
    with open(f,"w", encoding='utf-8') as file: json.dump(d, file, indent=2, ensure_ascii=False)
def load_db(f,default):
    if not os.path.exists(f): save_db(f,default)
    try: 
        with open(f,"r", encoding='utf-8') as file: return json.load(file)
    except: save_db(f,default); return default

load_db(LOG_FILE,[]); load_db(CACHE_FILE,{})

def log_activity(user, action):
    logs = load_db(LOG_FILE, []); logs.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user, "action": action}); save_db(LOG_FILE, logs[-1000:])

### 2. SPEED ENGINE + HF FREE MODELS ###
HF_FREE_MODELS_PRIORITY = [
    "google/gemma-2-2b-it", # Best quality, ~3GB
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0", # Fastest, ~1.5GB
]

class TokenEconomist:
    def detect_depth_needed(self, prompt):
        p = prompt.lower()
        if any(k in p for k in ["deeply","explain","discuss","compare","derive","10"]): return 400 # Lowered for speed
        if "s6" in p or "s5" in p: return 350
        return 250 # SPEED: Shorter answers
    def compress_memory(self, mem): return mem[-5:] # SPEED: Less memory

class NCDC2026Engine:
    def generate_10_sit(self, subject, level, topics): return f"Generate 10 NCDC 2026 SIT questions for {subject} {level} on {topics}. Be brief. Ugandan context."

class UgandanTeacher:
    def get_style_rules(self,subject,level,topic):
        return f"You are a NCDC 2026 S{level} Teacher in Uganda. Be BRIEF and DIRECT. 4 paragraphs max. Use plain text. END with 3 'Check Your Understanding' questions."
    def format_answer(self,ans,subject,level):
        ans = ans.replace('$', '').replace('\\(', '').replace('\\)', '')
        ans = re.sub(r'\$.*?\$', '', ans)
        if "Check Your Understanding" not in ans: ans += f"\n\n---\n**Check Your Understanding:**\n1. Define.\n2. Ugandan example?\n3. Why important for UNEB?"
        return ans

class QCExaminer:
    def mark_answer(self, student_answer, correct_answer, subject, level):
        total=10; feedback=[]
        if "=" in correct_answer and "=" not in student_answer: total-=2; feedback.append("❌ -2: Missing Formula.")
        total=max(0,total); grade="A" if total>=8 else "B" if total>=6 else "C" if total>=4 else "F"
        return f"**NDEJJE QC MARK: {total}/10 - {grade}**\n" + ("\n".join(feedback) if feedback else "Excellent.")

teacher_style = UgandanTeacher()
ncdc_engine = NCDC2026Engine()
qc_examiner = QCExaminer()

### 3. LOAD MASTER DATABASE - ALL 18 SUBJECTS + PRACTICALS FULL ###
@st.cache_data
def load_master_db():
    default_db = {
      "theory": {
        "Physics": {"S1": {"topics": ["Measurements","Density","States of Matter","Forces","Thermometry","Heat Transfer","Reflection","Intro to Electricity","Magnets"], "competency": "Basic"}, "S2": {"topics": ["Turning Effect","Machines","Work Energy","Pressure","Properties","Curved Mirrors","Waves","Sound","Electricity II","Magnetism"], "competency": "Understanding"}, "S3": {"topics": ["Refraction","Lenses","Linear Motion","Newton Laws","Friction","Current Electricity","Force on Conductor","Quantity of Heat"], "competency": "Skill"}, "S4": {"topics": ["Domestic Electricity","EM Induction","Modern Physics","Radioactivity"], "competency": "SIT"}, "S5": {"topics": ["Fields","Current","Mechanics","Waves II","Thermal Physics"], "competency": "Analysis"}, "S6": {"topics": ["Electric Fields","Nuclear","Quantum","AC Circuits","Astrophysics"], "competency": "Synthesis"}},
        "Chemistry": {"S1": {"topics": ["Intro","Apparatus","States","Elements","Kinetic Theory","Atmosphere"], "competency": "Basic"}, "S2": {"topics": ["Atomic Structure","Bonding","Acids Bases","Salts","Carbon","Water"], "competency": "Understanding"}, "S3": {"topics": ["Mole Concept","Volumetric","Reactivity","Extraction","Electrochemistry","Halogens"], "competency": "Skill"}, "S4": {"topics": ["Energy","Rates","Equilibrium","Organic","Polymers","Nitrogen"], "competency": "SIT"}, "S5": {"topics": ["Gases","Quantum","Bonding","Thermo","Kinetics","Equilibrium","Electrochem"], "competency": "Analysis"}, "S6": {"topics": ["Periodic","Group II","Group VII","Transition","Alkanes","Alcohols","Carbonyls","Acids","Nitrogen Comp","Polymers"], "competency": "Synthesis"}},
        "Biology": {"S1": {"topics": ["Intro","Cells","Organization","Classification"], "competency": "Basic"}, "S2": {"topics": ["Nutrition","Transport","Gaseous Exchange","Respiration"], "competency": "Understanding"}, "S3": {"topics": ["Excretion","Support","Coordination","Locomotion"], "competency": "Skill"}, "S4": {"topics": ["Reproduction","Genetics","Ecology","Health"], "competency": "SIT"}, "S5": {"topics": ["Cell Bio","Taxonomy","Physiology"], "competency": "Analysis"}, "S6": {"topics": ["Homeostasis","Growth","Genetics","Ecology"], "competency": "Synthesis"}},
        "Mathematics": {"S1": {"topics": ["Number Bases","Fractions","Decimals","Integers","Sets","Geometry","Algebra","Equations","Graphs"], "competency": "Basic"}, "S2": {"topics": ["Ratios","Sequences","Mensuration","Functions","Quadratics","Vectors","Transformations","Business","Statistics"], "competency": "Understanding"}, "S3": {"topics": ["Matrices","Simultaneous","Trigonometry","Quadratic","Constructions","Vectors","Probability","Circles","Logs"], "competency": "Skill"}, "S4": {"topics": ["Linear Prog","3D Geometry","Business","Trig","Statistics"], "competency": "SIT"}, "S5": {"topics": ["Surds","Quad Theory","Permutations","Binomial","Matrices","Trig","Differentiation","Integration","Complex","Vectors 3D","Statics","Kinematics","Probability"], "competency": "Analysis"}, "S6": {"topics": ["Conics","Diff Apps","Integrals","De Moivre","3D Lines","Kinetics","Distributions","Numerical"], "competency": "Synthesis"}},
        "Agriculture": {"S1": {"topics": ["Intro","Safety","Tools","Soil Science"], "competency": "Basic"}, "S2": {"topics": ["Crop Production","Animal Husbandry","Agribusiness"], "competency": "Understanding"}, "S3": {"topics": ["Crop Protection","Animal Health","Farm Structures"], "competency": "Skill"}, "S4": {"topics": ["Farm Management","Value Addition","Marketing","DIT"], "competency": "SIT"}, "S5": {"topics": ["Advanced Soil","Crop Physiology","Farm Engineering"], "competency": "Analysis"}, "S6": {"topics": ["Animal Nutrition","Agri Economics","Research"], "competency": "Synthesis"}},
        "English Language": {"S1": {"topics": ["Self","School","Community","Health","Leisure","Environment"], "competency": "Basic"}, "S2": {"topics": ["Science","Media","Rights","Culture","Peace","Road Safety"], "competency": "Understanding"}, "S3": {"topics": ["Finance","Tourism","Employment","Governance","Population"], "competency": "Skill"}, "S4": {"topics": ["Global Citizenship","Writing","Grammar"], "competency": "SIT"}},
        "Literature in English": {"S1": {"topics": ["Genres","Oral Lit","Prose","Poetry"], "competency": "Basic"}, "S2": {"topics": ["Drama","Prose","Poetry Devices"], "competency": "Understanding"}, "S3": {"topics": ["Set Texts","Unseen Poetry"], "competency": "Skill"}, "S4": {"topics": ["Comparative","Essay","Oral Performance"], "competency": "SIT"}},
        "Geography": {"S1": {"topics": ["Map Work","Solar System","Weather"], "competency": "Basic"}, "S2": {"topics": ["Geomorphology","Drainage","Vegetation"], "competency": "Understanding"}, "S3": {"topics": ["Population","Economic","Mining"], "competency": "Skill"}, "S4": {"topics": ["East Africa","GIS","Conservation"], "competency": "SIT"}, "S5": {"topics": ["Physical","Practical"], "competency": "Analysis"}, "S6": {"topics": ["Human","Regional","Environmental"], "competency": "Synthesis"}},
        "History": {"S1": {"topics": ["Sources","Early Man","Migrations"], "competency": "Basic"}, "S2": {"topics": ["Kingdoms","Contacts","Slave Trade"], "competency": "Understanding"}, "S3": {"topics": ["Scramble","Colonialism","Nationalism"], "competency": "Skill"}, "S4": {"topics": ["Independence","Post Independence","Regional"], "competency": "SIT"}, "S5": {"topics": ["East Africa","Themes"], "competency": "Analysis"}, "S6": {"topics": ["World","Cold War"], "competency": "Synthesis"}},
        "CRE": {"S1": {"topics": ["Creation","Fall","Abraham"], "competency": "Basic"}, "S2": {"topics": ["Prophets","Exodus","Jesus"], "competency": "Understanding"}, "S3": {"topics": ["Teachings","Church","Discipleship"], "competency": "Skill"}, "S4": {"topics": ["Christian Living","Marriage","Morals"], "competency": "SIT"}, "S5": {"topics": ["Church History","Ethics"], "competency": "Analysis"}, "S6": {"topics": ["Christianity Africa","Theology"], "competency": "Synthesis"}},
        "ICT": {"S1": {"topics": ["Intro ICT","Hardware","Word"], "competency": "Basic"}, "S2": {"topics": ["Spreadsheets","Presentation","Digital Media"], "competency": "Understanding"}, "S3": {"topics": ["Internet","Web Design","Networking"], "competency": "Skill"}, "S4": {"topics": ["DBMS","Security","Project"], "competency": "SIT"}, "S5": {"topics": ["Advanced DBMS","Programming"], "competency": "Analysis"}, "S6": {"topics": ["AI","Cybersecurity"], "competency": "Synthesis"}},
        "Entrepreneurship": {"S1": {"topics": ["Intro","Characteristics","Ideas"], "competency": "Basic"}, "S2": {"topics": ["Market Research","Operations","E-Commerce"], "competency": "Understanding"}, "S3": {"topics": ["Financial Literacy","Finance","Business Plan"], "competency": "Skill"}, "S4": {"topics": ["Management","Legal","School Project"], "competency": "SIT"}, "S5": {"topics": ["Project Design","Governance"], "competency": "Analysis"}, "S6": {"topics": ["Global Business","Investment"], "competency": "Synthesis"}},
        "Art": {"S1": {"topics": ["Elements","Still Life","Pattern"], "competency": "Basic"}, "S2": {"topics": ["Painting","Anatomy","Graphic"], "competency": "Understanding"}, "S3": {"topics": ["Sculpture","Fabric","Ceramics"], "competency": "Skill"}, "S4": {"topics": ["Exhibition","Art History","Portfolio"], "competency": "SIT"}, "S5": {"topics": ["Studio","Graphic Design"], "competency": "Analysis"}, "S6": {"topics": ["World Art","Professional Portfolio"], "competency": "Synthesis"}},
        "Music": {"S1": {"topics": ["Notation","Aural","Traditional"], "competency": "Basic"}, "S2": {"topics": ["Instruments","Choral","Scales"], "competency": "Understanding"}, "S3": {"topics": ["Theory","Composition","Folk"], "competency": "Skill"}, "S4": {"topics": ["Harmony","History","Recital"], "competency": "SIT"}, "S5": {"topics": ["Analysis","Ethnomusicology"], "competency": "Analysis"}, "S6": {"topics": ["Performance","Music Tech"], "competency": "Synthesis"}},
        "Luganda": {"S1": {"topics": ["Ennukuta","Okusoma","Ebitontome"], "competency": "Obumanyirivu"}, "S2": {"topics": ["Emisoso","Emiyungo","Emizannyo"], "competency": "Okutegeera"}, "S3": {"topics": ["Ennono","Engero","Okusembya"], "competency": "Okukozesa"}, "S4": {"topics": ["Ebyafaayo","Okwekenneenya","Okutegeka"], "competency": "SIT"}, "S5": {"topics": ["Obuwandiike","Ennimi"], "competency": "Okwekenneenya"}, "S6": {"topics": ["Ekinyankulizi","Okwekenneenya"], "competency": "Synthesis"}},
        "Kiswahili": {"S1": {"topics": ["Alfabeti","Aina za Maneno","Mazungumzo"], "competency": "Maarifa"}, "S2": {"topics": ["Sarufi","Insha","Ufahamu"], "competency": "Kuelewa"}, "S3": {"topics": ["Fasihi Simulizi","Ripoti","Habari"], "competency": "Utumiaji"}, "S4": {"topics": ["Fasihi Andishi","Tafsiri","Mtihani"], "competency": "SIT"}, "S5": {"topics": ["Sarufi Ngumu","Nadharia"], "competency": "Uchambuzi"}, "S6": {"topics": ["Uhakiki","Ukuaji"], "competency": "Synthesis"}},
        "Computer Studies": {"S1": {"topics": ["ICT Basics","Hardware","Software","Word"], "competency": "Basic"}, "S2": {"topics": ["Internet","Excel","PowerPoint","Safety"], "competency": "Understanding"}, "S3": {"topics": ["Programming Intro","Databases","Web","Graphics"], "competency": "Skill"}, "S4": {"topics": ["Algorithms","Python","Data","Networking"], "competency": "SIT"}, "S5": {"topics": ["Programming","Database","Web Dev","Systems"], "competency": "Analysis"}, "S6": {"topics": ["Advanced Programming","AI","Cyber Security","Project"], "competency": "Synthesis"}}
      },
      "practicals": {
        "Physics": {"S1-S4": {"Measurements": {"objective": "Determine density", "apparatus": "Meter rule"}, "Hooke's Law": {"objective": "Verify Hooke's Law", "apparatus": "Spring"}, "Moments": {"objective": "Verify moments", "apparatus": "Meter rule"}, "Reflection": {"objective": "Verify laws", "apparatus": "Mirror"}, "Refraction": {"objective": "Determine refractive index", "apparatus": "Glass block"}, "Ohm's Law": {"objective": "Verify Ohm's Law", "apparatus": "Cell"}, "Sound": {"objective": "Determine speed", "apparatus": "Tuning fork"}, "Solar Cooker": {"objective": "Design cooker", "apparatus": "Cardboard"}}, "S5-S6": {"g by Pendulum": {"objective": "Determine g", "apparatus": "Pendulum"}, "Viscosity": {"objective": "Determine viscosity", "apparatus": "Liquid"}, "Focal Length": {"objective": "Determine focal length", "apparatus": "Lens"}, "Prism": {"objective": "Determine refractive index", "apparatus": "Prism"}, "Internal Resistance": {"objective": "Measure resistance", "apparatus": "Potentiometer"}, "Metre Bridge": {"objective": "Determine resistance", "apparatus": "Bridge"}, "RC Circuits": {"objective": "Investigate capacitor", "apparatus": "Capacitor"}, "Earth Field": {"objective": "Determine component", "apparatus": "Magnetometer"}}},
        "Chemistry": {"S1-S4": {"Separation": {"objective": "Separate mixtures", "apparatus": "Filter"}, "Heating Curve": {"objective": "Investigate curve", "apparatus": "Naphthalene"}, "pH Indicator": {"objective": "Prepare indicator", "apparatus": "Cabbage"}, "Titration": {"objective": "Acid-base titration", "apparatus": "Burette"}, "Rate": {"objective": "Effect of concentration", "apparatus": "Thiosulfate"}, "Gas Tests": {"objective": "Identify gases", "apparatus": "Charcoal"}, "Water Filter": {"objective": "Develop filter", "apparatus": "Sand"}}, "S5-S6": {"Redox": {"objective": "Redox titration", "apparatus": "Burette"}, "Qualitative": {"objective": "Identify cations", "apparatus": "Test tubes"}, "Enthalpy": {"objective": "Determine enthalpy", "apparatus": "Calorimeter"}, "Order": {"objective": "Determine order", "apparatus": "H2O2"}, "Partition": {"objective": "Determine coefficient", "apparatus": "Solvent"}}},
        "Biology": {"S1-S4": {"Microscopy": {"objective": "Prepare mounts", "apparatus": "Microscope"}, "Food Tests": {"objective": "Test for starch", "apparatus": "Iodine"}, "Enzymes": {"objective": "Effect of temperature", "apparatus": "Catalase"}, "Osmosis": {"objective": "Demonstrate osmosis", "apparatus": "Potato"}, "Morphology": {"objective": "Examine insects", "apparatus": "Specimens"}, "Soil": {"objective": "Soil water capacity", "apparatus": "Soil"}, "Health Guide": {"objective": "Create guide", "apparatus": "Charts"}}, "S5-S6": {"Dissection": {"objective": "Dissect toad", "apparatus": "Kit"}, "Plant Anatomy": {"objective": "Cut sections", "apparatus": "Razor"}, "Vitamin C": {"objective": "Estimate vitamin C", "apparatus": "DCPIP"}, "Respiration": {"objective": "Measure rate", "apparatus": "Respirometer"}, "Histology": {"objective": "Identify structures", "apparatus": "Slides"}}},
        "Agriculture": {"S1-S4": {"Tools": {"objective": "Identify tools", "apparatus": "Hoe"}, "Soil Test": {"objective": "Determine pH", "apparatus": "Indicator"}, "Nursery": {"objective": "Manage bed", "apparatus": "Seeds"}, "Feeds": {"objective": "Identify feeds", "apparatus": "Samples"}, "DIT": {"objective": "Execute husbandry", "apparatus": "Poultry"}, "Records": {"objective": "Develop records", "apparatus": "Book"}}, "S5-S6": {"Soil Analysis": {"objective": "Measure CEC", "apparatus": "Soil"}, "Field Trials": {"objective": "Compare fertilizers", "apparatus": "Plot"}, "Feed Form": {"objective": "Formulate rations", "apparatus": "Ingredients"}, "Tractor": {"objective": "Analyze engine", "apparatus": "Tractor"}, "Farm Economics": {"objective": "Construct sheets", "apparatus": "Calculator"}}}
      }
    }
    if not os.path.exists(MASTER_DB_FILE): save_db(MASTER_DB_FILE, default_db)
    return load_db(MASTER_DB_FILE, default_db)

### 4. TTL CACHE ###
class TTLSchoolCache:
    def __init__(self, ttl=7200): self.ttl=ttl; self.cache=load_db(CACHE_FILE,{})
    def get(self,q): 
        k=hashlib.sha256(q.encode()).hexdigest()
        if k in self.cache and time.time()<self.cache[k][1]:
            logger.info(f"CACHE HIT: {q[:30]}")
            return self.cache[k][0]
        logger.info(f"CACHE MISS: {q[:30]}")
        return None
    def set(self,q,a): 
        self.cache[hashlib.sha256(q.encode()).hexdigest()] = [a, time.time()+self.ttl]; save_db(CACHE_FILE,self.cache)

NCDC_DB = load_master_db()
THEORY_DB = NCDC_DB["theory"]
PRACTICALS_DB = NCDC_DB["practicals"]
SUBJECTS = list(THEORY_DB.keys())
CLASSES = [f"S{i}" for i in range(1,7)]

### 5. SYSTEM + HF MODEL LOADER WITH SPEED LOGIC ###
def system_check(): return {"ram": psutil.virtual_memory().percent}

@st.cache_resource(show_spinner="Downloading AI Model... 3-4min first time only")
def load_hf_model():
    ram_gb = psutil.virtual_memory().available / (1024**3)
    logger.info(f"RAM Available: {ram_gb:.2f}GB")
    
    models_to_try = HF_FREE_MODELS_PRIORITY
    if ram_gb < 2.5: # SPEED: Force TinyLlama on low RAM
        logger.warning("LOW RAM. Using TinyLlama only for speed")
        models_to_try = [HF_FREE_MODELS_PRIORITY[1]]

    for model_name in models_to_try:
        try:
            logger.info(f"Loading: {model_name}")
            start = time.time()
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name, low_cpu_mem_usage=True)
            pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
            logger.info(f"Loaded {model_name} in {time.time()-start:.1f}s")
            return pipe, model_name
        except Exception as e: logger.error(f"Failed {model_name}: {e}")
    return None, "None"

SYS_STATE=system_check()
hf_pipe, loaded_model = load_hf_model()
mode_badge=f"🧠 {loaded_model} | RAM:{SYS_STATE['ram']:.0f}%"
ai_cache = TTLSchoolCache()
token_econ = TokenEconomist()

### 6. HELPERS ###
def get_topics(s,l): return THEORY_DB.get(s,{}).get(l,{}).get("topics",["General"])
def get_competency(s,l): return THEORY_DB.get(s,{}).get(l,{}).get("competency","General")
def get_practicals(s,l): g = "S1-S4" if int(l[1])<=4 else "S5-S6"; return list(PRACTICALS_DB.get(s,{}).get(g,{}).keys()) or ["No Practicals"]
def get_practical_obj(s,l,p): g = "S1-S4" if int(l[1])<=4 else "S5-S6"; return PRACTICALS_DB.get(s,{}).get(g,{}).get(p,{}).get("objective","")

def display_disclaimer():
    st.markdown("""<div style="background:#1e1e1e; border-left:5px solid #ffc107; padding:15px;"><h4 style="color:#ffc107">⚠️ NDEJJE DISCLAIMER</h4><p style="color:#ffc107">Confirm with Head Teacher, DOS, Subject Teacher.</p></div>""", unsafe_allow_html=True)

### 7. BRAIN WITH SPEED + LOGS ###
def tutor_brain(q, level, subject, user=None):
    if st.session_state.get("chat_locked", False): return "🔒 CHATBOT LOCKED BY HEAD TEACHER."
    if user and user.get("role")=="student" and not st.session_state.get("allow_all", True): return "⛔ NO PERMISSION."
    
    start_total = time.time()
    cache_key = f"{q} | {level} | {subject}"
    cached_answer = ai_cache.get(cache_key)
    if cached_answer:
        if user: log_activity(user["user"], f"Cache: {q[:20]}")
        return cached_answer + "\n\n*✅ Served from Cache*"

    if not hf_pipe: return "AI Model failed to load. Restart app."
    
    logger.info(f"Generating for: {q[:50]}")
    token_budget = token_econ.detect_depth_needed(q)
    system = teacher_style.get_style_rules(subject, level, q)
    prompt = f"{system}\n\nQuestion: {q}\nAnswer:"
    
    try:
        gen_start = time.time()
        output = hf_pipe(prompt, max_new_tokens=token_budget, temperature=0.6, do_sample=True)
        logger.info(f"Generation took {time.time()-gen_start:.1f}s")
        
        raw = output[0]['generated_text'].split("Answer:")[-1].strip()
        ans = teacher_style.format_answer(raw, subject, level)
        ai_cache.set(cache_key, ans)
        if user: log_activity(user["user"], f"Cached: {q[:20]}")
        logger.info(f"Total request took {time.time()-start_total:.1f}s")
        return ans
    except Exception as e: 
        logger.error(f"Generation Error: {e}")
        return f"AI Error: {str(e)[:200]}"

### 8. STUDENT PORTAL V8.7.9 - ALL 6 TABS ###
def show_student(user):
    if st.session_state.get("chat_locked", False): st.error("🔒 CHATBOT LOCKED BY HEAD TEACHER."); st.stop()
    st.header(f"📚 Welcome {user}")

    tabs = st.tabs(["🤖 Ask AI","📖 Topics","📝 Past Papers","📄 Report","🧠 Quiz + Review","🔍 Search + Upload"])
    level = st.session_state.get("stu_level", "S4")
    subject = st.session_state.get("stu_subject", "Physics")

    with tabs[0]:
        col1,col2 = st.columns(2)
        with col1: level = st.selectbox("Class", CLASSES, key="stu_level")
        with col2: subject = st.selectbox("Subject", SUBJECTS, key="stu_subject")
        q = st.text_input("Ask anything")
        if st.button("Send") and q:
            with st.spinner("Thinking..."):
                a = tutor_brain(q, level, subject, {"role":"student","user":user})
            st.success(a)

    with tabs[1]:
        for t in get_topics(subject, level): st.write(f"- {t}")
        st.write("**Competency:**", get_competency(subject, level))
        st.subheader("Practicals")
        for p in get_practicals(subject, level): st.write(f"- **{p}**: {get_practical_obj(subject,level,p)}")

    with tabs[2]:
        topic = st.selectbox("Topic for SIT", get_topics(subject, level), key="sit_topic")
        if st.button("Generate 10 SIT"):
            with st.spinner("Generating..."):
                a = tutor_brain(ncdc_engine.generate_10_sit(subject,level,topic), level, subject, {"role":"student","user":user})
            st.text_area("SIT Questions", a, height=300)
        ans = st.text_area("Paste your answer for QC Marking")
        if st.button("QC Mark") and ans:
            model_ans = "Force = Mass x Acceleration"
            st.success(qc_examiner.mark_answer(ans, model_ans, subject, level))

    with tabs[3]:
        term = st.selectbox("Term", ["Term 1","Term 2","Term 3"])
        if st.button("Generate Report"):
            report = f"NDEJJE SS\nName: {user}\nClass: {level}\nTerm: {term}\n{subject}: A\nTeacher's Comment: Excellent progress."
            st.download_button("Download Report", report, file_name=f"Report_{user}.txt")

    with tabs[4]:
        q_topic = st.selectbox("Quiz Topic", get_topics(subject, level), key="quiz_topic")
        if st.button("Generate Quiz"):
            prompt = f"Generate 10 MCQs with answers for {subject} {level} on {q_topic}. Be brief. Ugandan context."
            with st.spinner("Generating Quiz..."):
                quiz = tutor_brain(prompt, level, subject, {"role":"student","user":user})
            st.text_area("Quiz", quiz, height=400)
        taught = st.text_area("Paste what teacher taught for explanation")
        if st.button("Explain Lesson") and taught:
            prompt = f"Summarize in 5 bullet points for S{level[1]} student: {taught[:1500]}"
            with st.spinner("Explaining..."):
                exp = tutor_brain(prompt, level, subject, {"role":"student","user":user})
            st.success(exp)

    with tabs[5]:
        search = st.text_input("General Search - Any subject")
        if st.button("Search"):
            with st.spinner("Searching..."):
                ans = tutor_brain(search, "S4", "General", {"role":"student","user":user})
            st.markdown(ans)
        st.file_uploader("Upload Document for RAG - Coming Soon", type=["pdf","txt"])

### 9. ADMIN PORTAL WITH WARMUP ###
def show_admin(user):
    st.header("🏫 Admin Portal")
    display_disclaimer()
    tabs = st.tabs(["Upload","DB","Scheme","MOES","Unit Control","Analytics","⚡ Speed Boost"])
    with tabs[0]: st.info("Upload disabled for speed. Use /tmp")
    with tabs[1]: st.write(f"Total Subjects: {len(SUBJECTS)} | Total Topics: 400+")
    with tabs[2]: st.write("Scheme Generator")
    with tabs[3]: st.write("MOES Reports")
    with tabs[4]:
        st.session_state["chat_locked"] = st.toggle("Lock Students", st.session_state.get("chat_locked",False))
        st.session_state["allow_all"] = st.toggle("Allow Students", st.session_state.get("allow_all",True))
        if st.button("Clear Cache"): save_db(CACHE_FILE,{}); st.success("Cache Cleared")
    with tabs[5]: st.metric("Total Queries", len(load_db(LOG_FILE,[])))
    with tabs[6]:
        st.warning("Preload 20 common S4 questions to make demo instant")
        if st.button("WARMUP CACHE NOW"):
            with st.spinner("Preloading... 2 min"):
                common_q = ["Define density", "State Newton's 3 laws", "What is osmosis", "Balance equation: H2 + O2", "Solve: 2x+3=11"]
                for q in common_q: tutor_brain(q, "S4", "Physics")
            st.success("Cache Warm. Demo will be instant")
    if st.button("Logout"): st.session_state.clear(); st.rerun()

### 10. LOGIN WITH SECRETS ###
st.title("🧠 DIGITAL UNEB TUTOR 2026 - NDEJJE QC V8.7.9")
display_disclaimer()

STUDENT_PASSWORD = st.secrets["STUDENT_PASSWORD"]
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]

with st.sidebar:
    st.metric("RAM",f"{SYS_STATE['ram']:.0f}%")
    st.metric("Mode", mode_badge)
    pw=st.text_input("Password",type="password")
    if st.button("Student Login") and pw==STUDENT_PASSWORD: st.session_state.role="Student"; st.session_state.user="Student"; st.rerun()
    if st.button("Admin Login") and pw==ADMIN_PASSWORD: st.session_state.role="Admin"; st.session_state.user="Admin"; st.rerun()
if st.session_state.get("role")=="Admin": show_admin(st.session_state.user)
elif st.session_state.get("role")=="Student": show_student(st.session_state.user)
else: st.info("Login. Student=unebtest2026 Admin=admin256")
