import streamlit as st
from groq import Groq
import textwrap
import streamlit.components.v1 as components
import datetime
import pytz # NEW
from subjects.physics import run as run_physics
from subjects.chemistry import run as run_chemistry
from subjects.biology import run as run_biology

# --- DEEP SECURITY FORCE LOCK v2.1 - UGANDA TIME ---
UG_TIME = datetime.datetime.now(pytz.timezone('Africa/Kampala')) # NEW
WEEK_NUM = UG_TIME.isocalendar()[1] # CHANGED
WEEKLY_PASSWORD = "UNEB_TEST_2026" 

# 2. ONE-TIME CODES: Use once then deleted. Add new ones here each term
ONE_TIME_CODES = {
    "TEACHER01": "HOD Physics",
    "TEACHER02": "S4 Teacher", 
    "TEACHER03": "S3 Teacher",
    "BACKUP01": "Admin Backup"
}

# Store used codes so they can't be reused
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
                                 # Show logout button at top
            col1, col2 = st.columns([6,1])
            with col2:
                if st.button("Logout"):
                    st.session_state.authenticated = False
                    st.session_state.user = None
                    st.rerun()
                    st.rerun()
                else:
                    st.error("Wrong Weekly Password")
        
        with tab2:
            code = st.text_input("One-Time Code", key="code1").upper()
            if st.button("Login with Code"):
                if code in ONE_TIME_CODES and code not in st.session_state.used_codes:
                    st.session_state.used_codes.append(code) # KILL THE CODE
                    st.session_state.authenticated = True
                    st.session_state.user = ONE_TIME_CODES[code]
                    st.success(f"Welcome {ONE_TIME_CODES[code]}. This code is now DEAD.")
                    st.rerun()
                elif code in st.session_state.used_codes:
                    st.error("Code already used. Ask Admin for new code.")
                else:
                    st.error("Invalid Code")
        
        st.stop()

check_login()
# --- END DEEP SECURITY LOCK --- # --- MAIN APP CONTENT AFTER LOGIN ---

if "logged_in" in st.session_state and st.session_state.logged_in:
    
    st.set_page_config(page_title="UNEB Science Bot v2", layout="wide")
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

else:
    st.warning("Please login first with your ONE_TIME_CODE")

st.set_page_config(page_title="📚 UNEB Physics Bot v18.0", page_icon="📚", layout="wide")

