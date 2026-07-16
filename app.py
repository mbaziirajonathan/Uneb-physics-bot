import streamlit as st
import os, io, json, re, ast, pytz, numpy as np, tempfile
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime
from groq import Groq, GroqError
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
import base64
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS

# ============ PASSWORD GATE ============
def check_password():
    def password_entered():
        try:
            correct_pw = st.secrets.get("APP_PASSWORD", "")
        except:
            st.error("APP_PASSWORD not found in secrets")
            st.stop()

        if st.session_state["password"] == correct_pw:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔒 DIGITAL UNEB TUTOR 2026 - Login")
        st.text_input("Enter Password", type="password", on_change=password_entered, key="password")
        st.caption("Contact admin for access")
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔒 DIGITAL UNEB TUTOR 2026 - Login")
        st.text_input("Enter Password", type="password", on_change=password_entered, key="password")
        st.error("😞 Password incorrect")
        return False
    else:
        return True

if not check_password():
    st.stop()
# ============ END PASSWORD GATE ============

st.set_page_config(page_title="DIGITAL UNEB TUTOR 2026", page_icon="📚", layout="centered", initial_sidebar_state="expanded")

# FULL NCDC 2026 SYLLABUS - S1 TO S4
PRACTICAL_TOPICS = {
    "Physics": ["Simple Pendulum - Finding g", "Principle of Moments", "Hooke's Law", "Density and Upthrust", "Converging Lens - Focal Length", "Glass Block - Refractive Index", "Ohm's Law - V vs I", "Resistance vs Length"],
    "Chemistry": ["Acid-Base Titration", "Back Titration - Purity", "Heat of Neutralization", "Rates of Reaction", "Qualitative Analysis - Cations", "Qualitative Analysis - Anions", "Gas Tests", "Enthalpy Change"],
    "Biology": ["Food Tests", "Osmosis in Potato", "Photosynthesis Rate", "Respiration in Seeds", "Microscopy - Cells", "Ecological Sampling", "Transpiration - Potometer", "Enzyme Activity"]
}

# UPDATED TO FULL NCDC 2026 CURRICULUM + ASTROPHYSICS S4
UNEB_CURRICULUM_MAP = {
    "Physics": {
        "S1": ["Introduction to Physics", "Measurement", "Force", "Work, Energy and Power", "Pressure"],
        "S2": ["Current Electricity", "Light: Reflection", "Light: Refraction", "Waves", "Heat"],
        "S3": ["Hookes Law and Elasticity", "Specific Heat Capacity", "Magnetism", "Electrostatics", "Sound"],
        "S4": ["Transformers", "Electronics", "Nuclear Physics", "A.C Theory", "Cathode Rays and X-Rays", "Astrophysics"]
    },
    "Chemistry": {
        "S1": ["Introduction to Chemistry", "Structure of an Atom", "Chemical Bonding", "Periodic Table", "Chemical Formulas"],
        "S2": ["Water and Hydrogen", "Oxygen and Oxides", "Acids, Bases and Salts", "Metals", "Air and Combustion"],
        "S3": ["Rates of Reaction", "Energy Changes", "Organic Chemistry Intro", "Chemical Equations", "Mole Concept"],
        "S4": ["Electrochemistry", "Industrial Chemistry", "Organic Chemistry II", "Equilibrium", "Nuclear Chemistry"]
    },
    "Biology": {
        "S1": ["Introduction to Biology", "Plant Cell and Animal Cell", "Ecosystem", "Characteristics of Living Things", "Nutrition in Plants"],
        "S2": ["Circulatory System", "Photosynthesis", "Respiration", "Excretion", "Human Digestive System"],
        "S3": ["DNA and RNA", "Genetics", "Cell Division", "Ecology", "Reproduction in Plants"],
        "S4": ["Nervous System", "Immunity", "Human Reproductive System", "Evolution", "Environmental Conservation"]
    }
}

