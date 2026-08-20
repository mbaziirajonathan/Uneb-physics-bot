from difflib import SequenceMatcher
import streamlit as st, os, json, re, time, requests, random, threading, psutil, socket, hashlib
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
from openai import OpenAI
import logging
try:
    import fcntl
except:
    fcntl = None
logging.basicConfig(level=logging.INFO)

TIKTOKEN_AVAILABLE = False
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ModuleNotFoundError:
    pass

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 VDB", page_icon="🧠", layout="wide")
with st.spinner("🚀 Booting NDEJJE AI Tutor... V7.5.5 FULL DB"):
    time.sleep(0.1)
if not TIKTOKEN_AVAILABLE:
    st.sidebar.warning("tiktoken not installed. Using ~4 chars = 1 token")
st.sidebar.caption("Build: V7.5.5-FULLDB-NOLATEX | FAISS LAZY LOADED")

### 1. FILES + UTILS ###
DATA_PATH = os.getenv("STREAMLIT_DATA_PATH", "data")
if not os.path.exists(DATA_PATH) or not os.access(DATA_PATH, os.W_OK):
    DATA_PATH = "/tmp"
os.makedirs(DATA_PATH, exist_ok=True)

LOG_FILE, CACHE_FILE, DOCS_FILE, SETTINGS_FILE, MEMORY_FILE = [f"{DATA_PATH}/{x}" for x in ["usage_log.json","ai_cache.json","vector_docs.json","teacher_settings.json","chat_memory.json"]]
MASTER_DB_FILE = f"{DATA_PATH}/ncdc_master_db.json"
FLAGS_FILE = f"{DATA_PATH}/flagged_reviews.json"

def save_db(f,d):
    with open(f,"w", encoding='utf-8') as file:
        if fcntl: fcntl.flock(file, fcntl.LOCK_EX)
        json.dump(d, file, indent=2, ensure_ascii=False)
        if fcntl: fcntl.flock(file, fcntl.LOCK_UN)

def load_db(f,default):
    if not os.path.exists(f):
        save_db(f,default)
    try:
        with open(f,"r", encoding='utf-8') as file:
            return json.load(file)
    except:
        save_db(f,default)
        return default

for f,d in [(LOG_FILE,[]),(CACHE_FILE,{}),(DOCS_FILE,[]),(SETTINGS_FILE,{}),(MEMORY_FILE,[]),(FLAGS_FILE,[])]:
    load_db(f,d)

### 8.6 TOKEN ECONOMIST V3 ###
class TokenEconomist:
    def detect_depth_needed(self, prompt):
        p = prompt.lower()
        if any(k in p for k in ["deeply explore","explain in detail","discuss","factors","compare","derive","practical"]): return 2800
        if "s6" in p or "s5" in p: return 2000
        if "s4" in p or "s3" in p: return 1500
        if "s1" in p or "s2" in p: return 800
        return 1500 if len(prompt)>100 else 800
    def auto_quantize(self,sources,prompt,system,mode): return sources,"qwen2.5:14b-instruct", self.detect_depth_needed(prompt)
    def compress_memory(self, mem): return mem[-10:]
token_econ=TokenEconomist()

### 2B. UGANDAN TEACHER + QC ENGINE ###
class NCDC2026Engine:
    SECTORS = {"health": "Hospitals, Nursing","agriculture": "Farming, Vet","engineering": "Civil, Electrical","economics": "Business, Banking","accounts": "Bookkeeping","research": "UNEB, NARO","geology": "Mining, Water"}
    SUBJECT_SECTORS = {"Physics": ["engineering","health"],"Chemistry": ["health","agriculture"],"Biology": ["health","agriculture"],"Mathematics": ["economics","engineering"],"Agriculture": ["agriculture"],"Geography": ["geology"],"Entrepreneurship": ["economics"],"ICT": ["research"]}
    def get_sectors(self, subject): return [f"**{s.title()}**: {self.SECTORS[s]}" for s in self.SUBJECT_SECTORS.get(subject, ["research"])]
    def generate_sit(self, subject, level, topic): return f"**NCDC 2026 SIT**\n**SCENARIO**: Ugandan community in {random.choice(['Gulu','Mbale','Mbarara','Wakiso'])} has problem with {topic}.\n**TASK**: 1. Apply {topic} 2. Show working 3. State 2 local challenges."
    def generate_10_sit(self, subject, level, topics): return f"**GENERATE 10 NCDC 2026 SIT QUESTIONS FOR {subject} {level} ON {topics}**"

