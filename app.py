import streamlit as st
import os, io, pytz, random, difflib, re
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from subjects import CURRICULUM, PRACTICALS, get_topics

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

st.set_page_config(page_title="UCE/UACE DIGITAL TUTOR 2026 GOLD", page_icon="📚", layout="wide")
ADMIN_CONTACT = "256751040731"
UGANDA_TZ = pytz.timezone("Africa/Kampala")
BASE_DIR = Path(__file__).parent.resolve()
DIAGRAMS_DIR = BASE_DIR / "assets"
DIAGRAMS_DIR.mkdir(exist_ok=True)

SUBJECTS = ["Physics", "Chemistry", "Biology", "Mathematics"]
CLASSES = ["S1", "S2", "S3", "S4", "S5", "S6"]
GOLD_LOCKED_CLASSES = ["S5", "S6"]
GOLD_LOCKED_SUBJECTS = ["Physics", "Chemistry", "Biology", "Mathematics"]
MODES = ["Smart Search", "Theory Mode", "Lesson Preparation", "Diagrams Library", "Practicals Lab", "Quiz Mode", "Graph Generator", "Explainer Mode", "Predict Papers", "Voice Chat", "Progress Tracker", "Admin Dashboard", "Practical Assessment Generator", "Bulk Revision Generator"]

def generate_ai_response(client, prompt, subject, class_level):
    system_prompt = f"You are UCE/UACE DIGITAL TUTOR 2026. Teach {subject} for {class_level} Uganda. Use ONLY NCDC 2026 curriculum. Ugandan examples. Explain step by step."
    resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}], temperature=0.3, max_tokens=1024)
    return resp.choices[0].message.content

def find_diagram(topic):
    """Smart image finder: matches keywords even if names don't match exactly"""
    if not DIAGRAMS_DIR.exists(): return None
    all_pngs = list(DIAGRAMS_DIR.glob("*.png"))
    if not all_pngs: return None

    topic_lower = topic.lower()
    topic_words = set(re.findall(r'\w+', topic_lower)) # ['cells', 'structure']
    
    # 1. EXACT MATCH FIRST
    topic_clean = topic_lower.replace(" ", "_")
    for png_path in all_pngs:
        if topic_clean in png_path.name.lower():
            return str(png_path)

    # 2. KEYWORD MATCH: Score images by how many topic words they contain
    best_match = None
    best_score = 0
    for png_path in all_pngs:
        png_name = png_path.name.lower()
        png_words = set(re.findall(r'\w+', png_name))
        score = len(topic_words.intersection(png_words))
        if score > best_score:
            best_score = score
            best_match = png_path

    if best_score > 0: # At least 1 word matched
        return str(best_match)

    # 3. FUZZY MATCH FALLBACK
    png_names = [p.stem.lower() for p in all_pngs]
    matches = difflib.get_close_matches(topic_lower, png_names, n=1, cutoff=0.5)
    if matches:
        for png_path in all_pngs:
            if matches[0] in png_path.stem.lower():
                return str(png_path)
    return None

def log_activity(activity, subject, class_level):
    if "activities_log" not in st.session_state: st.session_state.activities_log = []
    st.session_state.activities_log.append({"time": datetime.now(UGANDA_TZ).strftime("%Y-%m-%d %H:%M:%S"), "activity": activity, "subject": subject, "class": class_level, "license": st.session_state.license})

def show_gold_upgrade():
    st.warning("🔒 **UPGRADE TO GOLD PACKAGE**")
    st.info("Unlock S5 & S6 + All Subjects + Predict Papers + Bulk Generator")
    st.markdown(f"**WhatsApp/Call: {ADMIN_CONTACT}** to get your GOLD Access Key")
    st.link_button(f"📱 WhatsApp {ADMIN_CONTACT}", f"https://wa.me/{ADMIN_CONTACT}")