DIAGRAM_FILES = {
    ("Physics","S1","Measurement"): "assets/vernier.png",
    ("Physics","S2","Current Electricity"): "assets/simple_circuit.png",
    ("Physics","S3","Hookes Law and Elasticity"): "assets/hookes_law.png",
    ("Physics","S4","Transformers"): "assets/ac_transformer.png",
    ("Physics","S4","Astrophysics"): "assets/solar_system.png",
    ("Biology","S1","Plant Cell and Animal Cell"): "assets/plant_cell.png",
    ("Biology","S2","Photosynthesis"): "assets/photosynthesis.png",
    ("Biology","S4","Nervous System"): "assets/neurone.png"
}

# SAMPLE UNEB PAST PAPERS
SAMPLE_PAST_PAPERS = [
    {"subject":"Physics","topic":"Current Electricity","year":"2022","paper":"P2","question":"State Ohm's Law and write the formula."},
    {"subject":"Physics","topic":"Hookes Law and Elasticity","year":"2023","paper":"P2","question":"A spring extends by 0.05m when a force of 10N is applied. Find the spring constant."},
    {"subject":"Chemistry","topic":"Acids, Bases and Salts","year":"2021","paper":"P1","question":"Which of the following is a weak acid? A.HCl B.H2SO4 C.CH3COOH D.HNO3"},
    {"subject":"Chemistry","topic":"Rates of Reaction","year":"2023","paper":"P3","question":"Describe an experiment to investigate the effect of temperature on rate of reaction."},
    {"subject":"Biology","topic":"Photosynthesis","year":"2022","paper":"P2","question":"State 3 factors that affect the rate of photosynthesis."},
    {"subject":"Biology","topic":"Nervous System","year":"2023","paper":"P1","question":"Which part of the brain controls balance? A.Cerebrum B.Cerebellum C.Medulla D.Hypothalamus"}
]

@st.cache_resource
def get_client():
    try:
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except:
        st.error("🚨 GROQ_API_KEY missing in secrets. Add it to Streamlit Cloud Settings > Secrets"); st.stop()

def safe_json_extract(text):
    if not text: return None, None
    match = re.search(r'```json(.*?)```', text, re.DOTALL)
    if not match: return None, None
    json_str = match.group(1).strip()
    try: return json.loads(json_str), match.group(0)
    except:
        try: return ast.literal_eval(json_str), match.group(0)
        except: return None, match.group(0)

def calc_gradient(df, x, y):
    try:
        slope, intercept = np.polyfit(df[x], df[y], 1)
        return f"**Gradient = {slope:.3f}** | Equation: y = {slope:.3f}x + {intercept:.3f}"
    except: return ""

def render_graph(df, x, y, title):
    st.subheader("📈 Auto-Generated Graph")
    try:
        df[x] = pd.to_numeric(df[x], errors='coerce')
        df[y] = pd.to_numeric(df[y], errors='coerce')
        df = df.dropna()
        if len(df) < 2: st.warning("Not enough valid data points to plot."); return

        fig = px.scatter(df, x=x, y=y, title=title, trendline="ols", template="plotly_white")
        fig.update_traces(marker=dict(size=9), line=dict(width=2))
        fig.update_layout(xaxis_title=x, yaxis_title=y, height=380)
        st.plotly_chart(fig, use_container_width=True)

        gradient_text = calc_gradient(df, x, y)
        if gradient_text: st.info(gradient_text + " - Use this in calculations")

        buf = io.BytesIO()
        plt.figure(figsize=(6,4)); plt.scatter(df[x], df[y])
        z = np.polyfit(df[x], df[y], 1); p = np.poly1d(z)
        plt.plot(df[x],p(df[x]),"r--",alpha=0.8)
        plt.title(title); plt.xlabel(x); plt.ylabel(y); plt.grid(True)
        plt.savefig(buf, format="png", dpi=150); buf.seek(0)
        st.download_button("📥 Download Graph PNG", buf, f"{title}.png", "image/png")
    except Exception as e:
        st.error(f"Graph failed: {e}")

