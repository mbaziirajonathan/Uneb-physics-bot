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

# TOKEN COUNTER - OPTIONAL DEPENDENCY
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ModuleNotFoundError:
    TIKTOKEN_AVAILABLE = False
    st.sidebar.warning("tiktoken not installed. Using rough token estimate ~4 chars = 1 token")

# LAZY LOAD HEAVY LIBS
numpy = None
faiss = None
SentenceTransformer = None

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 VDB", page_icon="🧠", layout="wide")
st.sidebar.caption("Build: V7.3.5-NDEJJE-QC-SIT | FULL 18 SUBJECTS + QC")

### 1. FILES + UTILS ###
DATA_PATH = os.getenv("STREAMLIT_DATA_PATH", "data")
if not os.path.exists(DATA_PATH) or not os.access(DATA_PATH, os.W_OK): DATA_PATH = "/tmp"
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
    try:
        with open(f,"r", encoding='utf-8') as file:
            return json.load(file)
    except:
        save_db(f,default); return default

for f,d in [(LOG_FILE,[]),(CACHE_FILE,{}),(DOCS_FILE,[]),(SETTINGS_FILE,{}),(MEMORY_FILE,[])]: load_db(f,d)

### 2. TOKEN ECONOMICS ENGINE ###
class TokenEconomist:
    def __init__(self):
        if TIKTOKEN_AVAILABLE:
            self.enc = tiktoken.get_encoding("cl100k_base")
        else:
            self.enc = None
        self.TOKEN_BUDGET = 3500
        self.PRESERVED_MEMORY_TOKENS = 400
    def count_tokens(self, text):
        if self.enc: return len(self.enc.encode(text))
        return len(text)//4
    def auto_quantize(self, rag_chunks, prompt, system_prompt):
        available = self.TOKEN_BUDGET - self.count_tokens(system_prompt) - self.count_tokens(prompt) - self.PRESERVED_MEMORY_TOKENS
        if available < 500: available = 500
        compressed_rag = []; used = 0
        for chunk in rag_chunks:
            chunk_tokens = self.count_tokens(chunk['txt'])
            if used + chunk_tokens < available:
                compressed_rag.append(chunk); used += chunk_tokens
            else: break
        model = "google/gemini-2.5-flash"
        if used > 3000: model = "google/gemini-2.0-flash-lite"
        return compressed_rag, model
    def compress_memory(self, messages):
        if len(messages) <= 4: return messages
        return messages[-4:]
token_econ = TokenEconomist()

### 2B. UGANDAN TEACHER + SIT + QC + SECTORS ENGINE ###
class NCDC2026Engine:
    SECTORS = {"health": "Hospitals, Nursing, Public Health","agriculture": "Farming, Vet, Agro-processing","engineering": "Civil, Electrical, Mechanical","economics": "Business, Banking, SACCOs","accounts": "Bookkeeping, Auditing","research": "UNEB, Universities, NARO","geology": "Mining, Water, Construction"}
    SUBJECT_SECTORS = {"Physics": ["engineering","health","agriculture"],"Chemistry": ["health","agriculture","engineering"],"Biology": ["health","agriculture"],"Mathematics": ["economics","accounts","engineering"],"Agriculture": ["agriculture","economics"],"Geography": ["geology","agriculture"],"Entrepreneurship": ["economics","accounts"],"ICT": ["research","engineering"]}
    def get_sectors(self, subject): return [f"**{s.title()}**: {self.SECTORS[s]}" for s in self.SUBJECT_SECTORS.get(subject, ["research"])]
    def generate_sit(self, subject, level, topic): return f"**NCDC 2026 SIT**\n**SCENARIO**: Ugandan community in {random.choice(['Gulu','Mbale','Mbarara','Wakiso'])} has problem with {topic}.\n**ITEM**: LC1 gives you data/equipment.\n**TASK**: 1. Apply {topic} 2. Show working 3. State 2 local challenges + solutions."
    def get_applications(self, subject, topic): return f"Use {topic} in: {', '.join(self.SUBJECT_SECTORS.get(subject, ['research']))}"
    def generate_10_sit(self, subject, level, topics): return f"**GENERATE 10 NCDC 2026 SIT QUESTIONS FOR {subject} {level} ON {topics}**\nEach with: Scenario, Item, Task, 10 mark marking guide."