def ask_bar(client, subject, class_level, mode, default_label="Ask a follow-up question"):
    st.markdown("---")
    user_q = st.text_input(f"💬 {default_label}", key=f"ask_{mode}_{subject}")
    if st.button("Ask AI", key=f"ask_btn_{mode}_{subject}") and user_q:
        with st.spinner("AI is answering..."):
            resp = generate_ai_response(client, user_q, subject, class_level)
        st.success(resp)

def main():
    if "activities_log" not in st.session_state: st.session_state.activities_log = []
    if "license" not in st.session_state: st.session_state.license = "FREE"

    st.markdown("""<div style="background:linear-gradient(90deg, #FFD700 0%, #FFA500 100%); padding:15px;"><h1 style="color:black; text-align:center">📚 UCE/UACE DIGITAL TUTOR 2026 GOLD</h1></div>""", unsafe_allow_html=True)

    # LOGIN GATE - 2 BOXES ON SAME PAGE
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("🔒 Enter Access Key")
        col1, col2 = st.columns(2)
        FREE_PASS = st.secrets.get("FREE_PASSWORD", "UNEB_TEST_2026").upper().strip()
        GOLD_PASS = st.secrets.get("GOLD_PASSWORD", "GOLD2026").upper().strip()
        with col1:
            with st.container(border=True):
                st.markdown("### 🟢 FREE PACKAGE")
                st.write("Access: S1 - S4")
                free_password = st.text_input("Enter FREE Key", type="password", key="free_login")
                if st.button("Login FREE", type="secondary", use_container_width=True):
                    if free_password.upper().strip() == FREE_PASS:
                        st.session_state.authenticated = True
                        st.session_state.license = "FREE"
                        st.rerun()
                    else:
                        st.error("Invalid FREE Key")
        with col2:
            with st.container(border=True):
                st.markdown("### ⭐ GOLD PACKAGE")
                st.write("Access: S1 - S6 + All Features")
                gold_password = st.text_input("Enter GOLD Key", type="password", key="gold_login")
                if st.button("Login GOLD", type="primary", use_container_width=True):
                    if gold_password.upper().strip() == GOLD_PASS:
                        st.session_state.authenticated = True
                        st.session_state.license = "GOLD"
                        st.rerun()
                    else:
                        st.error("Invalid GOLD Key")
                st.markdown(f"**Need GOLD?**")
                st.markdown(f"[📱 WhatsApp {ADMIN_CONTACT}](https://wa.me/{ADMIN_CONTACT})")
        st.stop()

    client = get_client()

    with st.sidebar:
        st.success(f"License: {st.session_state.license}")
        if st.session_state.license == "FREE":
            with st.container(border=True):
                st.markdown("### ⭐ UPGRADE TO GOLD")
                st.write("Unlock S5/S6 + All Features")
                st.markdown(f"**Call/WhatsApp: {ADMIN_CONTACT}**")
                st.link_button("Get Gold Key", f"https://wa.me/{ADMIN_CONTACT}")
        subject = st.selectbox("Subject", SUBJECTS)
        available_classes = ["S1", "S2", "S3", "S4"] if st.session_state.license == "FREE" else CLASSES
        class_level = st.selectbox("Class", available_classes)
        with st.expander(f"📖 {subject} {class_level} Topics"):
            for topic in get_topics(subject, class_level): st.write(f"• {topic}")
        mode = st.radio("Mode", MODES)
        st.markdown(f"### Need Help?")
        st.markdown(f"[📞 Call {ADMIN_CONTACT}](tel:{ADMIN_CONTACT})")
        st.markdown(f"[💬 WhatsApp {ADMIN_CONTACT}](https://wa.me/{ADMIN_CONTACT})")

    if class_level in GOLD_LOCKED_CLASSES and subject in GOLD_LOCKED_SUBJECTS and st.session_state.license == "FREE":
        st.error(f"🔒 **GOLD PACKAGE REQUIRED FOR {class_level} {subject}**")
        show_gold_upgrade()
        st.stop()

    # ===============================
    # ALL 14 MODES
    # ===============================
    if mode == "Smart Search":
        st.header("🧠 Smart Search")
        query = st.text_input("Ask any question")
        if st.button("Search") and query:
            with st.spinner("Thinking..."):
                resp = generate_ai_response(client, f"Explain {query}", subject, class_level)
            st.write(resp); log_activity(f"Smart: {query}", subject, class_level)
        ask_bar(client, subject, class_level, mode, "Ask another question")

    elif mode == "Theory Mode":
        st.header("📘 Theory Mode")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Generate Notes"):
            with st.spinner("Generating notes..."):
                resp = generate_ai_response(client, f"Detailed NCDC 2026 notes on {topic} for {class_level}", subject, class_level)
            st.write(resp); log_activity(f"Theory: {topic}", subject, class_level)
        ask_bar(client, subject, class_level, mode, "Ask about this topic")

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
        ask_bar(client, subject, class_level, mode, "Modify this lesson plan")

    elif mode == "Diagrams Library":
        st.header("🖼️ Diagrams Library")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        path = find_diagram(topic)
        all_images = list(DIAGRAMS_DIR.glob("*.png"))
        st.info(f"Found {len(all_images)} images in assets folder")
        
        if path and os.path.exists(path):
            st.image(path, caption=topic, use_container_width=True)
            st.success(f"✅ Found related diagram: {Path(path).name}")
        else:
            st.warning(f"No related diagram found for '{topic}'. Try naming images with topic keywords.")
            with st.expander("Show all images in assets"):
                for img in all_images[:10]: st.write(img.name)
        ask_bar(client, subject, class_level, mode, "Explain this diagram")

    elif mode == "Practicals Lab":
        st.header("🧪 Practicals Lab")
        if subject in PRACTICALS:
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
        else: st.info("No practicals for Mathematics yet.")
        ask_bar(client, subject, class_level, mode, "Ask about this practical")

    elif mode == "Quiz Mode":
        st.header("📝 Quiz Mode")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Generate 5 MCQs"):
            with st.spinner("Generating quiz..."):
                resp = generate_ai_response(client, f"Generate 5 competency-based MCQs with answers on {topic} for {class_level}", subject, class_level)
            st.write(resp); log_activity(f"Quiz: {topic}", subject, class_level)
        ask_bar(client, subject, class_level, mode, "Explain any answer")

    elif mode == "Graph Generator":
        st.header("📊 Graph Generator")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        graph_type = st.selectbox("Graph Type", ["Line Graph", "Bar Chart", "Scatter Plot"])
        col1, col2 = st.columns(2)
        with col1: x_label = st.text_input("X-Axis Label", "Time (s)")
        with col2: y_label = st.text_input("Y-Axis Label", "Distance (m)")
        num_points = st.slider("Number of Data Points", 5, 50, 20)
        if st.button("Generate Graph"):
            with st.spinner("Generating graph..."):
                if graph_type == "Line Graph":
                    x = np.linspace(0, 10, num_points)
                    y = x**2 * 0.5 + np.random.randn(num_points)*5
                    df = pd.DataFrame({x_label: x, y_label: y})
                    fig = generate_graph(df, x_label, y_label, f"{topic} - {graph_type}")
                elif graph_type == "Bar Chart":
                    categories = [f"Cat {i+1}" for i in range(num_points//2)]
                    values = np.random.randint(10, 100, len(categories))
                    df = pd.DataFrame({x_label: categories, y_label: values})
                    import plotly.express as px
                    fig = px.bar(df, x=x_label, y=y_label, title=f"{topic} - {graph_type}")
                else:
                    x = np.random.randn(num_points)
                    y = np.random.randn(num_points)
                    df = pd.DataFrame({x_label: x, y_label: y})
                    import plotly.express as px
                    fig = px.scatter(df, x=x_label, y=y_label, title=f"{topic} - {graph_type}")
                st.plotly_chart(fig, use_container_width=True)
                st.download_button("Download CSV", df.to_csv(index=False).encode(), "graph_data.csv")
                log_activity(f"Graph: {topic}", subject, class_level)
        if st.button("Explain This Graph"):
            with st.spinner("AI is explaining..."):
                resp = generate_ai_response(client, f"Explain how to interpret and draw a {graph_type} for {topic} in {class_level}. Give Ugandan example.", subject, class_level)
            st.success(resp)
        ask_bar(client, subject, class_level, mode, "Ask about graph interpretation")

    elif mode == "Explainer Mode":
        st.header("🎓 Explainer Mode")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        level = st.selectbox("Explanation Level", ["Simple", "Detailed", "Exam Focused"])
        if st.button("Explain Topic"):
            with st.spinner("Generating explanation..."):
                resp = generate_ai_response(client, f"Explain {topic} for {class_level} at {level} level. Use Ugandan examples. Give 3 worked examples.", subject, class_level)
            st.write(resp)
            log_activity(f"Explain: {topic}", subject, class_level)
        if st.button("Common Mistakes"):
            with st.spinner("Finding mistakes..."):
                resp = generate_ai_response(client, f"List 5 common mistakes students make on {topic} in {class_level} and how to avoid them", subject, class_level)
            st.warning(resp)
        ask_bar(client, subject, class_level, mode, "Ask a specific doubt")

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
        ask_bar(client, subject, class_level, mode, "Generate more questions")

    elif mode == "Predict Papers":
        st.header("📄 Predict Papers")
        if st.button("Predict Full Subject"):
            with st.spinner("Predicting paper..."):
                resp = generate_ai_response(client, f"Predict UCE/UACE competency-based questions for {class_level} {subject} with Ugandan context", subject, class_level)
            st.write(resp)
            pdf = create_pdf(resp, "predict.pdf")
            st.download_button("Download PDF", pdf, "predict.pdf")
            log_activity("Predict", subject, class_level)
        ask_bar(client, subject, class_level, mode, "Explain question 1")

    elif mode == "Voice Chat":
        st.header("🎤 Voice Chat")
        st.info("Voice Chat disabled in Cloud. Use text input below.")
        query = st.text_input("Type your question")
        if st.button("Send") and query:
            with st.spinner("Thinking..."):
                resp = generate_ai_response(client, query, subject, class_level)
            st.write(resp)
            log_activity(f"Voice: {query}", subject, class_level)
        ask_bar(client, subject, class_level, mode, "Ask another question")

    elif mode == "Progress Tracker":
        st.header("📊 Progress Tracker")
        if st.session_state.activities_log:
            df = pd.DataFrame(st.session_state.activities_log)
            st.dataframe(df, use_container_width=True)
        else: st.info("No activities yet.")
        ask_bar(client, subject, class_level, mode, "How can I improve?")

    elif mode == "Admin Dashboard":
        st.header("📈 Admin Dashboard")
        if st.session_state.activities_log:
            df = pd.DataFrame(st.session_state.activities_log)
            st.metric("Total Activities", len(df))
            st.metric("Subjects Used", df['subject'].nunique())
            st.dataframe(df, use_container_width=True)
            st.download_button("Download CSV", df.to_csv(index=False).encode(), "log.csv")
        else: st.info("No data yet")
        ask_bar(client, subject, class_level, mode, "Give admin insights")

    elif mode == "Practical Assessment Generator":
        st.header("🧪 Practical AoI Generator")
        topic = st.selectbox("Topic", get_topics(subject, class_level))
        if st.button("Generate AoI"):
            with st.spinner("Generating AoI..."):
                resp = generate_ai_response(client, f"Generate Competency-based Activity of Integration for {topic} with Ugandan household scenario", subject, class_level)
            st.write(resp)
            log_activity(f"AoI: {topic}", subject, class_level)
        ask_bar(client, subject, class_level, mode, "Make AoI harder/easier")

if __name__ == "__main__":
    main()
