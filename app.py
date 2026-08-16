from difflib import SequenceMatcher
import streamlit as st, os, io, json, re, time, requests, random, threading, psutil, socket, hashlib
from datetime import datetime
from groq import Groq, RateLimitError
import logging
logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 PRO", page_icon="📚", layout="wide")
st.sidebar.caption("Build: V6.1.6-NCDC-FINAL | NCDC 2026 CBC | ALL TOPICS + PRACTICALS LOADED")

### 1. FILES + UTILS ###
DATA_PATH = os.getenv("STREAMLIT_DATA_PATH", ".")
LOG_FILE, CACHE_FILE, DOCS_FILE, SETTINGS_FILE = [f"{DATA_PATH}/{x}" for x in ["usage_log.json","ai_cache.json","vector_docs.json","teacher_settings.json"]]
def save_db(f,d): json.dump(d, open(f,"w"), indent=2)
def load_db(f,default):
    if not os.path.exists(f): save_db(f,default)
    try: return json.load(open(f,"r"))
    except: save_db(f,default); return default
for f,d in [(LOG_FILE,[]),(CACHE_FILE,{}),(DOCS_FILE,[]),(SETTINGS_FILE,{})]: load_db(f,d)

### 2. SECRETS + MODELS ###
GROQ_API_KEY=os.getenv("GROQ_API_KEY",""); STUDENT_PASSWORD=os.getenv("STUDENT_PASSWORD","1234"); ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD","admin123")
if not GROQ_API_KEY: st.error("Missing GROQ_API_KEY in Render Environment"); st.stop()

### 3. OS SENSORS ###
def system_check():
    try: socket.create_connection(("1.1.1.1", 53), timeout=2); online = True
    except: online = False
    return {"online": online and GROQ_API_KEY!= "", "ram_ok": psutil.virtual_memory().percent < 80, "render": os.getenv("RENDER","false")=="true"}

