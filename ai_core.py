import streamlit as st
from groq import Groq
import os
import json
import pandas as pd
from datetime import datetime
import io

# ========== CONFIG ==========
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
client = Groq(api_key=GROQ_API_KEY)

SMART_SYSTEM = """You are DIGITAL UNEB TUTOR 2026, a Ugandan S1-S6 AI tutor.
Teach using NCDC curriculum. Use Ugandan examples. Be step by step. No cheating.
"""

EXAMINER_SYSTEM = """You are a senior UNEB examiner and NCDC teacher.
Generate professional Ugandan exam items, lesson plans, report cards. Use proper Bloom's taxonomy.
"""

UNEB_CURRICULUM_MAP = {
    "Mathematics": {"S1": ["Sets", "Integers"], "S2": ["Algebra"], "S3": ["Trigonometry"], "S4": ["Statistics"], "S5": ["Calculus"], "S6": ["Vectors"]},
    "Physics": {"S1": ["Measurement"], "S2": ["Energy"], "S3": ["Waves"], "S4": ["Electricity"], "S5": ["Mechanics"], "S6": ["Nuclear"]},
    "Chemistry": {"S1": ["Acids"], "S2": ["Salts"], "S3": ["Organic"], "S4": ["Electrochemistry"]},
    "Biology": {"S1": ["Cells"], "S2": ["Nutrition"], "S3": ["Reproduction"], "S4": ["Ecology"]},
    "Geography": {"S1": ["Maps"], "S2": ["Climate"], "S3": ["Population"], "S4": ["Industry"]},
    "History": {"S1": ["Ancient"], "S2": ["Colonialism"], "S3": ["WW1"], "S4": ["Post Independence"]}
}

# ========== ANTI-CHEAT ==========
CHEAT_KEYWORDS = ["exam now", "live exam", "during test", "help me cheat", "give me answers for this test"]
def check_cheating(query):
    for word in CHEAT_KEYWORDS:
        if word in query.lower():
            return True
    return False

# ========== LOGGING ==========
def log_activity(user_type, action, details, flagged=False):
    log_entry = {"timestamp": datetime.now().isoformat(), "user_type": user_type, "action": action, "details": details, "flagged": flagged}
    try:
        if os.path.exists("usage_log.json"):
            with open("usage_log.json", "r") as f: logs = json.load(f)
        else: logs = []
        logs.append(log_entry)
        with open("usage_log.json", "w") as f: json.dump(logs, f)
    except: pass

# ========== CORE AI FUNCTIONS - COPIED FROM YOUR APP.PY ==========
def ask_smart_brain(prompt, user_type="Student"):
    flagged = check_cheating(prompt)
    if flagged:
        return "⛔ Ministry Compliance: I cannot provide answers during an active exam. I can help you practice and learn the concept instead. Upload the topic and I’ll teach you."
    log_activity(user_type, "Smart Query", prompt[:50], flagged)
    messages = [{"role": "system", "content": SMART_SYSTEM}, {"role": "user", "content": prompt}]
    response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.3)
    return response.choices[0].message.content

def generate_lesson_plan(subject, topic, duration):
    log_activity("Admin", "Lesson Plan", f"{subject}-{topic}")
    prompt = f"Create a {duration} minute NCDC lesson plan for S1-S6 {subject} on {topic}. Include Objectives, Materials, Introduction, Development, Conclusion, Assessment. Use Ugandan context."
    messages = [{"role": "system", "content": EXAMINER_SYSTEM}, {"role": "user", "content": prompt}]
    response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.2)
    return response.choices[0].message.content

def generate_exam_items(subject, topic, count):
    log_activity("Admin", "Test Gen", f"{subject}-{topic}-{count}")
    prompt = f"Generate {count} UNEB-style ITEM/TASK/SCENARIO questions for S1-S6 {subject} on {topic}. Include marks."
    messages = [{"role": "system", "content": EXAMINER_SYSTEM}, {"role": "user", "content": prompt}]
    response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.4)
    return response.choices[0].message.content

def generate_practical(subject, topic):
    log_activity("Student", "Practical", f"{subject}-{topic}")
    prompt = f"Generate full NCDC practical for S1-S6 {subject} on {topic}. Include AIM, APPARATUS, PROCEDURE, DATA TABLE, CONCLUSION."
    messages = [{"role": "system", "content": SMART_SYSTEM}, {"role": "user", "content": prompt}]
    response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.3)
    return response.choices[0].message.content

def generate_report_card(student_name, scores_dict):
    log_activity("Admin", "Report Card", student_name)
    scores_text = "\n".join([f"{k}: {v}%" for k,v in scores_dict.items()])
    total = sum(scores_dict.values()); avg = total/len(scores_dict)
    prompt = f"Create professional NCDC Report Card for {student_name}. Scores:\n{scores_text}\nTotal: {total}, Average: {avg:.1f}%. Add grade, remarks, teacher comment, principal comment."
    messages = [{"role": "system", "content": EXAMINER_SYSTEM}, {"role": "user", "content": prompt}]
    response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.2)
    return response.choices[0].message.content