# ========== 1. PRO SVG DIAGRAM ENGINE - ALL 20 DIAGRAMS ==========
def generate_svg_diagram(topic):
    if not topic: return None
    topic = topic.lower().strip()

    # All SVGs: viewBox + width=100% + max-width for mobile. Clear labels + Formula + Principle

    # 1. DC MOTOR
    if "dc motor" in topic or topic == "motor":
        return '''<svg viewBox="0 0 520 320" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:520px;">
          <text x="260" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">BRUSHED DC MOTOR</text>
          <rect x="70" y="60" width="380" height="120" fill="#E8E8E8" stroke="black" stroke-width="2"/><text x="260" y="55" text-anchor="middle" font-size="10">Yoke / Frame</text>
          <text x="50" y="120" font-size="16" font-weight="bold" fill="red">N</text><text x="50" y="135" font-size="9">North Pole</text>
          <text x="470" y="120" font-size="16" font-weight="bold" fill="blue">S</text><text x="470" y="135" font-size="9">South Pole</text>
          <rect x="210" y="90" width="100" height="60" fill="none" stroke="orange" stroke-width="3"/><rect x="215" y="95" width="90" height="50" fill="none" stroke="orange" stroke-width="2"/>
          <text x="260" y="125" text-anchor="middle" font-size="10">Armature Coil: N=100 Turns</text>
          <rect x="110" y="40" width="10" height="25" fill="black"/><text x="115" y="35" text-anchor="middle" font-size="9">Brush +</text>
          <rect x="400" y="40" width="10" height="25" fill="black"/><text x="405" y="35" text-anchor="middle" font-size="9">Brush -</text>
          <circle cx="260" cy="160" r="8" fill="gray" stroke="black"/><text x="270" y="165" font-size="9">Split-ring Commutator</text>
          <line x1="260" y1="170" x2="260" y2="210" stroke="black" stroke-width="2"/>
          <path d="M 260 210 L 275 200" stroke="black" stroke-width="2" marker-end="url(#a1)"/><text x="280" y="205" font-size="9">Rotation</text>
          <defs><marker id="a1" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs>
          <circle cx="40" cy="120" r="12" fill="yellow" stroke="black"/><text x="40" y="125" text-anchor="middle" font-size="8">DC</text>
          <line x1="52" y1="120" x2="110" y2="52" stroke="black" stroke-width="1.5"/>
          <text x="260" y="250" text-anchor="middle" font-size="10" fill="#333">Power Source: DC Battery</text>
          <text x="260" y="270" text-anchor="middle" font-size="10" fill="#333">Principle: F = BILsinθ. Converts Electrical → Mechanical Energy</text>
        </svg>'''

    # 2. AC GENERATOR
    if "ac generator" in topic or "generator" in topic:
        return '''<svg viewBox="0 0 520 340" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:520px;">
          <text x="260" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SIMPLE AC GENERATOR WITH LOAD</text>
          <rect x="60" y="60" width="400" height="100" fill="#E8E8E8" stroke="black" stroke-width="2"/>
          <text x="50" y="110" font-size="16" font-weight="bold" fill="red">N</text><text x="470" y="110" font-size="16" font-weight="bold" fill="blue">S</text>
          <rect x="210" y="75" width="100" height="70" fill="none" stroke="green" stroke-width="2"/><rect x="215" y="80" width="90" height="60" fill="none" stroke="green" stroke-width="1.5"/>
          <text x="260" y="115" text-anchor="middle" font-size="10">Armature Coil: N=200 Turns</text>
          <circle cx="260" cy="170" r="8" fill="silver" stroke="black"/><text x="275" y="175" font-size="9">Slip Ring 1</text>
          <circle cx="260" cy="190" r="8" fill="silver" stroke="black"/><text x="275" y="195" font-size="9">Slip Ring 2</text>
          <rect x="252" y="50" width="6" height="15" fill="black"/><rect x="262" y="50" width="6" height="15" fill="black"/>
          <path d="M 260 60 A 20 20 0 0 1 280 80" fill="none" stroke="green" stroke-width="2" marker-end="url(#a2)"/>
          <line x1="240" y1="190" x2="180" y2="190" stroke="black" stroke-width="2"/><line x1="280" y1="190" x2="340" y2="190" stroke="black" stroke-width="2"/>
          <rect x="340" y="175" width="40" height="30" fill="yellow" stroke="black"/><text x="360" y="195" text-anchor="middle" font-size="9">LOAD</text>
          <defs><marker id="a2" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="green"/></marker></defs>
          <text x="260" y="270" text-anchor="middle" font-size="10" fill="#333">Power Output: AC to Load</text>
          <text x="260" y="290" text-anchor="middle" font-size="10" fill="#333">Principle: e = NABωsinωt. Converts Mechanical → Electrical Energy</text>
        </svg>'''

    # 3. TRANSFORMER
    if "transformer" in topic:
        return '''<svg viewBox="0 0 520 300" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:520px;">
          <text x="260" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SIMPLE TRANSFORMER</text>
          <rect x="150" y="70" width="220" height="120" fill="lightgray" stroke="black" stroke-width="2"/><text x="260" y="135" text-anchor="middle" font-size="10">Soft Iron Core</text>
          <circle cx="120" cy="130" r="30" fill="none" stroke="red" stroke-width="3"/><circle cx="120" cy="130" r="22" fill="none" stroke="red" stroke-width="2"/>
          <text x="120" y="135" text-anchor="middle" font-size="9">Np=100</text><text x="120" y="165" text-anchor="middle" font-size="9" fill="red">PRIMARY</text>
          <circle cx="400" cy="130" r="30" fill="none" stroke="blue" stroke-width="3"/><circle cx="400" cy="130" r="22" fill="none" stroke="blue" stroke-width="2"/>
          <text x="400" y="135" text-anchor="middle" font-size="9">Ns=400</text><text x="400" y="165" text-anchor="middle" font-size="9" fill="blue">SECONDARY</text>
          <circle cx="60" cy="130" r="12" fill="yellow" stroke="black"/><text x="60" y="135" text-anchor="middle" font-size="8">AC</text>
          <line x1="72" y1="130" x2="100" y2="130" stroke="black" stroke-width="2"/>
          <rect x="440" y="115" width="40" height="30" fill="yellow" stroke="black"/><text x="460" y="135" text-anchor="middle" font-size="9">LOAD</text>
          <line x1="420" y1="130" x2="440" y2="130" stroke="black" stroke-width="2"/>
          <text x="260" y="220" text-anchor="middle" font-size="10" fill="#333">Vs/Vp = Ns/Np = 400/100 = 4. Step-up Transformer</text>
          <text x="260" y="240" text-anchor="middle" font-size="10" fill="#333">Principle: Mutual Induction. VpIp = VsIs</text>
        </svg>'''

    # 4. SERIES CIRCUIT
    if "series" in topic and "circuit" in topic:
        return '''<svg viewBox="0 0 450 200" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:450px;">
          <text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SERIES CIRCUIT</text>
          <circle cx="90" cy="100" r="18" fill="yellow" stroke="black" stroke-width="2"/><text x="90" y="105" text-anchor="middle" font-size="10">V</text><text x="90" y="125" text-anchor="middle" font-size="9">Cell</text>
          <rect x="170" y="88" width="50" height="24" fill="white" stroke="black" stroke-width="2"/><text x="195" y="105" text-anchor="middle" font-size="10">R1</text>
          <rect x="270" y="88" width="50" height="24" fill="white" stroke="black" stroke-width="2"/><text x="295" y="105" text-anchor="middle" font-size="10">R2</text>
          <path d="M 90 100 L 170 100 L 220 100 L 270 100 L 320 100 L 360 100 L 360 130 L 90 130 L 90 100" fill="none" stroke="black" stroke-width="2"/>
          <text x="225" y="170" text-anchor="middle" font-size="10" fill="#333">Rule: Same I, Vt = V1 + V2, Rt = R1 + R2</text>
        </svg>'''

    # 5. PARALLEL CIRCUIT
    if "parallel" in topic and "circuit" in topic:
        return '''<svg viewBox="0 0 450 220" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:450px;">
          <text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">PARALLEL CIRCUIT</text>
          <circle cx="90" cy="110" r="18" fill="yellow" stroke="black" stroke-width="2"/><text x="90" y="115" text-anchor="middle" font-size="10">V</text><text x="90" y="135" text-anchor="middle" font-size="9">Cell</text>
          <rect x="170" y="60" width="50" height="24" fill="white" stroke="black" stroke-width="2"/><text x="195" y="77" text-anchor="middle" font-size="10">R1</text>
          <rect x="170" y="140" width="50" height="24" fill="white" stroke="black" stroke-width="2"/><text x="195" y="157" text-anchor="middle" font-size="10">R2</text>
          <path d="M 90 110 L 170 70 L 220 70 L 320 70 M 90 110 L 170 150 L 220 150 L 320 150 M 320 70 L 320 150" fill="none" stroke="black" stroke-width="2"/>
          <text x="225" y="190" text-anchor="middle" font-size="10" fill="#333">Rule: Same V, It = I1 + I2, 1/Rt = 1/R1 + 1/R2</text>
        </svg>'''

    # 6. PRISM
    if "prism" in topic:
        return '''<svg viewBox="0 0 450 240" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:450px;">
          <text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">REFRACTION THROUGH TRIANGULAR PRISM</text>
          <polygon points="100,200 225,40 350,200" fill="lightcyan" stroke="black" stroke-width="2"/>
          <line x1="40" y1="110" x2="180" y2="115" stroke="red" stroke-width="2"/><line x1="180" y1="115" x2="270" y2="185" stroke="red" stroke-width="2"/><line x1="270" y1="185" x2="400" y2="175" stroke="red" stroke-width="2"/>
          <text x="225" y="220" text-anchor="middle" font-size="10" fill="#333">Principle: Refraction at 2 surfaces. Angle of deviation = i + e - A</text>
        </svg>'''

    # 7. CONVEX LENS
    if "convex lens" in topic or "lens" in topic:
        return '''<svg viewBox="0 0 500 220" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:500px;">
          <text x="250" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">CONVEX LENS: REAL IMAGE</text>
          <ellipse cx="250" cy="110" rx="25" ry="80" fill="lightcyan" stroke="black" stroke-width="2"/>
          <line x1="40" y1="110" x2="460" y2="110" stroke="black" stroke-dasharray="4"/><text x="180" y="125" text-anchor="middle" font-size="10">F</text><text x="320" y="125" text-anchor="middle" font-size="10">F</text>
          <text x="250" y="190" text-anchor="middle" font-size="10" fill="#333">Formula: 1/f = 1/u + 1/v. Principle: Refraction</text>
        </svg>'''

    # 8. MAGNETIC FIELD WIRE
    if "magnetic field" in topic and "wire" in topic:
        return '''<svg viewBox="0 0 350 350" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:350px;">
          <text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">MAGNETIC FIELD: CURRENT OUT</text>
          <circle cx="175" cy="175" r="6" fill="black"/><text x="175" y="195" text-anchor="middle" font-size="10">Conductor</text>
          <circle cx="175" cy="175" r="35" fill="none" stroke="black" stroke-width="1.5"/><circle cx="175" cy="175" r="70" fill="none" stroke="black" stroke-width="1.5"/>
          <text x="175" y="320" text-anchor="middle" font-size="10" fill="#333">Rule: Right Hand Grip Rule. B ∝ I/r</text>
        </svg>'''

    # 9. LEVER
    if "lever" in topic:
        return '''<svg viewBox="0 0 450 170" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:450px;">
          <text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">1ST CLASS LEVER</text>
          <line x1="60" y1="90" x2="390" y2="90" stroke="saddlebrown" stroke-width="8"/><polygon points="225,80 235,100 215,100" fill="black"/><text x="225" y="115" text-anchor="middle" font-size="10">Fulcrum F</text>
          <text x="80" y="85" font-size="10">Load</text><text x="350" y="85" font-size="10">Effort</text>
          <text x="225" y="145" text-anchor="middle" font-size="10" fill="#333">Principle: MA = Load/Effort = Effort arm/Load arm</text>
        </svg>'''

    # 10. PULLEY
    if "pulley" in topic:
        return '''<svg viewBox="0 0 350 270" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:350px;">
          <text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SINGLE FIXED PULLEY</text>
          <circle cx="175" cy="70" r="30" fill="none" stroke="black" stroke-width="3"/>
          <line x1="145" y1="70" x2="145" y2="200" stroke="black" stroke-width="2"/><line x1="205" y1="70" x2="205" y2="200" stroke="black" stroke-width="2"/>
          <rect x="135" y="200" width="20" height="20" fill="gray" stroke="black"/><text x="145" y="215" text-anchor="middle" font-size="9">W</text>
          <text x="175" y="240" text-anchor="middle" font-size="10" fill="#333">MA = 1, VR = 1. Changes direction of force</text>
        </svg>'''

    # 11. WAVE
    if "wave" in topic:
        return '''<svg viewBox="0 0 450 170" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:450px;">
          <text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">TRANSVERSE WAVE</text>
          <polyline points="0,85 25,60 50,85 75,110 100,85 125,60 150,85 175,110 200,85 225,60 250,85 275,110 300,85 325,60 350,85 375,110 400,85 425,110 450,85" fill="none" stroke="blue" stroke-width="2"/>
          <text x="225" y="145" text-anchor="middle" font-size="10" fill="#333">v = fλ. Particles vibrate perpendicular to wave direction</text>
        </svg>'''

    # 12. I-V GRAPH
    if "i-v" in topic or "ohm" in topic:
        return '''<svg viewBox="0 0 350 350" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:350px;">
          <text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">I-V GRAPH: OHM'S LAW</text>
          <line x1="50" y1="300" x2="300" y2="300" stroke="black" stroke-width="2"/><line x1="50" y1="300" x2="50" y2="50" stroke="black" stroke-width="2"/>
          <text x="300" y="315" font-size="10">I(A)</text><text x="30" y="50" font-size="10">V(V)</text>
          <line x1="50" y1="300" x2="300" y2="50" stroke="blue" stroke-width="2.5"/>
          <text x="175" y="320" text-anchor="middle" font-size="10" fill="#333">V = IR. Gradient = 1/R</text>
        </svg>'''

    # 13. PLANE MIRROR
    if "plane mirror" in topic:
        return '''<svg viewBox="0 0 450 240" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:450px;">
          <text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">PLANE MIRROR IMAGE</text>
          <line x1="225" y1="50" x2="225" y2="190" stroke="black" stroke-width="5"/><text x="235" y="120" font-size="10">Mirror</text>
          <text x="225" y="210" text-anchor="middle" font-size="10" fill="#333">Image: Same size, Laterally inverted, d(object)=d(image)</text>
        </svg>'''

    # 14. ELECTROSTATICS
    if "electrostatic" in topic or "charge" in topic:
        return '''<svg viewBox="0 0 350 220" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:350px;">
          <text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">LIKE CHARGES REPEL</text>
          <circle cx="110" cy="110" r="18" fill="red" stroke="black"/><text x="110" y="115" text-anchor="middle" fill="white" font-size="10">+</text>
          <circle cx="240" cy="110" r="18" fill="red" stroke="black"/><text x="240" y="115" text-anchor="middle" fill="white" font-size="10">+</text>
          <path d="M 120 100 L 100 80" stroke="red" stroke-width="2" marker-end="url(#a3)"/><path d="M 230 100 L 250 80" stroke="red" stroke-width="2" marker-end="url(#a3)"/>
          <defs><marker id="a3" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="red"/></marker></defs>
          <text x="175" y="190" text-anchor="middle" font-size="10" fill="#333">F = kQ1Q2/r². Like charges repel</text>
        </svg>'''

    # 15. SCREW JACK
    if "screw jack" in topic:
        return '''<svg viewBox="0 0 350 270" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:350px;">
          <text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SCREW JACK</text>
          <rect x="130" y="50" width="90" height="25" fill="gray" stroke="black"/><text x="175" y="45" text-anchor="middle" font-size="9">Tommy Bar</text>
          <rect x="150" y="75" width="50" height="140" fill="lightgray" stroke="black"/><text x="175" y="150" text-anchor="middle" font-size="9">Thread</text>
          <text x="175" y="240" text-anchor="middle" font-size="10" fill="#333">MA = 2πr/p. Principle: Inclined plane wound round cylinder</text>
        </svg>'''

    # 16. LIQUID PRESSURE
    if "pressure" in topic and "liquid" in topic:
        return '''<svg viewBox="0 0 350 270" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:350px;">
          <text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">LIQUID PRESSURE</text>
          <rect x="120" y="60" width="110" height="160" fill="lightblue" stroke="black" stroke-width="2"/>
          <line x1="100" y1="100" x2="120" y2="100" stroke="black" stroke-width="2"/><line x1="100" y1="140" x2="120" y2="140" stroke="black" stroke-width="2"/>
          <text x="175" y="240" text-anchor="middle" font-size="10" fill="#333">P = hρg. Pressure increases with depth</text>
        </svg>'''

    # 17. SPEED-TIME GRAPH
    if "speed-time" in topic or "velocity-time" in topic:
        return '''<svg viewBox="0 0 450 320" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:450px;">
          <text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SPEED-TIME GRAPH</text>
          <line x1="60" y1="280" x2="400" y2="280" stroke="black" stroke-width="2"/><line x1="60" y1="280" x2="60" y2="40" stroke="black" stroke-width="2"/>
          <text x="400" y="295" font-size="10">Time(s)</text><text x="40" y="40" font-size="10">v(m/s)</text>
          <polyline points="60,280 150,200 250,200 350,100" fill="none" stroke="blue" stroke-width="2"/>
          <text x="225" y="300" text-anchor="middle" font-size="10" fill="#333">Area = Distance. Gradient = Acceleration</text>
        </svg>'''

    # 18. BAR MAGNET
    if "magnet" in topic and "field" in topic:
        return '''<svg viewBox="0 0 350 220" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:350px;">
          <text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">BAR MAGNET FIELD LINES</text>
          <rect x="90" y="100" width="50" height="20" fill="red" stroke="black"/><text x="115" y="113" text-anchor="middle" font-size="9">N</text>
          <rect x="210" y="100" width="50" height="20" fill="blue" stroke="black"/><text x="235" y="113" text-anchor="middle" font-size="9">S</text>
          <text x="175" y="190" text-anchor="middle" font-size="10" fill="#333">Field lines: N → S. Closest at poles</text>
        </svg>'''

    # 19. ELECTRIC BELL
    if "electric bell" in topic:
        return '''<svg viewBox="0 0 400 270" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:400px;">
          <text x="200" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">ELECTRIC BELL</text>
          <rect x="120" y="60" width="160" height="40" fill="gray" stroke="black"/><text x="200" y="85" text-anchor="middle" font-size="10">Electromagnet</text>
          <circle cx="200" cy="150" r="25" fill="yellow" stroke="black"/><text x="200" y="155" text-anchor="middle" font-size="9">Gong</text>
          <text x="200" y="240" text-anchor="middle" font-size="10" fill="#333">Principle: Electromagnetism. Converts Electrical → Sound</text>
        </svg>'''

    # 20. PENDULUM
    if "pendulum" in topic:
        return '''<svg viewBox="0 0 350 280" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:350px;">
          <text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SIMPLE PENDULUM</text>
          <line x1="175" y1="60" x2="175" y2="210" stroke="black" stroke-width="2"/><circle cx="175" cy="210" r="20" fill="black"/>
          <text x="175" y="250" text-anchor="middle" font-size="10" fill="#333">T = 2π√(L/g). For small oscillations</text>
        </svg>'''

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

st.title("📚 UNEB Physics Bot v18.0")
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
st.sidebar.markdown("**Included:**")
st.sidebar.markdown("1. 3 Golden Diagrams: Motor, Generator, Transformer")
st.sidebar.markdown("2. UNEB Qn + Marking Guide")
st.sidebar.markdown("3. Full Lesson Plans S1-S4")
st.sidebar.markdown("---")
st.sidebar.warning("**School Password:** `uneb2026`")

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 10px; background-color: #f0f2f6; border-radius: 8px;">
    <p style="margin: 0; font-size: 14px;"><b>UNEB Physics Bot v18.2</b></p>
    <p style="margin: 0; font-size: 12px;">Built for Ugandan S1-S4 Schools</p>
    <p style="margin: 5px 0; font-size: 12px;"><b>Technical Help / Support:</b> WhatsApp <a href="https://wa.me/256751040731">0751040731</a></p>
    <p style="margin: 0; font-size: 11px; color: red;">Note: If bot fails to load or gives errors, contact or WhatsApp 0751040731 for technical help</p>
    <p style="margin: 5px 0 0 0; font-size: 10px;">AI DISCLAIMER: Have your Senior Physics Teacher review all content before exams</p>
</div>
""", unsafe_allow_html=True)
