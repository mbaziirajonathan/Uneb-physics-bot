import streamlit as st # FIX 1: Removed duplicate pd import
import pytz
from datetime import datetime
from groq import Groq 
from assets.svg_sprites import load_svg_sprite
from subjects import biology, chemistry, physics

# Page Config
st.set_page_config(page_title="Uganda AI Tutor", page_icon="🇺🇬", layout="wide")

# Secrets Configuration
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"]) #.get() hides errors. Use [] to fail fast
except KeyError:
    st.error("🔑 GROQ_API_KEY not found in Secrets. Add it in Advanced Settings.")
    st.stop()

# Password Gate
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🇺🇬 Uganda National Exams Board AI Tutor")
    with st.form("login_form"):
        password = st.text_input("Enter Access Password", type="password")
        submit_button = st.form_submit_button("Login")
        if submit_button:
            if password == "UNEB_TEST_2026":
                st.session_state.authenticated = True
                st.rerun() # FIX 2: Removed st.invalidate_pages()
            else:
                st.error("❌ Incorrect password.")
    st.stop()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
tz = pytz.timezone("Africa/Kampala")
now = datetime.now(tz)
st.sidebar.markdown(f"🗓️ **Date:** `{now.strftime('%Y-%m-%d')}`")
st.sidebar.markdown(f"⏰ **Time:** `{now.strftime('%I:%M %p')}`")
st.sidebar.divider()

st.sidebar.title("📚 Navigation")
subject = st.sidebar.selectbox("Subject", ["Biology", "Chemistry", "Physics"])
level = st.sidebar.selectbox("Level", ["S1", "S2", "S3", "S4"])

subject_modules = {"Biology": biology, "Chemistry": chemistry, "Physics": physics}
current_module = subject_modules[subject]

topics = current_module.get_topics(level)
topic = st.sidebar.selectbox("Topic", topics)

# Main Content
st.title(f"{subject} — {level}")
st.header(f"📌 {topic}")

content = current_module.get_content(level, topic)
st.markdown(content["text"])

if content.get("diagram"):
    svg_html = load_svg_sprite(content["diagram"])
    if svg_html:
        st.markdown(svg_html, unsafe_allow_html=True)

# AI Chat Section
st.divider()
st.subheader("🤖 Ask your UNEB Assistant")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

with st.form("chat_input_form", clear_on_submit=True):
    user_q = st.text_input("Type your question here...")
    submit_q = st.form_submit_button("Ask AI")

if submit_q and user_q:
    st.session_state.messages.append({"role": "user", "content": user_q})
    
    system_prompt = {
        "role": "system", 
        "content": f"You are an expert Ugandan UNEB secondary school teacher. Student is studying {subject} at {level} level, topic '{topic}'. Answer clearly, aligned with Uganda National Curriculum. No hallucinations."
    }
    
    # FIX 3: Send full history + system prompt to AI
    messages_for_api = [system_prompt] + st.session_state.messages
    
    with st.spinner("Analyzing..."):
        try:
            chat_completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages_for_api
            )
            ai_response = chat_completion.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            st.rerun() # Rerun to display new message
        except Exception as e:
            st.error(f"AI Error: {e}")