class UgandanTeacher:
    def get_style_rules(self, subject, level, topic):
        is_science = subject in ["Physics","Chemistry","Biology","Mathematics","Agriculture"]
        level_num = int(level[1]); sectors = "\n".join(ncdc_engine.get_sectors(subject)); sit = ncdc_engine.generate_sit(subject, level, topic); apps = ncdc_engine.get_applications(subject, topic)
        if level_num <= 2: return f"TEACHING STYLE: SIMPLE UGANDAN TEACHER\n1. 4 bullets. 1 Local example: boda, posho, market.\n2. WHERE YOU CAN USE THIS:\n{sectors}\n3. End: 'Do you understand, student?'"
        if is_science and level_num >= 3: return f"TEACHING STYLE: DETAILED NCDC SCIENCE TEACHER\nRULE 1: FORMULA -> DEFINE -> SUBSTITUTE -> CALCULATE. Explain WHY scientifically.\nRULE 2: REAL APPLICATIONS: {apps}\nRULE 3: SECTORS YOU CAN HELP:\n{sectors}\nRULE 4: {sit}\nRULE 5: Use Ugandan context only."
        return f"TEACHING STYLE: NCDC HUMANITIES TEACHER\n1. Cause -> Effect -> Impact\n2. SECTORS:\n{sectors}\n3. {sit}"
    def format_answer(self, raw, subject, level): return raw

class QCExaminer:
    def mark_answer(self, student_answer, correct_answer, subject, level):
        total=10; feedback=[]; is_science = subject in ["Physics","Chemistry","Biology","Mathematics"]
        if is_science and "=" in correct_answer and "=" not in student_answer: total-=2; feedback.append("❌ -2: Missing Formula. State it first.")
        if is_science and int(level[1])>=3 and not all(s.lower() in student_answer.lower() for s in ["Define","Substitute","Calculate"]): total-=4; feedback.append("❌ -4: Missed working steps: Define, Substitute, Calculate")
        if is_science and not any(u in student_answer for u in ["N","m","s","J","kg","mol","dm3"]): total-=1; feedback.append("❌ -1: Missing Units. UNEB deducts 1 mark.")
        fundamentals = {"Physics": ["Force","Energy"],"Chemistry": ["Mole","Reaction"],"Biology": ["Cell","Enzyme"]}
        for fund in fundamentals.get(subject,[]):
            if fund.lower() in correct_answer.lower() and fund.lower() not in student_answer.lower(): total-=1; feedback.append(f"❌ -1: Missed core concept: '{fund}'")
        total=max(0,total); grade="A - Distinction" if total>=8 else "B - Credit" if total>=6 else "C - Revise"
        return f"**NDEJJE SS QC MARK: {total}/10**\n**Grade**: {grade}\n\n**TEACHER FEEDBACK**:\n" + "\n".join(feedback) if feedback else f"**NDEJJE SS QC MARK: {total}/10**\n**Grade**: {grade}\n**Feedback**: Excellent work. No errors."

ncdc_engine = NCDC2026Engine(); teacher_style = UgandanTeacher(); qc_examiner = QCExaminer()

### 3. LOAD MASTER DATABASE - FULL 18 SUBJECTS RESTORED ###
@st.cache_data
def load_master_db():
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

### 4-6. SECRETS, SYSTEM CHECK, CACHE ###
OPENROUTER_API_KEY=os.getenv("OPENROUTER_API_KEY",""); STUDENT_PASSWORD=os.getenv("STUDENT_PASSWORD","1234"); ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD","admin123")
IS_CLOUD = os.getenv("DEPLOY_ENV") == "cloud"
def system_check():
    try: socket.create_connection(("1.1.1.1", 53), timeout=2); online = True
    except: online = False
    ram = psutil.virtual_memory().percent; return {"online": online and OPENROUTER_API_KEY!= "", "ram": ram}
