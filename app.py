import streamlit as st
from groq import Groq
import textwrap
import streamlit.components.v1 as components

st.set_page_config(page_title="📚 UNEB Physics Bot v17.1", page_icon="📚", layout="wide")

# ========== 1. RESPONSIVE SVG DIAGRAM ENGINE ==========
def generate_svg_diagram(topic):
    if not topic: return None
    topic = topic.lower().strip()

    # KEY FIX: width="100%" and viewBox instead of fixed width
    # All SVGs now scale to fit phone screen

    # 1. DC MOTOR - RESPONSIVE
    if "dc motor" in topic or topic == "motor":
        return '''<svg viewBox="0 0 500 300" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:500px;">
          <text x="250" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">BRUSHED DC MOTOR</text>
          <rect x="80" y="70" width="340" height="120" fill="#D0D0D0" stroke="black" stroke-width="2"/>
          <text x="250" y="65" text-anchor="middle" font-size="10" fill="black">Yoke / Frame</text>
          <circle cx="250" cy="130" r="40" fill="white" stroke="black" stroke-width="2"/>
          <text x="250" y="135" text-anchor="middle" font-size="11" fill="black">Armature Coil</text>
          <rect x="100" y="50" width="15" height="30" fill="black"/><text x="107" y="45" text-anchor="middle" font-size="9">Brush</text>
          <rect x="385" y="50" width="15" height="30" fill="black"/><text x="392" y="45" text-anchor="middle" font-size="9">Brush</text>
          <text x="85" y="120" font-size="14" font-weight="bold" fill="red">N</text><text x="85" y="135" font-size="9">North Pole</text>
          <text x="450" y="120" font-size="14" font-weight="bold" fill="blue">S</text><text x="450" y="135" font-size="9">South Pole</text>
          <line x1="250" y1="170" x2="250" y2="200" stroke="orange" stroke-width="4"/><text x="255" y="190" font-size="9">Split-ring Commutator</text>
          <line x1="250" y1="200" x2="250" y2="240" stroke="black" stroke-width="2"/><text x="255" y="235" font-size="9">Axle</text>
          <text x="250" y="275" text-anchor="middle" font-size="10" fill="#333">Principle: F = BILsinθ</text>
        </svg>'''

    # 2. AC GENERATOR - RESPONSIVE
    if "ac generator" in topic or "generator" in topic:
        return '''<svg viewBox="0 0 500 300" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:500px;">
          <text x="250" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SIMPLE AC GENERATOR</text>
          <rect x="80" y="70" width="340" height="120" fill="#D0D0D0" stroke="black" stroke-width="2"/>
          <circle cx="250" cy="130" r="40" fill="white" stroke="black" stroke-width="2"/><text x="250" y="135" text-anchor="middle" font-size="11" fill="black">Armature Coil</text>
          <rect x="100" y="50" width="15" height="30" fill="black"/><text x="107" y="45" text-anchor="middle" font-size="9">Brush 1</text>
          <rect x="385" y="50" width="15" height="30" fill="black"/><text x="392" y="45" text-anchor="middle" font-size="9">Brush 2</text>
          <text x="85" y="120" font-size="14" font-weight="bold" fill="red">N</text>
          <text x="450" y="120" font-size="14" font-weight="bold" fill="blue">S</text>
          <circle cx="250" cy="170" r="8" fill="gray" stroke="black"/><text x="255" y="165" font-size="9">Slip Ring 1</text>
          <circle cx="250" cy="190" r="8" fill="gray" stroke="black"/><text x="255" y="185" font-size="9">Slip Ring 2</text>
          <line x1="250" y1="200" x2="250" y2="240" stroke="black" stroke-width="2"/><text x="255" y="235" font-size="9">Shaft</text>
          <text x="250" y="275" text-anchor="middle" font-size="10" fill="#333">Principle: e = NABωsinωt</text>
        </svg>'''

    # 3. SERIES CIRCUIT
    if "series" in topic and "circuit" in topic:
        return '''<svg viewBox="0 0 450 200" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:450px;"><text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SERIES CIRCUIT</text><circle cx="90" cy="100" r="18" fill="yellow" stroke="black" stroke-width="2"/><text x="90" y="105" text-anchor="middle" font-size="10">V</text><rect x="170" y="88" width="50" height="24" fill="white" stroke="black" stroke-width="2"/><text x="195" y="105" text-anchor="middle" font-size="10">R1</text><rect x="270" y="88" width="50" height="24" fill="white" stroke="black" stroke-width="2"/><text x="295" y="105" text-anchor="middle" font-size="10">R2</text><path d="M 90 100 L 170 100 L 220 100 L 270 100 L 320 100 L 360 100 L 360 130 L 90 130 L 90 100" fill="none" stroke="black" stroke-width="2"/><text x="225" y="170" text-anchor="middle" font-size="10" fill="#333">Rule: Same I, Rt = R1 + R2</text></svg>'''

    # 4. PARALLEL CIRCUIT
    if "parallel" in topic and "circuit" in topic:
        return '''<svg viewBox="0 0 450 220" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:450px;"><text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">PARALLEL CIRCUIT</text><circle cx="90" cy="110" r="18" fill="yellow" stroke="black" stroke-width="2"/><rect x="170" y="60" width="50" height="24" fill="white" stroke="black" stroke-width="2"/><text x="195" y="77" text-anchor="middle" font-size="10">R1</text><rect x="170" y="140" width="50" height="24" fill="white" stroke="black" stroke-width="2"/><text x="195" y="157" text-anchor="middle" font-size="10">R2</text><path d="M 90 110 L 170 70 L 220 70 L 320 70 M 90 110 L 170 150 L 220 150 L 320 150 M 320 70 L 320 150" fill="none" stroke="black" stroke-width="2"/><text x="225" y="190" text-anchor="middle" font-size="10" fill="#333">Rule: Same V, 1/Rt = 1/R1 + 1/R2</text></svg>'''

    # 5. PRISM
    if "prism" in topic:
        return '''<svg viewBox="0 0 450 240" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:450px;"><text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">REFRACTION THROUGH PRISM</text><polygon points="100,200 225,40 350,200" fill="lightcyan" stroke="black" stroke-width="2"/><line x1="40" y1="110" x2="180" y2="115" stroke="red" stroke-width="2"/><line x1="180" y1="115" x2="270" y2="185" stroke="red" stroke-width="2"/><line x1="270" y1="185" x2="400" y2="175" stroke="red" stroke-width="2"/></svg>'''

    # 6. CONVEX LENS
    if "convex lens" in topic or "lens" in topic:
        return '''<svg viewBox="0 0 500 220" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:500px;"><text x="250" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">CONVEX LENS</text><ellipse cx="250" cy="110" rx="25" ry="80" fill="lightcyan" stroke="black" stroke-width="2"/><line x1="40" y1="110" x2="460" y2="110" stroke="black" stroke-dasharray="4"/><text x="180" y="125" text-anchor="middle" font-size="10">F</text><text x="320" y="125" text-anchor="middle" font-size="10">F</text></svg>'''

    # 7. MAGNETIC FIELD WIRE
    if "magnetic field" in topic and "wire" in topic:
        return '''<svg viewBox="0 0 350 350" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:350px;"><text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">MAGNETIC FIELD</text><circle cx="175" cy="175" r="6" fill="black"/><circle cx="175" cy="175" r="35" fill="none" stroke="black" stroke-width="1.5"/><circle cx="175" cy="175" r="70" fill="none" stroke="black" stroke-width="1.5"/><circle cx="175" cy="175" r="105" fill="none" stroke="black" stroke-width="1.5"/></svg>'''

    # 8. LEVER
    if "lever" in topic:
        return '''<svg viewBox="0 0 450 170" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:450px;"><text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">1ST CLASS LEVER</text><line x1="60" y1="90" x2="390" y2="90" stroke="saddlebrown" stroke-width="8"/><polygon points="225,80 235,100 215,100" fill="black"/><text x="225" y="115" text-anchor="middle" font-size="10">Fulcrum F</text></svg>'''

    # 9. PULLEY
    if "pulley" in topic:
        return '''<svg viewBox="0 0 350 270" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:350px;"><text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SINGLE FIXED PULLEY</text><circle cx="175" cy="70" r="30" fill="none" stroke="black" stroke-width="3"/><line x1="145" y1="70" x2="145" y2="200" stroke="black" stroke-width="2"/><line x1="205" y1="70" x2="205" y2="200" stroke="black" stroke-width="2"/></svg>'''

    # 10. WAVE
    if "wave" in topic:
        return '''<svg viewBox="0 0 450 170" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:450px;"><text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">TRANSVERSE WAVE</text><polyline points="0,85 25,60 50,85 75,110 100,85 125,60 150,85 175,110 200,85 225,60 250,85 275,110 300,85 325,60 350,85 375,110 400,85 425,110 450,85" fill="none" stroke="blue" stroke-width="2"/></svg>'''

    # 11-20: ALL OTHERS UPDATED TO RESPONSIVE
    if "i-v" in topic or "ohm" in topic:
        return '''<svg viewBox="0 0 350 350" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:350px;"><text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">I-V GRAPH</text><line x1="50" y1="300" x2="300" y2="300" stroke="black" stroke-width="2"/><line x1="50" y1="300" x2="50" y2="50" stroke="black" stroke-width="2"/><line x1="50" y1="300" x2="300" y2="50" stroke="blue" stroke-width="2.5"/></svg>'''
    
    if "plane mirror" in topic:
        return '''<svg viewBox="0 0 450 240" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:450px;"><text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">PLANE MIRROR</text><line x1="225" y1="50" x2="225" y2="190" stroke="black" stroke-width="5"/></svg>'''
    
    if "transformer" in topic:
        return '''<svg viewBox="0 0 450 220" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:450px;"><text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">TRANSFORMER</text><rect x="120" y="70" width="210" height="80" fill="lightgray" stroke="black" stroke-width="2"/></svg>'''
    
    if "electrostatic" in topic or "charge" in topic:
        return '''<svg viewBox="0 0 350 220" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:350px;"><text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">LIKE CHARGES</text><circle cx="110" cy="110" r="18" fill="red"/><circle cx="240" cy="110" r="18" fill="red"/></svg>'''
    
    if "screw jack" in topic:
        return '''<svg viewBox="0 0 350 270" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:350px;"><text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SCREW JACK</text><rect x="130" y="50" width="90" height="25" fill="gray" stroke="black"/></svg>'''
    
    if "pressure" in topic and "liquid" in topic:
        return '''<svg viewBox="0 0 350 270" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:350px;"><text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">LIQUID PRESSURE</text><rect x="120" y="60" width="110" height="160" fill="lightblue" stroke="black" stroke-width="2"/></svg>'''
    
    if "speed-time" in topic or "velocity-time" in topic:
        return '''<svg viewBox="0 0 450 320" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:450px;"><text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SPEED-TIME GRAPH</text><line x1="60" y1="280" x2="400" y2="280" stroke="black" stroke-width="2"/></svg>'''
    
    if "magnet" in topic and "field" in topic:
        return '''<svg viewBox="0 0 350 220" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:350px;"><text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">BAR MAGNET</text><rect x="90" y="100" width="50" height="20" fill="red" stroke="black"/></svg>'''
    
    if "electric bell" in topic:
        return '''<svg viewBox="0 0 400 270" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:400px;"><text x="200" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">ELECTRIC BELL</text><rect x="120" y="60" width="160" height="40" fill="gray" stroke="black"/></svg>'''

    if "pendulum" in topic:
        return '''<svg viewBox="0 0 350 280" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial; max-width:350px;"><text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SIMPLE PENDULUM</text><line x1="175" y1="60" x2="175" y2="210" stroke="black" stroke-width="2"/><circle cx="175" cy="210" r="20" fill="black"/></svg>'''

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

st.title("📚 UNEB Physics Bot v17.1")
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

if prompt := st.chat_input("Student: Ask any S1-S4 Physics question"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        svg_code = generate_svg_diagram(prompt)
        if svg_code:
            st.markdown("**DIAGRAM:**")
            # KEY FIX: height auto, scrolling=True for mobile
            components.html(svg_code, height=320, scrolling=True)
            st.markdown("---")

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(st.session_state.messages)

        try:
            with st.spinner("Thinking..."):
                res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, max_tokens=1200, temperature=0.3)
            answer = res.choices[0].message.content
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"QC FAIL: AI Error. {e}")

st.sidebar.markdown("### v17.1 Mobile Fix")
st.sidebar.markdown("Diagrams now responsive. Fits phone screen.")
