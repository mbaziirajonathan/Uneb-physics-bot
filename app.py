import streamlit as st
import os
import json
import hashlib
import time
import re
from datetime import datetime
import pandas as pd
import psutil
import requests
from openai import OpenAI
from dotenv import load_dotenv

# PDF/DOCX Imports
from pypdf import PdfReader
from docx import Document

# ================== CONFIG ==================
load_dotenv()
APP_TITLE = "UNEB AI TUTOR V6.4.5-DIAGNOSTIC"
DATA_PATH = os.getenv("STREAMLIT_DATA_PATH", "/data")
ASSETS_PATH = os.path.join(DATA_PATH, "assets")
os.makedirs(ASSETS_PATH, exist_ok=True)

# File paths
CACHE_FILE = os.path.join(DATA_PATH, "ai_cache.json")
MEMORY_FILE = os.path.join(DATA_PATH, "chat_memory.json")
VECTOR_FILE = os.path.join(DATA_PATH, "vector_docs.json")
LOG_FILE = os.path.join(DATA_PATH, "usage_log.json")

# OpenRouter Config - PATCHED AUG 18 2026
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
AI_MODEL_LONG = "google/gemma-4-31b-it:free" # Only healthy one
AI_MODEL_SHORT = "deepseek/deepseek-r1:free" # Best math backup - VERIFIED
AI_MODEL_BACKUP = "meta-llama/llama-3.1-405b-instruct:free" # Old reliable - VERIFIED
ALL_MODELS = [AI_MODEL_LONG, AI_MODEL_SHORT, AI_MODEL_BACKUP]

# Passwords
STUDENT_PASSWORD = os.getenv("STUDENT_PASSWORD", "1234")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# ================== NCDC CURRICULUM & PRACTICALS - 100% KEPT ==================
UNEB_CURRICULUM_MAP = {
    "S1": {"Mathematics": ["Sets", "Numbers", "Algebra"], "Physics": ["Measurements", "Density", "Forces"], "Chemistry": ["Introduction", "Air and Combustion"], "Biology": ["Introduction", "Cell Structure"]},
    "S2": {"Mathematics": ["Quadratic Equations", "Trigonometry"], "Physics": ["Current Electricity", "Waves"], "Chemistry": ["Atomic Structure", "Acids Bases"], "Biology": ["Nutrition", "Respiration"]},
    "S3": {"Mathematics": ["Matrices", "Probability"], "Physics": ["Newton's Laws", "Work Energy Power"], "Chemistry": ["Mole Concept", "Rates of Reaction"], "Biology": ["Genetics", "Ecology"]},
    "S4": {"Mathematics": ["Vectors", "Statistics"], "Physics": ["Magnetism", "Electronics"], "Chemistry": ["Organic Chemistry", "Energetics"], "Biology": ["Evolution", "Human Physiology"]},
    "S5": {"Mathematics": ["Calculus", "Mechanics"], "Physics": ["Thermal Physics", "Fields"], "Chemistry": ["Reaction Kinetics", "Equilibria"], "Biology": ["Cell Physiology", "Plant Physiology"]},
    "S6": {"Mathematics": ["Differential Equations", "Linear Programming"], "Physics": ["Nuclear Physics", "AC Circuits"], "Chemistry": ["Electrochemistry", "Industrial Chemistry"], "Biology": ["Microbiology", "Applied Biology"]}
}

PRACTICAL_DATABASE = {
    "Physics": {"S3": ["Verifying Hooke's Law"], "S4": ["Verifying Ohm's Law"]},
    "Chemistry": {"S3": ["Preparation of Oxygen gas"], "S4": ["Titration: Acid vs Base"]},
    "Biology": {"S3": ["Testing for food nutrients"], "S4": ["Dissection of a toad"]},
}

# ================== SYSTEM PROMPTS ==================
SYSTEM_PROMPT_GENERATIVE = """You are UNEB AI Tutor Generative Mode. Explain ANY topic but prioritize Ugandan context.
Be helpful, accurate, and teach step-by-step like a Ugandan teacher. Use headings and examples."""