def keep_alive():
    while True: time.sleep(840);
    try: requests.get(os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8501"), timeout=5)
    except: pass
threading.Thread(target=keep_alive, daemon=True).start()
@st.cache_resource
def get_client(): return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY) if OPENROUTER_API_KEY else None
@st.cache_resource
def get_embedder(): global SentenceTransformer;
if SentenceTransformer is None: from sentence_transformers import SentenceTransformer; return SentenceTransformer('all-MiniLM-L6-v2')
@st.cache_resource
def get_faiss(): global faiss, numpy;
if faiss is None: import faiss;
if numpy is None: import numpy as np; return faiss, np
SYS_STATE=system_check(); client=get_client() if SYS_STATE["online"] else None; mode_badge=f"☁️ CLOUD | RAM:{SYS_STATE['ram']:.0f}%"
class TTLSchoolCache:
    def __init__(self, ttl=7200): self.ttl=ttl; self.cache=load_db(CACHE_FILE,{})
    def get(self,q): k=hashlib.sha256(q.encode()).hexdigest();
    if k in self.cache and time.time()<self.cache[k][1]: return self.cache[k][0]; return None
    def set(self,q,a): self.cache[hashlib.sha256(q.encode()).hexdigest()] = [a, time.time()+self.ttl]; save_db(CACHE_FILE,self.cache)
ai_cache = TTLSchoolCache()
class ChatMemory:
    def __init__(self, ttl=600): self.ttl=ttl; self.mem=load_db(MEMORY_FILE,[])
    def add(self, role, content): self.mem.append({"role":role,"content":content,"time":time.time()}); self.mem = [m for m in self.mem if time.time() - m["time"] < self.ttl]; save_db(MEMORY_FILE,self.mem)
    def get_context(self): compressed = token_econ.compress_memory(self.mem); return [{"role":m["role"],"content":m["content"]} for m in compressed]
chat_mem = ChatMemory()

### 7. HELPER FUNCTIONS ###
def get_topics(s,l): return THEORY_DB.get(s,{}).get(l,{}).get("topics",["General Topic"])
def get_competency(s,l): return THEORY_DB.get(s,{}).get(l,{}).get("competency","General")
def get_practicals(s,l): g = "S1-S4" if int(l[1])<=4 else "S5-S6"; return list(PRACTICALS_DB.get(s,{}).get(g,{}).keys()) or ["No Practicals"]
def get_practical_obj(s,l,p): g = "S1-S4" if int(l[1])<=4 else "S5-S6"; return PRACTICALS_DB.get(s,{}).get(g,{}).get(p,{}).get("objective","")
def get_related_practicals(s,l,topic):
    g = "S1-S4" if int(l[1])<=4 else "S5-S6"; related = []
    for p_name, p_data in PRACTICALS_DB.get(s,{}).get(g,{}).items():
        if SequenceMatcher(None, topic.lower(), p_name.lower()).ratio() > 0.4 or topic.lower() in p_data["objective"].lower():
            related.append(f"**{p_name}**: {p_data['objective']} | *Apparatus: {p_data['apparatus']}*")
    return "\n".join(related) if related else ""

def topic_exists_in_db(prompt, subject, level):
    prompt_l = prompt.lower(); g = "S1-S4" if int(level[1])<=4 else "S5-S6"
    for s in SUBJECTS:
        for l in CLASSES:
            if any(x.lower() in prompt_l for x in get_topics(s,l)): return True, s, l
    for p_name in PRACTICALS_DB.get(subject,{}).get(g,{}).keys():
        if p_name.lower() in prompt_l: return True, subject, level
    return False, subject, level

def display_preview(content,name,s,l):
    st.session_state.current_subject=s; st.session_state.current_level=l
    st.text_area("🤖 Tutor Output",content,height=450,key=f"p{name}")
    student_ans = st.text_area("✍️ Paste your answer for QC Marking", key=f"mark{name}")
    c1,c2,c3=st.columns(3)
    if c1.button("📥 Download",key=f"d{name}"): st.download_button("Download",content.encode(),f"{name}.txt",key=f"dl{name}")
    if c2.button("🔍 QC Mark My Answer",key=f"qc{name}") and student_ans: st.success(qc_examiner.mark_answer(student_ans, content, s, l))