# ============ NEW: UNIVERSAL SEARCH ENGINE ============
def universal_search(client, query, subject, level):
    prompt = f"""You are a UNEB {subject} tutor for {level} Uganda NCDC 2026.
    Student searched: "{query}"
    Answer directly in 5 bullet points max. Include: 1. Definition 2. UNEB example 3. Formula if any 4. Common mistake 5. Quick tip.
    Be exam focused. No filler."""
    try:
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], temperature=0.3, max_tokens=500)
        return res.choices[0].message.content
    except GroqError as e: return f"System Error: {e}"

# ============ NEW: QUIZ MODE ============
def generate_quiz(client, subject, level, topic):
    prompt = f"""You are UNEB examiner 2026. Generate 10 MCQ for {subject} {level} on topic: {topic}.
    Format strictly: Q1. Question? A. B. C. D. Answer: C
    Mix easy, medium, hard. NCDC 2026 Uganda."""
    try:
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], temperature=0.7, max_tokens=1200)
        return res.choices[0].message.content
    except GroqError as e: return f"System Error: {e}"

# ============ FEATURE 1: MARKING SCHEME ============
def generate_marking_scheme(client, subject, level, question, student_answer=""):
    prompt = f"""You are UNEB Head Examiner 2026 for {subject} {level} Uganda NCDC.
    Question: {question}
    Student Answer: {student_answer if student_answer else 'N/A'}
    Generate: 1. MODEL ANSWER 2. MARKING GUIDE: 1 mark points. Total 10 marks. 3. COMMON MISTAKES 4. TIPS TO SCORE 10/10
    Use official UNEB marking style."""
    try:
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], temperature=0.2, max_tokens=800)
        return res.choices[0].message.content
    except GroqError as e: return f"System Error: {e}"

# ============ FEATURE 2: PAST PAPERS ============
@st.cache_data
def load_past_papers():
    return SAMPLE_PAST_PAPERS

def search_past_papers(topic, subject):
    papers = load_past_papers()
    results = [q for q in papers if topic.lower() in q['topic'].lower() and q['subject']==subject]
    return results

# ============ FEATURE 3: APPARATUS BUDGET ============
def generate_apparatus_list(client, practical_topic):
    prompt = f"""For UNEB Uganda {practical_topic}, list all apparatus needed for a class of 40 students.
    Format: 1. List with quantity 2. Estimated cost in UGX per item 3. Total cost 4. Local cheap alternatives.
    Be realistic for Ugandan schools 2026."""
    try:
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], temperature=0.3, max_tokens=600)
        return res.choices[0].message.content
    except GroqError as e: return f"System Error: {e}"

# ============ FEATURE 4: LANGUAGE TRANSLATION ============
def translate_explanation(client, text, language="Luganda"):
    prompt = f"Translate this {st.session_state.subject} explanation to simple {language} for {st.session_state.level} students in Uganda. Keep science terms in English. Text: {text}"
    try:
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], temperature=0.5, max_tokens=400)
        return res.choices[0].message.content
    except GroqError as e: return f"System Error: {e}"

# ============ FEATURE 5: INSPECTOR REPORT ============
def generate_inspector_report(school_name, activities_done):
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); w,h = A4
    p.setFont("Helvetica-Bold",18); p.drawString(40,h-50,"DIGITAL UNEB TUTOR - ACTIVITY REPORT")
    p.setFont("Helvetica",12); p.drawString(40,h-80,f"School: {school_name}")
    p.drawString(40,h-100,f"Date: {datetime.now().strftime('%d/%m/%Y')}")
    p.drawString(40,h-120,"Activities Conducted This Term:")
    y=h-150
    for i, act in enumerate(activities_done,1):
        if y<100: p.showPage(); y=h-50
        p.drawString(50,y,f"{i}. {act}"); y-=20
    p.drawString(40,y-40,"Remarks: Digital support provided in line with Ministry Digital Agenda 2025-2032")
    p.drawString(40,y-70,"Signed: __________________ Stamp: __________________")
    p.save(); buffer.seek(0); return buffer

