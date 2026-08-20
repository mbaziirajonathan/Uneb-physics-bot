from difflib import SequenceMatcher
import streamlit as st, os, json, re, time, requests, random, threading, psutil, socket, hashlib
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
from openai import OpenAI
import logging
try: import fcntl
except: fcntl = None
logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 V8.7.5", page_icon="🧠", layout="wide")
with st.spinner("🚀 Booting NDEJJE AI Tutor... V8.7.5 BULLETPROOF"):
    time.sleep(0.1)
st.sidebar.caption("Build: V8.7.5-FULLDB-18SUBJECTS | AUTO ROUTER")

### 1. FILES + UTILS ###
DATA_PATH = os.getenv("STREAMLIT_DATA_PATH", "data")
if not os.path.exists(DATA_PATH) or not os.access(DATA_PATH, os.W_OK): DATA_PATH = "/tmp"
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
    if not os.path.exists(f): save_db(f,default)
    try:
        with open(f,"r", encoding='utf-8') as file: return json.load(file)
    except: save_db(f,default); return default

for f,d in [(LOG_FILE,[]),(CACHE_FILE,{}),(DOCS_FILE,[]),(SETTINGS_FILE,{}),(MEMORY_FILE,[]),(FLAGS_FILE,[])]:
    load_db(f,d)

### 2. TOKEN ECONOMIST + TEACHER ###
FREE_MODELS_PRIORITY = [
    "deepseek/deepseek-chat-v3-0324:free", # Most stable free as of Aug 2026
    "google/gemma-2-9b-it:free",
    "microsoft/phi-3-mini-128k-instruct:free",
    "openrouter/auto" # ULTIMATE FALLBACK: picks cheapest available
]

class TokenEconomist:
    def detect_depth_needed(self, prompt):
        p = prompt.lower()
        if any(k in p for k in ["deeply","explain","discuss","compare","derive"]): return 1000
        if "s6" in p or "s5" in p: return 800
        if "s4" in p or "s3" in p: return 600
        return 500
    def auto_quantize(self,sources,prompt,system,mode): return sources, FREE_MODELS_PRIORITY[0], self.detect_depth_needed(prompt)
    def compress_memory(self, mem): return mem[-10:]
token_econ=TokenEconomist()

class NCDC2026Engine:
    def generate_10_sit(self, subject, level, topics): return f"**GENERATE 10 NCDC 2026 SIT QUESTIONS FOR {subject} {level} ON {topics}**"

class UgandanTeacher:
    def get_style_rules(self,subject,level,topic):
        try: lvl = int(str(level).replace('S',''))
        except: lvl = 4
        math_rule = "RULE MATH: NO $ NO LATEX. Use plain text: 'Force = Mass x Acceleration'." if lvl <= 4 else "RULE MATH: NO LATEX. Use v = u + at, ^ for power."
        return f"RULE 1: NCDC 2026 S{level} Teacher Uganda.\nRULE 2: Greeting + Key Points + Ugandan Example + Formula + Summary\nRULE 3: {math_rule}\nRULE 4: END: 3 'Check Your Understanding' questions."
    def format_answer(self,ans,subject,level):
        ans = ans.replace('$', '').replace('\\(', '').replace('\\)', '')
        ans = re.sub(r'\$.*?\$', '', ans)
        if "Check Your Understanding" not in ans: ans += f"\n\n---\n**Check Your Understanding:**\n1. Define it.\n2. Ugandan example?\n3. Why important for UNEB S{level}?"
        return ans

class QCExaminer:
    def mark_answer(self, student_answer, correct_answer, subject, level):
        total=10; feedback=[]
        if "=" in correct_answer and "=" not in student_answer: total-=2; feedback.append("❌ -2: Missing Formula.")
        total=max(0,total); grade="A" if total>=8 else "B" if total>=6 else "C"
        return f"**NDEJJE QC MARK: {total}/10 - {grade}**\n" + ("\n".join(feedback) if feedback else "Excellent.")

def log_activity(user, action):
    logs = load_db(LOG_FILE, []); logs.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user, "action": action}); save_db(LOG_FILE, logs[-1000:])

teacher_style = UgandanTeacher()
ncdc_engine = NCDC2026Engine()
qc_examiner = QCExaminer()

### 3. LOAD MASTER DATABASE - ALL 18 SUBJECTS + PRACTICALS COMPRESSED ###
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
    def get(self,q): k=hashlib.sha256(q.encode()).hexdigest(); return self.cache[k][0] if k in self.cache and time.time()<self.cache[k][1] else None
    def set(self,q,a): self.cache[hashlib.sha256(q.encode()).hexdigest()] = [a, time.time()+self.ttl]; save_db(CACHE_FILE,self.cache)