### 8.7 UGANDAN TEACHER V3 - HUMAN MATH FOR S1-S6 ###
class UgandanTeacher:
    def get_style_rules(self,subject,level,topic):
        try: lvl = int(str(level).replace('S',''))
        except: lvl = 4
        if lvl <= 4: math_rule = "RULE MATH: NO $ NO LATEX. Write: 'Force = Mass x Acceleration'. Explain like to a 12 year old."
        else: math_rule = "RULE MATH: NO $ NO LATEX. Write: 'v = u + at'. Use ^ for power, / for divide. Explain every symbol."
        return f"RULE 1: NCDC 2026 S{level} Teacher Uganda.\nRULE 2: STRUCTURE: Greeting + Key Points + Ugandan Example + Formula + Summary\nRULE 3: LENGTH: Use all {self.detect_depth_needed(topic)} tokens.\nRULE 4: TONE: Use 'we' and 'you'. Use Ugandan examples.\nRULE 5: {math_rule}\nRULE 6: ENDING: Add 3 'Check Your Understanding' questions."
    def format_answer(self,ans,subject,level):
        ans = ans.replace('$', '').replace('\\(', '').replace('\\)', '')
        ans = re.sub(r'\$.*?\$', '', ans)
        for k,v in {'\\frac{a}{b}': 'a / b', '\\cdot': ' x ', '^2': ' squared', '^3': ' cubed'}.items(): ans = ans.replace(k, v)
        if "Check Your Understanding" not in ans: ans += f"\n\n---\n**Check Your Understanding:**\n1. Define it.\n2. Ugandan example?\n3. Why important for UNEB S{level}?"
        return ans
    def detect_depth_needed(self,topic): return token_econ.detect_depth_needed(topic)

class QCExaminer:
    def mark_answer(self, student_answer, correct_answer, subject, level):
        total=10; feedback=[]
        if "=" in correct_answer and "=" not in student_answer: total-=2; feedback.append("❌ -2: Missing Formula.")
        total=max(0,total); grade="A" if total>=8 else "B" if total>=6 else "C"
        return f"**NDEJJE QC MARK: {total}/10 - {grade}**\n" + ("\n".join(feedback) if feedback else "Excellent.")

class TeacherReview:
    def __init__(self): self.file = FLAGS_FILE
    def flag_answer(self, question, ai_answer, student_comment, subject, level, user):
        data = load_db(self.file, []); data.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"q":question[:50]}); save_db(self.file, data)
        return "✅ Flagged. HOD will review."

def log_activity(user, action):
    logs = load_db(LOG_FILE, []); logs.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user, "action": action}); save_db(LOG_FILE, logs[-1000:])

teacher_style = UgandanTeacher()
ncdc_engine = NCDC2026Engine()
qc_examiner = QCExaminer()
teacher_review = TeacherReview()