# ================== RAG + CACHE + MEMORY ==================
class VectorRAG:
    def __init__(self): self.docs = self.load_vector_db()
    def load_vector_db(self):
        if os.path.exists(VECTOR_FILE):
            with open(VECTOR_FILE, 'r') as f: return json.load(f)
        return []
    def save_vector_db(self):
        with open(VECTOR_FILE, 'w') as f: json.dump(self.docs, f)
    def add_document(self, text, source):
        doc_id = hashlib.md5(text.encode()).hexdigest()
        self.docs.append({"id": doc_id, "text": text[:1000], "source": source, "timestamp": datetime.now().isoformat()})
        self.save_vector_db()
    def search(self, query, top_k=3):
        query_words = set(query.lower().split())
        scored = []
        for doc in self.docs:
            doc_words = set(doc['text'].lower().split())
            score = len(query_words.intersection(doc_words))
            if score > 0: scored.append((score, doc))
        scored.sort(reverse=True, key=lambda x: x[0])
        return [doc for _, doc in scored[:top_k]]

ai_cache = {}
chat_mem = {}
rag = VectorRAG()

def load_cache():
    global ai_cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f: ai_cache = json.load(f)

def save_cache():
    with open(CACHE_FILE, 'w') as f: json.dump(ai_cache, f)

def log_usage(user, query):
    log = {"timestamp": datetime.now().isoformat(), "user": user, "query": query}
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f: logs = json.load(f)
    logs.append(log)
    with open(LOG_FILE, 'w') as f: json.dump(logs[-1000:], f)

# ================== KEY & MODEL HEALTH CHECKS ==================
def check_api_key():
    """Returns: status, message"""
    if not OPENROUTER_API_KEY:
        return "BROKEN", "ERROR: OPENROUTER_API_KEY not found in Environment Variables"
    if len(OPENROUTER_API_KEY) < 20 or not OPENROUTER_API_KEY.startswith("sk-or-"):
        return "BROKEN", f"ERROR: API Key format invalid. Should start with 'sk-or-'. Yours: {OPENROUTER_API_KEY[:10]}..."
    return "OK", "API Key Loaded"

def test_model_health(model_id):
    """Quick test call to see if model is up"""
    client = get_client()
    if not client: return "NO_KEY"
    try:
        client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=1
        )
        return "HEALTHY"
    except Exception as e:
        err = str(e)
        if "429" in err: return "RATE_LIMITED"
        if "404" in err or "400" in err: return "INVALID_ID"
        return f"ERROR: {err[:50]}"

def get_client():
    if not OPENROUTER_API_KEY: return None
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)

def ai_call(prompt, system_prompt):
    """Main AI call with full diagnostics"""
    # 1. KEY CHECK
    key_status, key_msg = check_api_key()
    if key_status == "BROKEN":
        return f"🔴 API KEY FAILURE\n\n{key_msg}"

    client = get_client()
    cache_key = hashlib.md5((prompt + system_prompt).encode()).hexdigest()
    if cache_key in ai_cache: return ai_cache[cache_key] + " [CACHED]"

    last_error = ""
    models_tried = []

    # 2. TRY ALL MODELS
    for m in ALL_MODELS:
        models_tried.append(m)
        try:
            st.sidebar.write(f"⏳ Trying: `{m.split('/')[-1]}`") # Show which model is trying
            resp = client.chat.completions.create(
                model=m,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                temperature=0.7, max_tokens=2000
            )
            answer = resp.choices[0].message.content
            ai_cache[cache_key] = answer
            save_cache()
            return f"{answer}\n\n---\n✅ *Success with: `{m}`*" # Show which model worked

        except Exception as e:
            err_str = str(e)
            last_error = err_str
            if "429" in err_str:
                st.sidebar.warning(f"⚠️ {m.split('/')[-1]}: Rate Limited")
                continue
            elif "404" in err_str or "400" in err_str:
                st.sidebar.error(f"❌ {m.split('/')[-1]}: Invalid Model ID")
                continue
            else:
                st.sidebar.error(f"❌ {m.split('/')[-1]}: {err_str[:50]}")
                continue

    # 3. ALL FAILED
    return f"""🔴 ALL MODELS FAILED

**Tried:** {', '.join([m.split('/')[-1] for m in models_tried])}
**Last Error:** {last_error}

**Diagnosis:**
1. If error = 429: You hit 50/day limit. Wait 1 hour or add $10 to OpenRouter.
2. If error = 400/404: Model ID is wrong.
3. If error = API Key: Key is invalid or revoked.

Check `openrouter.ai/activity` to see who used your key."""

