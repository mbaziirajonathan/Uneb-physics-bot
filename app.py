import streamlit as st
import os, io, json, re, ast, pytz, numpy as np, tempfile, random
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime
from groq import Groq
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
import base64
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS

def check_password():
    def password_entered():
        try: correct_pw = st.secrets.get("APP_PASSWORD", "")
        except: st.error("APP_PASSWORD not found in secrets"); st.stop()
        if st.session_state["password"] == correct_pw: st.session_state["password_correct"] = True; del st.session_state["password"]
        else: st.session_state["password_correct"] = False
    if "password_correct" not in st.session_state: st.title("🔒 DIGITAL UNEB TUTOR 2026 - Login"); st.text_input("Enter Password", type="password", on_change=password_entered, key="password"); st.caption("Contact admin for access"); return False
    elif not st.session_state["password_correct"]: st.title("🔒 DIGITAL UNEB TUTOR 2026 - Login"); st.text_input("Enter Password", type="password", on_change=password_entered, key="password"); st.error("😞 Password incorrect"); return False
    else: return True
if not check_password(): st.stop()

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026", page_icon="📚", layout="wide", initial_sidebar_state="expanded")

PRACTICAL_TOPICS = {
    "Physics": ["Simple Pendulum - Finding g","Principle of Moments - Lever","Hooke's Law - Spring Constant","Density and Upthrust - Archimedes","Converging Lens - Focal Length","Glass Block - Refractive Index","Ohm's Law - V vs I Graph","Resistance vs Length - Wire","Specific Heat Capacity - Water","Electrostatics - Gold Leaf Electroscope"],
    "Chemistry": ["Acid-Base Titration - HCl vs NaOH","Back Titration - Purity of Na2CO3","Heat of Neutralization","Rates of Reaction - HCl + CaCO3","Qualitative Analysis - Cations","Qualitative Analysis - Anions","Gas Tests - H2, CO2, O2, NH3","Enthalpy Change - Dissolution","Electrolysis of Water","Preparation and Properties of Oxygen"],
    "Biology": ["Food Tests - Starch, Protein, Lipids","Osmosis in Potato Cylinders","Photosynthesis Rate - Elodea","Respiration in Germinating Seeds","Microscopy - Onion and Cheek Cells","Ecological Sampling - Quadrat","Transpiration - Potometer","Enzyme Activity - Catalase","Human Blood Smear - WBC Count","Germination Conditions - Seeds"]
}

UNEB_CURRICULUM_MAP = {"Physics": {"S1": ["Introduction to Physics", "Measurement", "Force", "Work, Energy and Power", "Pressure"],"S2": ["Current Electricity", "Light: Reflection", "Light: Refraction", "Waves", "Heat"],"S3": ["Hookes Law and Elasticity", "Specific Heat Capacity", "Magnetism", "Electrostatics", "Sound"],"S4": ["Transformers", "Electronics", "Nuclear Physics", "A.C Theory", "Cathode Rays and X-Rays", "Astrophysics"]},"Chemistry": {"S1": ["Introduction to Chemistry", "Structure of an Atom", "Chemical Bonding", "Periodic Table", "Chemical Formulas"],"S2": ["Water and Hydrogen", "Oxygen and Oxides", "Acids, Bases and Salts", "Metals", "Air and Combustion"],"S3": ["Rates of Reaction", "Energy Changes", "Organic Chemistry Intro", "Chemical Equations", "Mole Concept"],"S4": ["Electrochemistry", "Industrial Chemistry", "Organic Chemistry II", "Equilibrium", "Nuclear Chemistry"]},"Biology": {"S1": ["Introduction to Biology", "Plant Cell and Animal Cell", "Ecosystem", "Characteristics of Living Things", "Nutrition in Plants"],"S2": ["Circulatory System", "Photosynthesis", "Respiration", "Excretion", "Human Digestive System"],"S3": ["DNA and RNA", "Genetics", "Cell Division", "Ecology", "Reproduction in Plants"],"S4": ["Nervous System", "Immunity", "Human Reproductive System", "Evolution", "Environmental Conservation"]}}

