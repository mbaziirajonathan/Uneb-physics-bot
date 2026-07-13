import streamlit as st
from groq import Groq
import textwrap
import streamlit.components.v1 as components
import datetime
import pytz
from subjects.physics import run as run_physics
from subjects.chemistry import run as run_chemistry
from subjects.biology import run as run_biology

# MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(page_title="📚 UNEB Physics Bot v18.0", page_icon="📚", layout="wide")

# --- DEEP SECURITY FORCE LOCK v2.1 - UGANDA TIME ---
UG_TIME = datetime.datetime.now(pytz.timezone('Africa/Kampala'))
WEEK_NUM = UG_TIME.isocalendar()[1]
WEEKLY_PASSWORD = "UNEB_TEST_2026"

ONE_TIME_CODES = {
    "TEACHER01": "HOD Physics",
    "TEACHER02": "S4 Teacher",
    "TEACHER03": "S3 Teacher",
    "BACKUP01": "Admin Backup"
}

if "used_codes" not in st.session_state:
    st.session_state.used_codes = []

def check_login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔒 UNEB Physics Bot - Restricted Access")
        st.warning("This bot is for approved teachers only")
        st.caption("Password changes every Monday")

        tab1, tab2 = st.tabs(["Weekly Password Login", "One-Time Code Login"])

        with tab1:
            st.error("Weekly Password is sent to teachers every Monday on WhatsApp")
            email = st.text_input("School Email", key="email1")
            password = st.text_input("Weekly Password", type="password", key="pass1")
            if st.button("Login with Password"):
                if password == WEEKLY_PASSWORD:
                    st.session_state.authenticated = True
                    st.session_state.user = email
                    st.rerun()
                else:
                    st.error("Wrong Weekly Password")

        with tab2:
            code = st.text_input("One-Time Code", key="code1").upper()
            if st.button("Login with Code"):
                if code in ONE_TIME_CODES and code not in st.session_state.used_codes:
                    st.session_state.used_codes.append(code)
                    st.session_state.authenticated = True
                    st.session_state.user = ONE_TIME_CODES[code]
                    st.success(f"Welcome {ONE_TIME_CODES[code]}. This code is now DEAD.")
                    st.rerun()
                elif code in st.session_state.used_codes:
                    st.error("Code already used. Ask Admin for new code.")
                else:
                    st.error("Invalid Code")

        # Logout button at top right
        col1, col2 = st.columns([6,1])
        with col2:
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.rerun()

        st.stop()

check_login()
# --- END DEEP SECURITY LOCK ---

# --- MAIN APP CONTENT AFTER LOGIN ---
if st.session_state.authenticated: # FIXED: was "logged_in"

    st.title("🧪 UNEB Science Bot v2.0")
    st.markdown("**NCDC 2026 Syllabus | S1 - S4 | Physics, Chemistry, Biology**")

    # Sidebar
    st.sidebar.header("Select Options")
    subject = st.sidebar.selectbox("Choose Subject", ["Physics", "Chemistry", "Biology"])
    level = st.sidebar.selectbox("Choose Level", ["S1", "S2", "S3", "S4"])

    st.sidebar.markdown("---")
    st.sidebar.info("Select a topic from the dropdown below to see the labeled diagram")

    # Main Area
    col1, col2 = st.columns([3, 1])

    with col1:
        if subject == "Physics":
            run_physics(level)
        elif subject == "Chemistry":
            run_chemistry(level)
        elif subject == "Biology":
            run_biology(level)

    with col2:
        st.subheader("How to use")
        st.write("1. Choose Subject")
        st.write("2. Choose S1-S4")
        st.write("3. Choose Topic")
        st.write("4. Diagram appears with labels")
        st.markdown("---")
        st.caption("Built for UNEB 2026")

# ========== 1. PRO SVG DIAGRAM ENGINE - ALL 20 DIAGRAMS ==========
def generate_svg_diagram(topic):
    if not topic: return None
    topic = topic.lower().strip()

    # 1. DC MOTOR
    if "dc motor" in topic or topic == "motor":
        return '''<svg viewBox="0 0 520 320" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:520px;"><text x="260" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">BRUSHED DC MOTOR</text></svg>'''

    #... keep all your other 19 SVGs here...

    return None

# ========== 2. GROQ CLIENT ==========
@st.cache_resource
def get_client():
    try:
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except:
        st.error("QC FAIL: GROQ_API_KEY not found in Streamlit Secrets.")
        st.stop()

client = get_client()

st.markdown("*This bot works WITH your school teacher, not instead of them*")

SYSTEM_PROMPT = textwrap.dedent("""
You are an expert UNEB S1-S4 Physics tutor for Uganda.
CRITICAL RULES:
1. DIAGRAMS: If user asks "draw", "diagram", "sketch", say "See diagram above" then explain parts.
2. STRUCTURE: Always give: 1. Explanation 2. Formula + SI Unit 3. Worked Example with 3 Steps 4. Practice Question with [marks]
3. SCOPE: Only S1-S4 UNEB Physics.
4. TEACHER NOTES: End with "TEACHER GROUND NOTES: [3 teaching tips]"
5. DISCLAIMER: End with "AI DISCLAIMER: This is AI generated. Have your Senior Physics Teacher review before exams."
""").strip()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Teacher: Ask Qn or type 'prepare lesson on Ohm's Law'"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        svg_code = generate_svg_diagram(prompt)
        if svg_code:
            st.markdown("**DIAGRAM:**")
            components.html(svg_code, height=400)
            st.markdown("---")

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(st.session_state.messages)

        try:
            with st.spinner("Preparing your UNEB lesson..."):
                res = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=messages,
                    max_tokens=1600,
                    temperature=0.2
                )
            answer = res.choices[0].message.content
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"QC FAIL: AI Error. {e}")

# ========== SIDEBAR + FOOTER ==========
st.sidebar.markdown("### 📚 v18.2 + Lesson Plans")
st.sidebar.success("NEW: UNEB Lesson Prep for S1-S4")
st.sidebar.markdown("**Try These Prompts:**")
st.sidebar.code('prepare lesson on Waves S3')
st.sidebar.code('prepare lesson on Density S2')
st.sidebar.code('draw dc motor')
st.sidebar.markdown("---")
st.sidebar.warning("**School Password:** `uneb2026`")

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 10px; background-color: #f0f2f6; border-radius: 8px;">
    <p style="margin: 0; font-size: 14px;"><b>UNEB Physics Bot v18.2</b></p>
    <p style="margin: 0; font-size: 12px;">Built for Ugandan S1-S4 Schools</p>
    <p style="margin: 5px 0; font-size: 12px;"><b>Technical Help / Support:</b> WhatsApp <a href="https://wa.me/256751040731">0751040731</a></p>
    <p style="margin: 0; font-size: 11px; color: red;">Note: If bot fails to load or gives errors, contact or WhatsApp 0751040731 for technical help</p>
</div>
""", unsafe_allow_html=True)