### 8. FAISS RAG ###
class VectorRAG:
    def __init__(self):
        self.docs=load_db(DOCS_FILE,[])
        self.index = None
        if os.path.exists(FAISS_FILE):
            faiss, np = get_faiss()
            self.index = faiss.read_index(FAISS_FILE)
        self._rebuild_if_needed()
    def _rebuild_if_needed(self):
        if len(self.docs) > 0 and (self.index is None or self.index.ntotal!= len(self.docs)):
            faiss, np = get_faiss(); embedder = get_embedder()
            with st.spinner("Building FAISS Index..."):
                embeddings = embedder.encode([d['txt'] for d in self.docs])
                self.index = faiss.IndexFlatL2(384)
                self.index.add(np.array(embeddings).astype('float32'))
                faiss.write_index(self.index, FAISS_FILE)
    def add(self,texts,fn):
        faiss, np = get_faiss(); embedder = get_embedder()
        new_docs = [{"src":fn,"chunk_id":i,"txt":t[:1200]} for i,t in enumerate(texts)]
        self.docs.extend(new_docs); save_db(DOCS_FILE,self.docs)
        embeddings = embedder.encode([d['txt'] for d in new_docs])
        if self.index is None: self.index = faiss.IndexFlatL2(384)
        self.index.add(np.array(embeddings).astype('float32')); faiss.write_index(self.index, FAISS_FILE)
    def search(self,q,k=3):
        if self.index is None or self.index.ntotal == 0: return []
        faiss, np = get_faiss(); embedder = get_embedder()
        q_vec = embedder.encode([q]); D, I = self.index.search(np.array(q_vec).astype('float32'), k)
        return [self.docs[i] for i in I[0] if i < len(self.docs)]
vector_rag=VectorRAG()

def chunk_text(text, sz=350):
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

### 9. BRAIN ###
def detect_complexity(prompt):
    p = prompt.lower()
    if any(x in p for x in ["define","what is","list"]): return "S1", 300
    if any(x in p for x in ["explain","how","why"]): return "S4", 600
    if any(x in p for x in ["derive","evaluate","research","design","exam"]): return "S6", 1200
    return "S4", 600

def get_level_rules(level):
    rules = {"S1": "Basic. 2-3 points.","S2": "Understanding. 3-4 points.","S3": "Skill Application. 4-5 points.","S4": "Scenario->Item->Task.","S5": "Analysis. Derivations.","S6": "Synthesis. Research."}
    return rules.get(level, rules["S4"])

SYSTEM_PROMPT_OFFICIAL="""You are DIGITAL UNEB TUTOR 2026. Mark like Ndejje SS HOD. Be creative like Gemini Pro. Use analogies. PRIORITIZE ncdc_master_db.json. {level_rules}"""
SYSTEM_PROMPT_GENERATIVE="""You are DIGITAL UNEB TUTOR 2026 - INVENT MODE. NCDC 2026 {subject} {level}. Ugandan context only."""

def call_openrouter_api(messages, model, max_tokens):
    res=client.chat.completions.create(model=model,messages=messages,max_tokens=max_tokens,temperature=0.2)
    return res.choices[0].message.content

def tutor_brain(prompt,level="S4",mode="smart",subject="General", allow_invent=False):
    global SYS_STATE; SYS_STATE=system_check(); chat_mem.add("user", prompt)
    detected_level, max_resp_tokens = detect_complexity(prompt) if level=="Auto" else (level, 600)
    sources=vector_rag.search(prompt,3)
    topic_exists, subject, detected_level = topic_exists_in_db(prompt, subject, detected_level)
    competency = get_competency(subject, detected_level); level_rules = get_level_rules(detected_level); practical_link = get_related_practicals(subject, detected_level, prompt)
    matched_topic = next((t for t in get_topics(subject, detected_level) if t.lower() in prompt.lower()), "General Topic")
    style_rules = teacher_style.get_style_rules(subject, detected_level, matched_topic)
    if not topic_exists and len(sources)==0 and not allow_invent: return "Per NCDC 2026 this is not in syllabus. Click 'Invent/Extend' to generate.", [], detected_level
    sys_prompt = SYSTEM_PROMPT_GENERATIVE.format(level_rules=level_rules, subject=subject, level=detected_level) if allow_invent and not topic_exists else SYSTEM_PROMPT_OFFICIAL.format(level_rules=level_rules)
    compressed_sources, AI_MODEL = token_econ.auto_quantize(sources, prompt, sys_prompt)
    full_prompt = f"{sys_prompt}\n{style_rules}\nLEVEL:{detected_level}\nSUBJECT:{subject}\nCOMPETENCY:{competency}\nRAG:{compressed_sources}\nPRACTICAL:{practical_link}\nTASK:{prompt}"
    cached=ai_cache.get(full_prompt+AI_MODEL);
    if cached: return f"[CACHED] {cached}", sources, detected_level
    if SYS_STATE["online"] and client:
        try:
            messages = chat_mem.get_context() + [{"role":"user","content":full_prompt}]; ans = call_openrouter_api(messages, AI_MODEL, max_resp_tokens)
            ans = teacher_style.format_answer(ans, subject, detected_level); chat_mem.add("assistant", ans)
            src_line = f"**Proof**: DB {subject} {detected_level}" if topic_exists else "**Proof**: [NCDC-GENERATIVE]"
            final_ans = ans + f"\n\n{src_line}\n**Level**: {detected_level}"; ai_cache.set(full_prompt+AI_MODEL,final_ans); return final_ans, sources, detected_level
        except Exception as e: st.sidebar.error(f"Cloud failed: {e}")
    return ("[OFFLINE] No internet. Upload notes.", [], detected_level)