DIAGRAM_FILES = {("Physics","S1","Measurement"): "assets/vernier.png",("Physics","S2","Current Electricity"): "assets/simple_circuit.png",("Physics","S3","Hookes Law and Elasticity"): "assets/hookes_law.png",("Physics","S4","Transformers"): "assets/ac_transformer.png",("Physics","S4","Astrophysics"): "assets/solar_system.png",("Biology","S1","Plant Cell and Animal Cell"): "assets/plant_cell.png",("Biology","S2","Photosynthesis"): "assets/photosynthesis.png",("Biology","S4","Nervous System"): "assets/neurone.png"}
SAMPLE_PAST_PAPERS = [{"subject":"Physics","topic":"Current Electricity","year":"2022","paper":"P2","question":"State Ohm's Law and write the formula."},{"subject":"Physics","topic":"Hookes Law and Elasticity","year":"2023","paper":"P2","question":"A spring extends by 0.05m when a force of 10N is applied. Find the spring constant."},{"subject":"Chemistry","topic":"Acids, Bases and Salts","year":"2021","paper":"P1","question":"Which of the following is a weak acid? A.HCl B.H2SO4 C.CH3COOH D.HNO3"},{"subject":"Chemistry","topic":"Rates of Reaction","year":"2023","paper":"P3","question":"Describe an experiment to investigate the effect of temperature on rate of reaction."},{"subject":"Biology","topic":"Photosynthesis","year":"2022","paper":"P2","question":"State 3 factors that affect the rate of photosynthesis."},{"subject":"Biology","topic":"Nervous System","year":"2023","paper":"P1","question":"Which part of the brain controls balance? A.Cerebrum B.Cerebellum C.Medulla D.Hypothalamus"}]

@st.cache_resource
def get_client():
    try: return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except: st.error("🚨 GROQ_API_KEY missing in secrets"); st.stop()

def safe_json_extract(text):
    if not text: return None, None
    match = re.search(r'```json(.*?)```', text, re.DOTALL)
    if not match: return None, None
    json_str = match.group(1).strip()
    try: return json.loads(json_str), match.group(0)
    except:
        try: return ast.literal_eval(json_str), match.group(0)
        except: return None, match.group(0)

def generate_default_data(topic):
    x_label, y_label = "Independent Variable", "Dependent Variable"
    data = [[i, round(random.uniform(i*2, i*2+5), 2)] for i in range(1,7)]
    if "Pendulum" in topic: x_label, y_label = "Length (m)", "Time^2 (s^2)"
    if "Ohm" in topic: x_label, y_label = "Current (A)", "Voltage (V)"
    if "Hooke" in topic: x_label, y_label = "Force (N)", "Extension (m)"
    if "Lens" in topic: x_label, y_label = "Object Distance (cm)", "Image Distance (cm)"
    if "Glass" in topic: x_label, y_label = "Angle of Incidence", "Angle of Refraction"
    if "Titration" in topic: x_label, y_label = "Volume of Base (cm3)", "pH"
    if "Photosynthesis" in topic: x_label, y_label = "Light Intensity", "Bubbles per minute"
    return {"x_label": x_label, "y_label": y_label, "data": data}

def calc_gradient(df, x, y):
    try: slope, intercept = np.polyfit(df[x], df[y], 1); return f"**Gradient = {slope:.3f}** | Equation: y = {slope:.3f}x + {intercept:.3f}"
    except: return ""