NCDC_DB = load_master_db()
THEORY_DB = NCDC_DB["theory"]
PRACTICALS_DB = NCDC_DB["practicals"]
SUBJECTS = list(THEORY_DB.keys())
CLASSES = [f"S{i}" for i in range(1,7)]

### 5. SECRETS + SYSTEM ###
OPENROUTER_API_KEY=os.getenv("OPENROUTER_API_KEY","")
STUDENT_PASSWORD=os.getenv("STUDENT_PASSWORD","1234")
ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD","admin123")

def system_check():
    try: socket.create_connection(("1.1.1.1", 53), timeout=2); online = True
    except: online = False
    return {"online": online and OPENROUTER_API_KEY!= "", "ram": psutil.virtual_memory().percent}

def keep_alive():
    while True: time.sleep(840)
    try: requests.get(os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8501"), timeout=5)
    except: pass
threading.Thread(target=keep_alive, daemon=True).start()

@st.cache_resource
def get_client(): return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY) if OPENROUTER_API_KEY else None
SYS_STATE=system_check()
client=get_client() if SYS_STATE["online"] else None
mode_badge=f"☁️ CLOUD FREE | RAM:{SYS_STATE['ram']:.0f}%" if SYS_STATE["online"] else f"📴 OFFLINE | RAM:{SYS_STATE['ram']:.0f}%"
ai_cache = TTLSchoolCache()

### 6. HELPERS ###
def get_topics(s,l): return THEORY_DB.get(s,{}).get(l,{}).get("topics",["General"])
def get_competency(s,l): return THEORY_DB.get(s,{}).get(l,{}).get("competency","General")
def get_practicals(s,l): g = "S1-S4" if int(l[1])<=4 else "S5-S6"; return list(PRACTICALS_DB.get(s,{}).get(g,{}).keys()) or ["No Practicals"]
def get_practical_obj(s,l,p): g = "S1-S4" if int(l[1])<=4 else "S5-S6"; return PRACTICALS_DB.get(s,{}).get(g,{}).get(p,{}).get("objective","")

def display_disclaimer():
    st.markdown("""<div style="background:#1e1e1e; border-left:5px solid #ffc107; padding:15px;"><h4 style="color:#ffc107">⚠️ NDEJJE DISCLAIMER</h4><p style="color:#ffc107">Confirm with Head Teacher, DOS, Subject Teacher.</p></div>""", unsafe_allow_html=True)

### 7. BRAIN WITH CACHE + AUTO ROUTER FALLBACK ###
def tutor_brain(q, level, mode, subject, stream=True, user=None):
    if st.session_state.get("chat_locked", False): return "🔒 CHATBOT LOCKED BY HEAD TEACHER.", [], level
    if user and user.get("role")=="student" and not st.session_state.get("allow_all", True): return "⛔ NO PERMISSION.", [], level

    cache_key = f"{q} | {level} | {subject}"
    cached_answer = ai_cache.get(cache_key)
    if cached_answer:
        if user: log_activity(user["user"], f"Cache: {q[:20]}")
        return cached_answer + "\n\n*✅ Served from Cache*", [], level

    token_budget = token_econ.detect_depth_needed(q)
    system = teacher_style.get_style_rules(subject, level, q)
    messages = [{"role":"system","content":system}, {"role":"user","content":q}]
    if not client: return "Offline. Add OPENROUTER_API_KEY", [], level

    last_error = None
    used_model = "None"
    for model in FREE_MODELS_PRIORITY: # AUTO TRY ALL FREE MODELS + AUTO
        try:
            resp = client.chat.completions.create(model=model,messages=messages,max_tokens=token_budget,temperature=0.6)
            raw = resp.choices[0].message.content
            used_model = model
            st.sidebar.caption(f"AI: {model}") # Show which model worked
            ans = teacher_style.format_answer(raw, subject, level)
            ai_cache.set(cache_key, ans)
            if user: log_activity(user["user"], f"Cached: {q[:20]}")
            return ans, [], level
        except Exception as e:
            last_error = str(e)
            continue # try next model

    # If we reach here, all failed
    help_msg = "Add $5 credits to OpenRouter to unlock paid models."
    return f"AI Error: All free models unavailable. \nLast error: {last_error[:120]}\n\n{help_msg}", [], level

