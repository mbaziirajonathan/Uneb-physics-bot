from difflib import SequenceMatcher
import streamlit as st, os, io, json, re, time, requests, random, threading, psutil, socket, hashlib
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
from openai import OpenAI
import logging
try: import fcntl
except: fcntl = None
logging.basicConfig(level=logging.INFO)

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 VDB", page_icon="🧠", layout="wide")
st.sidebar.caption("Build: V7.3.2-MERGED | NCDC 2026 CBC | AUTO PRACTICAL LINK")

### 1. FILES + UTILS ###
DATA_PATH = os.getenv("STREAMLIT_DATA_PATH", "data")
os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs("models", exist_ok=True)

LOG_FILE, CACHE_FILE, DOCS_FILE, SETTINGS_FILE, MEMORY_FILE = [f"{DATA_PATH}/{x}" for x in ["usage_log.json","ai_cache.json","vector_docs.json","teacher_settings.json","chat_memory.json"]]
MASTER_DB_FILE = f"{DATA_PATH}/ncdc_master_db.json"
FAISS_FILE = "models/faiss.index"

def save_db(f,d):
    with open(f,"w", encoding='utf-8') as file:
        if fcntl: fcntl.flock(file, fcntl.LOCK_EX)
        json.dump(d, file, indent=2, ensure_ascii=False)
        if fcntl: fcntl.flock(file, fcntl.LOCK_UN)

def load_db(f,default):
    if not os.path.exists(f): save_db(f,default)
    try: return json.load(open(f,"r", encoding='utf-8'))
    except: save_db(f,default); return default

for f,d in [(LOG_FILE,[]),(CACHE_FILE,{}),(DOCS_FILE,[]),(SETTINGS_FILE,{}),(MEMORY_FILE,[])]: load_db(f,d)