def render_graph(df, x, y, title):
    st.subheader("📈 Auto-Generated Graph")
    try:
        df[x] = pd.to_numeric(df[x], errors='coerce'); df[y] = pd.to_numeric(df[y], errors='coerce'); df = df.dropna()
        if len(df) < 2: st.warning("Not enough valid data points to plot."); return
        fig = px.scatter(df, x=x, y=y, title=title, trendline="ols", template="plotly_white"); fig.update_traces(marker=dict(size=9), line=dict(width=2)); fig.update_layout(xaxis_title=x, yaxis_title=y, height=380); st.plotly_chart(fig, use_container_width=True)
        gradient_text = calc_gradient(df, x, y)
        if gradient_text: st.info(gradient_text + " - Use this in calculations")
        buf = io.BytesIO(); plt.figure(figsize=(6,4)); plt.scatter(df[x], df[y]); z = np.polyfit(df[x], df[y], 1); p = np.poly1d(z); plt.plot(df[x],p(df[x]),"r--",alpha=0.8); plt.title(title); plt.xlabel(x); plt.ylabel(y); plt.grid(True); plt.savefig(buf, format="png", dpi=150); buf.seek(0)
        st.download_button("📥 Download Graph PNG", buf, f"{title}.png", "image/png")
    except Exception as e: st.error(f"Graph failed: {e}")

def validate_subject(text, subject):
    other_subjects = ["Physics", "Chemistry", "Biology"]
    other_subjects.remove(subject)
    for os in other_subjects:
        if f"UNEB {os}" in text or f"In {os}" in text: return False
    return True

def call_groq(client, messages, subject):
    for attempt in range(2):
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.1, max_tokens=1200)
        text = res.choices[0].message.content
        if validate_subject(text, subject) or attempt == 1: return text
    return text

def universal_search(client, query, subject, level, history):
    system = f"""ROLE: You are a UNEB {subject} tutor assistant for {level} Uganda NCDC 2026.
    RULES: 1. YOU ONLY TEACH {subject}. 2. IF QUESTION IS NOT ABOUT {subject}, SAY: "I only teach {subject}. Please select {subject} in the sidebar." 3. NEVER MENTION OTHER SUBJECTS. 4. BE EXAM FOCUSED."""
    user = f"SUBJECT: {subject} LEVEL: {level} TOPIC SEARCH: '{query}'. Answer in 5 bullets: 1.Definition 2.UNEB example 3.Formula 4.Common mistake 5.Quick tip. Use only {subject} examples."
    msgs = [{"role": "system", "content": system}] + history[-4:] + [{"role": "user", "content": user}]
    return call_groq(client, msgs, subject)

def explain_practical_detailed(client, subject, level, topic, history):
    system = f"ROLE: You are a UNEB {subject} examiner 2026. RULE: Only explain {subject} practicals following NCDC 2026 guidelines."
    user = f"SUBJECT: {subject} LEVEL: {level} PRACTICAL: {topic}. Provide: 1.DETAILED EXPLANATION of procedure 2.REQUIREMENTS/APPARATUS 3.RULES STUDENT MUST FOLLOW 4.CRITICAL POINTS TO SCORE FULL MARKS 5.GRAPH DESCRIPTION - how to draw, label axes, plot points, draw line of best fit 6.ILLUSTRATION EXAMPLE. Be specific for UNEB P3 2026."
    msgs = [{"role": "system", "content": system}] + history[-2:] + [{"role": "user", "content": user}]
    return call_groq(client, msgs, subject)

def explain_mistake(client, subject, level, question, wrong_answer, history):
    system = f"ROLE: You are a UNEB {subject} examiner for {level} Uganda. RULE: Only mark {subject} questions. Refuse other subjects."
    user = f"SUBJECT: {subject} Q: {question}\nStudent Wrong Answer: {wrong_answer}\nExplain: 1.Why wrong 2.What UNEB expects 3.How to get full marks 4.Related {subject} concept."
    msgs = [{"role": "system", "content": system}] + history[-2:] + [{"role": "user", "content": user}]
    return call_groq(client, msgs, subject)

def generate_quiz(client, subject, level, topic, history):
    system = f"ROLE: You are a UNEB {subject} tutor assistant 2026. RULE: Only generate {subject} questions."
    user = f"SUBJECT: {subject} LEVEL: {level} TOPIC: {topic}. Generate 10 MCQ. Format: Q1. Q? A. B. C. D. Answer: C. Only {subject} syllabus."
    msgs = [{"role": "system", "content": system}] + history[-2:] + [{"role": "user", "content": user}]
    return call_groq(client, msgs, subject)

