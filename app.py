from difflib import SequenceMatcher
import streamlit as st, os, io, json, re, time, requests, random, threading, psutil, socket, hashlib
from datetime import datetime
from groq import Groq, RateLimitError
import logging
logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 PRO", page_icon="📚", layout="wide")
st.sidebar.caption("Build: V6.1.2-CHATGPT-SMART | NCDC COMPLIANT | 512MB SAFE")

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

### 5. NCDC CURRICULUM - FIXED: ADDED ALL CLASSES FOR ALL SUBJECTS ###
UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Sets","Number Bases"],"S2": ["Rates","Algebra"],"S3": ["Quadratics","Trigonometry"],"S4": ["Functions","Matrices"],"S5": ["Differentiation","Integration"],"S6": ["Mechanics II","Statistics III"]},
    "Physics": {"S1": ["Measurement","Forces"],"S2": ["Pressure","Energy"],"S3": ["Light","Waves I"],"S4": ["Electronics","Waves II"],"S5": ["Fields I","Current"],"S6": ["Electric Fields","Nuclear Physics II"]},
    "Chemistry": {"S1": ["Intro","Lab"],"S2": ["Acids","Bases"],"S3": ["Bonding","Organic I"],"S4": ["Mole","Energetics"],"S5": ["Kinetics III","Organic II"],"S6": ["Equilibrium","Industrial"]},
    "Biology": {"S1": ["Cells","Classification"],"S2": ["Nutrition","Respiration"],"S3": ["Excretion","Reproduction"],"S4": ["Photosynthesis","Hormones I"],"S5": ["Coordination","Immunity"],"S6": ["Biotechnology II","Genetics IV"]},
    "Agriculture": {"S1": ["Soil Formation","Crops"],"S2": ["Livestock","Tools"],"S3": ["Weeds","Pests"],"S4": ["Crop Protection","Farm Management"],"S5": ["Agroforestry","Irrigation"],"S6": ["Agribusiness","Research"]},
    "Geography": {"S1": ["Map Reading","Weather"],"S2": ["Rocks","Rivers"],"S3": ["Climate","Vegetation"],"S4": ["GIS","Population Structure"],"S5": ["Industry","Trade"],"S6": ["Settlement","Env Issues"]},
    "History": {"S1": ["Early Man","Bantu Migrations"],"S2": ["Iron Age","Kingdoms"],"S3": ["Colonialism","Resistance"],"S4": ["OAU","Human Rights"],"S5": ["Cold War","Decolonization"],"S6": ["Uganda Since 1962","Global Issues"]},
    "Literature": {"S1": ["Oral Literature","Poetry"],"S2": ["Novel","Drama"],"S3": ["Prose","Shakespeare"],"S4": ["African Literature"],"S5": ["Set Books","Criticism"],"S6": ["Advanced Drama","Literary Theory"]},
    "CRE": {"S1": ["God and Man","Creation"],"S2": ["Prophets","Exodus"],"S3": ["Gospels","Parables"],"S4": ["Christian Living"],"S5": ["Church History","Ethics"],"S6": ["Theology","World Religions"]},
    "ICT": {"S1": ["Computer Basics","Word"],"S2": ["Excel","PowerPoint"],"S3": ["Internet","Email"],"S4": ["Web Design","Networking"],"S5": ["Databases","Programming"],"S6": ["AI","Cybersecurity"]},
    "Entrepreneurship": {"S1": ["Business Ideas"],"S2": ["Marketing"],"S3": ["Finance"],"S4": ["Management","Law"],"S5": ["Project"],"S6": ["Innovation"]},
    "Art": {"S1": ["Drawing","Color"],"S2": ["Painting"],"S3": ["Sculpture"],"S4": ["Design"],"S5": ["Craft"],"S6": ["Portfolio"]},
    "Music": {"S1": ["Notes","Rhythm"],"S2": ["Instruments"],"S3": ["Theory"],"S4": ["Composition"],"S5": ["History"],"S6": ["Performance"]},
    "Luganda": {"S1": ["Ebigambo","Ennukuta"],"S2": ["Ebiwandiiko"],"S3": ["Ennono"],"S4": ["Ebyafaayo"],"S5": ["Ebitontome"],"S6": ["Ekinyankulizi"]},
    "Kiswahili": {"S1": ["Alfabeti","Maneno"],"S2": ["Sarufi"],"S3": ["Insha"],"S4": ["Fasihi"],"S5": ["Tafsiri"],"S6": ["Uchambuzi"]}
}
PRACTICAL_DATABASE = {"Physics": {"S1-S4": {"Ohm's Law": {"objective": "Verify Ohm's Law"}},"S5-S6": {"RC Circuit": {"objective": "Find time constant"}}},"Chemistry": {"S1-S4": {"Titration": {"objective": "Determine HCl"}},"S5-S6": {"Rate": {"objective": "Order of reaction"}}},"Biology": {"S1-S4": {"Microscope": {"objective": "Observe cells"}},"S5-S6": {"Enzyme": {"objective": "Effect of pH"}}},"Agriculture": {"S1-S4": {"Soil pH": {"objective": "Determine pH"}},"S5-S6": {"Feed": {"objective": "Formulate feed"}}}}

