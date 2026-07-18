import streamlit as st
import os, io, pytz, random
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from subjects import CURRICULUM, PRACTICALS, get_topics

# ===============================
# LAZY IMPORTS + CACHING FOR SPEED
# ===============================
@st.cache_resource
def get_client():
    from groq import Groq
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

@st.cache_data
def create_pdf(content, filename):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 10)
    y = height - 50
    for line in content.split('\n'):
        for chunk in [line[i:i+95] for i in range(0, len(line), 95)]:
            c.drawString(50, y, chunk)
            y -= 15
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 50
    c.save()
    buffer.seek(0)
    return buffer

@st.cache_data
def generate_graph(data, x_col, y_col, title):
    import plotly.express as px
    fig = px.line(data, x=x_col, y=y_col, title=title, markers=True)
    fig.update_layout(template="plotly_white", height=400)
    return fig

# ===============================
# HARDCODED APP BRANDING
# ===============================
st.set_page_config(
    page_title="UCE/UACE DIGITAL TUTOR 2026 GOLD",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'Get Help': 'https://wa.me/256751040731', 'About': "NCDC S1-S6 Competency Based"}
)

# ===============================
# LICENSE CONTROL + LOCKS
# ===============================
ADMIN_CONTACT = "256751040731"
UGANDA_TZ = pytz.timezone("Africa/Kampala")

BASE_DIR = Path(__file__).parent.resolve()
DIAGRAMS_DIR = BASE_DIR / "assets"
DIAGRAMS_DIR.mkdir(exist_ok=True)

SUBJECTS = ["Physics", "Chemistry", "Biology", "Mathematics"]
CLASSES = ["S1", "S2", "S3", "S4", "S5", "S6"]
GOLD_LOCKED_CLASSES = ["S5", "S6"]
GOLD_LOCKED_SUBJECTS = ["Physics", "Chemistry", "Biology", "Mathematics"]
MODES = ["Smart Search", "Theory Mode", "Lesson Preparation", "Diagrams Library", "Practicals Lab", "Quiz Mode", "Predict Papers", "Voice Chat", "Progress Tracker", "Admin Dashboard", "Practical Assessment Generator", "Bulk Revision Generator"]

# ===============================
# CORE FUNCTIONS
# ===============================
def generate_ai_response(client, prompt, subject, class_level):
    system_prompt = f"You are UCE/UACE DIGITAL TUTOR 2026. Teach {subject} for {class_level} Uganda. Use ONLY the NCDC 2026 curriculum. Ugandan examples. Step by step. No hallucination."
    resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}], temperature=0.3, max_tokens=1024)
    return resp.choices[0].message.content

def find_diagram(topic):
    if not DIAGRAMS_DIR.exists(): return None
    all_pngs = list(DIAGRAMS_DIR.glob("*.png"))
    search_key = topic.lower().replace(" ", "_").replace("/", "_")
    for png_path in all_pngs:
        if search_key in png_path.name.lower(): return str(png_path)
    return None

def log_activity(activity, subject, class_level):
    if "activities_log" not in st.session_state: st.session_state.activities_log = []
    st.session_state.activities_log.append({"time": datetime.now(UGANDA_TZ).strftime("%Y-%m-%d %H:%M:%S"), "activity": activity, "subject": subject, "class": class_level, "license": st.session_state.license})

def show_gold_lock(subject):
    st.error(f"🔒 **GOLD PACKAGE REQUIRED**")
    st.info(f"S5 and S6 are GOLD ONLY for all subjects.")
    st.info(f"WhatsApp/Call **{ADMIN_CONTACT}** to get your access key")
    st.link_button(f"📱 WhatsApp {ADMIN_CONTACT}", f"https://wa.me/{ADMIN_CONTACT}")