def generate_marking_scheme(client, subject, level, question, student_answer, history):
    system = f"ROLE: You are a UNEB {subject} Head Examiner 2026 for {level}. RULE: Mark only {subject}."
    user = f"SUBJECT: {subject} Q: {question}\nStudent: {student_answer}\nGenerate: 1.MODEL ANSWER 2.MARKING GUIDE 3.COMMON MISTAKES 4.TIPS."
    msgs = [{"role": "system", "content": system}] + history[-2:] + [{"role": "user", "content": user}]
    return call_groq(client, msgs, subject)

@st.cache_data
def load_past_papers(): return SAMPLE_PAST_PAPERS
def search_past_papers(topic, subject): papers = load_past_papers(); return [q for q in papers if topic.lower() in q['topic'].lower() and q['subject']==subject]

def generate_apparatus_list(client, practical_topic, subject, history):
    system = f"ROLE: You are a UNEB {subject} lab technician. RULE: Only discuss {subject} practicals."
    user = f"SUBJECT: {subject} PRACTICAL: {practical_topic}. List apparatus for 40 students. Include cost in UGX and local alternatives."
    msgs = [{"role": "system", "content": system}] + [{"role": "user", "content": user}]
    return call_groq(client, msgs, subject)

def translate_explanation(client, text, language, subject, level, history):
    system = f"You are a translator for {subject} {level} Uganda."
    user = f"Translate this {subject} explanation to simple {language} for {level} students. Keep science terms English. Text: {text}"
    msgs = [{"role": "system", "content": system}] + [{"role": "user", "content": user}]
    return call_groq(client, msgs, subject)

def generate_inspector_report(school_name, activities_done):
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); w,h = A4; p.setFont("Helvetica-Bold",18); p.drawString(40,h-50,"DIGITAL UNEB TUTOR - ACTIVITY REPORT"); p.setFont("Helvetica",12); p.drawString(40,h-80,f"School: {school_name}"); p.drawString(40,h-100,f"Date: {datetime.now().strftime('%d/%m/%Y')}"); p.drawString(40,h-120,"Activities Conducted This Term:"); y=h-150
    for i, act in enumerate(activities_done,1):
        if y<100: p.showPage(); y=h-50
        p.drawString(50,y,f"{i}. {act}"); y-=20
    p.drawString(40,y-40,"Remarks: Digital support provided in line with Ministry Digital Agenda 2025-2032"); p.drawString(40,y-70,"Signed: __________________ Stamp: __________________"); p.save(); buffer.seek(0); return buffer

def generate_practical(client, subject, level, topic, history):
    system = f"ROLE: You are a UNEB {subject} examiner for {level} Uganda NCDC 2026. RULE: Only {subject} practicals."
    user = f"SUBJECT: {subject} TOPIC: {topic}. Generate complete practical report. Include AIM,HYPOTHESIS,VARIABLES,APPARATUS,PROCEDURE,SAFETY,DATA TABLE,GRAPH GUIDE,CONCLUSION. MUST END with JSON data: ```json {{\"x_label\": \"X\", \"y_label\": \"Y\", \"data\": [[1,2],[2,4],[3,6],[4,8],[5,10],[6,12]]}} ```"
    msgs = [{"role": "system", "content": system}] + [{"role": "user", "content": user}]
    return call_groq(client, msgs, subject)

def describe_and_draw_graph(client, prompt, subject, history):
    system = f"ROLE: You are a UNEB {subject} examiner Uganda 2026. RULE: Only {subject} graphs."
    user = f"SUBJECT: {subject} GRAPH: {prompt}. Return JSON then 3 UNEB marking points for {subject}."
    msgs = [{"role": "system", "content": system}] + [{"role": "user", "content": user}]
    return call_groq(client, msgs, subject)