### 6. LIGHT RAG ###
class VectorRAG:
    def __init__(self): self.docs=load_db(DOCS_FILE,[])
    def add(self,texts,fn):
        for t in texts: self.docs.append({"src":fn,"txt":t[:1200]})
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
            vector_rag.add(chunk_text(text),f.name); st.success("Added to RAG")

### 7. SMART CHATGPT CALLER - NEW ###
SYSTEM_PROMPT="""You are Senior NCDC Uganda Tutor + ChatGPT. Rules:
1. ANTI-HALLUCINATION: If not in CONTEXT say 'Per NCDC I cant confirm'.
2. SMART MODE: Detect intent. 'define'=2 sentences. 'explain/discuss'=6 points+2 UG examples. 'notes'=in-depth 800 words with headings.
3. FORMAT: **Concept**:X **UG Example**:Y **Exam Tip**:Z.
4. UG: Use Kampala,matooke,boda,busoga,nile examples.
5. ALL SUBJECTS: Math, Physics, Chem, Bio, Agric, Geo, History, Lit, CRE, ICT, Ent, Art, Music, Luganda, Kiswahili"""

def call_groq_os(prompt,level="S4",mode="smart"):
    global SYS_STATE; SYS_STATE=system_check()
    if not SYS_STATE["online"]:
        res=vector_rag.search(prompt,3);
        return (f"[OFFLINE] Based on school notes:\n{chr(10).join([r['txt'][:400] for r in res])}",res) if res else ("[OFFLINE] Upload notes first",[])

    force_short=any(w in prompt.lower() for w in ["define","state","brief","1 mark"])
    if mode=="notes": tokens=1200
    elif force_short: tokens=350
    else: tokens=1000

    cached=ai_cache.get(prompt+mode);
    if cached: return f"[CACHED] {cached}",[]

    context="\n".join([r['txt'] for r in vector_rag.search(prompt,3)])
    full=f"{SYSTEM_PROMPT}\nLEVEL:{level}\nMODE:{mode}\nCONTEXT:{context}\nTASK:{prompt}"

    model=AI_MODEL_SHORT if force_short and SYS_STATE["ram_ok"] else AI_MODEL_LONG
    try:
        res=client.chat.completions.create(model=model,messages=[{"role":"user","content":full}],max_tokens=tokens,temperature=0.3)
        ans=res.choices[0].message.content; ai_cache.set(prompt+mode,ans)
        save_db(LOG_FILE,load_db(LOG_FILE,[])+[{"time":str(datetime.now()),"q":prompt[:30]}])
        return ans,[context]
    except Exception as e: return f"[AUTO-FIX] Error: {e}. Try again",[]

