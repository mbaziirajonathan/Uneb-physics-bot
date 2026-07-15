import streamlit as st
import os, io, json, re, pytz, numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime
from groq import Groq, GroqError
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

st.set_page_config(page_title="UNEB AI Tutor 2026", page_icon="📚", layout="centered", initial_sidebar_state="expanded")

PRACTICAL_TOPICS = {
    "Physics": ["Simple Pendulum - Finding g", "Principle of Moments", "Hooke's Law", "Density and Upthrust", "Converging Lens - Focal Length", "Glass Block - Refractive Index", "Ohm's Law - V vs I", "Resistance vs Length"],
    "Chemistry": ["Acid-Base Titration", "Back Titration - Purity", "Heat of Neutralization", "Rates of Reaction", "Qualitative Analysis - Cations", "Qualitative Analysis - Anions", "Gas Tests", "Enthalpy Change"],
    "Biology": ["Food Tests", "Osmosis in Potato", "Photosynthesis Rate", "Respiration in Seeds", "Microscopy - Cells", "Ecological Sampling", "Transpiration - Potometer", "Enzyme Activity"]
}

UNEB_CURRICULUM_MAP = {
    "Physics": {"S1": ["Measurement", "Force"], "S2": ["Current Electricity", "Refraction", "Waves"], "S3": ["Hookes Law", "Specific Heat Capacity", "Magnetism"], "S4": ["Transformers", "Electronics", "Nuclear Physics"]},
    "Chemistry": {"S1": ["Structure of an Atom", "Chemical Bonding"], "S2": ["Water and Hydrogen", "Metals"], "S3": ["Rates of Reaction", "Organic Chemistry"], "S4": ["Electrochemistry", "Industrial Chemistry"]},
    "Biology": {"S1": ["Plant Cell", "Ecosystem"], "S2": ["Circulatory System", "Photosynthesis"], "S3": ["DNA", "Genetics"], "S4": ["Nervous System", "Immunity"]}
}

DIAGRAM_FILES = {("Physics","S1","Measurement"): "assets/vernier.png", ("Physics","S2","Current Electricity"): "assets/simple_circuit.png", ("Physics","S3","Hookes Law"): "assets/hookes_law.png", ("Physics","S4","Transformers"): "assets/ac_transformer.png", ("Biology","S1","Plant Cell"): "assets/plant_cell.png", ("Biology","S2","Photosynthesis"): "assets/photosynthesis.png", ("Biology","S4","Nervous System"): "assets/neurone.png"}

@st.cache_resource
def get_client():
    try:
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except:
        st.error("🚨 GROQ_API_KEY missing in secrets. Add it to.streamlit/secrets.toml"); st.stop()

def calc_gradient(df, x, y):
    try:
        slope, intercept = np.polyfit(df[x], df[y], 1)
        return f"**Gradient = {slope:.3f}** | Equation: y = {slope:.3f}x + {intercept:.3f}"
    except: return ""

def render_graph(df, x, y, title):
    st.subheader("📈 Auto-Generated Graph")
    fig = px.scatter(df, x=x, y=y, title=title, trendline="ols", template="plotly_white")
    fig.update_traces(marker=dict(size=9), line=dict(width=2))
    fig.update_layout(xaxis_title=x, yaxis_title=y, height=380)
    st.plotly_chart(fig, use_container_width=True)

    gradient_text = calc_gradient(df, x, y)
    if gradient_text: st.info(gradient_text + " - Use this in calculations")

    buf = io.BytesIO()
    plt.figure(figsize=(6,4)); plt.scatter(df[x], df[y]);
    z = np.polyfit(df[x], df[y], 1); p = np.poly1d(z)
    plt.plot(df[x],p(df[x]),"r--",alpha=0.8)
    plt.title(title); plt.xlabel(x); plt.ylabel(y); plt.grid(True)
    plt.savefig(buf, format="png", dpi=150); buf.seek(0)
    st.download_button("📥 Download Graph PNG", buf, f"{title}.png", "image/png")