### 2. LOAD MASTER DATABASE - MERGED WITH YOUR DATA ###
@st.cache_data
def load_master_db():
    # YOUR FULL MERGED DATABASE HERE
    default_db = {
      "theory": {
        "Physics": {"S1": {"topics": ["Measurements","Density","States of Matter","Introduction to Forces","Thermometry","Heat Transfer","Rectilinear Propagation","Reflection at Plane Surfaces","Intro to Electricity Part I","Magnets"], "competency": "Basic knowledge. Observe, Measure, Classify. AOI: Home safety"}, "S2": {"topics": ["Turning Effect of Forces","Machines","Work Energy and Power","Pressure","Properties of Matter","Reflection at Curved Surfaces","Wave Motion","Properties of Waves","Sound Waves","Intro to Electricity Part II","Magnetic Effect of Current"], "competency": "Understanding. Interpret, Explain. AOI: Simple machines"}, "S3": {"topics": ["Refraction of Light","Lenses","Linear Motion","Newton's Laws of Motion","Friction","Current Electricity","Force on a Conductor","Quantity of Heat"], "competency": "Skill Application. Apply laws, Solve problems"}, "S4": {"topics": ["Domestic Electricity","Electromagnetic Induction","Modern Physics Electronics","Modern Physics Radioactivity"], "competency": "Values & Attitudes. Scenario-Item-Task. AOI: Community projects"}, "S5": {"topics": ["Fields I","Current","Advanced Mechanics","Waves II","Thermal Physics"], "competency": "Analysis. Derivations, Paper 1 & 2 split"}, "S6": {"topics": ["Electric Fields","Nuclear Physics II","Quantum Physics","AC Circuits","Astrophysics"], "competency": "Synthesis & Evaluation. Research, University prep"}},
        "Chemistry": {"S1": {"topics": ["Introduction to Chemistry and Society","Experimental Chemistry Apparatus and Measurement","States of Matter and Kinetic Theory","Elements Mixtures and Compounds","Particulate Nature of Matter","The Atmosphere and Combustion"], "competency": "Basic knowledge"}, "S2": {"topics": ["Atomic Structure and The Periodic Table","Chemical Bonding and Structure","Acids Bases and Indicators","Salts and their Preparation","Properties of Carbon and its Inorganic Compounds","Water and Hydrogen"], "competency": "Understanding"}, "S3": {"topics": ["The Mole Concept and Stoichiometry","Volumetric Analysis","Reactivity Series of Metals","Extraction of Metals","Electrochemistry","Halogens and their Compounds"], "competency": "Skill Application"}, "S4": {"topics": ["Energy Changes in Chemical Reactions","Rates of Chemical Reactions","Reversible Reactions and Equilibrium","Introduction to Organic Chemistry","Synthetic Polymers and Materials","Nitrogen and its Compounds"], "competency": "Scenario-Item-Task"}, "S5": {"topics": ["Gases and Kinetic Theory","Atomic Structure and Quantum Mechanics","Chemical Bonding and Structure VSEPR","Chemical Thermodynamics","Chemical Kinetics","Chemical Equilibrium","Electrochemistry Nernst"], "competency": "Analysis"}, "S6": {"topics": ["Periodic Trends Period 3","Group II Elements","Group VII Elements","Transition Chemistry d-block","Aliphatic Hydrocarbons","Halogenoalkanes","Hydroxy Compounds","Carbonyl Compounds","Carboxylic Acids and Derivatives","Nitrogen Compounds","Polymerization"], "competency": "Synthesis"}},
        "Biology": {"S1": {"topics": ["Introduction to Biology","Cells and Microscopy","Levels of Organization","Classification of Living Things"], "competency": "Basic knowledge"}, "S2": {"topics": ["Nutrition in Plants and Animals","Transport of Materials in Plants and Animals","Gaseous Exchange and Respiration"], "competency": "Understanding"}, "S3": {"topics": ["Excretion and Homeostasis","Support and Movement","Coordination (Nervous and Endocrine Systems)","Locomotion"], "competency": "Skill Application"}, "S4": {"topics": ["Reproduction in Plants and Animals","Genetics, Inheritance and Variation","Ecology and Ecosystems","Human Health and Disease"], "competency": "Scenario-Item-Task"}, "S5": {"topics": ["Cell Biology and Biochemistry","Taxonomy and Evolution","Plant and Animal Physiology"], "competency": "Analysis"}, "S6": {"topics": ["Homeostasis and Coordination","Growth and Development","Genetics, Selection and Evolution","Ecology and Environmental Biology"], "competency": "Synthesis"}},
        "Mathematics": {"S1": {"topics": ["Number Bases & Systems","Working with Fractions","Decimals and Percentages","Integers and Directed Numbers","Sets and Venn Diagrams","Introduction to Geometry","Algebra Expressions & Formulae","Equations and Inequalities","Coordinates and Linear Graphs"], "competency": "Basic knowledge"}, "S2": {"topics": ["Ratios Proportions & Scale","Sequences and Number Patterns","Length Area and Volume","Mapping and Functions","Graphs of Quadratic Functions","Vectors in a 2D Plane","Transformation Geometry","Business Mathematics","Data Handling & Statistics"], "competency": "Understanding"}, "S3": {"topics": ["Matrices & Transformations","Simultaneous Linear Equations","Pythagoras Theorem & Intro Trig","Quadratic Equations","Loci and Geometric Constructions","Further Vectors and Gradients","Probability Theory","Circles and Circle Theorems","Logarithms and Indices"], "competency": "Skill Application"}, "S4": {"topics": ["Linear Programming","Three-Dimensional Geometry","Advanced Business Calculations","Trigonometry Non-Right Triangles","Advanced Statistical Dispersion","Revision & Synthesis"], "competency": "Scenario-Item-Task"}, "S5": {"topics": ["Surds Indices Logarithmic Functions","Quadratic Theory","Permutations and Combinations","Binomial Theorem","Partial Fractions","Matrices and Determinants 3x3","Compound Multiple Angle Formulae","Trigonometric Equations","Straight Line Circle","Limits and Continuity","Differentiation","Integration Techniques","Complex Numbers","Vectors in 3D","Statics","Kinematics","Probability","Numerical Methods"], "competency": "Analysis"}, "S6": {"topics": ["Conic Sections","Applications of Differentiation","Definite Integrals Volume of Revolution","De Moivre Theorem","Equations of lines and planes 3D","Kinetics","Discrete Random Variables","Continuous Distributions","Newton-Raphson method","Numerical Integration"], "competency": "Synthesis"}},
        "Agriculture": {"S1": {"topics": ["Introduction to Agriculture","Safety and Welfare in Agriculture","Farm Tools, Equipment and Workshop Technology","Soil Science"], "competency": "Basic knowledge"}, "S2": {"topics": ["Crop Production and Agronomy","Animal Production and Husbandry","Agribusiness and Basic Farming Economics"], "competency": "Understanding"}, "S3": {"topics": ["Crop Protection","Animal Health and Disease Control","Farm Structures and Farm Mechanisation"], "competency": "Skill Application"}, "S4": {"topics": ["Advanced Sustainable Farm Management","Value Addition and Post-Harvest Technology","Agricultural Marketing and Enterprise Planning","DIT Vocational Competency Portfolio Review"], "competency": "Scenario-Item-Task"}, "S5": {"topics": ["Advanced Soil Science and Chemistry","Advanced Crop Physiology and Agronomy","Agricultural Engineering and Power Sources"], "competency": "Analysis"}, "S6": {"topics": ["Advanced Animal Nutrition and Livestock Production","Agricultural Economics, Extension and Agribusiness Management","Agricultural Field Research Methodology"], "competency": "Synthesis"}},
        "English Language": {"S1": {"topics": ["Self and Personal Identity","School Life and Environment","Community and Occupations","Health and Hygiene","Leisure and Recreation","Environment and Climate Change"], "competency": "Basic communication"}, "S2": {"topics": ["Science and Technology","Communication and Media","Human Rights and Civic Duties","Culture and Heritage","Peace and Conflict Resolution","Traffic and Road Safety"], "competency": "Understanding"}, "S3": {"topics": ["Financial Literacy and Banking","Tourism and Hospitality","Employment and Career Paths","Governance and Leadership","Population and Development","Regional Issues"], "competency": "Skill Application"}, "S4": {"topics": ["Global Citizenship","Synthesis and Precis Summaries","Advanced Functional Writing","Consolidation of Grammar and Oral Skills"], "competency": "Scenario-Item-Task"}},
        "Literature in English": {"S1": {"topics": ["Introduction to Literature and Genres","Introduction to Oral Literature","Understanding Prose Fiction","Appreciating Basic Poetry"], "competency": "Basic appreciation"}, "S2": {"topics": ["Characterization and Themes in Drama","Context and Setting in Prose","Stylistic Devices in Poetry"], "competency": "Understanding"}, "S3": {"topics": ["Study of Prescribed Prose Set-Texts","Study of Prescribed Drama Set-Texts","Unseen Poetry Analysis"], "competency": "Skill Application"}, "S4": {"topics": ["Comparative Literary Analysis","Critical Essay Writing","Oral Performance and Interpretation"], "competency": "Scenario-Item-Task"}},
        "Geography": {"S1": {"topics": ["Introduction to Geography and Map Work","The Solar System and the Earth","Weather and Climate"], "competency": "Basic knowledge"}, "S2": {"topics": ["Geomorphology","Drainage Systems","Vegetation Zones and Wildlife"], "competency": "Understanding"}, "S3": {"topics": ["Population and Settlement","Economic Activities","Mining and Industrialization"], "competency": "Skill Application"}, "S4": {"topics": ["Geography of East Africa","Introduction to GIS and Remote Sensing","Environmental Conservation"], "competency": "Scenario-Item-Task"}, "S5": {"topics": ["Physical Geography","Practical Geography"], "competency": "Analysis"}, "S6": {"topics": ["Human and Economic Geography","Regional Geography of Africa","Environmental Management"], "competency": "Synthesis"}},
        "History": {"S1": {"topics": ["Introduction to History and Sources","Early Man in East Africa","Migrations and Settlement"], "competency": "Basic knowledge"}, "S2": {"topics": ["Pre-Colonial Kingdoms","Early Contacts","Abolition of Slave Trade"], "competency": "Understanding"}, "S3": {"topics": ["Scramble and Partition","Colonial Administration","African Nationalism"], "competency": "Skill Application"}, "S4": {"topics": ["Road to Independence","Post-Independence Challenges","Regional Cooperation"], "competency": "Scenario-Item-Task"}, "S5": {"topics": ["Advanced History of East Africa","Themes in African History"], "competency": "Analysis"}, "S6": {"topics": ["Modern World History","The Cold War Era"], "competency": "Synthesis"}},
        "CRE": {"S1": {"topics": ["God's Creation","The Fall of Man","Abrahamic Covenant"], "competency": "Basic knowledge"}, "S2": {"topics": ["Prophets and Kings","The Exodus","Life of Jesus Christ"], "competency": "Understanding"}, "S3": {"topics": ["Teachings of Jesus","Early Church","Christian Discipleship"], "competency": "Skill Application"}, "S4": {"topics": ["Christian Living","Marriage and Family","Moral Challenges"], "competency": "Scenario-Item-Task"}, "S5": {"topics": ["Church History","Christian Ethics"], "competency": "Analysis"}, "S6": {"topics": ["Christianity in Modern Africa","Comparative Theology"], "competency": "Synthesis"}},
        "ICT": {"S1": {"topics": ["Introduction to ICT","Computer Hardware and Software","Introduction to Word Processing"], "competency": "Basic skills"}, "S2": {"topics": ["Electronic Spreadsheets","Electronic Presentation","Digital Media Production"], "competency": "Understanding"}, "S3": {"topics": ["Internet and Email","Web Design HTML/CSS","Computer Networking"], "competency": "Skill Application"}, "S4": {"topics": ["Information Systems and DBMS","Data Security and Ethics","Project Portfolio"], "competency": "Scenario-Item-Task"}, "S5": {"topics": ["Advanced DBMS","Programming and Algorithms"], "competency": "Analysis"}, "S6": {"topics": ["Artificial Intelligence","Cybersecurity and Data Analytics"], "competency": "Synthesis"}},
        "Entrepreneurship": {"S1": {"topics": ["Introduction to Entrepreneurship","Characteristics of Entrepreneurs","Generating Business Ideas"], "competency": "Basic knowledge"}, "S2": {"topics": ["Market Research","Business Operations","E-Commerce"], "competency": "Understanding"}, "S3": {"topics": ["Financial Literacy","Sources of Finance","Business Planning"], "competency": "Skill Application"}, "S4": {"topics": ["Business Management","Legal Frameworks","School Enterprise Project"], "competency": "Scenario-Item-Task"}, "S5": {"topics": ["Project Design","Corporate Governance"], "competency": "Analysis"}, "S6": {"topics": ["Global Business","Investment and Wealth Creation"], "competency": "Synthesis"}},
        "Art": {"S1": {"topics": ["Elements of Design","Still Life Drawing","Basic Pattern Design"], "competency": "Basic skills"}, "S2": {"topics": ["Painting Techniques","Human Anatomy Drawing","Graphic Design"], "competency": "Understanding"}, "S3": {"topics": ["Sculpture and Modelling","Fabric Decoration","Ceramics and Pottery"], "competency": "Skill Application"}, "S4": {"topics": ["Exhibition Layouts","History of East African Art","Final Portfolio"], "competency": "Scenario-Item-Task"}, "S5": {"topics": ["Advanced Studio Practicum","Advanced Graphic Design"], "competency": "Analysis"}, "S6": {"topics": ["World Art History","Professional Portfolio Development"], "competency": "Synthesis"}},
        "Music": {"S1": {"topics": ["Music Notation and Rhythm","Aural Training","Ugandan Traditional Music"], "competency": "Basic skills"}, "S2": {"topics": ["Musical Instruments","Choral Performance","Musical Scales"], "competency": "Understanding"}, "S3": {"topics": ["Music Theory","Melodic Composition","Folk Song Arrangement"], "competency": "Skill Application"}, "S4": {"topics": ["Harmonic Analysis","History of Western Music","Final Recital"], "competency": "Scenario-Item-Task"}, "S5": {"topics": ["Music Analysis","Ethnomusicology"], "competency": "Analysis"}, "S6": {"topics": ["Performance Virtuosity","Music Technology"], "competency": "Synthesis"}},
        "Luganda": {"S1": {"topics": ["Ennukuta n'Ebigambo","Okusoma n'Okuwandiika","Ebitontome n'Engero"], "competency": "Obumanyirivu bw'olulimi"}, "S2": {"topics": ["Emisoso gy'Ebiwandiiko","Emiyungo n'Amannya","Emizannyo gy'Ekiganda"], "competency": "Okutegeera"}, "S3": {"topics": ["Ennono n'Ennyimba","Engero ez'Enfumo","Okusembya Ebiwandiiko"], "competency": "Okukozesa"}, "S4": {"topics": ["Ebyafaayo by'Oluganda","Okwekenneenya Ebitabo","Okutegeka Emboozi"], "competency": "Scenario-Item-Task"}, "S5": {"topics": ["Obuwandiike Obw'Ennono","Ennimi z'Abantu"], "competency": "Okwekenneenya"}, "S6": {"topics": ["Ekinyankulizi","Okwekenneenya Okw'Okuntikko"], "competency": "Synthesis"}},
        "Kiswahili": {"S1": {"topics": ["Alfabeti na Matamshi","Aina za Maneno","Mazungumzo na Salamu"], "competency": "Maarifa ya msingi"}, "S2": {"topics": ["Sarufi ya Kiswahili","Uandishi wa Insha na Barua","Ufahamu na Ufupisho"], "competency": "Kuelewa"}, "S3": {"topics": ["Fasihi Simulizi","Uandishi wa Ripoti","Uchambuzi wa Habari"], "competency": "Utumiaji"}, "S4": {"topics": ["Fasihi Andishi","Tafsiri na Ukalimani","Maandalizi ya Mtihani"], "competency": "Scenario-Item-Task"}, "S5": {"topics": ["Sarufi Ngumu","Nadharia za Tafsiri"], "competency": "Uchambuzi"}, "S6": {"topics": ["Uhakiki wa Fasihi","Ukuaji wa Kiswahili"], "competency": "Synthesis"}}
      },
      "practicals": {
        "Physics": {"S1-S4": {"Measurements & Density": {"objective": "Determine density of regular and irregular solids using local materials", "apparatus": "Meter rule, Beam balance, Displacement can"}, "Mechanics (Hooke's Law)": {"objective": "Verify Hooke's Law using extension springs", "apparatus": "Spring, Masses, Meter rule"}, "Mechanics (Moments)": {"objective": "Verify principle of moments", "apparatus": "Meter rule, Pivot"}, "Light (Reflection)": {"objective": "Verify laws of reflection", "apparatus": "Plane mirror, Pins, Protractor"}, "Light (Refraction)": {"objective": "Determine refractive index of glass block", "apparatus": "Glass block, Pins"}, "Current Electricity": {"objective": "Verify Ohm's Law", "apparatus": "Cell, Ammeter, Voltmeter, Resistors"}, "Waves & Sound": {"objective": "Determine speed of sound in air", "apparatus": "Tuning fork, Resonance tube"}, "Activities of Integration (AOI)": {"objective": "Design solar cooker using local materials", "apparatus": "Cardboard, Foil, Glass"}}, "S5-S6": {"Advanced Mechanics": {"objective": "Determine acceleration due to gravity g", "apparatus": "Pendulum, Stopwatch, Meter rule"}, "Surface Tension & Viscosity": {"objective": "Determine coefficient of viscosity", "apparatus": "Viscous liquid, Steel balls"}, "Advanced Optics (Lenses)": {"objective": "Determine focal length using u-v method", "apparatus": "Lens, Optical bench"}, "Advanced Optics (Prism)": {"objective": "Determine refractive index using prism", "apparatus": "Triangular prism, Pins"}, "Advanced Electricity (Potentiometer)": {"objective": "Measure internal resistance of a cell", "apparatus": "Potentiometer wire, Jockey"}, "Advanced Electricity (Bridge Circuits)": {"objective": "Determine unknown resistance using Metre Bridge", "apparatus": "Metre bridge, Galvanometer"}, "RC Circuits": {"objective": "Investigate charging and discharging of capacitor", "apparatus": "Capacitor, Resistor"}, "Magnetic Fields": {"objective": "Determine horizontal component of Earth's magnetic field", "apparatus": "Deflection magnetometer"}}},
        "Chemistry": {"S1-S4": {"Separation of Mixtures": {"objective": "Separate sand, salt and ink", "apparatus": "Filter paper, Beaker"}, "States of Matter": {"objective": "Investigate heating and cooling curves", "apparatus": "Naphthalene, Bunsen burner"}, "Acids, Bases & Indicators": {"objective": "Prepare natural pH indicator", "apparatus": "Red cabbage, Household items"}, "Volumetric Analysis (Introductory)": {"objective": "Acid-base titration", "apparatus": "Burette, Pipette"}, "Rates of Reaction": {"objective": "Effect of concentration on rate", "apparatus": "Sodium thiosulfate, HCl"}, "Chemical Tests for Gases": {"objective": "Produce and identify O2, H2, CO2", "apparatus": "Charcoal, Limewater"}, "Activities of Integration (AOI)": {"objective": "Develop water filter prototype", "apparatus": "Sand, Charcoal, Bottle"}}, "S5-S6": {"Volumetric Quantitative Analysis": {"objective": "Redox titration using KMnO4", "apparatus": "Burette, KMnO4"}, "Qualitative Inorganic Analysis": {"objective": "Identify cations and anions", "apparatus": "Test tubes, Reagents"}, "Thermochemistry": {"objective": "Determine enthalpy of neutralization", "apparatus": "Calorimeter"}, "Chemical Kinetics": {"objective": "Determine order of reaction", "apparatus": "H2O2, KI"}, "Equilibrium & Partition Coefficient": {"objective": "Determine partition coefficient", "apparatus": "Ethanoic acid, Organic solvent"}}},
        "Biology": {"S1-S4": {"Microscopy & Cell Observation": {"objective": "Prepare wet mounts of onion cells", "apparatus": "Microscope, Slide"}, "Food Tests": {"objective": "Test for starch, proteins, lipids", "apparatus": "Test tubes, Iodine"}, "Enzyme Action": {"objective": "Effect of temperature on catalase", "apparatus": "Hydrogen peroxide, Liver"}, "Cell Physiology (Osmosis)": {"objective": "Demonstrate osmosis using potato", "apparatus": "Potato, Salt solutions"}, "Plant & Animal Morphology": {"objective": "Examine external features of insects", "apparatus": "Specimens, Hand lens"}, "Soil Ecology": {"objective": "Determine soil water holding capacity", "apparatus": "Soil samples"}, "Activities of Integration (AOI)": {"objective": "Create public health guide", "apparatus": "Charts, Paper"}}, "S5-S6": {"Biological Dissections": {"objective": "Dissect a toad", "apparatus": "Dissection kit, Specimen"}, "Advanced Plant Anatomy": {"objective": "Cut sections of monocot and dicot stem", "apparatus": "Razor, Microscope"}, "Advanced Biochemistry & Food Tests": {"objective": "Estimate vitamin C concentration", "apparatus": "Fruit juice, DCPIP"}, "Physiology (Respiration & Photosynthesis)": {"objective": "Measure rate of respiration", "apparatus": "Respirometer, Seeds"}, "Histological Slide Identification": {"objective": "Identify micro-anatomical structures", "apparatus": "Prepared slides, Microscope"}}},
        "Agriculture": {"S1-S4": {"Farm Tools Identification": {"objective": "Identify and maintain farm tools", "apparatus": "Hoe, Panga"}, "Physical & Chemical Soil Testing": {"objective": "Determine soil pH and texture", "apparatus": "Soil sample, pH indicator"}, "Crop Agronomy (Nursery Bed Management)": {"objective": "Manage nursery bed", "apparatus": "Seeds, Watering can"}, "Livestock Management Exercises": {"objective": "Identify animal feeds and parasites", "apparatus": "Feed samples"}, "DIT Vocational Assessment Practice": {"objective": "Execute Level 1 husbandry", "apparatus": "Poultry equipment"}, "Activities of Integration (AOI)": {"objective": "Develop farm record keeping framework", "apparatus": "Book, Pen"}}, "S5-S6": {"Advanced Soil Science Analysis": {"objective": "Measure soil cation exchange capacity", "apparatus": "Soil, Reagents"}, "Agronomic Field Trials": {"objective": "Compare organic vs inorganic fertilizer", "apparatus": "Plot, Fertilizers"}, "Animal Nutrition & Feed Formulation": {"objective": "Formulate balanced rations", "apparatus": "Feed ingredients, Scale"}, "Agricultural Engineering & Mechanisation": {"objective": "Analyze tractor engine systems", "apparatus": "Tractor"}, "Farm Economics & Management Portfolio": {"objective": "Construct balance sheets", "apparatus": "Calculator, Records"}}}
      }
    }
    return load_db(MASTER_DB_FILE, default_db)