def display_preview(content,name):
    st.text_area("AI Output - EDIT",content,height=400,key=f"p{name}")
    st.download_button("📥 Download TXT",content.encode(),f"{name}.txt")

def get_topics(s,l): return UNEB_CURRICULUM_MAP.get(s,{}).get(l,["General Topic"])

### 8. STUDENT PORTAL - ALL TABS NOW HAVE "ASK/TASK" BUTTON ###
def show_student():
    st.header("📚 Student Portal")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    t1,t2,t3,t4=st.tabs(["🔍 Smart Search","📖 Learn + Notes","🧪 Practicals","🖼️ Diagrams"])

    with t1:
        render_upload("s1"); s=st.selectbox("Subject",list(UNEB_CURRICULUM_MAP),key="s1s"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="s1l"); q=st.text_area("Ask Anything",placeholder="e.g. Explain differentiation or Solve this math",key="s1q")
        c1,c2=st.columns(2)
        if c1.button("Ask AI",key="s1b") and q: a,src=call_groq_os(q,l,"smart"); display_preview(a,"s1")
        if c2.button("Task Mode",key="s1t") and q: a,src=call_groq_os(q,l,"task"); display_preview(a,"s1t")

    with t2:
        render_upload("s2"); s=st.selectbox("Subject",list(UNEB_CURRICULUM_MAP),key="s2s"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="s2l"); t=st.selectbox("Topic",get_topics(s,l),key="s2t")
        c1,c2=st.columns(2)
        if c1.button("Quick Notes",key="s2b"): a,src=call_groq_os(f"Notes on {t} for {l} {s}",l,"notes"); display_preview(a,"s2")
        if c2.button("Ask About Topic",key="s2q"): a,src=call_groq_os(f"Explain {t} for {l} {s}",l,"smart"); display_preview(a,"s2q")

    with t3:
        render_upload("s3"); s=st.selectbox("Subject",list(PRACTICAL_DATABASE),key="s3s"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="s3l"); g="S1-S4" if int(l[1])<=4 else "S5-S6"; p=st.selectbox("Practical",list(PRACTICAL_DATABASE.get(s,{}).get(g,{})),key="s3p")
        c1,c2=st.columns(2)
        if c1.button("Generate Practical",key="s3b") and p: a,src=call_groq_os(f"Full UNEB practical for {p}. {PRACTICAL_DATABASE[s][g][p]['objective']}. Uganda",l,"notes"); display_preview(a,"s3")
        if c2.button("Ask About Practical",key="s3q") and p: a,src=call_groq_os(f"Explain {p} practical for {l}",l,"smart"); display_preview(a,"s3q")

    with t4:
        render_upload("s4"); s=st.selectbox("Subject",list(UNEB_CURRICULUM_MAP),key="s4s"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="s4l"); t=st.selectbox("Topic",get_topics(s,l),key="s4t")
        c1,c2=st.columns(2)
        if c1.button("Generate Diagrams",key="s4b"): a,src=call_groq_os(f"2 diagrams JSON + description for {l} {s} '{t}' Ugandan example",l,"smart"); display_preview(a,"s4")
        if c2.button("Ask About Diagram",key="s4q"): a,src=call_groq_os(f"How to draw and label diagram for {t} in {s}",l,"smart"); display_preview(a,"s4q")