### 10. STUDENT + ADMIN PORTAL ###
def show_student():
    st.header("🧠 Digital Tutor V7.3.5");
    if st.button("Logout", key="student_logout"): st.session_state.clear(); st.rerun()
    t1,t2,t3,t4,t5=st.tabs(["💬 Chat","📖 Learn","🧪 Practicals","🖼️ Diagrams","🔬 Research"])
    with t1:
        render_upload("s1"); s=st.selectbox("Subject",SUBJECTS,key="s1s"); l=st.selectbox("Class",["Auto"]+CLASSES,key="s1l"); q=st.text_area("Ask",key="s1q")
        c1,c2=st.columns(2)
        if c1.button("Ask Official",key="s1b") and q: lvl = "S4" if l=="Auto" else l; a,src,lvl_out=tutor_brain(q,lvl,"smart",s, False); display_preview(a,"s1",s,lvl_out)
        if c2.button("Invent/Extend",key="s1gen") and q: lvl = "S4" if l=="Auto" else l; a,src,lvl_out=tutor_brain(q,lvl,"smart",s, True); display_preview(a,"s1gen",s,lvl_out)
    with t2:
        render_upload("s2"); s=st.selectbox("Subject",SUBJECTS,key="s2s"); l=st.selectbox("Class",CLASSES,key="s2l"); t=st.selectbox("Topic",get_topics(s,l),key="s2t")
        c1,c2,c3=st.columns(3)
        if c1.button("Notes From DB",key="s2b"): a,src,lvl=tutor_brain(f"Teach {t} for {l} {s}",l,"notes",s, False); display_preview(a,"s2",s,l)
        if c2.button("Quiz Me",key="s2q"): a,src,lvl=tutor_brain(f"Quiz me on {t} for {l} {s}",l,"smart",s, False); display_preview(a,"s2q",s,l)
        if c3.button("10 SIT Questions",key="s2sit"): a,src,lvl=tutor_brain(ncdc_engine.generate_10_sit(s,l,t),l,"notes",s, False); display_preview(a,"s2sit",s,l)
    with t3:
        render_upload("s3"); s=st.selectbox("Subject",list(PRACTICALS_DB.keys()),key="s3s"); l=st.selectbox("Class",CLASSES,key="s3l"); p=st.selectbox("Practical",get_practicals(s,l),key="s3p")
        if st.button("Teach Practical",key="s3b"): obj=get_practical_obj(s,l,p); a,src,lvl=tutor_brain(f"Teach {p} practical for {l}. Objective: {obj}",l,"notes",s, False); display_preview(a,"s3",s,l)
    with t4:
        render_upload("s4"); s=st.selectbox("Subject",SUBJECTS,key="s4s"); l=st.selectbox("Class",CLASSES,key="s4l"); t=st.selectbox("Topic",get_topics(s,l),key="s4t")
        if st.button("Explain Diagram",key="s4b"): a,src,lvl=tutor_brain(f"Explain diagram for {t} in {s} {l}",l,"smart",s, False); display_preview(a,"s4",s,l)
    with t5:
        render_upload("s5"); s=st.selectbox("Subject",SUBJECTS,key="s5s"); l=st.selectbox("Class",CLASSES,key="s5l")
        rq=st.text_area("Research Topic",key="s5rq")
        c1,c2=st.columns(2)
        if c1.button("Research From DB",key="s5rb") and rq: a,src,lvl=tutor_brain(f"Research project on {rq} for {l} {s}",l,"research",s, False); display_preview(a,"s5res",s,l)
        if c2.button("Invent Research Idea",key="s5gen") and rq: a,src,lvl=tutor_brain(f"Invent new NCDC research topic related to {rq} for {l} {s}",l,"research",s, True); display_preview(a,"s5gen",s,l)