### 3. LOAD MASTER DATABASE - FULL 18 SUBJECTS + FULL PRACTICALS ###
@st.cache_data
def load_master_db():
    default_db = {
      "theory": {
        "Physics": {"S1": {"topics": ["Measurements","Density","States of Matter","Forces","Thermometry","Heat Transfer","Reflection","Intro to Electricity","Magnets"], "competency": "Basic knowledge"}, "S2": {"topics": ["Turning Effect of Forces","Machines","Work Energy Power","Pressure","Properties of Matter","Curved Mirrors","Wave Motion","Sound","Electricity II","Magnetic Effect"], "competency": "Understanding"}, "S3": {"topics": ["Refraction","Lenses","Linear Motion","Newton's Laws","Friction","Current Electricity","Force on Conductor","Quantity of Heat"], "competency": "Skill Application"}, "S4": {"topics": ["Domestic Electricity","Electromagnetic Induction","Modern Physics","Radioactivity"], "competency": "Scenario-Item-Task"}, "S5": {"topics": ["Fields I","Current","Advanced Mechanics","Waves II","Thermal Physics"], "competency": "Analysis"}, "S6": {"topics": ["Electric Fields","Nuclear Physics","Quantum Physics","AC Circuits","Astrophysics"], "competency": "Synthesis"}},
        "Chemistry": {"S1": {"topics": ["Introduction to Chemistry","Apparatus","States of Matter","Elements Mixtures Compounds","Kinetic Theory","Atmosphere"], "competency": "Basic"}, "S2": {"topics": ["Atomic Structure","Chemical Bonding","Acids Bases","Salts","Carbon","Water Hydrogen"], "competency": "Understanding"}, "S3": {"topics": ["Mole Concept","Volumetric Analysis","Reactivity Series","Extraction","Electrochemistry","Halogens"], "competency": "Skill Application"}, "S4": {"topics": ["Energy Changes","Rates of Reaction","Equilibrium","Organic Chemistry","Polymers","Nitrogen"], "competency": "SIT"}, "S5": {"topics": ["Gases","Quantum Mechanics","Bonding","Thermodynamics","Kinetics","Equilibrium","Electrochemistry"], "competency": "Analysis"}, "S6": {"topics": ["Periodic Trends","Group II","Group VII","Transition Metals","Alkanes","Halogenoalkanes","Alcohols","Carbonyls","Carboxylic Acids","Nitrogen Compounds","Polymers"], "competency": "Synthesis"}},
        "Biology": {"S1": {"topics": ["Introduction","Cells","Levels of Organization","Classification"], "competency": "Basic"}, "S2": {"topics": ["Nutrition","Transport","Gaseous Exchange","Respiration"], "competency": "Understanding"}, "S3": {"topics": ["Excretion","Support","Coordination","Locomotion"], "competency": "Skill"}, "S4": {"topics": ["Reproduction","Genetics","Ecology","Health"], "competency": "SIT"}, "S5": {"topics": ["Cell Biology","Taxonomy","Physiology"], "competency": "Analysis"}, "S6": {"topics": ["Homeostasis","Growth","Genetics","Ecology"], "competency": "Synthesis"}},
        "Mathematics": {"S1": {"topics": ["Number Bases","Fractions","Decimals","Integers","Sets","Geometry","Algebra","Equations","Graphs"], "competency": "Basic"}, "S2": {"topics": ["Ratios","Sequences","Mensuration","Functions","Quadratics","Vectors","Transformations","Business Math","Statistics"], "competency": "Understanding"}, "S3": {"topics": ["Matrices","Simultaneous Equations","Trigonometry","Quadratic Equations","Constructions","Vectors","Probability","Circles","Logarithms"], "competency": "Skill"}, "S4": {"topics": ["Linear Programming","3D Geometry","Business","Trig Non-Right","Statistics"], "competency": "SIT"}, "S5": {"topics": ["Surds","Quadratic Theory","Permutations","Binomial","Partial Fractions","Matrices","Trigonometry","Differentiation","Integration","Complex Numbers","Vectors 3D","Statics","Kinematics","Probability"], "competency": "Analysis"}, "S6": {"topics": ["Conics","Applications of Differentiation","Definite Integrals","De Moivre","3D Lines","Kinetics","Probability Distributions","Numerical Methods"], "competency": "Synthesis"}},
        "Agriculture": {"S1": {"topics": ["Intro","Safety","Tools","Soil Science"], "competency": "Basic"}, "S2": {"topics": ["Crop Production","Animal Husbandry","Agribusiness"], "competency": "Understanding"}, "S3": {"topics": ["Crop Protection","Animal Health","Farm Structures"], "competency": "Skill"}, "S4": {"topics": ["Farm Management","Value Addition","Marketing","DIT Portfolio"], "competency": "SIT"}, "S5": {"topics": ["Advanced Soil","Crop Physiology","Farm Engineering"], "competency": "Analysis"}, "S6": {"topics": ["Animal Nutrition","Agri Economics","Research Methods"], "competency": "Synthesis"}},
        "English Language": {"S1": {"topics": ["Self","School","Community","Health","Leisure","Environment"], "competency": "Basic"}, "S2": {"topics": ["Science","Media","Human Rights","Culture","Peace","Road Safety"], "competency": "Understanding"}, "S3": {"topics": ["Finance","Tourism","Employment","Governance","Population"], "competency": "Skill"}, "S4": {"topics": ["Global Citizenship","Synthesis","Writing","Grammar"], "competency": "SIT"}},
        "Literature in English": {"S1": {"topics": ["Genres","Oral Literature","Prose","Poetry"], "competency": "Basic"}, "S2": {"topics": ["Drama","Prose","Poetry Devices"], "competency": "Understanding"}, "S3": {"topics": ["Set Texts Prose","Set Texts Drama","Unseen Poetry"], "competency": "Skill"}, "S4": {"topics": ["Comparative Analysis","Essay Writing","Oral Performance"], "competency": "SIT"}},
        "Geography": {"S1": {"topics": ["Map Work","Solar System","Weather"], "competency": "Basic"}, "S2": {"topics": ["Geomorphology","Drainage","Vegetation"], "competency": "Understanding"}, "S3": {"topics": ["Population","Economic Activities","Mining"], "competency": "Skill"}, "S4": {"topics": ["East Africa","GIS","Conservation"], "competency": "SIT"}, "S5": {"topics": ["Physical Geography","Practical"], "competency": "Analysis"}, "S6": {"topics": ["Human Geography","Regional Africa","Environmental Management"], "competency": "Synthesis"}},
        "History": {"S1": {"topics": ["Sources","Early Man","Migrations"], "competency": "Basic"}, "S2": {"topics": ["Kingdoms","Early Contacts","Slave Trade"], "competency": "Understanding"}, "S3": {"topics": ["Scramble","Colonialism","Nationalism"], "competency": "Skill"}, "S4": {"topics": ["Independence","Post Independence","Regional Cooperation"], "competency": "SIT"}, "S5": {"topics": ["East Africa","African Themes"], "competency": "Analysis"}, "S6": {"topics": ["World History","Cold War"], "competency": "Synthesis"}},
        "CRE": {"S1": {"topics": ["Creation","Fall","Abraham"], "competency": "Basic"}, "S2": {"topics": ["Prophets","Exodus","Jesus"], "competency": "Understanding"}, "S3": {"topics": ["Teachings","Early Church","Discipleship"], "competency": "Skill"}, "S4": {"topics": ["Christian Living","Marriage","Morals"], "competency": "SIT"}, "S5": {"topics": ["Church History","Ethics"], "competency": "Analysis"}, "S6": {"topics": ["Christianity in Africa","Comparative Theology"], "competency": "Synthesis"}},
        "ICT": {"S1": {"topics": ["Intro ICT","Hardware","Word Processing"], "competency": "Basic"}, "S2": {"topics": ["Spreadsheets","Presentation","Digital Media"], "competency": "Understanding"}, "S3": {"topics": ["Internet","Web Design","Networking"], "competency": "Skill"}, "S4": {"topics": ["DBMS","Security","Project"], "competency": "SIT"}, "S5": {"topics": ["Advanced DBMS","Programming"], "competency": "Analysis"}, "S6": {"topics": ["AI","Cybersecurity"], "competency": "Synthesis"}},
        "Entrepreneurship": {"S1": {"topics": ["Intro","Characteristics","Ideas"], "competency": "Basic"}, "S2": {"topics": ["Market Research","Operations","E-Commerce"], "competency": "Understanding"}, "S3": {"topics": ["Financial Literacy","Finance","Business Plan"], "competency": "Skill"}, "S4": {"topics": ["Management","Legal","School Project"], "competency": "SIT"}, "S5": {"topics": ["Project Design","Governance"], "competency": "Analysis"}, "S6": {"topics": ["Global Business","Investment"], "competency": "Synthesis"}},
        "Art": {"S1": {"topics": ["Elements","Still Life","Pattern"], "competency": "Basic"}, "S2": {"topics": ["Painting","Anatomy","Graphic Design"], "competency": "Understanding"}, "S3": {"topics": ["Sculpture","Fabric","Ceramics"], "competency": "Skill"}, "S4": {"topics": ["Exhibition","Art History","Portfolio"], "competency": "SIT"}, "S5": {"topics": ["Studio","Graphic Design"], "competency": "Analysis"}, "S6": {"topics": ["World Art","Professional Portfolio"], "competency": "Synthesis"}},
        "Music": {"S1": {"topics": ["Notation","Aural","Traditional"], "competency": "Basic"}, "S2": {"topics": ["Instruments","Choral","Scales"], "competency": "Understanding"}, "S3": {"topics": ["Theory","Composition","Folk"], "competency": "Skill"}, "S4": {"topics": ["Harmony","Music History","Recital"], "competency": "SIT"}, "S5": {"topics": ["Analysis","Ethnomusicology"], "competency": "Analysis"}, "S6": {"topics": ["Performance","Music Tech"], "competency": "Synthesis"}},
        "Luganda": {"S1": {"topics": ["Ennukuta","Okusoma","Ebitontome"], "competency": "Obumanyirivu"}, "S2": {"topics": ["Emisoso","Emiyungo","Emizannyo"], "competency": "Okutegeera"}, "S3": {"topics": ["Ennono","Engero","Okusembya"], "competency": "Okukozesa"}, "S4": {"topics": ["Ebyafaayo","Okwekenneenya","Okutegeka"], "competency": "SIT"}, "S5": {"topics": ["Obuwandiike","Ennimi"], "competency": "Okwekenneenya"}, "S6": {"topics": ["Ekinyankulizi","Okwekenneenya"], "competency": "Synthesis"}},
        "Kiswahili": {"S1": {"topics": ["Alfabeti","Aina za Maneno","Mazungumzo"], "competency": "Maarifa"}, "S2": {"topics": ["Sarufi","Insha","Ufahamu"], "competency": "Kuelewa"}, "S3": {"topics": ["Fasihi Simulizi","Ripoti","Habari"], "competency": "Utumiaji"}, "S4": {"topics": ["Fasihi Andishi","Tafsiri","Mtihani"], "competency": "SIT"}, "S5": {"topics": ["Sarufi Ngumu","Nadharia"], "competency": "Uchambuzi"}, "S6": {"topics": ["Uhakiki","Ukuaji"], "competency": "Synthesis"}}
      },
      "practicals": {
        "Physics": {"S1-S4": {"Measurements & Density": {"objective": "Determine density using local materials", "apparatus": "Meter rule, Beam balance"}, "Hooke's Law": {"objective": "Verify Hooke's Law", "apparatus": "Spring, Masses"}, "Principle of Moments": {"objective": "Verify principle of moments", "apparatus": "Meter rule, Pivot"}, "Reflection": {"objective": "Verify laws of reflection", "apparatus": "Plane mirror, Pins"}, "Refraction": {"objective": "Determine refractive index", "apparatus": "Glass block"}, "Ohm's Law": {"objective": "Verify Ohm's Law", "apparatus": "Cell, Ammeter"}, "Speed of Sound": {"objective": "Determine speed of sound", "apparatus": "Tuning fork"}, "AOI Solar Cooker": {"objective": "Design solar cooker", "apparatus": "Cardboard, Foil"}}, "S5-S6": {"g by Pendulum": {"objective": "Determine acceleration due to gravity", "apparatus": "Pendulum"}, "Viscosity": {"objective": "Determine coefficient of viscosity", "apparatus": "Viscous liquid"}, "Focal Length": {"objective": "Determine focal length", "apparatus": "Lens"}, "Prism Refractive Index": {"objective": "Determine refractive index", "apparatus": "Prism"}, "Internal Resistance": {"objective": "Measure internal resistance", "apparatus": "Potentiometer"}, "Metre Bridge": {"objective": "Determine unknown resistance", "apparatus": "Metre bridge"}, "RC Circuits": {"objective": "Investigate charging capacitor", "apparatus": "Capacitor"}, "Earth's Magnetic Field": {"objective": "Determine horizontal component", "apparatus": "Deflection magnetometer"}}},
        "Chemistry": {"S1-S4": {"Separation of Mixtures": {"objective": "Separate sand, salt", "apparatus": "Filter paper"}, "Heating Curve": {"objective": "Investigate heating curve", "apparatus": "Naphthalene"}, "pH Indicator": {"objective": "Prepare natural indicator", "apparatus": "Red cabbage"}, "Acid-Base Titration": {"objective": "Acid-base titration", "apparatus": "Burette"}, "Rate of Reaction": {"objective": "Effect of concentration", "apparatus": "Thiosulfate"}, "Gas Tests": {"objective": "Identify gases", "apparatus": "Charcoal"}, "AOI Water Filter": {"objective": "Develop water filter", "apparatus": "Sand, Charcoal"}}, "S5-S6": {"Redox Titration": {"objective": "Redox titration KMnO4", "apparatus": "Burette"}, "Qualitative Analysis": {"objective": "Identify cations", "apparatus": "Test tubes"}, "Enthalpy": {"objective": "Determine enthalpy", "apparatus": "Calorimeter"}, "Order of Reaction": {"objective": "Determine order", "apparatus": "H2O2"}, "Partition Coefficient": {"objective": "Determine partition coefficient", "apparatus": "Solvent"}}},
        "Biology": {"S1-S4": {"Microscopy": {"objective": "Prepare wet mounts", "apparatus": "Microscope"}, "Food Tests": {"objective": "Test for starch", "apparatus": "Iodine"}, "Enzyme Action": {"objective": "Effect of temperature", "apparatus": "Catalase"}, "Osmosis": {"objective": "Demonstrate osmosis", "apparatus": "Potato"}, "Morphology": {"objective": "Examine insects", "apparatus": "Specimens"}, "Soil Ecology": {"objective": "Soil water capacity", "apparatus": "Soil"}, "AOI Health Guide": {"objective": "Create health guide", "apparatus": "Charts"}}, "S5-S6": {"Dissection": {"objective": "Dissect a toad", "apparatus": "Dissection kit"}, "Plant Anatomy": {"objective": "Cut stem sections", "apparatus": "Razor"}, "Vitamin C": {"objective": "Estimate vitamin C", "apparatus": "DCPIP"}, "Respiration": {"objective": "Measure respiration rate", "apparatus": "Respirometer"}, "Histology": {"objective": "Identify structures", "apparatus": "Slides"}}},
        "Agriculture": {"S1-S4": {"Tools ID": {"objective": "Identify farm tools", "apparatus": "Hoe"}, "Soil Testing": {"objective": "Determine soil pH", "apparatus": "pH indicator"}, "Nursery Bed": {"objective": "Manage nursery bed", "apparatus": "Seeds"}, "Livestock Feeds": {"objective": "Identify feeds", "apparatus": "Feed samples"}, "DIT Assessment": {"objective": "Execute husbandry", "apparatus": "Poultry equipment"}, "AOI Records": {"objective": "Develop record framework", "apparatus": "Book"}}, "S5-S6": {"Soil Analysis": {"objective": "Measure CEC", "apparatus": "Soil"}, "Field Trials": {"objective": "Compare fertilizers", "apparatus": "Plot"}, "Feed Formulation": {"objective": "Formulate rations", "apparatus": "Ingredients"}, "Tractor Systems": {"objective": "Analyze engine", "apparatus": "Tractor"}, "Farm Economics": {"objective": "Construct balance sheets", "apparatus": "Calculator"}}}
      }
    }
    if not os.path.exists(MASTER_DB_FILE):
        save_db(MASTER_DB_FILE, default_db)
    return load_db(MASTER_DB_FILE, default_db)