def keep_alive():
    while True:
        time.sleep(840)
        try: requests.get(os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8501"), timeout=5)
        except: pass
threading.Thread(target=keep_alive, daemon=True).start()

@st.cache_resource
def get_client(): return Groq(api_key=GROQ_API_KEY)
client=get_client(); SYS_STATE=system_check()
AI_MODEL_LONG="llama-3.3-70b-versatile" if SYS_STATE["online"] else "offline"; AI_MODEL_SHORT="llama-3.1-8b-instant" if SYS_STATE["online"] else "offline"
OFFLINE_MODE = not SYS_STATE["online"]
if OFFLINE_MODE: st.sidebar.warning("🔌 OFFLINE RAG MODE")

### 4. TTL CACHE ###
class TTLSchoolCache:
    def __init__(self, ttl=7200): self.ttl=ttl; self.cache=load_db(CACHE_FILE,{})
    def get(self,q):
        k=hashlib.sha256(q.encode()).hexdigest();
        if k in self.cache and time.time()<self.cache[k][1]: return self.cache[k][0]
        return None
    def set(self,q,a): self.cache[hashlib.sha256(q.encode()).hexdigest()] = [a, time.time()+self.ttl]; save_db(CACHE_FILE,self.cache)
ai_cache = TTLSchoolCache()

### 5. NCDC MASTER CURRICULUM - ALL SUBJECTS S1-S6 INTACT ###
UNEB_CURRICULUM_MAP = {
    "Physics": {
        "S1": ["Measurements","Density","States of Matter","Introduction to Forces","Thermometry","Heat Transfer","Rectilinear Propagation","Reflection at Plane Surfaces","Intro to Electricity Part I","Magnets"],
        "S2": ["Turning Effect of Forces","Machines","Work Energy and Power","Pressure","Properties of Matter","Reflection at Curved Surfaces","Wave Motion","Properties of Waves","Sound Waves","Intro to Electricity Part II","Magnetic Effect of Current"],
        "S3": ["Refraction of Light","Lenses","Linear Motion","Newton's Laws of Motion","Friction","Current Electricity","Force on a Conductor","Quantity of Heat"],
        "S4": ["Domestic Electricity","Electromagnetic Induction","Modern Physics Electronics","Modern Physics Radioactivity"],
        "S5": ["Fields I","Current","Advanced Mechanics","Waves II","Thermal Physics"],
        "S6": ["Electric Fields","Nuclear Physics II","Quantum Physics","AC Circuits","Astrophysics"]
    },
    "Mathematics": {
        "S1": ["Number Bases & Systems","Working with Fractions","Decimals and Percentages","Integers and Directed Numbers","Sets and Venn Diagrams","Introduction to Geometry","Algebra Expressions & Formulae","Equations and Inequalities","Coordinates and Linear Graphs"],
        "S2": ["Ratios Proportions & Scale","Sequences and Number Patterns","Length Area and Volume","Mapping and Functions","Graphs of Quadratic Functions","Vectors in a 2D Plane","Transformation Geometry","Business Mathematics","Data Handling & Statistics"],
        "S3": ["Matrices & Transformations","Simultaneous Linear Equations","Pythagoras Theorem & Intro Trig","Quadratic Equations","Loci and Geometric Constructions","Further Vectors and Gradients","Probability Theory","Circles and Circle Theorems","Logarithms and Indices"],
        "S4": ["Linear Programming","Three-Dimensional Geometry","Advanced Business Calculations","Trigonometry Non-Right Triangles","Advanced Statistical Dispersion","Revision & Synthesis"],
        "S5": ["Surds Indices Logarithmic Functions","Quadratic Theory","Permutations and Combinations","Binomial Theorem","Partial Fractions","Matrices and Determinants 3x3","Compound Multiple Angle Formulae","Trigonometric Equations","Straight Line Circle","Limits and Continuity","Differentiation","Integration Techniques","Complex Numbers","Vectors in 3D","Statics","Kinematics","Probability","Numerical Methods"],
        "S6": ["Conic Sections","Applications of Differentiation","Definite Integrals Volume of Revolution","De Moivre Theorem","Equations of lines and planes 3D","Kinetics","Discrete Random Variables","Continuous Distributions","Newton-Raphson method","Numerical Integration"]
    },
    "Chemistry": {
        "S1": ["Introduction to Chemistry and Society","Experimental Chemistry Apparatus and Measurement","States of Matter and Kinetic Theory","Elements Mixtures and Compounds","Particulate Nature of Matter","The Atmosphere and Combustion"],
        "S2": ["Atomic Structure and The Periodic Table","Chemical Bonding and Structure","Acids Bases and Indicators","Salts and their Preparation","Properties of Carbon and its Inorganic Compounds","Water and Hydrogen"],
        "S3": ["The Mole Concept and Stoichiometry","Volumetric Analysis","Reactivity Series of Metals","Extraction of Metals","Electrochemistry","Halogens and their Compounds"],
        "S4": ["Energy Changes in Chemical Reactions","Rates of Chemical Reactions","Reversible Reactions and Equilibrium","Introduction to Organic Chemistry","Synthetic Polymers and Materials","Nitrogen and its Compounds"],
        "S5": ["Gases and Kinetic Theory","Atomic Structure and Quantum Mechanics","Chemical Bonding and Structure VSEPR","Chemical Thermodynamics","Chemical Kinetics","Chemical Equilibrium","Electrochemistry Nernst"],
        "S6": ["Periodic Trends Period 3","Group II Elements","Group VII Elements","Transition Chemistry d-block","Aliphatic Hydrocarbons","Halogenoalkanes","Hydroxy Compounds","Carbonyl Compounds","Carboxylic Acids and Derivatives","Nitrogen Compounds","Polymerization"]
    },
    "Biology": {
        "S1": ["Introduction to Biology", "Cells and Microscopy", "Levels of Organization", "Classification of Living Things (Grouping Living Organisms)"],
        "S2": ["Nutrition in Plants and Animals", "Transport of Materials in Plants and Animals", "Gaseous Exchange and Respiration"],
        "S3": ["Excretion and Homeostasis", "Support and Movement", "Coordination (Nervous and Endocrine Systems)", "Locomotion"],
        "S4": ["Reproduction in Plants and Animals", "Genetics, Inheritance and Variation", "Ecology and Ecosystems", "Human Health and Disease"],
        "S5": ["Cell Biology and Biochemistry", "Taxonomy and Evolution", "Plant and Animal Physiology (Nutrition, Transport, Respiration)"],
        "S6": ["Homeostasis and Coordination", "Growth and Development", "Genetics, Selection and Evolution", "Ecology and Environmental Biology"]
    },
    "Agriculture": {
        "S1": ["Introduction to Agriculture", "Safety and Welfare in Agriculture", "Farm Tools, Equipment and Workshop Technology", "Soil Science (Origin, Profiles, and Physics)"],
        "S2": ["Crop Production and Agronomy (Nursery Management, Soil Fertility)", "Animal Production and Husbandry (Breeds, Anatomy, and Systems)", "Agribusiness and Basic Farming Economics"],
        "S3": ["Crop Protection (Weed, Pest, and Disease Management)", "Animal Health and Disease Control (Parasitology and Vaccines)", "Farm Structures and Farm Mechanisation"],
        "S4": ["Advanced Sustainable Farm Management", "Value Addition and Post-Harvest Technology", "Agricultural Marketing and Enterprise Planning", "DIT Vocational Competency Portfolio Review"],
        "S5": ["Advanced Soil Science and Chemistry", "Advanced Crop Physiology and Agronomy", "Agricultural Engineering and Power Sources"],
        "S6": ["Advanced Animal Nutrition and Livestock Production", "Agricultural Economics, Extension and Agribusiness Management", "Agricultural Field Research Methodology"]
    },
    "English Language": {
        "S1": ["Self and Personal Identity", "School Life and Environment", "Community, Occupations and Occupations", "Health and Hygiene", "Leisure and Recreation", "Environment and Climate Change"],
        "S2": ["Science and Technology", "Communication and Media", "Human Rights and Civic Duties", "Culture and Heritage", "Peace and Conflict Resolution", "Traffic and Road Safety"],
        "S3": ["Financial Literacy and Banking", "Tourism and Hospitality", "Employment and Career Paths", "Governance and Leadership", "Population and Development", "Regional Sub-County and Community Issues"],
        "S4": ["Global Citizenship and International Trends", "Synthesis and Précis Summaries", "Advanced Functional and Professional Writing", "Consolidation of Grammar and Oral Skills"]
    },
    "Literature in English": {
        "S1": ["Introduction to Literature and Genres", "Introduction to Oral Literature", "Understanding Prose Fiction and Plot Development", "Appreciating Basic Poetry"],
        "S2": ["Characterization and Themes in Drama", "Context and Setting in Prose Fiction", "Stylistic Devices and Literary Imagery in Poetry"],
        "S3": ["Study of Prescribed Prose Set-Texts", "Study of Prescribed Drama Set-Texts", "Unseen Poetry and Comprehensive Contextual Analysis"],
        "S4": ["Comparative Literary Analysis", "Critical and Evaluative Essay Writing", "Oral Performance and Dramatic Interpretation Techniques"]
    },
    "Geography": {
        "S1": ["Introduction to Geography and Map Work", "The Solar System and the Earth", "Weather and Climate"],
        "S2": ["Geomorphology (Rocks, Weathering, and Landforms)", "Drainage Systems and River Development", "Vegetation Zones and Wildlife Management"],
        "S3": ["Population and Settlement Dynamics", "Economic Activities (Agriculture, Forestry, and Fishing)", "Mining, Industrialization, and Infrastructure Development"],
        "S4": ["Geography of East Africa (Themed Contextual Case Studies)", "Introduction to GIS, Remote Sensing, and Photographic Interpretation", "Environmental Conservation and Sustainable Development"],
        "S5": ["Physical Geography (Geomorphology, Climatology, and Oceanography)", "Practical Geography (Statistical Methods, Advanced Map Work, and Fieldwork Skills)"],
        "S6": ["Human and Economic Geography (World Development Studies)", "Regional Geography of Africa", "Environmental Management and Global Sustainability Issues"]
    },
    "History": {
        "S1": ["Introduction to History and Sources", "Early Man and Evolution in East Africa", "Migrations, Settlement, and Inter-ethnic Interactions of African Peoples"],
        "S2": ["Pre-Colonial Socio-Political Organizations and Kingdoms", "Early Contacts between East Africa and the Outside World", "The Abolition of Slave Trade and Rise of Long Distance Trade"],
        "S3": ["The Scramble, Partition, and Establishment of Colonial Rule", "Colonial Administrative Systems and Economic Policies", "African Nationalism and Resonances of Resistance"],
        "S4": ["The Road to Independence and Decolonization", "Post-Independence Achievements and Challenges in Uganda and East Africa", "Regional and International Cooperation (EAC, AU, UN)"],
        "S5": ["Advanced History of East Africa (1840 to Present)", "Themes in African History (Late 19th Century to Post-Independence)"],
        "S6": ["Modern World History (The World Since 1870)", "The Cold War Era, International Alliances, and Post-Cold War Global Dynamics"]
    },
    "CRE": {
        "S1": ["God's Creation and Human Talents", "The Fall of Man and God's Plan of Salvation", "Introduction to Abrahamic Faith and Covenant"],
        "S2": ["The Leadership of Prophets and Kings in Israel", "The Exodus Experience and God's Guidance", "The Life, Ministry, and Teachings of Jesus Christ"],
        "S3": ["The Teachings of Jesus (Parables and Miracles)", "The Early Church and the Spread of Christianity", "Christian Discipleship, Community Service, and Witnessing"],
        "S4": ["Christian Living and Personal Values (Work, Leisure, Justice)", "Courtship, Marriage, and Family in Modern Society", "Contemporary Moral, Ethical, and Social Integrity Challenges"],
        "S5": ["Advanced Church History and Doctrinal Development", "Christian Ethics and Systematic Moral Theology"],
        "S6": ["Christianity in Modern Africa", "Comparative Theology and Inter-Faith Relations (World Religions)"]
    },
    "ICT": {
        "S1": ["Introduction to ICT Services and Information Literacy", "Computer Hardware, Software, and Architecture", "Introduction to Word Processing"],
        "S2": ["Electronic Spreadsheets (Data Formatting and Calculations)", "Electronic Presentation Applications (Design and Communication)", "Digital Media, Graphics and Creative Audio Production"],
        "S3": ["The Internet, World Wide Web, and Electronic Communication (Emails)", "Web Design Technologies (HTML/CSS Foundations and Management)", "Computer Networking Architecture and Hardware Setups"],
        "S4": ["Introduction to Information Systems and Database Management", "Data Security, Computer Ethics, Privacy, and Emerging Trends", "Project-Based Practical Integration Portfolio"],
        "S5": ["Advanced Database Management Systems", "Fundamentals of Programming, Algorithms, and Software Development"],
        "S6": ["Artificial Intelligence Foundations and Machine Learning Concepts", "Cybersecurity Protocols, Systems Auditing, and Data Analytics"]
    },
    "Entrepreneurship": {
        "S1": ["Introduction to Entrepreneurship and Creative Innovation", "Characteristics and Mindsets of Successful Entrepreneurs", "Generating and Screening Viable Business Ideas"],
        "S2": ["Market Research, Customer Segmentation, and Marketing Mix", "Business Operations, Production Planning, and Quality Management", "E-Commerce and Digital Business Strategies"],
        "S3": ["Financial Literacy, Bookkeeping, and Basic Business Accounting", "Sources of Business Finance, Capitalization, and Budgeting", "Business Planning, Resource Mobilization, and Structural Setup"],
        "S4": ["Business Management, Leadership Dynamics, and Ethics", "Legal Frameworks, Business Formations, and Taxation Systems in Uganda", "School-Based Practical Enterprise Project Evaluation"],
        "S5": ["Advanced Enterprise Project Design and Project Management Plans", "Corporate Governance, Strategic Management, and Business Environment Dynamics"],
        "S6": ["Global Business Innovation, Risk Management, and Financial Analysis", "Investment Portfolios, Stock Markets, and Sustainable Wealth Creation"]
    },
    "Art": {
        "S1": ["Foundations of Art and Elements of Design (Line, Tone, Color)", "Still Life and Nature Drawing Techniques", "Basic Pattern Design and Structural Craftwork"],
        "S2": ["Techniques of Painting and Color Mixing Theories", "Human Anatomy Drawing and Life Sketching", "Graphic Design and Creative Visual Communication"],
        "S3": ["Introduction to Sculpture, Carving, and Modelling", "Fabric Decoration (Tie-Dye, Batik, Printing)", "Ceramics, Pottery, and Form Formation"],
        "S4": ["Advanced Practical Presentation and Exhibition Layouts", "History of East African Art and Cultural Heritage Appreciation", "Final Creative Arts Exhibition Portfolio Assessment"],
        "S5": ["Advanced Fine Art Studio Practicum (Life, Still-Life, Nature)", "Advanced Creative Graphic Design and Spatial Typography"],
        "S6": ["Advanced Theoretical Appreciations of World Art History", "Professional Portfolio Development and Curatorial Execution Protocols"]
    },
    "Music": {
        "S1": ["Fundamentals of Music Notation, Pitch, and Rhythm", "Aural Training and Sight-Reading Exercises", "Introduction to Ugandan Traditional Musical Forms"],
        "S2": ["Classification and Execution of Western and African Instruments", "Choral Performance, Ensemble Playing, and Vocal Technique", "Introduction to Musical Scale Constructions (Major and Minor)"],
        "S3": ["Intermediate Music Theory (Intervals, Transposition, Harmony)", "Principles of Melodic Composition and Creative Songwriting", "Traditional Folk Song Arrangement and Musical Scriptwriting"],
        "S4": ["Advanced Harmonic Analysis and Part-Writing Dynamics", "History of Western Music and Evolution of Contemporary Popular Forms", "Final Ensemble Performance, Conducting, and Recital Assessments"],
        "S5": ["Advanced Western Music Analysis and Structural Composition Theory", "Advanced African Ethnomusicology Research Frameworks"],
        "S6": ["Advanced Performance Virtuosity and Instrumental Recitals", "Music Technology, Digital Sequencing, Scoring, and Sound Engineering"]
    },
    "Luganda": {
        "S1": ["Ennukuta, Enkyukakyuka mu Mpandiika n'Ebigambo", "Okusoma n'Okuwandiika Empandiika Entongole (Orthography)", "Ebitontome n'Engero ez'Olulyo"],
        "S2": ["Emisoso gy'Ebiwandiiko (Ebbaluwa, Emboozi, n'Ezisanyusa)", "Emiyungo, Amannya, n'Obusirikitu mu Lulimi", "Emizannyo n'Emisoso gy'Okuzina Ekiganda"],
        "S3": ["Ennono, Ennyimba n'Emizannyo gy'Abalere n'Abaana", "Engero ez'Enfumo n'Ebisoko mu Lulimi Oluganda", "Okusembya n'Okuvvuunula Ebiwandiiko eby'Enjawulo"],
        "S4": ["Ebyafaayo by'Oluganda, Olubiri, n'Ebuwangwa", "Okwekenneenya Obuwandiike bw'Ebitabo eby'Oluganda", "Okutegeka Emboozi y'Akafananyi n'Okusunsula Ebiwandiiko"],
        "S5": ["Obuwandiike bw'Oluganda Obw'Omulembe n'Obw'Ennono Okutwalizaamu", "Ennimi z'Abantu, Amakulu G'Ebigambo (Semantics) n'Empandiika Ennyonnyoli"],
        "S6": ["Ekinyankulizi, Okusembya n'Okuvvuunula ku Mutindo gw'Okuntikko", "Okwekenneenya Okw'Okuntikko okw'Ebitabo n'Emizannyo gy'Oluganda"]
    },
    "Kiswahili": {
        "S1": ["Alfabeti ya Kiswahili, Matamshi na Tahajia Sahihi", "Aina za Maneno na Miundo ya Sentensi Rahisi", "Mazungumzo, Salamu na Utambulisho wa Awali"],
        "S2": ["Sarufi ya Kiswahili (Ngeli za Nomino na Unyambulishaji)", "Uandishi wa Insha na Barua (Zikiwemo za Kiofisi)", "Ufahamu na Ufupisho wa Maandishi Mbalimbali"],
        "S3": ["Fasihi Simulizi (Hadithi, Methali, Vitendawili, na Nyimbo)", "Uandishi wa Insha za Kitaaluma na Ripoti", "Uchambuzi wa Magazeti, Habari na Mawasiliano katika Jamii"],
        "S4": ["Fasihi Andishi (Uchambuzi wa Riwaya, Tamthilia na Ushairi)", "Tafsiri ya Matini na Ukalimani wa Msingi", "Maandalizi ya Mtihani na Mikakati ya Mawasiliano ya Kimataifa"],
        "S5": ["Sarufi Ngumu na Fasihi ya Kiswahili kwa Kiwango cha Juu", "Nadharia za Tafsiri na Ukalimani wa Kitaalamu"],
        "S6": ["Uchambuzi wa Kina wa Kazi za Fasihi na Uhakiki", "Ukuaji wa Kiswahili, Lugha za Kibantu na Isimu Jamii"]
    }
}
### 6. PRACTICAL_DATABASE - UPDATED WITH YOUR FULL LIST + AOI LOGIC ###
PRACTICAL_DATABASE = {
    "Physics": {
        "S1-S4": {
            "Measurements & Density": {"objective": "Determine density of regular and irregular solids using local materials and displacement methods."},
            "Mechanics (Hooke's Law)": {"objective": "Verify Hooke's Law using local extension springs and determine the spring constant."},
            "Mechanics (Moments)": {"objective": "Verify the principle of moments using a meter rule pivot setup."},
            "Heat Transfer": {"objective": "Investigate mechanisms of conduction, convection, and radiation using everyday school items."},
            "Light (Reflection)": {"objective": "Verify laws of reflection and determine the position of virtual images in plane mirrors."},
            "Light (Refraction)": {"objective": "Determine the refractive index of a glass block using pin-tracing methods."},
            "Current Electricity": {"objective": "Construct simple series and parallel circuits; verify Ohm's Law using ammeters and voltmeters."},
            "Waves & Sound": {"objective": "Determine the speed of sound in air using resonant tuning forks and air columns."},
            "Activities of Integration (AOI)": {"objective": "Design a functional solar cooker or simple water heater using locally sourced insulative materials."}
        },
        "S5-S6": {
            "Advanced Mechanics": {"objective": "Determine the acceleration due to gravity (g) using a simple pendulum and a rigid bar pendulum with error analysis."},
            "Surface Tension & Viscosity": {"objective": "Determine the coefficient of viscosity of a liquid using terminal velocity of a falling sphere."},
            "Advanced Optics (Lenses)": {"objective": "Determine the focal length of convex lenses and concave mirrors using u-v and displacement methods."},
            "Advanced Optics (Prism)": {"objective": "Determine the refractive index of glass using a spectrometer or pin-tracing through a triangular prism."},
            "Advanced Electricity (Potentiometer)": {"objective": "Measure internal resistance of a cell and calibrate an ammeter using a potentiometer wire setup."},
            "Advanced Electricity (Bridge Circuits)": {"objective": "Determine unknown resistance and temperature coefficient of resistance using a Metre Bridge."},
            "RC Circuits": {"objective": "Investigate the charging and discharging of a capacitor to calculate the circuit time constant."},
            "Magnetic Fields": {"objective": "Determine the horizontal component of the Earth's magnetic field using a deflection magnetometer."}
        }
    },
    "Chemistry": {
        "S1-S4": {
            "Separation of Mixtures": {"objective": "Separate components of sand, salt, and ink using filtration, evaporation, and simple paper chromatography."},
            "States of Matter": {"objective": "Investigate heating and cooling curves of naphthalene or water to establish melting and boiling points."},
            "Acids, Bases & Indicators": {"objective": "Prepare a natural pH indicator from red cabbage or plant flower extracts and test household solutions."},
            "Volumetric Analysis (Introductory)": {"objective": "Perform basic acid-base titrations using hydrochloric acid and sodium hydroxide with phenolphthalein."},
            "Rates of Reaction": {"objective": "Investigate the effect of concentration and temperature changes on the reaction rate between sodium thiosulfate and hydrochloric acid."},
            "Chemical Tests for Gases": {"objective": "Produce and identify oxygen, hydrogen, and carbon dioxide gases using charcoal, splints, and limewater."},
            "Activities of Integration (AOI)": {"objective": "Develop a small-scale prototype filter to treat turbid/hard water from local community sources."}
        },
        "S5-S6": {
            "Volumetric Quantitative Analysis": {"objective": "Perform double titrations, back titrations, and redox titrations using KMnO4, Fe2+ salts, and sodium thiosulfate iodine systems."},
            "Qualitative Inorganic Analysis": {"objective": "Systematically identify cations and anions via semi-micro analysis."},
            "Thermochemistry": {"objective": "Determine the enthalpy of neutralization of an acid-base reaction and enthalpy of displacement of copper by zinc."},
            "Chemical Kinetics": {"objective": "Determine the order of reaction and activation energy for the reaction between hydrogen peroxide and iodide ions."},
            "Equilibrium & Partition Coefficient": {"objective": "Determine the partition coefficient of ethanoic acid or iodine between water and an organic solvent."}
        }
    },
    "Biology": {
        "S1-S4": {
            "Microscopy & Cell Observation": {"objective": "Prepare temporary wet mounts of onion epidermal cells and human cheek cells to observe under a light microscope."},
            "Food Tests": {"objective": "Perform qualitative tests for reducing sugars, starch, proteins, and lipids."},
            "Enzyme Action": {"objective": "Investigate the effect of temperature and catalase concentrations on the breakdown of hydrogen peroxide."},
            "Cell Physiology (Osmosis)": {"objective": "Demonstrate living osmosis using Irish potato cups immersed in varying concentrations of salt/sugar solutions."},
            "Plant & Animal Morphology": {"objective": "Examine, draw, and label external features of insects, lower plants, and simple flowers."},
            "Soil Ecology": {"objective": "Determine soil water-holding capacity, drainage rates, and organic matter content from different school garden plots."},
            "Activities of Integration (AOI)": {"objective": "Create an illustrated public health guide detailing how to break transmission vectors for local infectious pathogens."}
        },
        "S5-S6": {
            "Biological Dissections": {"objective": "Dissect, display, and draw the internal systems of a small mammal or amphibian."},
            "Advanced Plant Anatomy": {"objective": "Cut thin transverse sections of monocotyledonous and dicotyledonous stems/roots; stain and observe vascular bundles."},
            "Advanced Biochemistry & Food Tests": {"objective": "Quantitatively estimate vitamin C concentration or evaluate complex food mixtures using serial dilutions."},
            "Physiology (Respiration & Photosynthesis)": {"objective": "Measure the rate of respiration using a simple respirometer and demonstrate oxygen production during plant photosynthesis."},
            "Histological Slide Identification": {"objective": "Identify, draw, and annotate micro-anatomical structures from prepared slides."}
        }
    },
    "Agriculture": {
        "S1-S4": {
            "Farm Tools Identification": {"objective": "Identify, state the functions of, and practice routine maintenance on hand tools and farm implements."},
            "Physical & Chemical Soil Testing": {"objective": "Determine soil texture by feel, calculate soil moisture content, and measure pH using a universal indicator."},
            "Crop Agronomy (Nursery Bed Management)": {"objective": "Prepare, sow, water, weed, and prick out vegetables on a school garden nursery bed."},
            "Livestock Management Exercises": {"objective": "Identify common animal feeds, identify internal/external parasites, and practice basic poultry management steps."},
            "DIT Vocational Assessment Practice": {"objective": "Execute hands-on husbandry competencies aligned with Level 1 Directorate of Industrial Training requirements."},
            "Activities of Integration (AOI)": {"objective": "Develop a farm record-keeping framework and design a seasonal crop rotation plan for a specific plot of community land."}
        },
        "S5-S6": {
            "Advanced Soil Science Analysis": {"objective": "Quantitatively measure soil cation exchange capacity, total nitrogen, phosphorus levels, and mechanical soil fraction analysis."},
            "Agronomic Field Trials": {"objective": "Set up and track a controlled field experiment comparing crop yield responses under organic vs. inorganic fertilizer treatments."},
            "Animal Nutrition & Feed Formulation": {"objective": "Analyze components of animal feeding stuffs and compute balanced livestock rations using Pearson's Square method."},
            "Agricultural Engineering & Mechanisation": {"objective": "Analyze the mechanics, cooling, and fuel systems of a farm tractor engine and evaluate modern drip irrigation mechanics."},
            "Farm Economics & Management Portfolio": {"objective": "Construct balance sheets, profit & loss statements, production functions, and complete an agricultural field study research report."}
        }
    }
}

### 7. LIGHT RAG WITH SOURCE TRACKING ###
class VectorRAG:
    def __init__(self): self.docs=load_db(DOCS_FILE,[])
    def add(self,texts,fn):
        for i,t in enumerate(texts): self.docs.append({"src":fn,"chunk_id":i,"txt":t[:1200]})
        save_db(DOCS_FILE,self.docs)
    def search(self,q,k=3):
        qw=set(q.lower().split()); scored=[(len(qw&set(d['txt'].lower().split())),d) for d in self.docs]
        return [d for s,d in sorted(scored,reverse=True)[:k] if s>0]
vector_rag=VectorRAG()

def chunk_text(text, sz=500):
    s = re.split(r'(?<=[.!?]) +', text); chunks = []; cur = ""
    for x in s:
        if len(cur) + len(x) < sz: cur += x + " "
        else: chunks.append(cur); cur = x
    if cur: chunks.append(cur)
    return chunks

def render_upload(key="d"):
    f=st.file_uploader("Upload PDF/DOCX/TXT",type=["pdf","docx","txt"],key=key)
    if f:
        text=""
        try:
            if f.name.endswith(".pdf"): from pypdf import PdfReader; text="".join([p.extract_text() or "" for p in PdfReader(f).pages])
            elif f.name.endswith(".docx"): from docx import Document; text="\n".join([p.text for p in Document(f).paragraphs])
            else: text=f.getvalue().decode("utf-8")
        except Exception as e: st.error(e); return
        if st.button(f"Add {len(chunk_text(text))} chunks",key=f"add{key}"):
            vector_rag.add(chunk_text(text),f.name); st.success(f"Added to RAG from {f.name}")

### 8. LEVEL-SMART BRAIN WITH NCDC 2026 FRAMEWORK ###
def get_level_rules(level):
    rules = {
        "S1": "Competence: Basic knowledge. Use simple language. 2-3 points. Real life UG examples. Activity of Integration style.",
        "S2": "Competence: Understanding. 3-4 points. Introduce terms. 1 UG scenario. Basic calculations.",
        "S3": "Competence: Skill Application. 4-5 points. Diagrams. 2 UG examples. Problem solving.",
        "S4": "Competence: Values & Attitudes. UNEB Scenario->Item->Task format. 5-6 points. Context-rich problems.",
        "S5": "A-Level: Analysis. 6-8 points. Derivations, case studies, critical thinking. Paper 1 & 2 split.",
        "S6": "A-Level: Synthesis & Evaluation. 8-10 points. University prep. Research, evaluation, complex modeling."
    }
    return rules.get(level, rules["S4"])

SYSTEM_PROMPT="""You are Senior NCDC Uganda Examiner 2026. CRITICAL RULES:
1. ANTI-HALLUCINATION: Only use CONTEXT and official NCDC topics. If not in CONTEXT say 'Per NCDC 2026 CBC I cant confirm'.
2. LEVEL LOCK: Follow LEVEL_RULES strictly. S1≠S2≠S3≠S4≠S5≠S6. Never teach S6 content to S1.
3. ASSESSMENT: For S1-S4 use Scenario-Item-Task + AOI format. For S5-S6 use Paper1 Paper2 competency frame.
4. PRACTICALS: If asked practical, use PRACTICAL_DATABASE objectives. Emphasize local materials and competency.
5. FORMAT: **Concept**:X **UG Example**:Y **Exam Tip**:Z.
6. CITATION: At end add **Sources**: [filename chunk#] **Level**: {level}
7. UG: Use Kampala,matooke,boda,busoga,nile,health center examples."""

def call_groq_os(prompt,level="S4",mode="smart"):
    global SYS_STATE; SYS_STATE=system_check()
    sources=vector_rag.search(prompt,3)

    if not SYS_STATE["online"]:
        if sources: ctx=chr(10).join([f"[{r['src']} c{r['chunk_id']}] {r['txt'][:300]}" for r in sources])
        else: ctx="";
        return (f"[OFFLINE] Based on NCDC notes:\n{ctx}", sources) if ctx else ("[OFFLINE] Upload NCDC notes first", [])

    level_rules = get_level_rules(level)
    force_short=any(w in prompt.lower() for w in ["define","state","brief","quiz","1 mark"])

    if mode=="research_s5s6": tokens=1800; use_long=True
    elif mode=="research_s1s4": tokens=800; use_long=False
    elif mode=="notes" or mode=="exam" or "practical" in prompt.lower(): tokens=1500; use_long=True
    elif force_short: tokens=400; use_long=False
    else: tokens=1000; use_long=int(level[1])>=5

    cached=ai_cache.get(prompt+mode+level);
    if cached: return f"[CACHED] {cached}", sources

    context="\n".join([f"[{r['src']} c{r['chunk_id']}] {r['txt']}" for r in sources])
    full=f"{SYSTEM_PROMPT}\nLEVEL:{level}\nLEVEL_RULES:{level_rules}\nMODE:{mode}\nCONTEXT:\n{context}\nTASK:{prompt}"

    model=AI_MODEL_LONG if use_long else AI_MODEL_SHORT
    try:
        res=client.chat.completions.create(model=model,messages=[{"role":"user","content":full}],max_tokens=tokens,temperature=0.1)
        ans=res.choices[0].message.content
        if sources: src_line = "**Sources**: " + ", ".join([f"{r['src']} c{r['chunk_id']}" for r in sources])
        else: src_line = "**Sources**: NCDC 2026 CBC Master Syllabus"
        ans = ans + "\n\n" + src_line + f"\n**Level**: {level} | **Curriculum**: NCDC 2026 CBC"
        ai_cache.set(prompt+mode+level,ans)
        save_db(LOG_FILE,load_db(LOG_FILE,[])+[{"time":str(datetime.now()),"q":prompt[:30],"level":level,"model":model}])
        return ans, sources
    except Exception as e: return f"[AUTO-FIX] Error: {e}. Try again", sources

def display_preview(content,name):
    st.text_area("AI Output - EDIT",content,height=400,key=f"p{name}")
    st.download_button("📥 Download TXT",content.encode(),f"{name}.txt")

def get_topics(s,l): return UNEB_CURRICULUM_MAP.get(s,{}).get(l,["General Topic"])

def get_practicals(s,l):
    g = "S1-S4" if int(l[1])<=4 else "S5-S6"
    return list(PRACTICAL_DATABASE.get(s,{}).get(g,{}).keys())

### 9. STUDENT PORTAL ###
def show_student():
    st.header("📚 Student Portal")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    t1,t2,t3,t4,t5=st.tabs(["🔍 Smart Search","📖 Learn + Notes","🧪 Practicals","🖼️ Diagrams","🔬 Research"])

    with t1:
        render_upload("s1"); s=st.selectbox("Subject",list(UNEB_CURRICULUM_MAP),key="s1s"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="s1l"); q=st.text_area("Ask Anything",placeholder=f"AI answers at {l} NCDC level",key="s1q")
        c1,c2,c3=st.columns(3)
        if c1.button("Ask AI",key="s1b") and q: a,src=call_groq_os(q,l,"smart"); display_preview(a,"s1")
        if c2.button("Scenario Task",key="s1t") and q: a,src=call_groq_os(f"Create Scenario->Item->Task question on {q} for {l} {s}",l,"smart"); display_preview(a,"s1t")
        if c3.button("Quick 5Q Quiz",key="s1quiz") and q: a,src=call_groq_os(f"Generate 5 short quiz questions + answers on {q} for {l} {s} per NCDC",l,"quiz"); display_preview(a,"s1quiz")

    with t2:
        render_upload("s2"); s=st.selectbox("Subject",list(UNEB_CURRICULUM_MAP),key="s2s"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="s2l"); t=st.selectbox("Topic",get_topics(s,l),key="s2t")
        c1,c2,c3=st.columns(3)
        if c1.button("NCDC Notes",key="s2b"): a,src=call_groq_os(f"Detailed NCDC notes on {t} for {l} {s}. Follow 2026 syllabus depth",l,"notes"); display_preview(a,"s2")
        if c2.button("Ask About Topic",key="s2q"): a,src=call_groq_os(f"Explain {t} for {l} {s} using NCDC competency",l,"smart"); display_preview(a,"s2q")
        if c3.button("Topic Quiz 10Q",key="s2quiz"): a,src=call_groq_os(f"Generate 10 UNEB style questions + marking guide on {t} for {l} {s}",l,"quiz"); display_preview(a,"s2quiz")

    with t3:
        render_upload("s3"); s=st.selectbox("Subject",list(PRACTICAL_DATABASE),key="s3s"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="s3l"); p=st.selectbox("Practical",get_practicals(s,l),key="s3p")
        c1,c2=st.columns(2)
        if c1.button("Generate Practical",key="s3b") and p:
            g="S1-S4" if int(l[1])<=4 else "S5-S6"
            obj=PRACTICAL_DATABASE[s][g][p]['objective']
            a,src=call_groq_os(f"Full NCDC practical write-up for {p}. Objective: {obj}. Include: Apparatus, Method, Observations, Calculations, Precautions, Conclusion. Use local materials. Level: {l}",l,"notes"); display_preview(a,"s3")
        if c2.button("Ask About Practical",key="s3q") and p: a,src=call_groq_os(f"Explain {p} practical for {l} per NCDC. Safety and AOI tips",l,"smart"); display_preview(a,"s3q")

    with t4:
        render_upload("s4"); s=st.selectbox("Subject",list(UNEB_CURRICULUM_MAP),key="s4s"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="s4l"); t=st.selectbox("Topic",get_topics(s,l),key="s4t")
        c1,c2,c3=st.columns(3)
        if c1.button("Generate Diagrams",key="s4b"): a,src=call_groq_os(f"2 diagrams JSON + description for {l} {s} '{t}' NCDC example",l,"smart"); display_preview(a,"s4")
        if c2.button("Ask About Diagram",key="s4q"): a,src=call_groq_os(f"How to draw and label diagram for {t} in {s} {l}",l,"smart"); display_preview(a,"s4q")
        if c3.button("Diagram Quiz",key="s4quiz"): a,src=call_groq_os(f"5 quiz questions on labeling {t} diagram for {l} {s}",l,"quiz"); display_preview(a,"s4quiz")

    with t5:
        st.subheader("Research Projects")
        render_upload("s5"); s=st.selectbox("Subject",list(UNEB_CURRICULUM_MAP),key="s5s"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="s5l")
        if int(l[1]) >= 5:
            st.info("🎓 ADVANCED LEVEL RESEARCH: S5-S6. University style, citations, Paper1+Paper2")
            rq=st.text_area("Research Topic",placeholder="e.g. Applications of Differentiation in Drone Logistics",key="s5rq")
            if st.button("Generate Research Project",key="s5rb") and rq:
                a,src=call_groq_os(f"Full NCDC research project on {rq} for {l} {s}. Include: Background, Methodology, Analysis, Conclusion, References. 1200 words",l,"research_s5s6"); display_preview(a,"s5res")
        else:
            st.info("📚 LOWER SECONDARY RESEARCH: S1-S4. Basic queries, Scenario + AOI based")
            rq=st.text_area("Research Query",placeholder="e.g. Heat transfer in solar refrigeration",key="s5rq2")
            if st.button("Find Basic Info",key="s5rb2") and rq:
                a,src=call_groq_os(f"Research and summarize {rq} for {l} {s}. Simple language, Scenario-Item-Task + AOI, 3-5 key points",l,"research_s1s4"); display_preview(a,"s5res2")

### 10. ADMIN PORTAL ###
def show_admin():
    st.header("🏫 Admin Portal")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tabs=st.tabs(["📊 Analytics","📖 Curriculum","🧪 Practicals","📤 Bulk","📚 RAG KB","📝 Lesson","📄 Reports","📈 Predictive","📝 Exams"])

    with tabs[0]:
        st.subheader("Analytics"); q=st.text_area("Ask about analytics",key="aq");
        if st.button("Ask",key="ab"): a,src=call_groq_os(f"Analyze this: {q}", "S4"); display_preview(a,"a")

    with tabs[1]:
        st.subheader("NCDC Curriculum"); s=st.selectbox("Subject",list(UNEB_CURRICULUM_MAP),key="as"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="al"); t=st.multiselect("Topics",get_topics(s,l))
        if st.button("Generate Scheme"): a,src=call_groq_os(f"NCDC Term Scheme for {l} {s} {t}. 2026 CBC with AOI",l,"notes"); display_preview(a,"scheme")
        if st.button("Ask Curriculum"): a,src=call_groq_os(f"How to teach {s} {l} per NCDC 2026",l); display_preview(a,"ac")

    with tabs[2]:
        st.subheader("Practicals"); s=st.selectbox("Subject",list(PRACTICAL_DATABASE),key="ps"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="pl"); p=st.selectbox("Practical",get_practicals(s,l),key="pp")
        if st.button("Generate Practical Guide"):
            g="S1-S4" if int(l[1])<=4 else "S5-S6"
            obj=PRACTICAL_DATABASE[s][g][p]['objective']
            a,src=call_groq_os(f"Generate full lab manual for {p}. Objective: {obj}. Level: {l}",l,"notes"); display_preview(a,"pg")
        q=st.text_area("Ask about any practical",key="pq")
        if st.button("Ask"): a,src=call_groq_os(q,"S4"); display_preview(a,"p")

    with tabs[3]:
        st.subheader("Bulk"); s=st.selectbox("Subject",list(UNEB_CURRICULUM_MAP),key="bs"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="bl"); t=st.multiselect("Topics",get_topics(s,l)); n=st.slider("Qs",10,100,50);
        if st.button("Generate"): a,src=call_groq_os(f"Generate {n} NCDC 2026 Qs + Marking guide from {t} for {l} {s}",l,"notes"); display_preview(a,"bulk")
        if st.button("Ask"): a,src=call_groq_os(f"Ideas for setting {s} paper {l}",l); display_preview(a,"abk")

    with tabs[4]:
        st.subheader("RAG KB"); st.metric("Chunks",len(vector_rag.docs)); render_upload("a5")
        q=st.text_area("Ask RAG",key="ragq")
        if st.button("Ask RAG"): a,src=call_groq_os(q,"S4"); display_preview(a,"rag")
        if st.button("Reset RAG"): vector_rag.docs=[]; save_db(DOCS_FILE,[]); st.success("Reset")

    with tabs[5]:
        st.subheader("Lesson"); s=st.selectbox("Subject",list(UNEB_CURRICULUM_MAP),key="ls"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="ll"); t=st.selectbox("Topic",get_topics(s,l),key="lt")
        if st.button("NCDC Lesson Plan"): a,src=call_groq_os(f"NCDC 40min Lesson Plan {l} {s} {t}. Competencies,Activities,Assessment,AOI,UG example",l,"notes"); display_preview(a,"lesson")
        if st.button("Ask"): a,src=call_groq_os(f"Teaching tips for {t} {l}",l); display_preview(a,"al")

    with tabs[6]:
        st.subheader("Reports"); n=st.number_input("Students",1,1000,100)
        if st.button("Report Cards"): a,src=call_groq_os(f"Generate {n} NCDC Report Cards with competencies and comments","S4","notes"); display_preview(a,"report")
        q=st.text_area("Custom Report Task",key="rq")
        if st.button("Ask"): a,src=call_groq_os(q,"S4"); display_preview(a,"ar")

    with tabs[7]:
        st.subheader("📈 Predictive"); st.metric("Status","Online" if SYS_STATE["online"] else "Offline")
        q=st.text_area("Ask Predictor",key="prq")
        if st.button("Ask"): a,src=call_groq_os(q,"S4"); display_preview(a,"pr")

    with tabs[8]:
        st.subheader("📝 NCDC Exam + Test Generator")
        s=st.selectbox("Subject",list(UNEB_CURRICULUM_MAP),key="exs"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="exl"); t=st.multiselect("Topics",get_topics(s,l))
        c1,c2,c3=st.columns(3)
        if c1.button("Full Exam 100mks"): a,src=call_groq_os(f"Generate full NCDC 2026 exam 100 marks for {l} {s} on {t}. Scenario-Item-Task + AOI format + Marking guide",l,"exam"); display_preview(a,"exam")
        if c2.button("CAT 30mks"): a,src=call_groq_os(f"Generate 30 marks NCDC CAT for {l} {s} on {t}. 1hr + Marking guide",l,"exam"); display_preview(a,"cat")
        if c3.button("Pop Quiz 10mks"): a,src=call_groq_os(f"Generate 10 marks NCDC pop quiz for {l} {s} on {t}. 20min",l,"quiz"); display_preview(a,"quiz")
        custom=st.text_area("Custom Exam Task",placeholder="e.g. Make AOI for Physics S2 Machines")
        if st.button("Generate Custom"): a,src=call_groq_os(custom,l,"exam"); display_preview(a,"custom")

### 10. LOGIN ###
st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO V6.1.6")
with st.sidebar:
    st.metric("RAM",f"{psutil.virtual_memory().percent}%"); st.metric("Internet","Online" if SYS_STATE["online"] else "Offline")
    pw=st.text_input("Password",type="password")
    c1,c2=st.columns(2)
    if c1.button("Student") and pw==STUDENT_PASSWORD: st.session_state.role="Student"; st.rerun()
    if c2.button("Admin") and pw==ADMIN_PASSWORD: st.session_state.role="Admin"; st.rerun()
if st.session_state.get("role")=="Admin": show_admin()
elif st.session_state.get("role")=="Student": show_student()
else: st.info("Login to continue")