def show_admin():
    st.header("🏫 Admin Portal");
    if st.button("Logout", key="admin_logout"): st.session_state.clear(); st.rerun()
    tabs=st.tabs(["📊 Analytics","📖 Curriculum","🧪 Practicals","📤 Bulk","📚 RAG KB","📝 Lesson","📄 Reports","📈 Predictive","📝 Exams"])
    with tabs[0]:
        q=st.text_area("Ask Analytics",key="aq")
        if st.button("Ask"): a,src,lvl=tutor_brain(q,"S4","smart","General", False); display_preview(a,"a","General","S4")
    with tabs[1]:
        s=st.selectbox("Subject",SUBJECTS,key="as"); l=st.selectbox("Class",CLASSES,key="al"); t=st.multiselect("Topics",get_topics(s,l), key="a1_topics")
        if st.button("Scheme"): a,src,lvl=tutor_brain(f"Scheme for {l} {s} {t}",l,"notes",s, False); display_preview(a,"scheme",s,l)
    with tabs[2]:
        s=st.selectbox("Subject",list(PRACTICALS_DB.keys()),key="ps"); l=st.selectbox("Class",CLASSES,key="pl"); p=st.selectbox("Practical",get_practicals(s,l)+["Invent"],key="pp")
        if st.button("Guide"): a,src,lvl=tutor_brain(f"Lab manual for {p} {l} {s}",l,"notes",s, "Invent" in p); display_preview(a,"pg",s,l)
    with tabs[3]:
        s=st.selectbox("Subject",SUBJECTS,key="bs"); l=st.selectbox("Class",CLASSES,key="bl"); t=st.multiselect("Topics",get_topics(s,l), key="a2_topics"); n=st.slider("Qs",10,100,50)
        if st.button("Bulk"): a,src,lvl=tutor_brain(f"{n} NCDC Qs + Marking from {t} for {l} {s}",l,"notes",s, False); display_preview(a,"bulk",s,l)
    with tabs[4]:
        st.metric("FAISS Chunks",len(vector_rag.docs)); render_upload("a5")
        q=st.text_area("Ask RAG",key="ragq")
        if st.button("Ask RAG"): a,src,lvl=tutor_brain(q,"S4","smart","General", False); display_preview(a,"rag","General","S4")
    with tabs[5]:
        s=st.selectbox("Subject",SUBJECTS,key="ls"); l=st.selectbox("Class",CLASSES,key="ll"); t=st.selectbox("Topic",get_topics(s,l),key="lt")
        if st.button("Lesson"): a,src,lvl=tutor_brain(f"Lesson Plan {l} {s} {t}",l,"notes",s, False); display_preview(a,"lesson",s,l)
    with tabs[6]:
        n=st.number_input("Students",1,1000,100)
        if st.button("Reports"): a,src,lvl=tutor_brain(f"{n} Report Cards","S4","notes","General", False); display_preview(a,"report","General","S4")
    with tabs[7]:
        q=st.text_area("Predictor",key="prq")
        if st.button("Ask"): a,src,lvl=tutor_brain(q,"S4","smart","General", False); display_preview(a,"pr","General","S4")
    with tabs[8]:
        s=st.selectbox("Subject",SUBJECTS,key="exs"); l=st.selectbox("Class",CLASSES,key="exl"); t=st.multiselect("Topics",get_topics(s,l), key="a3_topics")
        if st.button("Full Exam"): a,src,lvl=tutor_brain(f"Full NCDC exam 100 marks for {l} {s} on {t}",l,"exam",s, False); display_preview(a,"exam",s,l)

### 11. LOGIN ###
st.title("🧠 DIGITAL UNEB TUTOR 2026 - NDEJJE QC")
with st.sidebar:
    st.metric("RAM",f"{SYS_STATE['ram']:.0f}%"); st.metric("Mode", mode_badge)
    pw=st.text_input("Password",type="password", key="main_login_pw")
    if st.button("Student Login") and pw==STUDENT_PASSWORD: st.session_state.role="Student"; st.rerun()
    if st.button("Admin Login") and pw==ADMIN_PASSWORD: st.session_state.role="Admin"; st.rerun()
if st.session_state.get("role")=="Admin": show_admin()
elif st.session_state.get("role")=="Student": show_student()
else: st.info("Login. Student=1234 Admin=admin123")