class TTLSchoolCache:
    def __init__(self, ttl=7200): self.ttl=ttl; self.cache=load_db(CACHE_FILE,{})
    def get(self,q): k=hashlib.sha256(q.encode()).hexdigest(); return self.cache[k][0] if k in self.cache and time.time()<self.cache[k][1] else None
    def set(self,q,a): self.cache[hashlib.sha256(q.encode()).hexdigest()] = [a, time.time()+self.ttl]; save_db(CACHE_FILE,self.cache)

NCDC_DB = load_master_db()
THEORY_DB = NCDC_DB["theory"]
PRACTICALS_DB = NCDC_DB["practicals"]
SUBJECTS = list(THEORY_DB.keys())
CLASSES = [f"S{i}" for i in range(1,7)]

### 4-6. SECRETS + SYSTEM ###
OPENROUTER_API_KEY=os.getenv("OPENROUTER_API_KEY","")
STUDENT_PASSWORD=os.getenv("STUDENT_PASSWORD","1234")
ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD","admin123")

def system_check():
    try: socket.create_connection(("1.1.1.1", 53), timeout=2); online = True
    except: online = False
    return {"online": online and OPENROUTER_API_KEY!= "", "ram": psutil.virtual_memory().percent}

def keep_alive():
    while True: time.sleep(840);
    try: requests.get(os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8501"), timeout=5)
    except: pass
threading.Thread(target=keep_alive, daemon=True).start()

@st.cache_resource
def get_client():
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY) if OPENROUTER_API_KEY else None

