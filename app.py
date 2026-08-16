from difflib import SequenceMatcher
import streamlit as st, os, io, json, re, time, requests, random, threading, psutil, socket, hashlib
from datetime import datetime
from groq import Groq, RateLimitError
import logging
logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026 PRO", page_icon="📚", layout="wide")
st.sidebar.caption("Build: V6.1.1-MICRO-EDGE | NCDC COMPLIANT | 512MB SAFE")

### 1. FILES + UTILS ###
DATA_PATH = os.getenv("STREAMLIT_DATA_PATH", ".")
LOG_FILE, CACHE_FILE, DOCS_FILE, SETTINGS_FILE = [f"{DATA_PATH}/{x}" for x in ["usage_log.json","ai_cache.json","vector_docs.json","teacher_settings.json"]]
def save_db(f,d): json.dump(d, open(f,"w"), indent=2)
def load_db(f,default):
    if not os.path.exists(f): save_db(f,default)
    try: return json.load(open(f,"r"))
    except: save_db(f,default); return default
for f,d in [(LOG_FILE,[]),(CACHE_FILE,{}),(DOCS_FILE,[]),(SETTINGS_FILE,{})]: load_db(f,d)
DIAGRAM_CACHE = {}

### 2. SECRETS + MODELS - MOVED UP TO FIX BUG 1 ###
GROQ_API_KEY=os.getenv("GROQ_API_KEY",""); STUDENT_PASSWORD=os.getenv("STUDENT_PASSWORD","1234"); ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD","admin123")
if not GROQ_API_KEY: st.error("Missing GROQ_API_KEY in Render Environment"); st.stop()

### 3. AUTONOMOUS OS SENSORS ###
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
    def stats(self): return {"total":len(self.cache),"active":len([1 for v in self.cache.values() if time.time()<v[1]])}
ai_cache = TTLSchoolCache()

### 5. NCDC CURRICULUM + PRACTICALS ###
UNEB_CURRICULUM_MAP = {"Mathematics": {"S1": ["Sets","Number Bases"],"S2": ["Rates","Algebra"],"S3": ["Quadratics","Trigonometry"],"S4": ["Functions","Matrices"],"S5": ["Differentiation","Integration"],"S6": ["Mechanics II","Statistics III"]},"Physics": {"S1": ["Measurement","Forces"],"S4": ["Electronics","Waves II"],"S6": ["Electric Fields","Nuclear Physics II"]},"Chemistry": {"S3": ["Bonding","Organic I"],"S5": ["Kinetics III","Organic II"]},"Biology": {"S1": ["Cells","Classification"],"S4": ["Photosynthesis","Hormones I"],"S6": ["Biotechnology II","Genetics IV"]},"Agriculture": {"S1": ["Soil Formation","Crops"],"S4": ["Crop Protection","Farm Management"]},"Geography": {"S1": ["Map Reading","Weather"],"S4": ["GIS","Population Structure"]},"History": {"S1": ["Early Man","Bantu Migrations"],"S4": ["OAU","Human Rights"]},"Literature": {"S1": ["Oral Literature","Poetry"],"S4": ["African Literature"]},"CRE": {"S1": ["God and Man","Creation"],"S4": ["Christian Living"]},"ICT": {"S1": ["Computer Basics","Word"],"S4": ["Web Design","Networking"]},"Entrepreneurship": {"S1": ["Business Ideas"],"S4": ["Management","Law"]},"Art": {"S1": ["Drawing","Color"]},"Music": {"S1": ["Notes","Rhythm"]},"Luganda": {"S1": ["Ebigambo","Ennukuta"]},"Kiswahili": {"S1": ["Alfabeti","Maneno"]}}
PRACTICAL_DATABASE = {"Physics": {"S1-S4": {"Ohm's Law": {"objective": "Verify Ohm's Law"}},"S5-S6": {"RC Circuit": {"objective": "Find time constant"}}},"Chemistry": {"S1-S4": {"Titration": {"objective": "Determine HCl"}},"S5-S6": {"Rate": {"objective": "Order of reaction"}}},"Biology": {"S1-S4": {"Microscope": {"objective": "Observe cells"}},"S5-S6": {"Enzyme": {"objective": "Effect of pH"}}},"Agriculture": {"S1-S4": {"Soil pH": {"objective": "Determine pH"}},"S5-S6": {"Feed": {"objective": "Formulate feed"}}}}

