# ai_logic.py
import os, io, json, re, numpy as np, random
import pandas as pd
import plotly.express as px
from groq import Groq
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
from pathlib import Path
from gtts import gTTS
import streamlit as st # ONLY for st.secrets. We will remove this later

# COPY ALL YOUR DATA STRUCTURES HERE FROM app.py
SUBJECTS = ["Physics", "Chemistry", "Biology"]
CLASSES = ["S1", "S2", "S3", "S4"]
SYLLABUS = {...} # PASTE YOUR FULL SYLLABUS DICT HERE
PRACTICALS = {...} # PASTE YOUR FULL PRACTICALS DICT HERE

BASE_DIR = Path(__file__).parent.resolve()
DIAGRAMS_DIR = BASE_DIR / "assets"

# 1. CORE AI FUNCTION
def get_client():
    api_key = st.secrets["GROQ_API_KEY"] # For now. Later use os.getenv
    return Groq(api_key=api_key)

def generate_ai_response(client, prompt, subject, class_level):
    system_prompt = f"You are UCE/UACE DIGITAL TUTOR 2026. You teach {subject} for {class_level} in Uganda. Answer ONLY according to NCDC Uganda Syllabus 2026 and UNEB guidelines. Be accurate, cite NCDC where possible. Use Ugandan examples. Be clear and step-by-step. If question is outside NCDC syllabus, say 'This is outside NCDC 2026 syllabus'."
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
            temperature=0.3, max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# 2. UTILS COPIED FROM app.py
def generate_graph(data, x_col, y_col, title):
    fig = px.line(data, x=x_col, y=y_col, title=title, markers=True)
    fig.update_layout(template="plotly_white")
    return fig

def create_pdf(content, filename):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 12)
    y = height - 50
    for line in content.split('\n'):
        c.drawString(50, y, line[:90])
        y -= 20
        if y < 50: c.showPage(); y = height - 50
    c.save()
    buffer.seek(0)
    return buffer

def sanitize_filename(name):
    name = name.lower()
    name = re.sub(r'[^a-z0-9\s]', '', name)
    return name

def find_diagram(topic):
    if not DIAGRAMS_DIR.exists(): return None, []
    all_pngs = list(DIAGRAMS_DIR.glob("*.png"))
    search_key = sanitize_filename(topic)
    KEYWORD_MAP = {"respiration": ["respiratory_system"], "human eye": ["human_eye"], "cells": ["animal_cell", "plant_cell"]} # SHORTENED FOR BREVITY. PASTE YOUR FULL MAP
    for key, possible_files in KEYWORD_MAP.items():
        if key in search_key:
            for pf in possible_files:
                for f in all_pngs:
                    if pf in f.name.lower(): return str(f), []
    return None, []

def generate_tts(text, filename="response.mp3"):
    tts = gTTS(text)
    tts.save(filename)
    return filename