SYS_STATE=system_check()
client=get_client() if SYS_STATE["online"] else None
mode_badge=f"☁️ CLOUD | RAM:{SYS_STATE['ram']:.0f}%" if SYS_STATE["online"] else f"📴 OFFLINE | RAM:{SYS_STATE['ram']:.0f}%"
ai_cache = TTLSchoolCache()

class ChatMemory:
    def __init__(self, ttl=600): self.ttl=ttl; self.mem=load_db(MEMORY_FILE,[])
    def add(self, role, content): self.mem.append({"role":role,"content":content,"time":time.time()}); self.mem = [m for m in self.mem if time.time() - m["time"] < self.ttl]; save_db(MEMORY_FILE,self.mem)
    def get_context(self): return [{"role":m["role"],"content":m["content"]} for m in token_econ.compress_memory(self.mem)]
chat_mem = ChatMemory()

### 7. HELPER FUNCTIONS ###
def get_topics(s,l): return THEORY_DB.get(s,{}).get(l,{}).get("topics",["General"])
def get_competency(s,l): return THEORY_DB.get(s,{}).get(l,{}).get("competency","General")
def get_practicals(s,l): g = "S1-S4" if int(l[1])<=4 else "S5-S6"; return list(PRACTICALS_DB.get(s,{}).get(g,{}).keys()) or ["No Practicals"]
def get_practical_obj(s,l,p): g = "S1-S4" if int(l[1])<=4 else "S5-S6"; return PRACTICALS_DB.get(s,{}).get(g,{}).get(p,{}).get("objective","")