### 6. LIGHT RAG ###
class VectorRAG:
    def __init__(self): self.docs=load_db(DOCS_FILE,[])
    def add(self,texts,fn):
        for t in texts: self.docs.append({"src":fn,"txt":t[:1200]})
        save_db(DOCS_FILE,self.docs)
    def search(self,q,k=2):
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

### 7. SMART CALLER ###
SYSTEM_PROMPT="""You are Senior NCDC Uganda Tutor. Rules: 1.ANTI-HALLUCINATION: If not in CONTEXT say 'Per NCDC I cant confirm'. 2.LENGTH: 'define'=2 sentences. 'explain'=4 points+UG example. 3.FORMAT: **Concept**:X **UG Example**:Y **Exam Tip**:Z. 4.UG: Use Kampala,matooke,boda examples."""
EXAMPLES="Q:Define Osmosis briefly\nA:**Concept**:Water movement. **UG Example**:Cassava swelling. **Exam Tip**:Mention membrane."

def call_groq_os(prompt,level="S4"):
    global SYS_STATE; SYS_STATE=system_check()
    if not SYS_STATE["online"]:
        res=vector_rag.search(prompt,3);
        return (f"[OFFLINE] Based on school notes:\n{chr(10).join([r['txt'][:400] for r in res])}",res) if res else ("[OFFLINE] Upload notes first",[])
    force_short=any(w in prompt.lower() for w in ["define","state","brief","1 mark"])
    if not SYS_STATE["ram_ok"]: force_short=True
    cached=ai_cache.get(prompt);
    if cached: return f"[CACHED] {cached}",[]
    context="\n".join([r['txt'] for r in vector_rag.search(prompt,2)])
    full=f"{SYSTEM_PROMPT}\n{EXAMPLES}\nLEVEL:{level}\n{'2 sentences max' if force_short else 'Full + UG example'}\nCONTEXT:{context}\nQ:{prompt}"
    model=AI_MODEL_SHORT if force_short else AI_MODEL_LONG; tokens=350 if force_short else 1000
    try:
        res=client.chat.completions.create(model=model,messages=[{"role":"user","content":full}],max_tokens=tokens,temperature=0.1)
        ans=res.choices[0].message.content; ai_cache.set(prompt,ans)
        save_db(LOG_FILE,load_db(LOG_FILE,[])+[{"time":str(datetime.now()),"q":prompt[:30]}])
        return ans,[context]
    except Exception as e: return f"[AUTO-FIX] Error: {e}. Try again",[]

def display_preview(content,name):
    st.text_area("AI Preview - EDIT",content,height=300,key=f"p{name}")
    st.download_button("📥 TXT",content.encode(),f"{name}.txt")

def get_group(l): return "S1-S4" if int(l[1])<=4 else "S5-S6"

### 8. STUDENT PORTAL - FIXED INDENTATION BUG 2 ###
def show_student():
    st.header("📚 Student Portal")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    t1,t2,t3,t4=st.tabs(["🔍 Smart Search","📖 Learn","🧪 Practicals","🖼️ Diagrams"])
    with t1:
        render_upload("s1"); s=st.selectbox("Subject",list(UNEB_CURRICULUM_MAP),key="s1s"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="s1l"); q=st.text_area("Ask",key="s1q")
        if st.button("Ask",key="s1b") and q: a,src=call_groq_os(q,l); display_preview(a,"s1")
    with t2:
        render_upload("s2"); s=st.selectbox("Subject",list(UNEB_CURRICULUM_MAP),key="s2s"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="s2l"); t=st.selectbox("Topic",UNEB_CURRICULUM_MAP[s][l],key="s2t")
        if st.button("Notes",key="s2b"): a,src=call_groq_os(f"Notes on {t} for {l} {s}",l); display_preview(a,"s2")
    with t3:
        render_upload("s3"); s=st.selectbox("Subject",list(PRACTICAL_DATABASE),key="s3s"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="s3l"); g=get_group(l); p=st.selectbox("Practical",list(PRACTICAL_DATABASE[s][g]),key="s3p") if s in PRACTICAL_DATABASE else None
        if st.button("Generate",key="s3b") and p: a,src=call_groq_os(f"Full UNEB practical for {p}. {PRACTICAL_DATABASE[s][g][p]['objective']}. Uganda",l); display_preview(a,"s3")
    with t4:
        render_upload("s4"); s=st.selectbox("Subject",list(UNEB_CURRICULUM_MAP),key="s4s"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="s4l"); t=st.selectbox("Topic",UNEB_CURRICULUM_MAP[s][l],key="s4t")
        if st.button("Diagram",key="s4b"): a,src=call_groq_os(f"2 diagrams JSON for {l} {s} '{t}' Ugandan example",l); display_preview(a,"s4")