def generate_practical(client, subject, level, topic):
    prompt = f"""You are a UNEB examiner for {subject} {level} Uganda 2026. Generate a complete practical report for: {topic}.
    Format strictly:
    1. AIM
    2. HYPOTHESIS
    3. VARIABLES: Independent, Dependent, 3 Controlled
    4. APPARATUS
    5. PROCEDURE
    6. SAFETY PRECAUTIONS
    7. DATA TABLE
    8. GRAPH GUIDE: State what to plot on X and Y axis
    9. CONCLUSION
    At the end include realistic mock data in this exact JSON: ```json {{"x_label": "X", "y_label": "Y", "data": [[1,2],[2,4],[3,6],[4,8],[5,10],[6,12]]}} ```
    Use competency-based curriculum language. Be precise. 6 data points."""
    try:
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], temperature=0.2, max_tokens=2000)
        return res.choices[0].message.content
    except GroqError as e: return f"AI Error: {e}"

def generate_prediction(client, subject, paper):
    prompts = {
        "P1": f"You are UNEB Head of Examinations 2026. Generate 40 MCQ for {subject} Paper 1. Mix S1-S4. 4 options A-D. Syllabus 2026. Mark answers at end.",
        "P2": f"You are UNEB Head 2026. Generate 5 Theory questions for {subject} Paper 2. S3-S4. Include 2 calculations, 1 diagram question. 10 marks each. Provide marking guide.",
        "P3": f"You are UNEB Head 2026. Generate 3 Practical scenarios for {subject} Paper 3. Competency-based. Include apparatus and method."
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

def main():
    client = get_client()
    st.sidebar.title("📚 UNEB AI Tutor 2026")
    mode = st.sidebar.radio("Mode", ["📖 Learn Theory", "🧪 Practicals Lab", "🔮 Predict Papers"])
    subject = st.sidebar.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
    level = st.sidebar.selectbox("Class Level", ["S1","S2","S3","S4"])
    tz = pytz.timezone("Africa/Kampala"); st.sidebar.divider(); st.sidebar.caption(f"Kampala: {datetime.now(tz).strftime('%A %H:%M %p')}")

    if mode == "📖 Learn Theory":
        st.title(f"Theory: {subject} {level}")
        topic = st.sidebar.selectbox("Topic", UNEB_CURRICULUM_MAP[subject][level])
        col1,col2 = st.columns([1.2,1])
        with col1:
            if st.button("Generate UNEB Notes", use_container_width=True):
                with st.spinner("Generating notes..."):
                    prompt = f"Give 6 concise UNEB {level} exam notes for {subject} topic: {topic}. Ugandan syllabus 2026. Exam focused."
                    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], max_tokens=400)
                    st.session_state.notes = res.choices[0].message.content
            if "notes" in st.session_state:
                st.markdown(st.session_state.notes)
                pdf = create_pdf(topic,subject,level,st.session_state.notes);
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
        if st.button(f"Generate Full Report: {topic}", use_container_width=True):
            with st.spinner("AI Examiner writing full UNEB report..."):
                report = generate_practical(client,subject,level,topic)
                match = re.search(r'```json(.*?)```', report, re.DOTALL)
                if match:
                    try:
                        data = json.loads(match.group(1));
                        df = pd.DataFrame(data["data"], columns=[data["x_label"], data["y_label"]])
                        st.dataframe(df, use_container_width=True);
                        render_graph(df,data["x_label"],data["y_label"],topic)
                    except Exception as e:
                        st.warning(f"Could not parse data table: {e}")
                st.markdown(report.replace(match.group(0),"") if match else report)

    elif mode == "🔮 Predict Papers":
        st.title(f"🔮 UNEB 2026 Prediction: {subject}")
        st.info("AI predicted based on UNEB trends 2016-2023. For revision only.")
        c1,c2,c3 = st.columns(3)
        with c1:
            if st.button("Generate P1 MCQ", use_container_width=True):
                with st.spinner("..."): st.session_state.p1 = generate_prediction(client,subject,"P1")
            if "p1" in st.session_state: st.text_area("Paper 1", st.session_state.p1, height=400)
        with c2:
            if st.button("Generate P2 Theory", use_container_width=True):
                with st.spinner("..."): st.session_state.p2 = generate_prediction(client,subject,"P2")
            if "p2" in st.session_state: st.text_area("Paper 2", st.session_state.p2, height=400)
        with c3:
            if st.button("Generate P3 Practical", use_container_width=True):
                with st.spinner("..."): st.session_state.p3 = generate_prediction(client,subject,"P3")
            if "p3" in st.session_state: st.text_area("Paper 3", st.session_state.p3, height=400)

if __name__ == "__main__": main()