# ===============================
# MAIN APP
# ===============================
def main():
    if "activities_log" not in st.session_state: st.session_state.activities_log = []
    if "license" not in st.session_state: st.session_state.license = "FREE"

    st.markdown("""<div style="background:linear-gradient(90deg, #FFD700 0%, #FFA500 100%); padding:15px;"><h1 style="color:black; text-align:center">📚 UCE/UACE DIGITAL TUTOR 2026 GOLD</h1></div>""", unsafe_allow_html=True)

    # LOGIN GATE - CASE INSENSITIVE - NEW PASSWORD
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("🔒 Login")
        password = st.text_input("Enter Access Key", type="password")
        if st.button("Login", type="primary"):
            FREE_PASS = st.secrets.get("FREE_PASSWORD", "UNEB_TEST_2026").upper().strip()
            GOLD_PASS = st.secrets.get("GOLD_PASSWORD", "GOLD2026").upper().strip()
            user_input = password.upper().strip()

            if user_input == GOLD_PASS: st.session_state.authenticated = True; st.session_state.license = "GOLD"; st.rerun()
            elif user_input == FREE_PASS: st.session_state.authenticated = True; st.session_state.license = "FREE"; st.rerun()
            else: st.error("Invalid Access Key. Contact Admin on WhatsApp.")
        st.stop()

    client = get_client()

    with st.sidebar:
        st.success(f"License: {st.session_state.license}")
        subject = st.selectbox("Subject", SUBJECTS)
        available_classes = ["S1", "S2", "S3", "S4"] if st.session_state.license == "FREE" else CLASSES
        class_level = st.selectbox("Class", available_classes)
        with st.expander(f"📖 {subject} {class_level} Topics"):
            for topic in get_topics(subject, class_level): st.write(f"• {topic}")
        mode = st.radio("Mode", MODES)
        st.markdown(f"[📞 WhatsApp Admin](https://wa.me/256{ADMIN_CONTACT[1:]})")

    # LOCK CHECK - S5/S6 ALL SUBJECTS = GOLD ONLY
    if class_level in GOLD_LOCKED_CLASSES and subject in GOLD_LOCKED_SUBJECTS and st.session_state.license == "FREE":
        show_gold_lock(subject); st.stop()

    # ===============================
    # ALL 12 MODES - FULL CODE
    # ===============================
    if mode == "Smart Search":
        st.header("🧠 Smart Search")
        query = st.text_input("Ask any question")
        if st.button("Search") and query:
            with st.spinner("Thinking..."):
                resp = generate_ai_response(client, f"Explain {query}", subject, class_level)
            st.write(resp); log_activity(f"Smart: {query}", subject, class_level)

    elif mode == "Theory Mode":
        st.header("📘 Theory Mode")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Generate Notes"):
            with st.spinner("Generating notes..."):
                resp = generate_ai_response(client, f"Detailed NCDC 2026 notes on {topic} for {class_level}", subject, class_level)
            st.write(resp); log_activity(f"Theory: {topic}", subject, class_level)

    elif mode == "Lesson Preparation":
        st.header("👨‍🏫 Lesson Preparation")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Generate Lesson Plan + AoI"):
            with st.spinner("Generating lesson plan..."):
                resp = generate_ai_response(client, f"40min competency-based lesson plan with AoI for {topic} in Ugandan context", subject, class_level)
            st.write(resp)
            pdf = create_pdf(resp, "lesson.pdf")
            st.download_button("Download PDF", pdf, "lesson.pdf")
            log_activity(f"Lesson: {topic}", subject, class_level)

    elif mode == "Diagrams Library":
        st.header("🖼️ Diagrams Library")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        path = find_diagram(topic)
        if path and os.path.exists(path):
            st.image(path, caption=topic, use_container_width=True)
        else: st.warning("Diagram not found in /assets folder. Upload PNG with name matching topic.")

    elif mode == "Practicals Lab":
        st.header("🧪 Practicals Lab")
        practical = st.selectbox("Select Practical", [p["name"] for p in PRACTICALS[subject]])
        if st.button("Show Practical"):
            p = next(p for p in PRACTICALS[subject] if p["name"] == practical)
            st.write(f"**Aim:** {p['aim']}")
            st.write(f"**Materials:** {p['materials']}")
            st.write(f"**Procedure:** {p['procedure']}")
            if p["graph"]:
                if st.button("Generate Sample Graph"):
                    x = np.linspace(0,10,20)
                    y = x * random.uniform(0.5,2) + np.random.randn(20)*2
                    fig = generate_graph(pd.DataFrame({"X":x,"Y":y}), "X","Y", p["graph"])
                    st.plotly_chart(fig, use_container_width=True)
            log_activity(f"Practical: {practical}", subject, class_level)

    elif mode == "Quiz Mode":
        st.header("📝 Quiz Mode")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Generate 5 MCQs"):
            with st.spinner("Generating quiz..."):
                resp = generate_ai_response(client, f"Generate 5 competency-based MCQs with answers on {topic} for {class_level}", subject, class_level)
            st.write(resp); log_activity(f"Quiz: {topic}", subject, class_level)

    elif mode == "Bulk Revision Generator":
        st.header("📚 Bulk Revision Generator")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        num_q = st.slider("Questions", 10, 50, 20)
        if st.button("Generate"):
            with st.spinner("Generating bulk questions..."):
                resp = generate_ai_response(client, f"Generate {num_q} UCE/UACE revision questions with answers on {topic}", subject, class_level)
            st.write(resp)
            pdf = create_pdf(resp, "revision.pdf")
            st.download_button("Download PDF", pdf, "revision.pdf")
            log_activity(f"Bulk: {topic}", subject, class_level)

    elif mode == "Predict Papers":
        st.header("📄 Predict Papers")
        if st.button("Predict Full Subject"):
            with st.spinner("Predicting paper..."):
                resp = generate_ai_response(client, f"Predict UCE/UACE competency-based questions for {class_level} {subject} with Ugandan context", subject, class_level)
            st.write(resp)
            pdf = create_pdf(resp, "predict.pdf")
            st.download_button("Download PDF", pdf, "predict.pdf")
            log_activity("Predict", subject, class_level)

    elif mode == "Voice Chat":
        st.header("🎤 Voice Chat")
        st.info("Voice Chat disabled in Cloud. Use text input below.")
        query = st.text_input("Type your question")
        if st.button("Send") and query:
            with st.spinner("Thinking..."):
                resp = generate_ai_response(client, query, subject, class_level)
            st.write(resp)
            log_activity(f"Voice: {query}", subject, class_level)

    elif mode == "Progress Tracker":
        st.header("📊 Progress Tracker")
        if st.session_state.activities_log:
            df = pd.DataFrame(st.session_state.activities_log)
            st.dataframe(df, use_container_width=True)
        else: st.info("No activities yet. Use any mode to start tracking.")

    elif mode == "Admin Dashboard":
        st.header("📈 Admin Dashboard")
        if st.session_state.activities_log:
            df = pd.DataFrame(st.session_state.activities_log)
            st.metric("Total Activities", len(df))
            st.metric("Subjects Used", df['subject'].nunique())
            st.dataframe(df, use_container_width=True)
            st.download_button("Download CSV", df.to_csv(index=False).encode(), "log.csv")
        else: st.info("No data yet")

    elif mode == "Practical Assessment Generator":
        st.header("🧪 Practical AoI Generator")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Generate AoI"):
            with st.spinner("Generating AoI..."):
                resp = generate_ai_response(client, f"Generate Competency-based Activity of Integration for {topic} with Ugandan household scenario", subject, class_level)
            st.write(resp)
            log_activity(f"AoI: {topic}", subject, class_level)

if __name__ == "__main__":
    main()