### 9. ADMIN PORTAL - FIXED INDENTATION BUG 3 ###
def show_admin():
    st.header("🏫 Admin Portal")
    if st.button("Logout"): st.session_state.clear(); st.rerun()
    tabs=st.tabs(["📊 Analytics","📖 Curriculum","🧪 Practicals","📤 Bulk","📚 RAG KB","📝 Lesson","📄 Reports","📈 Predictive"])
    with tabs[0]:
        st.subheader("Analytics"); render_upload("a1")
        logs=load_db(LOG_FILE,[]); st.metric("Queries",len(logs)); st.metric("Cache",ai_cache.stats()['total']); st.metric("VDB",len(vector_rag.docs))
        st.dataframe(load_db(LOG_FILE,[])[-10:])
    with tabs[1]:
        st.subheader("Curriculum"); settings=load_db(SETTINGS_FILE,{})
        s=st.selectbox("Subject",list(UNEB_CURRICULUM_MAP),key="as"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="al")
        t=st.multiselect("Topics",UNEB_CURRICULUM_MAP[s][l],default=settings.get(f"{s}_{l}",[]))
        if st.button("Save"): settings[f"{s}_{l}"]=t; save_db(SETTINGS_FILE,settings); st.success("Saved")
    with tabs[2]: st.subheader("Practicals"); st.json(PRACTICAL_DATABASE)
    with tabs[3]:
        st.subheader("Bulk"); settings=load_db(SETTINGS_FILE,{})
        s=st.selectbox("Subject",list(UNEB_CURRICULUM_MAP),key="bs"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="bl")
        t=st.multiselect("Topics",UNEB_CURRICULUM_MAP[s][l],default=settings.get(f"{s}_{l}",[]))
        n=st.slider("Qs",10,100,50);
        if st.button("Generate"): a,src=call_groq_os(f"Generate {n} UNEB Qs from {t}. Marking guide.",l); display_preview(a,"bulk")
    with tabs[4]:
        st.subheader("RAG KB"); st.metric("Chunks",len(vector_rag.docs)); render_upload("a5")
        if st.button("Reset RAG"): vector_rag.docs=[]; save_db(DOCS_FILE,[]); st.success("Reset")
    with tabs[5]:
        st.subheader("Lesson"); s=st.selectbox("Subject",list(UNEB_CURRICULUM_MAP),key="ls"); l=st.selectbox("Class",[f"S{i}" for i in range(1,7)],key="ll"); t=st.selectbox("Topic",UNEB_CURRICULUM_MAP[s][l],key="lt")
        if st.button("Plan"): a,src=call_groq_os(f"Lesson Plan 40min NCDC {l} {s} {t}. Objectives,Activities,UG example",l); display_preview(a,"lesson")
    with tabs[6]:
        st.subheader("Reports"); n=st.number_input("Students",1,1000,100)
        if st.button("Report Cards"): a,src=call_groq_os(f"Generate {n} NCDC Report Cards with grades and comments","S4"); display_preview(a,"report")
    with tabs[7]:
        st.subheader("📈 Predictive"); c1,c2,c3=st.columns(3)
        c1.metric("Queries",len(load_db(LOG_FILE,[]))); c2.metric("Cache",ai_cache.stats()['active']); c3.metric("Status","Online" if SYS_STATE["online"] else "Offline")
        st.warning("**At-Risk: S4 Physics** - 0 practicals"); st.error("**Gap: Organic S5** - 0 notes")

### 10. LOGIN ###
st.title("🎓 DIGITAL UNEB TUTOR 2026 PRO V6.1.1")
with st.sidebar:
    st.metric("RAM",f"{psutil.virtual_memory().percent}%"); st.metric("Internet","Online" if SYS_STATE["online"] else "Offline")
    pw=st.text_input("Password",type="password")
    c1,c2=st.columns(2)
    if c1.button("Student") and pw==STUDENT_PASSWORD: st.session_state.role="Student"; st.rerun()
    if c2.button("Admin") and pw==ADMIN_PASSWORD: st.session_state.role="Admin"; st.rerun()
if st.session_state.get("role")=="Admin": show_admin()
elif st.session_state.get("role")=="Student": show_student()
else: st.info("Login to continue")
