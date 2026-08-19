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
from google import genai # NEW: Modern Google GenAI library
from google.genai import types
from dotenv import load_dotenv

# PDF/DOCX Imports
from pypdf import PdfReader
from docx import Document

# ================== CONFIG ==================
load_dotenv()
APP_TITLE = "UNEB AI TUTOR V6.4.8-MODERN"

# FREE TIER FIX: Use /tmp if /data doesn't exist
DATA_PATH = os.getenv("STREAMLIT_DATA_PATH", "/data")
if not os.path.exists(DATA_PATH) or not os.access(DATA_PATH, os.W_OK):
    DATA_PATH = "/tmp"
    
ASSETS_PATH = os.path.join(DATA_PATH, "assets")
os.makedirs(ASSETS_PATH, exist_ok=True)

# File paths
CACHE_FILE = os.path.join(DATA_PATH, "ai_cache.json")
MEMORY_FILE = os.path.join(DATA_PATH, "chat_memory.json")
VECTOR_FILE = os.path.join(DATA_PATH, "vector_docs.json")
LOG_FILE = os.path.join(DATA_PATH, "usage_log.json")

# Keys Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Cleaned Active 2026 Model Fallback Array
AI_MODEL = os.getenv("AI_MODEL", "gemini-2.5-flash") 
ALL_MODELS = [
    "gemini-2.5-flash", # Primary: Direct SDK - uses AQ key
    "openrouter/free" # Backup: Router for free models
]

# Passwords
STUDENT_PASSWORD = os.getenv("STUDENT_PASSWORD", "1234")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# ================== NCDC CURRICULUM ==================
UNEB_CURRICULUM_MAP = {
    "S1": {"Mathematics": ["Sets", "Numbers", "Algebra"], "Physics": ["Measurements", "Density"], "Chemistry": ["Introduction", "Air"], "Biology": ["Introduction", "Cell"]},
    "S2": {"Mathematics": ["Quadratic Equations"], "Physics": ["Current Electricity"], "Chemistry": ["Atomic Structure"], "Biology": ["Nutrition"]},
    "S3": {"Mathematics": ["Matrices"], "Physics": ["Newton's Laws"], "Chemistry": ["Mole Concept"], "Biology": ["Genetics"]},
    "S4": {"Mathematics": ["Vectors"], "Physics": ["Magnetism"], "Chemistry": ["Organic Chemistry"], "Biology": ["Evolution"]},
    "S5": {"Mathematics": ["Calculus"], "Physics": ["Thermal Physics"], "Chemistry": ["Reaction Kinetics"], "Biology": ["Cell Physiology"]},
    "S6": {"Mathematics": ["Differential Equations"], "Physics": ["Nuclear Physics"], "Chemistry": ["Industrial Chemistry"], "Biology": ["Microbiology"]}
}

SYSTEM_PROMPT = """You are UNEB AI Tutor for Uganda NCDC. Explain step-by-step like a Ugandan teacher. 
Use simple English, headings, and 2 local examples.
Subject: {subject} | Level: {level}"""

# ================== RAG + CACHE ==================
ai_cache = {}
rag_docs = []

def load_cache():
    global ai_cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f: ai_cache = json.load(f)
load_cache()

def save_cache():
    try:
        with open(CACHE_FILE, 'w') as f: json.dump(ai_cache, f)
    except: pass

def log_usage(user, query):
    pass # Add your log function back

# ================== HEALTH CHECK SIDEBAR ==================
def health_check():
    st.sidebar.title("🔧 System Health")
    st.sidebar.write(f"**Data Path:** `{DATA_PATH}`")
    
    # 1. Check Keys
    if GEMINI_API_KEY and GEMINI_API_KEY.startswith("AQ"):
        st.sidebar.success("✅ GEMINI_API_KEY: Loaded")
    else:
        st.sidebar.error("❌ GEMINI_API_KEY: Missing or Invalid")
        
    if OPENROUTER_API_KEY and OPENROUTER_API_KEY.startswith("sk-or"):
        st.sidebar.success("✅ OPENROUTER_API_KEY: Loaded")
    else:
        st.sidebar.warning("⚠️ OPENROUTER_API_KEY: Missing")
    
    # 2. Check Disk Space
    disk = psutil.disk_usage(DATA_PATH)
    st.sidebar.info(f"💾 Disk Free: {disk.free / 1024 / 1024:.1f} MB")
    
    # 3. Test Gemini Call
    if st.sidebar.button("🧪 Test Gemini Key"):
        with st.sidebar.spinner("Pinging gemini-2.5-flash..."):
            try:
                client = genai.Client(api_key=GEMINI_API_KEY)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[types.Content(role="user", parts=[types.Part(text="Say OK")])]
                )
                st.sidebar.success(f"✅ Gemini OK: {response.text[:10]}")
            except Exception as e:
                st.sidebar.error(f"❌ Gemini Failed: {str(e)[:80]}")

health_check()

# ================== AI CALL V6.4.8 ==================
def ai_call(prompt, system_prompt, subject, level):
    system_prompt = system_prompt.format(subject=subject, level=level)
    full_prompt = f"{system_prompt}\n\nStudent Question: {prompt}"
    cache_key = hashlib.md5(full_prompt.encode()).hexdigest()
    if cache_key in ai_cache: return ai_cache[cache_key] + " [CACHED]"

    models_to_try = [AI_MODEL] + [m for m in ALL_MODELS if m!= AI_MODEL]
    last_error = ""

    for m in models_to_try:
        try:
            st.sidebar.write(f"⏳ Trying: `{m}`")
            
            # --- PATH 1: DIRECT GEMINI SDK with AQ key ---
            if "gemini" in m:
                if not GEMINI_API_KEY: raise ValueError("GEMINI_API_KEY missing")
                
                client = genai.Client(api_key=GEMINI_API_KEY)
                response = client.models.generate_content(
                    model=m,
                    contents=[
                        types.Content(role="user", parts=[types.Part(text=full_prompt)])
                    ]
                )
                answer = response.text

            # --- PATH 2: OPENROUTER ROUTER ---
            else:
                if not OPENROUTER_API_KEY: raise ValueError("OPENROUTER_API_KEY missing")
                or_client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=OPENROUTER_API_KEY
                )
                resp = or_client.chat.completions.create(
                    model=m,
                    messages=[{"role": "user", "content": full_prompt}],
                    max_tokens=1200
                )
                answer = resp.choices[0].message.content

            answer += f"\n\n---\n✅ *Powered by: `{m}`*"
            ai_cache[cache_key] = answer
            save_cache()
            return answer

        except Exception as e:
            last_error = str(e)[:100]
            st.sidebar.error(f"❌ {m}: {last_error}")
            continue

    return f"🔴 ALL MODELS FAILED\nLast Error: {last_error}\n\nCheck Render Env Vars: GEMINI_API_KEY and OPENROUTER_API_KEY"

# ================== STUDENT UI ==================
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(f"🎓 {APP_TITLE}")

col1, col2, col3 = st.columns(3)
with col1: level = st.selectbox("Level", list(UNEB_CURRICULUM_MAP.keys()))
with col2: subject = st.selectbox("Subject", list(UNEB_CURRICULUM_MAP[level].keys()))
with col3: topic = st.selectbox("Topic", UNEB_CURRICULUM_MAP[level][subject])

query = st.text_area("Ask your UNEB Question:", height=100)

if st.button("Ask AI Tutor"):
    if query:
        with st.spinner("Thinking..."):
            answer = ai_call(query, SYSTEM_PROMPT, subject, level)
            st.markdown(answer)
            log_usage("student", query)
    else:
        st.warning("Please type a question")