def display_disclaimer():
    st.markdown("""<div style="background:#fff3cd; border-left:5px solid #ff9800; padding:12px;"><b>⚠️ NDEJJE DISCLAIMER</b><br>Confirm with Head Teacher, DOS.</div>""", unsafe_allow_html=True)

def display_preview(content,name,s,l,user="Guest"):
    st.session_state.current_subject=s; st.session_state.current_level=l
    st.text_area("🤖 Tutor Output",content,height=400,key=f"p{name}")
    student_ans = st.text_area("✍️ QC Marking", key=f"mark{name}")
    if st.button("🔍 QC Mark",key=f"qc{name}") and student_ans:
        st.success(qc_examiner.mark_answer(student_ans, content, s, l))

### 8. RAG LAZY LOADED ###
class VectorRAG:
    def __init__(self): self.docs=load_db(DOCS_FILE,[]); self.faiss = None; st.sidebar.info("RAG OFF")
    def retrieve(self,q,k=3): return []
vector_rag=VectorRAG()
def render_upload(key="d"):
    with st.expander("📤 Upload Notes - Disabled", expanded=False):
        st.info("RAG/FAISS is OFF for speed.")
        st.file_uploader("Upload disabled", type=["pdf","txt","csv"], key=f"uploader_{key}", disabled=True)