def generate_practical(client, subject, level, topic):
    prompt = f"""You are a UNEB examiner for {subject} {level} Uganda NCDC 2026. Generate a complete practical report for: {topic}.
    Format strictly:
    1. AIM 2. HYPOTHESIS 3. VARIABLES: Independent, Dependent, 3 Controlled 4. APPARATUS 5. PROCEDURE 6. SAFETY PRECAUTIONS 7. DATA TABLE 8. GRAPH GUIDE 9. CONCLUSION
    At the end include realistic mock data in this exact JSON: ```json {{"x_label": "X", "y_label": "Y", "data": [[1,2],[2,4],[3,6],[4,8],[5,10],[6,12]]}} ```
    Use competency-based curriculum. 6 data points."""
    try:
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], temperature=0.2, max_tokens=2000)
        return res.choices[0].message.content
    except GroqError as e: return f"System Error: {e}"

def describe_and_draw_graph(client, prompt):
    sys_prompt = "You are a UNEB examiner Uganda 2026. Return ONLY realistic data for that experiment."
    user_prompt = f"Describe and generate data for this graph: {prompt}. Return format: ```json {{\"x_label\": \"X axis\", \"y_label\": \"Y axis\", \"data\": [[x1,y1],[x2,y2],[x3,y3],[x4,y4],[x5,y5],[x6,y6]]}} ``` Then give 3 UNEB marking points."
    try:
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":sys_prompt},{"role":"user","content":user_prompt}], temperature=0.3, max_tokens=1200)
        return res.choices[0].message.content
    except GroqError as e: return f"System Error: {e}"

def describe_uploaded_graph(client, image_bytes):
    b64 = base64.b64encode(image_bytes).decode()
    sys_prompt = "You are a UNEB examiner. Analyze this student graph image. Describe what the graph shows, identify axes, trend, and give 3 UNEB marking points."
    user_prompt = f"Describe this graph image and tell me what experiment it likely represents for UNEB Uganda 2026."
    try:
        res = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {"role":"system","content":sys_prompt},
                {"role":"user","content":[
                    {"type":"text","text":user_prompt},
                    {"type":"image_url","image_url":{"url":f"data:image/png;base64,{b64}"}}
                ]}
            ],
            temperature=0.3, max_tokens=800
        )
        return res.choices[0].message.content
    except GroqError as e: return f"Vision System Error: {e}"

def voice_chat(client, audio_bytes):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        with open(tmp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(file=audio_file, model="whisper-large-v3")
        user_text = transcription.text

        llm_prompt = f"You are a UNEB {st.session_state.subject} tutor for {st.session_state.level} Uganda NCDC 2026. Answer concisely in 4 sentences max. Question: {user_text}"
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":llm_prompt}], temperature=0.5, max_tokens=300)
        answer_text = res.choices[0].message.content

        tts = gTTS(text=answer_text, lang='en')
        audio_buf = io.BytesIO()
        tts.write_to_fp(audio_buf)
        audio_buf.seek(0)

        return user_text, answer_text, audio_buf
    except Exception as e:
        return "", f"Voice Error: {e}", None

def generate_prediction(client, subject, paper):
    prompts = {
        "P1": f"You are UNEB Head of Examinations 2026. Generate 40 MCQ for {subject} Paper 1. Mix S1-S4. Include Astrophysics for Physics. 4 options A-D. NCDC Syllabus 2026. Mark answers at end.",
        "P2": f"You are UNEB Head 2026. Generate 5 Theory questions for {subject} Paper 2. S3-S4. Include Astrophysics for Physics. Include 2 calculations, 1 diagram question. 10 marks each. Provide marking guide.",
        "P3": f"You are UNEB Head 2026. Generate 3 Practical scenarios for {subject} Paper 3. Competency-based NCDC 2026. Include apparatus and method."
    }
    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompts[paper]}], temperature=0.7, max_tokens=1600)
    return res.choices[0].message.content