NCDC_DB = load_master_db()
THEORY_DB = NCDC_DB["theory"]
PRACTICALS_DB = NCDC_DB["practicals"]
SUBJECTS = list(THEORY_DB.keys())
CLASSES = [f"S{i}" for i in range(1,7)]

### 3. SECRETS + MODELS ###
OPENROUTER_API_KEY=os.getenv("OPENROUTER_API_KEY",""); STUDENT_PASSWORD=os.getenv("STUDENT_PASSWORD","1234"); ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD","admin123")
IS_CLOUD = os.getenv("DEPLOY_ENV") == "cloud"
if not OPENROUTER_API_KEY and IS_CLOUD: st.error("Missing OPENROUTER_API_KEY in Render Environment Variables"); st.stop()

### 4. SYSTEM CHECK ###
def system_check():
    try: socket.create_connection(("1.1.1.1", 53), timeout=2); online = True
    except: online = False
    return {"online": online and OPENROUTER_API_KEY!= "", "ram_ok": psutil.virtual_memory().percent < 80, "render": IS_CLOUD}

def keep_alive():
    while True:
        time.sleep(840)
        try: requests.get(os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8501"), timeout=5)
        except: pass
threading.Thread(target=keep_alive, daemon=True).start()

@st.cache_resource
def get_client(): return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY) if OPENROUTER_API_KEY else None
@st.cache_resource
def get_embedder(): return SentenceTransformer('all-MiniLM-L6-v2')