### 9. ADMIN PORTAL - ASK BUTTON ADDED TO ALL 8 TABS ###
def show_admin():
    st.header("🏫 Admin Portal")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tabs=st.tabs(["📊 Analytics","📖 Curriculum","🧪 Practicals","📤 Bulk","📚 RAG KB","📝 Lesson","📄 Reports","📈 Predictive"])

    with tabs[0]:
        st.subheader("Analytics"); q=st.text_area("Ask about analytics",key="aq");
        if st.button("Ask",key="ab"): a,src=call_groq_os(f"Analyze this: {q}", "S4"); display_preview(a,"a")

    with tabs[1]:
        st.subheader("Curriculum"); s=st.selectbox("Subject",list(UNEB_CURRICULUM_MAP),key="as"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="al"); t=st.multiselect("Topics",get_topics(s,l))
        if st.button("Generate Scheme"): a,src=call_groq_os(f"Term Scheme for {l} {s} {t}",l,"notes"); display_preview(a,"scheme")
        if st.button("Ask Curriculum"): a,src=call_groq_os(f"How to teach {s} {l}",l); display_preview(a,"ac")

    with tabs[2]:
        st.subheader("Practicals"); q=st.text_area("Ask about any practical",key="pq")
        if st.button("Ask"): a,src=call_groq_os(q,"S4"); display_preview(a,"p")

    with tabs[3]:
        st.subheader("Bulk"); s=st.selectbox("Subject",list(UNEB_CURRICULUM_MAP),key="bs"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="bl"); t=st.multiselect("Topics",get_topics(s,l)); n=st.slider("Qs",10,100,50);
        if st.button("Generate"): a,src=call_groq_os(f"Generate {n} UNEB Qs + Marking guide from {t} for {l} {s}",l,"notes"); display_preview(a,"bulk")
        if st.button("Ask"): a,src=call_groq_os(f"Ideas for setting {s} paper",l); display_preview(a,"abk")

    with tabs[4]:
        st.subheader("RAG KB"); st.metric("Chunks",len(vector_rag.docs)); render_upload("a5")
        q=st.text_area("Ask RAG",key="ragq")
        if st.button("Ask RAG"): a,src=call_groq_os(q,"S4"); display_preview(a,"rag")
        if st.button("Reset RAG"): vector_rag.docs=[]; save_db(DOCS_FILE,[]); st.success("Reset")

    with tabs[5]:
        st.subheader("Lesson"); s=st.selectbox("Subject",list(UNEB_CURRICULUM_MAP),key="ls"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="ll"); t=st.selectbox("Topic",get_topics(s,l),key="lt")
        if st.button("Plan"): a,src=call_groq_os(f"Lesson Plan 40min NCDC {l} {s} {t}. Objectives,Activities,UG example",l,"notes"); display_preview(a,"lesson")
        if st.button("Ask"): a,src=call_groq_os(f"Teaching tips for {t}",l); display_preview(a,"al")

    with tabs[6]:
        st.subheader("Reports"); n=st.number_input("Students",1,1000,100)
        if st.button("Report Cards"): a,src=call_groq_os(f"Generate {n} NCDC Report Cards with grades and comments","S4","notes"); display_preview(a,"report")
        q=st.text_area("Custom Report Task",key="rq")
        if st.button("Ask"): a,src=call_groq_os(q,"S4"); display_preview(a,"ar")

    with tabs[7]:
        st.subheader("📈 Predictive"); st.metric("Status","Online" if SYS_STATE["online"] else "Offline")
        q=st.text_area("Ask Predictor",key="prq")
        if st.button("Ask"): a,src=call_groq_os(q,"S4"); display_preview(a,"pr")

### 10. LOGIN ###
st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO V6.1.2")
with st.sidebar:
    st.metric("RAM",f"{psutil.virtual_memory().percent}%"); st.metric("Internet","Online" if SYS_STATE["online"] else "Offline")
    pw=st.text_input("Password",type="password")
    c1,c2=st.columns(2)
    if c1.button("Student") and pw==STUDENT_PASSWORD: st.session_state.role="Student"; st.rerun()
    if c2.button("Admin") and pw==ADMIN_PASSWORD: st.session_state.role="Admin"; st.rerun()
if st.session_state.get("role")=="Admin": show_admin()
elif st.session_state.get("role")=="Student": show_student()
else: st.info("Login to continue")