def create_pdf(topic, subject, level, notes):
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); w,h = A4
    p.setFont("Helvetica-Bold",16); p.drawString(40,h-50,f"UNEB 2026: {subject} {level}"); p.drawString(40,h-75,f"Topic: {topic}")
    p.setFont("Helvetica",10); y=h-110; p.drawString(40,y,"Key Notes:"); y-=20
    for line in notes.split('\n'):
        if y<100: p.showPage(); y=h-50
        p.drawString(50,y,f"• {line[:90]}"); y-=15
    p.save(); buffer.seek(0); return buffer

def ask_box(client, context, key):
    st.text_input("❓ Ask anything about this:", key=f"ask_{key}")
    if st.button("Ask Tutor", key=f"btn_{key}"):
        query = st.session_state[f"ask_{key}"]
        if query:
            with st.spinner("Thinking..."):
                answer = universal_search(client, query, st.session_state.subject, st.session_state.level)
                st.success(answer)
                c1,c2 = st.columns(2)
                with c1:
                    if st.button("🌍 Luganda", key=f"lug_{key}"): st.info(translate_explanation(client, answer, "Luganda"))
                with c2:
                    if st.button("🌍 Swahili", key=f"swa_{key}"): st.info(translate_explanation(client, answer, "Swahili"))