SYS_STATE=system_check()
client=get_client() if SYS_STATE["online"] else None
embedder=get_embedder()
AI_MODEL="google/gemini-2.5-flash"
mode_badge="☁️ CLOUD OPENROUTER" if SYS_STATE["online"] else "📴 OFFLINE RAG"

### 5. TTL CACHE + CHAT MEMORY ###
class TTLSchoolCache:
    def __init__(self, ttl=7200): self.ttl=ttl; self.cache=load_db(CACHE_FILE,{})
    def get(self,q):
        k=hashlib.sha256(q.encode()).hexdigest();
        if k in self.cache and time.time()<self.cache[k][1]: return self.cache[k][0]
        return None
    def set(self,q,a): self.cache[hashlib.sha256(q.encode()).hexdigest()] = [a, time.time()+self.ttl]; save_db(CACHE_FILE,self.cache)
ai_cache = TTLSchoolCache()

class ChatMemory:
    def __init__(self, ttl=300): self.ttl=ttl; self.mem=load_db(MEMORY_FILE,[])
    def add(self, role, content):
        self.mem.append({"role":role,"content":content,"time":time.time()})
        self.mem = [m for m in self.mem if time.time() - m["time"] < self.ttl]
        save_db(MEMORY_FILE,self.mem)
    def get_context(self):
        return [{"role":m["role"],"content":m["content"]} for m in self.mem]
