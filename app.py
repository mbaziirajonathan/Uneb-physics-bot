import streamlit as st
import os
import pytz
from datetime import datetime
from groq import Groq, GroqError
from typing import Dict, Any

# Ensure Sprites.py is in the same directory
try:
    from Sprites import DiagramManager, UNEB_CURRICULUM_MAP
except ImportError:
    st.error("🚨 Critical Error: 'Sprites.py' not found. Please ensure it is in the same directory as app.py.")
    st.stop()

# Graceful import of subject content (Fallback if modules are incomplete)
try:
    import subjects.physics as physics
    import subjects.chemistry as chemistry
    import subjects.biology as biology
    SUBJECT_MODULES = {"Physics": physics, "Chemistry": chemistry, "Biology": biology}
except ImportError:
    SUBJECT_MODULES = {}
    st.warning("⚠️ Subject content modules not fully found. Defaulting to AI & Diagram generation only.")

# ==========================================
# 1. APPLICATION CONFIGURATION & STATE
# ==========================================
st.set_page_config(
    page_title="UNEB AI Tutor 2026",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session_state():
    """Initializes strictly typed session state variables."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # Track the current topic to clear chat history when the topic changes
    if "current_topic" not in st.session_state:
        st.session_state.current_topic = None

# ==========================================
# 2. AUTHENTICATION GATE
# ==========================================
def render_auth_gate():
    """Renders a secure login portal before accessing the engine."""
    st.title("🛡️ UNEB AI Tutor - Secure Access")
    with st.form("login_form"):
        pwd = st.text_input("Enter Access Token", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            # Note: In production, map this to st.secrets["APP_PASSWORD"]
            if pwd == "UNEB_TEST_2026":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid token. Access denied.")
    st.stop()

# ==========================================
# 3. AI ENGINE INTEGRATION
# ==========================================
def get_groq_client() -> Groq:
    """Safely instantiates the Groq client catching deployment secret errors."""
    try:
        api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("API Key missing.")
        return Groq(api_key=api_key)
    except Exception as e:
        st.error(f"🚨 Integration Error: Groq API Key not configured properly in Streamlit secrets.")
        st.stop()

def generate_ai_response(client: Groq, subject: str, level: str, topic: str, user_prompt: str):
    """Handles API calls to Groq with strict UNEB system prompting."""
    system_prompt = (
        f"You are an expert UNEB examiner and tutor for {subject} {level}. "
        f"The current topic is: {topic}. "
        "Strictly align your answers with the Ugandan Lower Secondary Curriculum. "
        "Use clear, direct language. Use bullet points for readability. "
        "Never use ASCII art. If a user asks for a diagram, tell them: 'Please refer to the diagram rendered in the interactive viewer above'."
    )
    
    messages_payload = [{"role": "system", "content": system_prompt}] + st.session_state.messages
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages_payload,
            temperature=0.3, # Low temperature for factual accuracy
            max_tokens=1024
        )
        return response.choices[0].message.content
    except GroqError as e:
        return f"⚠️ Connection Error to AI Engine: {str(e)}"

# ==========================================
# 4. MAIN UI ORCHESTRATION
# ==========================================
def main():
    init_session_state()
    
    if not st.session_state.logged_in:
        render_auth_gate()

    # Inject DOM Sprites silently
    DiagramManager.initialize_sprites()
    client = get_groq_client()

    # --- SIDEBAR NAVIGATION ---
    st.sidebar.title("📚 UNEB Navigation")
    
    # Drive navigation dynamically from the Sprites.py Curriculum Map
    subject = st.sidebar.selectbox("Subject", list(UNEB_CURRICULUM_MAP.keys()))
    level = st.sidebar.selectbox("Class Level", list(UNEB_CURRICULUM_MAP[subject].keys()))
    topics_list = list(UNEB_CURRICULUM_MAP[subject][level].keys())
    
    if not topics_list:
        st.sidebar.warning("No topics mapped for this level yet.")
        st.stop()
        
    topic = st.sidebar.selectbox("Topic", topics_list)

    # Clear chat history if the user switches topics
    if st.session_state.current_topic != f"{subject}_{level}_{topic}":
        st.session_state.messages = []
        st.session_state.current_topic = f"{subject}_{level}_{topic}"

    # Timezone Display
    tz = pytz.timezone("Africa/Kampala")
    st.sidebar.divider()
    st.sidebar.caption(f"📍 Kampala Time: {datetime.now(tz).strftime('%A, %H:%M %p')}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # --- MAIN CONTENT AREA ---
    st.title(f"{subject} {level}: {topic}")
    
    # Layout: Content on Left, Diagram on Right
    col_text, col_visual = st.columns([1.2, 1])
    
    with col_text:
        st.subheader("📖 Topic Overview")
        # Try to load hardcoded module text if it exists
        if subject in SUBJECT_MODULES:
            try:
                content = SUBJECT_MODULES[subject].get_content(level, topic)
                st.markdown(content.get("text", "No text overview provided in module."))
            except Exception:
                st.info("Ask the AI Tutor below for an overview of this topic.")
        else:
            st.info("Ask the AI Tutor below for a detailed explanation of this topic.")

    with col_visual:
        st.subheader("🔬 Interactive Diagram")
        # Command Sprites.py to fetch and render the correct diagram
        symbol_id = DiagramManager.get_symbol_by_curriculum(subject, level, topic)
        DiagramManager.render(symbol_id)

    st.divider()

    # --- CHATBOT INTERFACE ---
    st.subheader("🤖 Ask the UNEB AI Tutor")
    
    # Render existing messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input Box
    if prompt := st.chat_input("E.g., Explain how this diagram works..."):
        # Append User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and Append AI Message
        with st.chat_message("assistant"):
            with st.spinner("Analyzing UNEB syllabus..."):
                answer = generate_ai_response(client, subject, level, topic, prompt)
                st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

if __name__ == "__main__":
    main()
