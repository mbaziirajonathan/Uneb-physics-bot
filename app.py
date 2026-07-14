import streamlit as st
from groq import Groq
import pytz
from datetime import datetime
import subjects.physics as physics
import subjects.chemistry as chemistry
import subjects.biology as biology

# ========= FIX 1: FORCE LOAD ALL SVG SPRITES =========
# This must be at the very top so <use href="#atom"> works everywhere
with open("svg_sprites.py", "r", encoding="utf-8") as f:
    svg_sprites = f.read()
st.markdown(svg_sprites, unsafe_allow_html=True)
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
        # if pwd == "UNEB_TEST_2026":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong password")
    st.stop()

# Sidebar
st.sidebar.title("UNEB AI Tutor")
subject = st.sidebar.selectbox("Subject", ["Physics", "Chemistry", "Biology"])
level = st.sidebar.selectbox("Level", ["S1", "S2", "S3", "S4"])

# Map subject to module
modules = {"Physics": physics, "Chemistry": chemistry, "Biology": biology}
current_module = modules[subject]

# ========= FIX 2: SAFE TOPICS CALL =========
topics = current_module.get_topics(level)
if not topics:
    topics = ["No topics yet"]
topic = st.sidebar.selectbox("Topic", topics)
# ===========================================

# Main Area
st.title(f"{subject} - {level}: {topic}")

# Get content from subject file
content = current_module.get_content(level, topic)

# Show notes
st.markdown(content["text"])

# ========= FIX 3: FORCE RENDER SVG DIAGRAM =========
# This forces it to render the real SVG instead of AI ASCII
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
# ===================================================

st.divider()

# AI Chat
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

# Footer time
tz = pytz.timezone("Africa/Kampala")
st.sidebar.write(f"Kampala Time: {datetime.now(tz).strftime('%H:%M')}")