chat_mem = ChatMemory()

### 6. HELPER FUNCTIONS + AUTO PRACTICAL LINK ###
def get_topics(s,l): return THEORY_DB.get(s,{}).get(l,{}).get("topics",["General Topic"])
def get_competency(s,l): return THEORY_DB.get(s,{}).get(l,{}).get("competency","General")
def get_practicals(s,l):
    g = "S1-S4" if int(l[1])<=4 else "S5-S6"
    return list(PRACTICALS_DB.get(s,{}).get(g,{}).keys()) or ["No Practicals for this Level"]
def get_practical_obj(s,l,p):
    g = "S1-S4" if int(l[1])<=4 else "S5-S6"
    return PRACTICALS_DB.get(s,{}).get(g,{}).get(p,{}).get("objective","")
def get_related_practicals(s,l,topic):
    # NEW: Auto link topic to practical
    g = "S1-S4" if int(l[1])<=4 else "S5-S6"
    related = []
    for p_name, p_data in PRACTICALS_DB.get(s,{}).get(g,{}).items():
        if SequenceMatcher(None, topic.lower(), p_name.lower()).ratio() > 0.4 or topic.lower() in p_data["objective"].lower():
            related.append(f"**{p_name}**: {p_data['objective']} | *Apparatus: {p_data['apparatus']}*")
    return "\n".join(related) if related else "No direct practical found for this topic."