# ================== UTILS ==================
def render_upload(uploaded_file):
    if uploaded_file.name.endswith('.pdf'):
        reader = PdfReader(uploaded_file)
        return "\n".join([page.extract_text() for page in reader.pages])
    elif uploaded_file.name.endswith('.docx'):
        doc = Document(uploaded_file)
        return "\n".join([p.text for p in doc.paragraphs])
    else: return uploaded_file.getvalue().decode("utf-8")

# ================== STUDENT UI ==================
def show_student():
    st.title("🎓 Student Portal")
    if 'student_name' not in st.session_state: st.session_state.student_name = "Student"

    col1, col2 = st.columns(2)
    with col1: subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP["S1"].keys()))
    with col2: level = st.selectbox("Level", ["S1", "S2", "S3", "S4", "S5", "S6"])

    query = st.text_area("Ask any question", placeholder="e.g. Define Physics S1")

    if st.button("Get Answer", type="primary"):
        if query:
            with st.spinner("Running diagnostics..."):
                log_usage(st.session_state.student_name, query)
                rag_results = rag.search(query)
                context = "\n".join([r['text'] for r in rag_results])
                prompt = f"Context: {context}\n\nQuestion: {query}\nSubject: {subject}\nLevel: {level}\nUse Ugandan examples."
                answer = ai_call(prompt, SYSTEM_PROMPT_GENERATIVE)
                st.success(answer)
                if st.session_state.student_name not in chat_mem: chat_mem[st.session_state.student_name] = []
                chat_mem[st.session_state.student_name].append({"q": query, "a": answer})

# ================== ADMIN UI ==================
def show_admin():
    st.title("👨‍🏫 Admin Portal - DIAGNOSTICS")
    tab1, tab2, tab3 = st.tabs(["System Health", "Upload Docs", "View Logs"])

    with tab1:
        st.subheader("1. API Key Check")
        key_status, key_msg = check_api_key()
        if key_status == "OK": st.success(key_msg)
        else: st.error(key_msg)

        st.subheader("2. Model Health Check")
        if st.button("Run Health Check on All 3 Models"):
            for model in ALL_MODELS:
                with st.spinner(f"Testing {model}..."):
                    status = test_model_health(model)
                    if status == "HEALTHY": st.success(f"✅ {model}: HEALTHY")
                    elif status == "RATE_LIMITED": st.warning(f"⚠️ {model}: RATE LIMITED - Hit 50/day")
                    elif status == "INVALID_ID": st.error(f"❌ {model}: INVALID MODEL ID")
                    else: st.error(f"❌ {model}: {status}")

        st.subheader("3. Cache & Data")
        st.write(f"Cache Items: {len(ai_cache)}")
        st.write(f"RAG Docs: {len(rag.docs)}")
        if st.button("Clear Cache"): ai_cache.clear(); save_cache(); st.success("Cleared")

    with tab2:
        uploaded_file = st.file_uploader("Upload PDF/DOCX/TXT")
        if uploaded_file:
            text = render_upload(uploaded_file)
            st.text_area("Preview", text[:1000], height=200)
            if st.button("Add to Knowledge Base"):
                rag.add_document(text, uploaded_file.name)
                st.success("Added to RAG!")

    with tab3:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f: logs = json.load(f)
            st.dataframe(pd.DataFrame(logs[-50:]))

# ================== MAIN APP ==================
st.set_page_config(page_title=APP_TITLE, layout="wide")
load_cache()

with st.sidebar:
    st.write(f"**Build:** {APP_TITLE}")
    st.write(f"**RAM:** {psutil.virtual_memory().percent}%")

    key_status, key_msg = check_api_key()
    if key_status == "OK": st.success("🔑 API Key: OK")
    else: st.error("🔑 API Key: BROKEN")

    st.write("**Models Loaded:**")
    for m in ALL_MODELS: st.caption(f"- {m.split('/')[-1]}")

    st.caption("Free Tier: 50 requests/day per model")

    password = st.text_input("Password", type="password")
    if st.button("Student Login"):
        if password == STUDENT_PASSWORD: st.session_state.role = "Student"; st.rerun()
        else: st.error("Wrong password")
    if st.button("Admin Login"):
        if password == ADMIN_PASSWORD: st.session_state.role = "Admin"; st.rerun()
        else: st.error("Wrong password")

if st.session_state.get("role") == "Student":
    show_student()
elif st.session_state.get("role") == "Admin":
    show_admin()
else:
    st.title("Welcome to UNEB AI Tutor V6.4.5")
    st.write("Go to Admin > System Health to diagnose API issues")