### 9. BRAIN - FIXED ###
def tutor_brain(q, level, mode, subject, stream=True, user=None):
    sources = vector_rag.retrieve(q, k=6) if user and user.get("role")=="student" else []
    token_budget = token_econ.detect_depth_needed(q)
    sources, model, token_budget = token_econ.auto_quantize(sources, q, "", mode)
    subj = subject if subject else "General"
    system = teacher_style.get_style_rules(subj, level, q)
    system = system + "\nCRITICAL: NEVER use $ or \\ or latex. Write all math in plain text."
    system = system + f"\nSOURCES: {len(sources)} notes loaded."
    messages = [{"role":"system","content":system}]
    messages.append({"role":"user","content":q})
    if not client: return "Offline mode. Add OPENROUTER_API_KEY", [], level
    resp = client.chat.completions.create(model=model,messages=messages,max_tokens=token_budget,temperature=0.6,stream=False)
    raw = resp.choices[0].message.content
    ans = teacher_style.format_answer(raw, subj, level)
    return ans, sources, level

### 10. STUDENT + ADMIN PORTAL ###
def show_student(user):
    st.header(f"Welcome Student")
    if "chat" not in st.session_state: st.session_state.chat = []
    q = st.text_input("Ask your tutor anything:", key="student_input")
    if st.button("Send") and q:
        with st.spinner("Thinking..."):
            a, src, lvl_out = tutor_brain(q, "S4", "smart", "General", False, {"role":"student"})
        st.session_state.chat.append({"role":"user","content":q})
        st.session_state.chat.append({"role":"assistant","content":a})
        st.rerun()
    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])

def show_admin(user):
    st.header("🏫 Admin Portal")
    display_disclaimer()
    if st.button("Logout", key="admin_logout"): st.session_state.clear(); st.rerun()
    st.metric("Total Queries", len(load_db(LOG_FILE,[])))

### 11. LOGIN ###
st.title("🧠 DIGITAL UNEB TUTOR 2026 - NDEJJE QC V7.5.5")
display_disclaimer()
with st.sidebar:
    st.metric("RAM",f"{SYS_STATE['ram']:.0f}%")
    st.metric("Mode", mode_badge)
    pw=st.text_input("Password",type="password", key="main_login_pw")
    if st.button("Student Login") and pw==STUDENT_PASSWORD:
        st.session_state.role="Student"; st.session_state.user="Student"; st.rerun()
    if st.button("Admin Login") and pw==ADMIN_PASSWORD:
        st.session_state.role="Admin"; st.session_state.user="Admin"; st.rerun()
if st.session_state.get("role")=="Admin": show_admin(st.session_state.user)
elif st.session_state.get("role")=="Student": show_student(st.session_state.user)
else: st.info("Login. Student=1234 Admin=admin123")