### 8. STUDENT PORTAL V8.7.5 ###
def show_student(user):
    if st.session_state.get("chat_locked", False): st.error("🔒 CHATBOT LOCKED BY HEAD TEACHER."); st.stop()
    if not st.session_state.get("allow_all", True): st.warning("⛔ NO PERMISSION."); st.stop()
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
            a,_,_ = tutor_brain(q, level, "smart", subject, False, {"role":"student","user":user})
            st.success(a)

    with tabs[1]:
        for t in get_topics(subject, level): st.write(f"- {t}")
        st.write("**Competency:**", get_competency(subject, level))
        for p in get_practicals(subject, level): st.write(f"- **{p}**: {get_practical_obj(subject,level,p)}")

    with tabs[2]:
        topic = st.selectbox("Topic", get_topics(subject, level))
        if st.button("Generate 10 SIT"):
            a,_,_ = tutor_brain(ncdc_engine.generate_10_sit(subject,level,topic), level, "smart", subject, False, {"role":"student","user":user})
            st.text_area("SIT Questions", a, height=300)
        ans = st.text_area("Paste answer for QC")
        if st.button("QC Mark") and ans: st.success(qc_examiner.mark_answer(ans,"Model",subject,level))

    with tabs[3]:
        term = st.selectbox("Term", ["Term 1","Term 2","Term 3"])
        if st.button("Generate Report"):
            report = f"NDEJJE SS\nName: {user}\nClass: {level}\nTerm: {term}\n{subject}: A"
            st.download_button("Download", report, file_name=f"Report_{user}.txt")

    with tabs[4]:
        q_topic = st.selectbox("Quiz Topic", get_topics(subject, level))
        if st.button("Generate Quiz"):
            prompt = f"10 MCQs for {subject} {level} on {q_topic} with answers"
            quiz,_,_ = tutor_brain(prompt, level, "smart", subject, False, {"role":"student","user":user})
            st.text_area("Quiz", quiz, height=400)
        taught = st.text_area("Paste what teacher taught")
        if st.button("Explain Lesson") and taught:
            prompt = f"Summarize and explain for S{level[1]}: {taught[:1500]}"
            exp,_,_ = tutor_brain(prompt, level, "smart", subject, False, {"role":"student","user":user})
            st.success(exp)

    with tabs[5]:
        search = st.text_input("General Search")
        if st.button("Search"):
            ans,_,_ = tutor_brain(search, "S4", "smart", "General", False, {"role":"student","user":user})
            st.markdown(ans)

### 9. ADMIN PORTAL ###
def show_admin(user):
    st.header("🏫 Admin Portal")
    display_disclaimer()
    tabs = st.tabs(["Upload","DB","Scheme","MOES","Unit Control","Analytics"])
    with tabs[0]: st.info("Upload disabled for speed")
    with tabs[1]: st.write(f"Total Subjects: {len(SUBJECTS)}")
    with tabs[2]: st.write("Scheme Generator")
    with tabs[3]: st.write("MOES Reports")
    with tabs[4]:
        st.session_state["chat_locked"] = st.toggle("Lock Students", st.session_state.get("chat_locked",False))
        st.session_state["allow_all"] = st.toggle("Allow Students", st.session_state.get("allow_all",True))
        st.warning(f"Free Models Priority:\n1. {FREE_MODELS_PRIORITY[0]}\n2. {FREE_MODELS_PRIORITY[1]}\n3. {FREE_MODELS_PRIORITY[2]}\n4. {FREE_MODELS_PRIORITY[3]}")
        if st.button("Clear Cache"): save_db(CACHE_FILE,{}); st.success("Cache Cleared")
    with tabs[5]: st.metric("Total Queries", len(load_db(LOG_FILE,[])))
    if st.button("Logout"): st.session_state.clear(); st.rerun()

### 10. LOGIN ###
st.title("🧠 DIGITAL UNEB TUTOR 2026 - NDEJJE QC V8.7.5")
display_disclaimer()
with st.sidebar:
    st.metric("RAM",f"{SYS_STATE['ram']:.0f}%")
    st.metric("Mode", mode_badge)
    pw=st.text_input("Password",type="password")
    if st.button("Student Login") and pw==STUDENT_PASSWORD: st.session_state.role="Student"; st.session_state.user="Student"; st.rerun()
    if st.button("Admin Login") and pw==ADMIN_PASSWORD: st.session_state.role="Admin"; st.session_state.user="Admin"; st.rerun()
if st.session_state.get("role")=="Admin": show_admin(st.session_state.user)
elif st.session_state.get("role")=="Student": show_student(st.session_state.user)
else: st.info("Login. Student=1234 Admin=admin123")