def describe_uploaded_graph(client, image_bytes, subject):
    b64 = base64.b64encode(image_bytes).decode(); system = f"ROLE: You are a UNEB {subject} examiner. RULE: Analyze only {subject} graphs."; user = f"SUBJECT: {subject} Describe this graph image and tell me what {subject} experiment it represents for UNEB Uganda 2026."
    res = client.chat.completions.create(model="llama-3.2-11b-vision-preview", messages=[{"role":"system","content":system},{"role":"user","content":[{"type":"text","text":user},{"type":"image_url","image_url":{"url":f"data:image/png;base64,{b64}"}}]}], temperature=0.2, max_tokens=800)
    return res.choices[0].message.content

def voice_chat(client, audio_bytes, subject, level, history):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp: tmp.write(audio_bytes); tmp_path = tmp.name
    with open(tmp_path, "rb") as audio_file: transcription = client.audio.transcriptions.create(file=audio_file, model="whisper-large-v3")
    user_text = transcription.text; system = f"ROLE: You are a UNEB {subject} tutor assistant for {level} Uganda NCDC 2026. RULE: Only answer {subject}."
    msgs = [{"role": "system", "content": system}] + history[-2:] + [{"role": "user", "content": f"SUBJECT: {subject} Question: {user_text}. Answer in 4 sentences max."}]
    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=msgs, temperature=0.3, max_tokens=300)
    answer_text = res.choices[0].message.content; tts = gTTS(text=answer_text, lang='en'); audio_buf = io.BytesIO(); tts.write_to_fp(audio_buf); audio_buf.seek(0)
    return user_text, answer_text, audio_buf

def generate_prediction(client, subject, paper, history):
    system = f"ROLE: You are a UNEB {subject} Head of Examinations 2026. RULE: Only {subject} papers."
    prompts = {"P1": f"SUBJECT: {subject} Generate 40 MCQ for {subject} Paper 1. Mix {subject} topics S1-S4. 4 options A-D. NCDC 2026. Mark answers.","P2": f"SUBJECT: {subject} Generate 5 Theory questions for {subject} Paper 2. S3-S4. Include 2 calculations, 1 diagram. 10 marks each. Marking guide.","P3": f"SUBJECT: {subject} Generate 3 Practical scenarios for {subject} Paper 3. Competency-based NCDC 2026. Include apparatus."}
    msgs = [{"role": "system", "content": system}] + [{"role": "user", "content": prompts[paper]}]
    return call_groq(client, msgs, subject)

def create_pdf(topic, subject, level, notes):
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); w,h = A4; p.setFont("Helvetica-Bold",16); p.drawString(40,h-50,f"UNEB 2026: {subject} {level}"); p.drawString(40,h-75,f"Topic: {topic}"); p.setFont("Helvetica",10); y=h-110; p.drawString(40,y,"Key Notes:"); y-=20
    for line in notes.split('\n'):
        if y<100: p.showPage(); y=h-50
        p.drawString(50,y,f"• {line[:90]}"); y-=15
    p.save(); buffer.seek(0); return buffer

def ask_box(client, key, subject, level):
    st.text_input("❓ Ask anything about this:", key=f"ask_{key}")
    if st.button("Ask Tutor", key=f"btn_{key}"):
        query = st.session_state[f"ask_{key}"]
        if query:
            with st.spinner("Thinking..."):
                answer = universal_search(client, query, subject, level, st.session_state.chat_history)
                st.success(answer); st.session_state.chat_history.append({"role":"user","content":query}); st.session_state.chat_history.append({"role":"assistant","content":answer})
                c1,c2 = st.columns(2)
                with c1:
                    if st.button("🌍 Luganda", key=f"lug_{key}"): st.info(translate_explanation(client, answer, "Luganda", subject, level, st.session_state.chat_history))
                with c2:
                    if st.button("🌍 Swahili", key=f"swa_{key}"): st.info(translate_explanation(client, answer, "Swahili", subject, level, st.session_state.chat_history))

