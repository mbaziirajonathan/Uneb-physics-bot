import streamlit as st
from groq import Groq
import pytz
from datetime import datetime
import subjects.physics as physics
import subjects.chemistry as chemistry
import subjects.biology as biology

# ========= FIX: EMBED ALL SVG SPRITES DIRECTLY =========
# No more FileNotFoundError. Everything is in this string
SVG_SPRITES = """
<svg style="display:none;">
  <symbol id="atom" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="10" fill="#FF6B6B"/>
    <ellipse cx="50" cy="50" rx="40" ry="10" stroke="#4ECDC4" stroke-width="2" fill="none" transform="rotate(0 50 50)"/>
    <ellipse cx="50" cy="50" rx="40" ry="10" stroke="#4ECDC4" stroke-width="2" fill="none" transform="rotate(60 50 50)"/>
    <ellipse cx="50" cy="50" rx="40" ry="10" stroke="#4ECDC4" stroke-width="2" fill="none" transform="rotate(120 50 50)"/>
  </symbol>
  <symbol id="transformer" viewBox="0 0 120 100">
    <rect x="10" y="20" width="30" height="60" fill="#95E1D3"/><rect x="80" y="20" width="30" height="60" fill="#95E1D3"/>
    <path d="M40 50 Q60 30 80 50 Q60 70 40 50" stroke="#F38181" stroke-width="3" fill="none"/>
    <text x="25" y="15" font-size="10">Primary</text><text x="85" y="15" font-size="10">Secondary</text>
  </symbol>
  <symbol id="plant_cell" viewBox="0 0 100 100">
    <rect x="10" y="10" width="80" height="80" fill="none" stroke="#2D5016" stroke-width="2"/>
    <circle cx="50" cy="50" r="15" fill="#A8E6CF"/><rect x="15" y="20" width="8" height="8" fill="#2D5016"/>
    <text x="50" y="95" text-anchor="middle" font-size="8">Plant Cell</text>
  </symbol>
  <symbol id="hookes_law" viewBox="0 0 100 100">
    <line x1="50" y1="10" x2="50" y2="30" stroke="#000" stroke-width="2"/>
    <path d="M45 30 L55 35 L45 40 L55 45 L45 50 L55 55 L45 60 L55 65 L45 70" stroke="#000" fill="none"/>
    <rect x="40" y="70" width="20" height="15" fill="#FFD93D"/>
    <text x="50" y="95" text-anchor="middle" font-size="8">F = kx</text>
  </symbol>
  <symbol id="xray_tube" viewBox="0 0 120 80">
    <rect x="10" y="20" width="100" height="40" fill="#C7CEEA" stroke="#000"/>
    <circle cx="30" cy="40" r="5" fill="#FFD93D"/><polygon points="90,25 110,40 90,55" fill="#FF6B6B"/>
    <text x="60" y="15" text-anchor="middle" font-size="8">X-Ray Tube</text>
  </symbol>
  <symbol id="dna" viewBox="0 0 100 100">
    <path d="M30 10 Q50 30 30 50 Q50 70 30 90" stroke="#4ECDC4" stroke-width="3" fill="none"/>
    <path d="M70 10 Q50 30 70 50 Q50 70 70 90" stroke="#FF6B6B" stroke-width="3" fill="none"/>
    <line x1="30" y1="20" x2="70" y2="20" stroke="#95E1D3"/><line x1="30" y1="40" x2="70" y2="40" stroke="#95E1D3"/>
  </symbol>
  <symbol id="ecosystem" viewBox="0 0 100 100">
    <rect x="0" y="70" width="100" height="30" fill="#8B4513"/><circle cx="20" cy="50" r="15" fill="#2D5016"/>
    <circle cx="50" cy="40" r="10" fill="#2D5016"/><circle cx="80" cy="55" r="12" fill="#2D5016"/>
    <circle cx="50" cy="20" r="15" fill="#FFD93D"/>
  </symbol>
  <symbol id="circulatory" viewBox="0 0 100 100">
    <path d="M50 20 C30 20 20 40 20 50 C20 70 50 90 50 90 C50 90 80 70 80 50 C80 40 70 20 50 20" fill="none" stroke="#FF6B6B" stroke-width="3"/>
    <circle cx="50" cy="45" r="8" fill="#FF6B6B"/>
  </symbol>
  <symbol id="photosynthesis" viewBox="0 0 100 100">
    <rect x="10" y="60" width="80" height="10" fill="#8B4513"/><rect x="40" y="30" width="20" height="30" fill="#2D5016"/>
    <circle cx="20" cy="20" r="10" fill="#FFD93D"/><text x="50" y="95" text-anchor="middle" font-size="8">CO2 + H2O -> Glucose</text>
  </symbol>
  <symbol id="electroscope" viewBox="0 0 100 100">
    <rect x="40" y="10" width="20" height="40" fill="#C7CEEA"/><circle cx="50" cy="60" r="20" fill="none" stroke="#000"/>
    <line x1="50" y1="50" x2="40" y2="70" stroke="#FFD93D" stroke-width="2"/><line x1="50" y1="50" x2="60" y2="70" stroke="#FFD93D" stroke-width="2"/>
  </symbol>
  <symbol id="refraction" viewBox="0 0 100 100">
    <line x1="0" y1="50" x2="100" y2="50" stroke="#999"/><line x1="10" y1="20" x2="50" y2="50" stroke="#FF6B6B" stroke-width="2"/>
    <line x1="50" y1="50" x2="90" y2="70" stroke="#FF6B6B" stroke-width="2"/>
  </symbol>
  <symbol id="specific_heat" viewBox="0 0 100 100">
    <rect x="20" y="40" width="60" height="40" fill="#C7CEEA"/><path d="M50 20 Q60 30 50 40" fill="#FF6B6B"/>
    <text x="50" y="95" text-anchor="middle" font-size="8">Q = mcΔT</text>
  </symbol>
</svg>
"""
st.markdown(SVG_SPRITES, unsafe_allow_html=True)
# =====================================================