def display_preview(content,name): st.text_area("🤖 Tutor Output",content,height=450,key=f"p{name}"); st.download_button("📥 Download",content.encode(),f"{name}.txt")

### 7. FAISS RAG ###
class VectorRAG:
    def __init__(self):
        self.docs=load_db(DOCS_FILE,[])
        self.index = None
        if os.path.exists(FAISS_FILE): self.index = faiss.read_index(FAISS_FILE)
        self._rebuild_if_needed()
    def _rebuild_if_needed(self):
        if len(self.docs) > 0 and (self.index is None or self.index.ntotal!= len(self.docs)):
            with st.spinner("Building FAISS Index..."):
                embeddings = embedder.encode([d['txt'] for d in self.docs], show_progress_bar=True)
                self.index = faiss.IndexFlatL2(384)
                self.index.add(np.array(embeddings).astype('float32'))
                faiss.write_index(self.index, FAISS_FILE)
    def add(self,texts,fn):
        new_docs = [{"src":fn,"chunk_id":i,"txt":t[:1200]} for i,t in enumerate(texts)]
        self.docs.extend(new_docs); save_db(DOCS_FILE,self.docs)
        embeddings = embedder.encode([d['txt'] for d in new_docs])
        if self.index is None: self.index = faiss.IndexFlatL2(384)
        self.index.add(np.array(embeddings).astype('float32')); faiss.write_index(self.index, FAISS_FILE)
    def search(self,q,k=4):
        if self.index is None or self.index.ntotal == 0: return []
        q_vec = embedder.encode([q]); D, I = self.index.search(np.array(q_vec).astype('float32'), k)
        return [self.docs[i] for i in I[0] if i < len(self.docs)]
vector_rag=VectorRAG()

def chunk_text(text, sz=500):
    s = re.split(r'(?<=[.!?]) +', text); chunks = []; cur = ""
    for x in s:
        if len(cur) + len(x) < sz: cur += x + " "
        else: chunks.append(cur); cur = x
    if cur: chunks.append(cur)
    return chunks

def render_upload(key="d"):
    f=st.file_uploader("Upload PDF/DOCX/TXT NCDC Notes",type=["pdf","docx","txt"],key=key)
    if f:
        text=""
        try:
            if f.name.endswith(".pdf"): from pypdf import PdfReader; text="".join([p.extract_text() or "" for p in PdfReader(f).pages])
            elif f.name.endswith(".docx"): from docx import Document; text="\n".join([p.text for p in Document(f).paragraphs])
            else: text=f.getvalue().decode("utf-8")
        except Exception as e: st.error(e); return
        if st.button(f"Add {len(chunk_text(text))} chunks to RAG",key=f"add{key}"):
            vector_rag.add(chunk_text(text),f.name); st.success(f"Added to FAISS RAG")

### 8. BRAIN ###
def detect_complexity(prompt):
    p = prompt.lower()
    if any(x in p for x in ["define","what is","list"]): return "S1-S2"
    if any(x in p for x in ["explain","how","why"]): return "S3-S4"
    if any(x in p for x in ["derive","evaluate","research","design"]): return "S5-S6"
    return "S4"

def get_level_rules(level):
    rules = {"S1": "Basic knowledge. 2-3 points. Simple UG examples.","S2": "Understanding. 3-4 points. 1 UG scenario.","S3": "Skill Application. 4-5 points. Diagrams.","S4": "Values. Scenario->Item->Task format.","S5": "Analysis. 6-8 points. Derivations.","S6": "Synthesis. 8-10 points. Research."}
    return rules.get(level, rules["S4"])

SYSTEM_PROMPT_OFFICIAL="""You are DIGITAL UNEB TUTOR 2026. PRIMARY SOURCE: ncdc_master_db.json + RAG Context.
RULE 1: ONLY ANSWER FROM PROVIDED DATABASE TOPICS AND RAG CONTEXT.
RULE 2: CITE EVERY ANSWER: **Proof**: Database ncdc_master_db.json {subject} {level} + RAG [file]
RULE 3: If topic NOT in DB and NOT in RAG, say: "Per NCDC 2026 this is not in syllabus. Click 'Invent/Extend' to generate."
RULE 4: Use CHAT MEMORY to follow what student asked in last 5 minutes.
RULE 5: Be interactive tutor. {level_rules}
"""

SYSTEM_PROMPT_GENERATIVE="""You are DIGITAL UNEB TUTOR 2026 - INVENT MODE.
RULE 1: Topic must be RELATED to NCDC 2026 {subject} {level}. NO USA CURRICULUM.
RULE 2: Start with **[NCDC-GENERATIVE: topic]**
RULE 3: Use Ugandan context only. Cite: **Proof**: [NCDC-GENERATIVE AI 2026]
RULE 4: {level_rules}
"""

def call_openrouter_api(full_prompt):
    tokens=1800 if "research" in full_prompt or "exam" in full_prompt else 600
    messages = chat_mem.get_context() + [{"role":"user","content":full_prompt}]
    res=client.chat.completions.create(model=AI_MODEL,messages=messages,max_tokens=tokens,temperature=0.2)
    return res.choices[0].message.content