def main():
    client = get_client()
    if "activities_log" not in st.session_state: st.session_state.activities_log = []

    st.sidebar.title("📚 DIGITAL UNEB TUTOR 2026")
    mode = st.sidebar.radio("Mode", ["🔍 Smart Search", "📖 Learn Theory", "🧪 Practicals Lab", "📈 Graph Describer", "🎙️ Voice Chat", "📝 Quiz Mode", "🔮 Predict Papers", "🛠️ Teacher Tools"])
    subject = st.sidebar.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
    level = st.sidebar.selectbox("Class Level", ["S1","S2","S3","S4"])
    st.session_state.subject = subject
    st.session_state.level = level
    tz = pytz.timezone("Africa/Kampala"); st.sidebar.divider(); st.sidebar.caption(f"Kampala: {datetime.now(tz).strftime('%A %H:%M %p')}")

    # ============ NEW MODE: SMART SEARCH ============
    if mode == "🔍 Smart Search":
        st.title("🔍 Smart Search - Ask Anything")
        st.write("Don't scroll. Just type what you need. UNEB, Practical, Graph, Formula...")
        search_q = st.text_input("Search:", placeholder="e.g. Ohm's Law formula, Photosynthesis graph, Acid base titration")
        if st.button("Search", use_container_width=True):
            if search_q:
                with st.spinner("Searching UNEB database..."):
                    result = universal_search(client, search_q, subject, level)
                    st.markdown(result)
                    st.session_state.activities_log.append(f"Searched: {search_q}")

    elif mode == "📖 Learn Theory":
        st.title(f"Theory: {subject} {level}")
        topic = st.sidebar.selectbox("Topic", UNEB_CURRICULUM_MAP[subject][level])
        col1,col2 = st.columns([1.2,1])
        with col1:
            if st.button("Generate UNEB Notes", use_container_width=True):
                with st.spinner("Generating notes..."):
                    prompt = f"Give 6 concise UNEB {level} exam notes for {subject} topic: {topic}. NCDC Uganda syllabus 2026. Competency based."
                    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], max_tokens=400)
                    st.session_state.notes = res.choices[0].message.content
                    st.session_state.activities_log.append(f"Generated notes for {topic}")

            # FEATURE 2: PAST PAPERS
            st.divider()
            if st.button("🔍 Get 5 UNEB Past Paper Questions", use_container_width=True):
                papers = search_past_papers(topic, subject)
                if papers:
                    st.success(f"Found {len(papers)} past questions")
                    for p in papers: st.markdown(f"**{p['year']} {p['paper']}**: {p['question']}")
                else: st.info("No past papers yet for this topic.")

            # ASK BOX HERE
            st.divider()
            ask_box(client, f"Theory: {topic}", "theory")

            if "notes" in st.session_state:
                st.markdown("### Key Notes")
                st.markdown(st.session_state.notes)
                pdf = create_pdf(topic,subject,level,st.session_state.notes)
                st.download_button("📄 Download PDF",pdf,f"UNEB_{subject}_{level}_{topic}.pdf", use_container_width=True)
        with col2:
            key = (subject,level,topic)
            if key in DIAGRAM_FILES and os.path.exists(DIAGRAM_FILES[key]):
                st.image(DIAGRAM_FILES[key], caption=topic, use_column_width=True)
            else: st.info("No diagram for this topic yet")

    elif mode == "🧪 Practicals Lab":
        st.title(f"🧪 Practicals Lab: {subject} {level}")
        st.warning("Master these 8 topics. They repeat every year in UNEB.")
        topic = st.sidebar.selectbox("Select Practical", PRACTICAL_TOPICS[subject])

        if st.button(f"💰 Get Apparatus & Budget: {topic}", use_container_width=True):
            with st.spinner("Calculating budget..."):
                budget = generate_apparatus_list(client, topic)
                st.markdown(budget)
                st.session_state.activities_log.append(f"Budget for {topic}")

        st.divider()
        if st.button(f"Generate Full Report: {topic}", use_container_width=True):
            with st.spinner("System generating full UNEB report..."):
                report = generate_practical(client,subject,level,topic)
                data, json_block = safe_json_extract(report)
                if data and "data" in data:
                    try:
                        df = pd.DataFrame(data["data"], columns=[data["x_label"], data["y_label"]])
                        st.dataframe(df, use_container_width=True)
                        render_graph(df,data["x_label"],data["y_label"],topic)
                    except Exception as e:
                        st.warning(f"Could not parse data table: {e}")
                else:
                    st.warning("System did not return valid data table.")
                st.markdown(report.replace(json_block,"") if json_block else report)
                st.session_state.activities_log.append(f"Practical report: {topic}")

        # ASK BOX FOR PRACTICALS
        st.divider()
        ask_box(client, f"Practical: {topic}", "practical")

    elif mode == "📈 Graph Describer":
        st.title("📈 Graph Describer & Drawer")
        tab1, tab2 = st.tabs(["✍️ Describe Graph", "🖼️ Upload Graph Image"])

        with tab1:
            user_graph = st.text_area("Describe the graph you need:", height=100, key="desc_text")
            if st.button("Generate & Draw Graph", use_container_width=True, key="btn_desc"):
                if not user_graph.strip(): st.warning("Please describe a graph first.")
                else:
                    with st.spinner("Generating graph..."):
                        result = describe_and_draw_graph(client, user_graph)
                        data, json_block = safe_json_extract(result)
                        if data and "data" in data:
                            try:
                                df = pd.DataFrame(data["data"], columns=[data["x_label"], data["y_label"]])
                                st.dataframe(df, use_container_width=True)
                                render_graph(df, data["x_label"], data["y_label"], user_graph)
                            except Exception as e:
                                st.error(f"Failed to draw: {e}")
                        else:
                            st.warning("System did not return valid data.")
                        st.markdown("### Explanation")
                        st.markdown(result.replace(json_block,"") if json_block else result)
                        st.session_state.activities_log.append(f"Graph: {user_graph}")

            # ASK BOX FOR GRAPHS
            st.divider()
            ask_box(client, "Graph Topic", "graph")

        with tab2:
            uploaded_file = st.file_uploader("Choose an image", type=["png","jpg","jpeg"], key="img_upload")
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Graph", use_column_width=True)
                if st.button("Analyze Graph", use_container_width=True, key="btn_analyze"):
                    with st.spinner("Analyzing image..."):
                        image_bytes = uploaded_file.getvalue()
                        result = describe_uploaded_graph(client, image_bytes)
                        st.markdown("### Analysis")
                        st.markdown(result)

    elif mode == "🎙️ Voice Chat":
        st.title("🎙️ Voice Chat Tutor")
        st.write(f"Talk to the tutor about {subject} {level}.")
        audio = mic_recorder(start_prompt="🎤 Hold to Record", stop_prompt="⏹️ Stop", key='recorder')
        if audio:
            st.audio(audio['bytes'])
            with st.spinner("Listening and processing..."):
                user_q, tutor_a, tutor_audio = voice_chat(client, audio['bytes'])
            if user_q:
                st.markdown(f"**You:** {user_q}")
                st.markdown(f"**Digital Tutor:** {tutor_a}")
                if tutor_audio: st.audio(tutor_audio, format="audio/mp3")

    # ============ NEW MODE: QUIZ MODE ============
    elif mode == "📝 Quiz Mode":
        st.title(f"📝 UNEB Quiz Mode: {subject} {level}")
        topic = st.selectbox("Select Topic for Quiz", UNEB_CURRICULUM_MAP[subject][level])
        if st.button("Generate 10 MCQ Quiz", use_container_width=True):
            with st.spinner("Generating quiz..."):
                quiz = generate_quiz(client, subject, level, topic)
                st.markdown(quiz)
                st.session_state.activities_log.append(f"Generated Quiz: {topic}")

        st.divider()
        ask_box(client, f"Quiz on {topic}", "quiz")

    elif mode == "🔮 Predict Papers":
        st.title(f"🔮 UNEB 2026 Prediction: {subject}")
        st.info("Predictions based on UNEB trends 2016-2023 + NCDC 2026.")
        c1,c2,c3 = st.columns(3)
        with c1:
            if st.button("Generate P1 MCQ", use_container_width=True):
                with st.spinner("..."): st.session_state.p1 = generate_prediction(client,subject,"P1")
                st.session_state.activities_log.append(f"Generated P1 for {subject}")
            if "p1" in st.session_state: st.text_area("Paper 1", st.session_state.p1, height=400)
        with c2:
            if st.button("Generate P2 Theory", use_container_width=True):
                with st.spinner("..."): st.session_state.p2 = generate_prediction(client,subject,"P2")
                st.session_state.activities_log.append(f"Generated P2 for {subject}")
            if "p2" in st.session_state: st.text_area("Paper 2", st.session_state.p2, height=400)
        with c3:
            if st.button("Generate P3 Practical", use_container_width=True):
                with st.spinner("..."): st.session_state.p3 = generate_prediction(client,subject,"P3")
                st.session_state.activities_log.append(f"Generated P3 for {subject}")
            if "p3" in st.session_state: st.text_area("Paper 3", st.session_state.p3, height=400)

    elif mode == "🛠️ Teacher Tools":
        st.title("🛠️ Teacher Support Tools")
        tab1, tab2 = st.tabs(["📝 Marking Helper", "📄 Inspector Report"])
        with tab1:
            qn = st.text_area("Paste UNEB Question:", height=100)
            ans = st.text_area("Paste Student Answer (optional):", height=100)
            if st.button("Generate Marking Scheme"):
                if qn:
                    with st.spinner("Generating marking guide..."):
                        scheme = generate_marking_scheme(client, subject, level, qn, ans)
                        st.markdown(scheme)
                        st.session_state.activities_log.append(f"Marking scheme for {subject}")
                else: st.warning("Please enter a question")
        with tab2:
            school = st.text_input("School Name:", value="Nabiswera Progressive SS")
            if st.button("Generate PDF Report"):
                if st.session_state.activities_log:
                    pdf = generate_inspector_report(school, st.session_state.activities_log)
                    st.download_button("📥 Download Activity Report", pdf, f"Report_{school}.pdf")
                else:
                    st.warning("No activities logged yet.")

if __name__ == "__main__": main()