st.set_page_config(page_title="UNEB AI Tutor", layout="wide")

# Password Gate
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("UNEB AI Tutor - Login")
    pwd = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if pwd == "UNEB_TEST_2026":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong password")
    st.stop()

# Sidebar
st.sidebar.title("UNEB AI Tutor")
subject = st.sidebar.selectbox("Subject", ["Physics", "Chemistry", "Biology"])
level = st.sidebar.selectbox("Level", ["S1", "S2", "S3", "S4"])

modules = {"Physics": physics, "Chemistry": chemistry, "Biology": biology}
current_module = modules[subject]

topics = current_module.get_topics(level)
if not topics:
    topics = ["No topics yet"]
topic = st.sidebar.selectbox("Topic", topics)

# Main Area
st.title(f"{subject} - {level}: {topic}")
content = current_module.get_content(level, topic)
st.markdown(content["text"])

# FORCE RENDER SVG
if content.get("diagram"):
    st.markdown(f"""
    <div style="display:flex; justify-content:center; padding:20px; background:#f0f2f6; border-radius:10px;">
        <svg width="100%" height="350" style="max-width:500px;">
            <use href="#{content['diagram']}"></use>
        </svg>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("No diagram available for this topic yet")

st.divider()
st.subheader("Ask AI Tutor")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about this topic..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        system_prompt = f"You are a UNEB examiner for {subject} {level}. Topic: {topic}. Answer clearly, use Ugandan syllabus. Use simple language. Never use ASCII art. If asked for a diagram, say 'See diagram above'."
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages
        )
        answer = response.choices[0].message.content
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

tz = pytz.timezone("Africa/Kampala")
st.sidebar.write(f"Kampala Time: {datetime.now(tz).strftime('%H:%M')}")