def tutor_brain(prompt,level="S4",mode="smart",subject="General", allow_invent=False):
    global SYS_STATE; SYS_STATE=system_check()
    chat_mem.add("user", prompt)
    detected_level = detect_complexity(prompt) if level=="Auto" else level

    sources=vector_rag.search(prompt,4)
    rag_context="\n".join([f"[{r['src']} c{r['chunk_id']}] {r['txt']}" for r in sources])

    topic_exists = False
    competency = get_competency(subject, detected_level)
    for s in SUBJECTS:
        for l in CLASSES:
            if any(x.lower() in prompt.lower() for x in get_topics(s,l)):
                topic_exists = True
                competency = get_competency(s,l)
                subject = s
                break

    level_rules = get_level_rules(detected_level)
    practical_link = get_related_practicals(subject, detected_level, prompt) # NEW
    if practical_link: full_prompt_addon = f"\nRELATED PRACTICAL: {practical_link}"
    else: full_prompt_addon = ""

    if allow_invent and not topic_exists and len(sources)==0:
        sys_prompt = SYSTEM_PROMPT_GENERATIVE.format(level_rules=level_rules, subject=subject, level=detected_level)
    else:
        sys_prompt = SYSTEM_PROMPT_OFFICIAL.format(level_rules=level_rules, subject=subject, level=detected_level)

    full_prompt = f"""{sys_prompt}
LEVEL:{detected_level}
SUBJECT:{subject}
COMPETENCY:{competency}
RAG_CONTEXT:\n{rag_context}
DATABASE_TOPICS: {get_topics(subject, detected_level)}
{practical_link}
TASK:{prompt}"""

    cached=ai_cache.get(full_prompt+mode+detected_level+str(allow_invent));
    if cached: return f"[CACHED] {cached}", sources, detected_level

    # PRIORITY 1: OPENROUTER CLOUD ONLY
    if SYS_STATE["online"] and client:
        try:
            ans = call_openrouter_api(full_prompt)
            chat_mem.add("assistant", ans)
            src_line = "**Proof**: DB ncdc_master_db.json + " + ", ".join([f"{r['src']}" for r in sources]) if sources else "**Proof**: [NCDC-GENERATIVE AI 2026]"
            final_ans = ans + f"\n\n{src_line}\n**Level**: {detected_level} | **Mode**: CLOUD"
            ai_cache.set(full_prompt+mode+detected_level+str(allow_invent),final_ans)
            return final_ans, sources, detected_level
        except Exception as e: st.sidebar.error(f"Cloud failed: {e}")

    if rag_context: return (f"[OFFLINE RAG]\n**Proof**: {rag_context[:1000]}", sources, detected_level)
    else: return ("[OFFLINE] No internet. Upload notes.", [], detected_level)

### 9. STUDENT PORTAL ###
def show_student():
    st.header("🧠 Digital Tutor - VDB Memory Active")
    if st.button("Logout", key="student_logout"): st.session_state.clear(); st.rerun()
    t1,t2,t3,t4,t5=st.tabs(["💬 Chat","📖 Learn","🧪 Practicals","🖼️ Diagrams","🔬 Research"])

    with t1:
        st.text_input("🔎 Search", key="search_t1")
        render_upload("s1");
        s=st.selectbox("Subject",SUBJECTS,key="s1s");
        l=st.selectbox("Class",["Auto Detect"]+CLASSES,key="s1l");
        q=st.text_area("Ask",placeholder="Follow up questions work here",key="s1q")
        c1,c2=st.columns(2)
        if c1.button("Ask Official",key="s1b") and q:
            lvl = "Auto" if l=="Auto Detect" else l
            a,src,lvl_out=tutor_brain(q,lvl,"smart",s, allow_invent=False); display_preview(a,"s1")
        if c2.button("Invent/Extend",key="s1gen") and q:
            lvl = "Auto" if l=="Auto Detect" else l
            a,src,lvl_out=tutor_brain(q,lvl,"smart",s, allow_invent=True); display_preview(a,"s1gen")

    with t2:
        st.text_input("🔎 Search", key="search_t2")
        render_upload("s2")
        s=st.selectbox("Subject",SUBJECTS,key="s2s")
        l=st.selectbox("Class",CLASSES,key="s2l")
        t=st.selectbox("Topic",get_topics(s,l),key="s2t_topics")
        c1,c2,c3=st.columns(3)
        if c1.button("Notes From DB",key="s2b"): a,src,lvl=tutor_brain(f"Teach {t} for {l} {s}",l,"notes",s, False); display_preview(a,"s2")
        if c2.button("Quiz Me",key="s2q"): a,src,lvl=tutor_brain(f"Quiz me on {t} for {l} {s}",l,"smart",s, False); display_preview(a,"s2q")
        if c3.button("Invent Related Topic",key="s2gen"): a,src,lvl=tutor_brain(f"Invent new NCDC topic related to {t} for {l} {s}",l,"notes",s, True); display_preview(a,"s2gen")

    with t3:
        st.text_input("🔎 Search", key="search_t3")
        render_upload("s3"); s=st.selectbox("Subject",list(PRACTICALS_DB.keys()),key="s3s"); l=st.selectbox("Class",CLASSES,key="s3l"); p=st.selectbox("Practical",get_practicals(s,l)+["Invent Practical"],key="s3p")
        if st.button("Teach Practical",key="s3b"):
            if p=="Invent Practical":
                a,src,lvl=tutor_brain(f"Invent basic practical for {l} {s} using local materials",l,"notes",s, True)
            else:
                obj=get_practical_obj(s,l,p)
                a,src,lvl=tutor_brain(f"Teach {p} practical for {l}. Objective: {obj}",l,"notes",s, False)
            display_preview(a,"s3")

    with t4:
        st.text_input("🔎 Search", key="search_t4")
        render_upload("s4"); s=st.selectbox("Subject",SUBJECTS,key="s4s"); l=st.selectbox("Class",CLASSES,key="s4l"); t=st.selectbox("Topic",get_topics(s,l),key="s4t_topics")
        if st.button("Explain Diagram",key="s4b"): a,src,lvl=tutor_brain(f"Explain diagram for {t} in {s} {l}",l,"smart",s, False); display_preview(a,"s4")

    with t5:
        st.text_input("🔎 Search", key="search_t5")
        st.subheader("Research")
        render_upload("s5"); s=st.selectbox("Subject",SUBJECTS,key="s5s"); l=st.selectbox("Class",CLASSES,key="s5l")
        rq=st.text_area("Research Topic",key="s5rq")
        c1,c2=st.columns(2)
        if c1.button("Research From DB",key="s5rb") and rq: a,src,lvl=tutor_brain(f"Research project on {rq} for {l} {s}",l,"research",s, False); display_preview(a,"s5res")
        if c2.button("Invent Research Idea",key="s5gen") and rq: a,src,lvl=tutor_brain(f"Invent new NCDC research topic related to {rq} for {l} {s}",l,"research",s, True); display_preview(a,"s5gen")