def main():
    client = get_client()
    if "activities_log" not in st.session_state: st.session_state.activities_log = []
    if "chat_history" not in st.session_state: st.session_state.chat_history = []

    st.sidebar.title("📚 DIGITAL UNEB TUTOR 2026")
    mode = st.sidebar.radio("Mode", ["🔍 Smart Search", "📖 Learn Theory", "🧪 Practicals Lab", "📈 Graph Describer", "🎙️ Voice Chat", "📝 Quiz Mode", "🧠 Mistake Explainer", "💬 Chat Memory", "🔮 Predict Papers", "🛠️ Teacher Tools"])
    subject = st.sidebar.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
    level = st.sidebar.selectbox("Class Level", ["S1","S2","S3","S4"])
    st.session_state.subject = subject; st.session_state.level = level
    tz = pytz.timezone("Africa/Kampala"); st.sidebar.divider(); st.sidebar.caption(f"Kampala: {datetime.now(tz).strftime('%A %H:%M %p')}")

    if mode == "🔍 Smart Search":
        st.title("🔍 Smart Search - Ask Anything")
        search_q = st.text_input("Search:", placeholder="e.g. Ohm's Law formula, Acid and Bases, Photosynthesis graph, Glass Block practical")
        if st.button("Search", use_container_width=True):
            if search_q:
                with st.spinner("Searching UNEB database..."):
                    result = universal_search(client, search_q, subject, level, st.session_state.chat_history)
                    st.markdown(result); st.session_state.chat_history.append({"role":"user","content":search_q}); st.session_state.chat_history.append({"role":"assistant","content":result}); st.session_state.activities_log.append(f"Searched {subject}: {search_q}")

    elif mode == "📖 Learn Theory":
        st.title(f"Theory: {subject} {level}"); topic = st.sidebar.selectbox("Topic", UNEB_CURRICULUM_MAP[subject][level]); col1,col2 = st.columns([1.2,1])
        with col1:
            if st.button("Generate UNEB Notes", use_container_width=True):
                with st.spinner("Generating notes..."):
                    prompt = f"ROLE: UNEB {subject} tutor. SUBJECT: {subject} LEVEL: {level} TOPIC: {topic}. Give 6 concise UNEB exam notes. NCDC Uganda syllabus 2026. Competency based."
                    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are UNEB {subject} tutor only."},{"role":"user","content":prompt}], max_tokens=400); st.session_state.notes = res.choices[0].message.content; st.session_state.activities_log.append(f"Generated {subject} notes for {topic}")
            st.divider()
            if st.button("🔍 Get 5 UNEB Past Paper Questions", use_container_width=True):
                papers = search_past_papers(topic, subject)
                if papers: st.success(f"Found {len(papers)} past questions"); [st.markdown(f"**{p['year']} {p['paper']}**: {p['question']}") for p in papers]
                else: st.info("No past papers yet for this topic.")
            st.divider(); ask_box(client, "theory", subject, level)
            if "notes" in st.session_state: st.markdown("### Key Notes"); st.markdown(st.session_state.notes); pdf = create_pdf(topic,subject,level,st.session_state.notes); st.download_button("📄 Download PDF",pdf,f"UNEB_{subject}_{level}_{topic}.pdf", use_container_width=True)
        with col2: key = (subject,level,topic)
        if key in DIAGRAM_FILES and os.path.exists(DIAGRAM_FILES[key]): st.image(DIAGRAM_FILES[key], caption=topic, use_column_width=True)
        else: st.info("No diagram for this topic yet")

    elif mode == "🧪 Practicals Lab":
        st.title(f"🧪 Practicals Lab: {subject} {level}"); st.warning("Master these 10 topics. They repeat every year in UNEB P3.")
        topic = st.sidebar.selectbox("Select Practical", PRACTICAL_TOPICS[subject], key="practical_topic")
        st.divider()
        if st.button(f"📖 Explain Full Practical: {topic}", use_container_width=True):
            with st.spinner("Generating detailed explanation..."):
                explanation = explain_practical_detailed(client, subject, level, topic, st.session_state.chat_history)
                st.markdown(explanation); st.session_state.activities_log.append(f"Explained {subject} Practical: {topic}")
        st.divider()
        if st.button(f"💰 Get Apparatus & Budget: {topic}", use_container_width=True):
            with st.spinner("Calculating budget..."): budget = generate_apparatus_list(client, topic, subject, st.session_state.chat_history); st.markdown(budget); st.session_state.activities_log.append(f"Budget for {subject}: {topic}")
        st.divider()
        if st.button(f"Generate Full Report + Graph: {topic}", use_container_width=True):
            with st.spinner("System generating full UNEB report..."):
                report = generate_practical(client,subject,level,topic, st.session_state.chat_history)
                data, json_block = safe_json_extract(report)
                if not data or "data" not in data:
                    st.warning("AI failed to generate data. Using default data so graph works.")
                    data = generate_default_data(topic)
                try:
                    df = pd.DataFrame(data["data"], columns=[data["x_label"], data["y_label"]])
                    st.dataframe(df, use_container_width=True)
                    render_graph(df,data["x_label"],data["y_label"],topic)
                except Exception as e: st.warning(f"Could not parse data table: {e}")
                st.markdown(report.replace(json_block,"") if json_block else report)
                st.session_state.activities_log.append(f"{subject} Practical report: {topic}")
        st.divider(); ask_box(client, "practical", subject, level)

    elif mode == "📈 Graph Describer":
        st.title("📈 Graph Describer & Drawer"); tab1, tab2 = st.tabs(["✍️ Describe Graph", "🖼️ Upload Graph Image"])
        with tab1:
            user_graph = st.text_area("Describe the graph you need:", height=100, key="desc_text")
            if st.button("Generate & Draw Graph", use_container_width=True, key="btn_desc"):
                if not user_graph.strip(): st.warning("Please describe a graph first.")
                else:
                    with st.spinner("Generating graph..."):
                        result = describe_and_draw_graph(client, user_graph, subject, st.session_state.chat_history); data, json_block = safe_json_extract(result)
                        if not data or "data" not in data: data = generate_default_data(user_graph)
                        try: df = pd.DataFrame(data["data"], columns=[data["x_label"], data["y_label"]]); st.dataframe(df, use_container_width=True); render_graph(df, data["x_label"], data["y_label"], user_graph)
                        except Exception as e: st.error(f"Failed to draw: {e}")
                        st.markdown("### Explanation"); st.markdown(result.replace(json_block,"") if json_block else result); st.session_state.activities_log.append(f"{subject} Graph: {user_graph}")
            st.divider(); ask_box(client, "graph", subject, level)
        with tab2:
            uploaded_file = st.file_uploader("Choose an image", type=["png","jpg","jpeg"], key="img_upload")
            if uploaded_file: image = Image.open(uploaded_file); st.image(image, caption="Uploaded Graph", use_column_width=True)
            if st.button("Analyze Graph", use_container_width=True, key="btn_analyze"):
                with st.spinner("Analyzing image..."): image_bytes = uploaded_file.getvalue(); result = describe_uploaded_graph(client, image_bytes, subject); st.markdown("### Analysis"); st.markdown(result)

    elif mode == "🎙️ Voice Chat":
        st.title("🎙️ Voice Chat Tutor"); st.write(f"Talk to the tutor about {subject} {level}.")
        audio = mic_recorder(start_prompt="🎤 Hold to Record", stop_prompt="⏹️ Stop", key='recorder')
        if audio: st.audio(audio['bytes'])
        with st.spinner("Listening and processing..."):
            user_q, tutor_a, tutor_audio = voice_chat(client, audio['bytes'], subject, level, st.session_state.chat_history)
        if user_q: st.markdown(f"**You:** {user_q}"); st.markdown(f"**UNEB {subject} Tutor:** {tutor_a}"); st.session_state.chat_history.append({"role":"user","content":user_q}); st.session_state.chat_history.append({"role":"assistant","content":tutor_a});
        if tutor_audio: st.audio(tutor_audio, format="audio/mp3")

    elif mode == "📝 Quiz Mode":
        st.title(f"📝 UNEB Quiz Mode: {subject} {level}"); topic = st.selectbox("Select Topic for Quiz", UNEB_CURRICULUM_MAP[subject][level])
        if st.button("Generate 10 MCQ Quiz", use_container_width=True):
            with st.spinner("Generating quiz..."): quiz = generate_quiz(client, subject, level, topic, st.session_state.chat_history); st.markdown(quiz); st.session_state.activities_log.append(f"Generated {subject} Quiz: {topic}")
        st.divider(); ask_box(client, "quiz", subject, level)

    elif mode == "🧠 Mistake Explainer":
        st.title(f"🧠 Mistake Explainer: {subject} {level}"); st.write("Paste student wrong answer. I will explain why it's wrong and how to score 10/10")
        qn = st.text_area("UNEB Question:"); wrong = st.text_area("Student Wrong Answer:")
        if st.button("Explain Mistake", use_container_width=True):
            if qn and wrong:
                with st.spinner("Analyzing..."): explanation = explain_mistake(client, subject, level, qn, wrong, st.session_state.chat_history); st.error(explanation); st.session_state.activities_log.append(f"Explained mistake in {subject}")
            else: st.warning("Enter both question and answer")

    elif mode == "💬 Chat Memory":
        st.title("💬 Chat Memory - Yesterday's Explanations")
        mem_q = st.text_input("Search Memory:", placeholder="e.g. what did we say about titration")
        if st.button("Recall", use_container_width=True):
            if mem_q:
                context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history[-10:]])
                with st.spinner("Searching memory..."):
                    result = universal_search(client, f"Based on this chat history: {context}. Now answer: {mem_q}", subject, level, [])
                    st.markdown(result)

    elif mode == "🔮 Predict Papers":
        st.title(f"🔮 UNEB 2026 Prediction: {subject}"); st.info("Predictions based on UNEB trends 2016-2023 + NCDC 2026.")
        c1,c2,c3 = st.columns(3)
        with c1:
            if st.button("Generate P1 MCQ", use_container_width=True):
                with st.spinner("..."): st.session_state.p1 = generate_prediction(client,subject,"P1", st.session_state.chat_history); st.session_state.activities_log.append(f"Generated {subject} P1")
            if "p1" in st.session_state: st.text_area("Paper 1", st.session_state.p1, height=400)
        with c2:
            if st.button("Generate P2 Theory", use_container_width=True):
                with st.spinner("..."): st.session_state.p2 = generate_prediction(client,subject,"P2", st.session_state.chat_history); st.session_state.activities_log.append(f"Generated {subject} P2")
            if "p2" in st.session_state: st.text_area("Paper 2", st.session_state.p2, height=400)
        with c3:
            if st.button("Generate P3 Practical", use_container_width=True):
                with st.spinner("..."): st.session_state.p3 = generate_prediction(client,subject,"P3", st.session_state.chat_history); st.session_state.activities_log.append(f"Generated {subject} P3")
            if "p3" in st.session_state: st.text_area("Paper 3", st.session_state.p3, height=400)

    elif mode == "🛠️ Teacher Tools":
        st.title("🛠️ Teacher Support Tools"); tab1, tab2 = st.tabs(["📝 Marking Helper", "📄 Inspector Report"])
        with tab1: qn = st.text_area("Paste UNEB Question:", height=100); ans = st.text_area("Paste Student Answer (optional):", height=100)
        if st.button("Generate Marking Scheme"):
            if qn:
                with st.spinner("Generating marking guide..."): scheme = generate_marking_scheme(client, subject, level, qn, ans, st.session_state.chat_history); st.markdown(scheme); st.session_state.activities_log.append(f"{subject} Marking scheme")
            else: st.warning("Please enter a question")
        with tab2: school = st.text_input("School Name:", value="Nabiswera Progressive SS")
        if st.button("Generate PDF Report"):
            if st.session_state.activities_log: pdf = generate_inspector_report(school, st.session_state.activities_log); st.download_button("📥 Download Activity Report", pdf, f"Report_{school}.pdf")
            else: st.warning("No activities logged yet.")

if __name__ == "__main__": main()