### 10. ADMIN PORTAL ###
def show_admin():
    st.header("🏫 Admin Portal")
    if st.button("Logout", key="admin_logout"): st.session_state.clear(); st.rerun()
    tabs=st.tabs(["📊 Analytics","📖 Curriculum","🧪 Practicals","📤 Bulk","📚 RAG KB","📝 Lesson","📄 Reports","📈 Predictive","📝 Exams"])

    with tabs[0]:
        q=st.text_area("Ask Analytics",key="aq")
        if st.button("Ask"): a,src,lvl=tutor_brain(q,"S4","smart","General", False); display_preview(a,"a")
    with tabs[1]:
        s=st.selectbox("Subject",SUBJECTS,key="as"); l=st.selectbox("Class",CLASSES,key="al"); t=st.multiselect("Topics",get_topics(s,l), key="a1_topics")
        if st.button("Scheme"): a,src,lvl=tutor_brain(f"Scheme for {l} {s} {t}",l,"notes",s, False); display_preview(a,"scheme")
    with tabs[2]:
        s=st.selectbox("Subject",list(PRACTICALS_DB.keys()),key="ps"); l=st.selectbox("Class",CLASSES,key="pl"); p=st.selectbox("Practical",get_practicals(s,l)+["Invent"],key="pp")
        if st.button("Guide"): a,src,lvl=tutor_brain(f"Lab manual for {p} {l} {s}",l,"notes",s, "Invent" in p); display_preview(a,"pg")
    with tabs[3]:
        s=st.selectbox("Subject",SUBJECTS,key="bs"); l=st.selectbox("Class",CLASSES,key="bl"); t=st.multiselect("Topics",get_topics(s,l), key="a2_topics"); n=st.slider("Qs",10,100,50)
        if st.button("Bulk"): a,src,lvl=tutor_brain(f"{n} NCDC Qs + Marking from {t} for {l} {s}",l,"notes",s, False); display_preview(a,"bulk")
    with tabs[4]:
        st.metric("FAISS Chunks",len(vector_rag.docs)); render_upload("a5")
        q=st.text_area("Ask RAG",key="ragq")
        if st.button("Ask RAG"): a,src,lvl=tutor_brain(q,"S4","smart","General", False); display_preview(a,"rag")
    with tabs[5]:
        s=st.selectbox("Subject",SUBJECTS,key="ls"); l=st.selectbox("Class",CLASSES,key="ll"); t=st.selectbox("Topic",get_topics(s,l),key="lt_topics")
        if st.button("Lesson"): a,src,lvl=tutor_brain(f"Lesson Plan {l} {s} {t}",l,"notes",s, False); display_preview(a,"lesson")
    with tabs[6]:
        n=st.number_input("Students",1,1000,100)
        if st.button("Reports"): a,src,lvl=tutor_brain(f"{n} Report Cards","S4","notes","General", False); display_preview(a,"report")
    with tabs[7]:
        q=st.text_area("Predictor",key="prq")
        if st.button("Ask"): a,src,lvl=tutor_brain(q,"S4","smart","General", False); display_preview(a,"pr")
    with tabs[8]:
        s=st.selectbox("Subject",SUBJECTS,key="exs"); l=st.selectbox("Class",CLASSES,key="exl"); t=st.multiselect("Topics",get_topics(s,l), key="a3_topics")
        if st.button("Exam"): a,src,lvl=tutor_brain(f"Full NCDC exam 100 marks for {l} {s} on {t}",l,"exam",s, False); display_preview(a,"exam")

### 11. LOGIN ###
st.title("🧠 DIGITAL UNEB TUTOR 2026 - VDB MEMORY")
with st.sidebar:
    st.metric("RAM",f"{psutil.virtual_memory().percent}%")
    st.metric("Mode", mode_badge)
    st.metric("Memory", f"{len(chat_mem.mem)} msgs")
    pw=st.text_input("Password",type="password", key="main_login_pw")
    c1,c2=st.columns(2)
    if c1.button("Student Login",key="btn_student_login") and pw==STUDENT_PASSWORD: st.session_state.role="Student"; st.rerun()
    if c2.button("Admin Login",key="btn_admin_login") and pw==ADMIN_PASSWORD: st.session_state.role="Admin"; st.rerun()
if st.session_state.get("role")=="Admin": show_admin()
elif st.session_state.get("role")=="Student": show_student()
else: st.info("Login. Student=1234 Admin=admin123")
