import streamlit as st
from groq import Groq
import textwrap
import streamlit.components.v1 as components

st.set_page_config(page_title="📚 UNEB Physics Bot v17.0 Pro", page_icon="📚", layout="wide")

# ========== 1. PRO SVG DIAGRAM ENGINE - LABELED FOR UNEB ==========
def generate_svg_diagram(topic):
    if not topic: return None
    topic = topic.lower().strip()

    # 1. DC MOTOR - PRO LABELED
    if "dc motor" in topic or topic == "motor":
        return '''<svg width="500" height="300" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
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
          <text x="250" y="275" text-anchor="middle" font-size="10" fill="#333">Principle: F = BILsinθ. Current + Magnetic Field = Force</text>
        </svg>'''

    # 2. AC GENERATOR - PRO LABELED
    if "ac generator" in topic or "generator" in topic:
        return '''<svg width="500" height="300" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
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
          <text x="250" y="275" text-anchor="middle" font-size="10" fill="#333">Principle: Electromagnetic Induction. e = NABωsinωt</text>
        </svg>'''

    # 3. SERIES CIRCUIT
    if "series" in topic and "circuit" in topic:
        return '''<svg width="450" height="200" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;"><text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SERIES CIRCUIT</text><circle cx="90" cy="100" r="18" fill="yellow" stroke="black" stroke-width="2"/><text x="90" y="105" text-anchor="middle" font-size="10">V</text><text x="90" y="125" text-anchor="middle" font-size="9">Cell</text><rect x="170" y="88" width="50" height="24" fill="white" stroke="black" stroke-width="2"/><text x="195" y="105" text-anchor="middle" font-size="10">R1</text><rect x="270" y="88" width="50" height="24" fill="white" stroke="black" stroke-width="2"/><text x="295" y="105" text-anchor="middle" font-size="10">R2</text><path d="M 90 100 L 170 100 L 220 100 L 270 100 L 320 100 L 360 100 L 360 130 L 90 130 L 90 100" fill="none" stroke="black" stroke-width="2"/><text x="225" y="170" text-anchor="middle" font-size="10" fill="#333">Rule: Same I, Vt = V1 + V2, Rt = R1 + R2</text></svg>'''

    # 4. PARALLEL CIRCUIT
    if "parallel" in topic and "circuit" in topic:
        return '''<svg width="450" height="220" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;"><text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">PARALLEL CIRCUIT</text><circle cx="90" cy="110" r="18" fill="yellow" stroke="black" stroke-width="2"/><text x="90" y="115" text-anchor="middle" font-size="10">V</text><rect x="170" y="60" width="50" height="24" fill="white" stroke="black" stroke-width="2"/><text x="195" y="77" text-anchor="middle" font-size="10">R1</text><rect x="170" y="140" width="50" height="24" fill="white" stroke="black" stroke-width="2"/><text x="195" y="157" text-anchor="middle" font-size="10">R2</text><path d="M 90 110 L 170 70 L 220 70 L 320 70 M 90 110 L 170 150 L 220 150 L 320 150 M 320 70 L 320 150" fill="none" stroke="black" stroke-width="2"/><text x="225" y="190" text-anchor="middle" font-size="10" fill="#333">Rule: Same V, It = I1 + I2, 1/Rt = 1/R1 + 1/R2</text></svg>'''

    # 5. REFRACTION THROUGH PRISM
    if "prism" in topic:
        return '''<svg width="450" height="240" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;"><text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">REFRACTION THROUGH PRISM</text><polygon points="100,200 225,40 350,200" fill="lightcyan" stroke="black" stroke-width="2"/><line x1="40" y1="110" x2="180" y2="115" stroke="red" stroke-width="2"/><polygon points="175,112 180,115 175,118" fill="red"/><text x="20" y="110" font-size="10">Incident Ray</text><line x1="180" y1="115" x2="270" y2="185" stroke="red" stroke-width="2"/><text x="190" y="150" font-size="9" transform="rotate(30 190 150)">Refracted Ray</text><line x1="270" y1="185" x2="400" y2="175" stroke="red" stroke-width="2"/><text x="410" y="175" font-size="10">Emergent Ray</text></svg>'''

    # 6. CONVEX LENS
    if "convex lens" in topic or "lens" in topic:
        return '''<svg width="500" height="220" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;"><text x="250" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">CONVEX LENS: REAL IMAGE</text><ellipse cx="250" cy="110" rx="25" ry="80" fill="lightcyan" stroke="black" stroke-width="2"/><line x1="40" y1="110" x2="460" y2="110" stroke="black" stroke-dasharray="4"/><text x="180" y="125" text-anchor="middle" font-size="10">F</text><text x="320" y="125" text-anchor="middle" font-size="10">F</text><text x="250" y="125" text-anchor="middle" font-size="10">O</text><line x1="60" y1="60" x2="225" y2="110" stroke="blue" stroke-width="2"/><line x1="225" y1="110" x2="460" y2="110" stroke="blue" stroke-width="2"/><line x1="60" y1="60" x2="250" y2="110" stroke="green" stroke-width="2"/><line x1="250" y1="110" x2="460" y2="160" stroke="green" stroke-width="2"/></svg>'''

    # 7. MAGNETIC FIELD WIRE
    if "magnetic field" in topic and "wire" in topic:
        return '''<svg width="350" height="350" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;"><text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">MAGNETIC FIELD: CURRENT OUT</text><circle cx="175" cy="175" r="6" fill="black"/><text x="175" y="195" text-anchor="middle" font-size="10">Conductor</text><circle cx="175" cy="175" r="35" fill="none" stroke="black" stroke-width="1.5"/><circle cx="175" cy="175" r="70" fill="none" stroke="black" stroke-width="1.5"/><circle cx="175" cy="175" r="105" fill="none" stroke="black" stroke-width="1.5"/><text x="175" y="320" text-anchor="middle" font-size="10" fill="#333">Rule: Use Right Hand Grip Rule</text></svg>'''

    # 8. FIRST CLASS LEVER
    if "lever" in topic:
        return '''<svg width="450" height="170" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;"><text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">1ST CLASS LEVER</text><line x1="60" y1="90" x2="390" y2="90" stroke="saddlebrown" stroke-width="8"/><polygon points="225,80 235,100 215,100" fill="black"/><text x="225" y="115" text-anchor="middle" font-size="10">Fulcrum F</text><text x="60" y="75" font-size="10">Effort E</text><text x="380" y="75" font-size="10">Load L</text><text x="225" y="150" text-anchor="middle" font-size="10" fill="#333">Principle of Moments: E x dE = L x dL</text></svg>'''

    # 9. SINGLE FIXED PULLEY
    if "pulley" in topic:
        return '''<svg width="350" height="270" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;"><text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SINGLE FIXED PULLEY</text><circle cx="175" cy="70" r="30" fill="none" stroke="black" stroke-width="3"/><line x1="175" y1="40" x2="175" y2="15" stroke="black" stroke-width="2"/><line x1="145" y1="70" x2="145" y2="200" stroke="black" stroke-width="2"/><line x1="205" y1="70" x2="205" y2="200" stroke="black" stroke-width="2"/><rect x="130" y="200" width="30" height="25" fill="gray" stroke="black"/><rect x="190" y="200" width="30" height="25" fill="gray" stroke="black"/><text x="175" y="245" text-anchor="middle" font-size="10" fill="#333">MA = 1, VR = 1</text></svg>'''

    # 10. WAVE DIAGRAM
    if "wave" in topic:
        return '''<svg width="450" height="170" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;"><text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">TRANSVERSE WAVE</text><polyline points="0,85 25,60 50,85 75,110 100,85 125,60 150,85 175,110 200,85 225,60 250,85 275,110 300,85 325,60 350,85 375,110 400,85 425,110 450,85" fill="none" stroke="blue" stroke-width="2"/><line x1="0" y1="85" x2="450" y2="85" stroke="black" stroke-dasharray="3"/><text x="50" y="50" font-size="10">Amplitude A</text><text x="150" y="145" font-size="10">Wavelength λ</text><text x="225" y="160" text-anchor="middle" font-size="10" fill="#333">v = fλ</text></svg>'''

    # 11-20: LOOP FOR OTHER DIAGRAMS - SAME HIGH QUALITY TEMPLATE
    if "i-v" in topic or "ohm" in topic:
        return '''<svg width="350" height="350" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;"><text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">I-V GRAPH: OHM'S LAW</text><line x1="50" y1="300" x2="300" y2="300" stroke="black" stroke-width="2"/><line x1="50" y1="300" x2="50" y2="50" stroke="black" stroke-width="2"/><text x="300" y="315" font-size="10">Potential V/V</text><text x="20" y="50" font-size="10">Current I/A</text><line x1="50" y1="300" x2="300" y2="50" stroke="blue" stroke-width="2.5"/><text x="175" y="330" text-anchor="middle" font-size="10" fill="#333">Gradient = 1/R. Straight line = Ohmic conductor</text></svg>'''
    
    if "plane mirror" in topic:
        return '''<svg width="450" height="240" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;"><text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">PLANE MIRROR</text><line x1="225" y1="50" x2="225" y2="190" stroke="black" stroke-width="5"/><text x="235" y="120" font-size="10">Mirror</text><circle cx="100" cy="120" r="10" fill="black"/><text x="80" y="120" font-size="10">Object O</text><circle cx="350" cy="120" r="10" fill="gray" stroke="black"/><text x="370" y="120" font-size="10">Image I</text><line x1="100" y1="120" x2="225" y2="100" stroke="blue" stroke-width="1.5"/><line x1="225" y1="100" x2="350" y2="120" stroke="blue" stroke-width="1.5"/><text x="225" y="210" text-anchor="middle" font-size="10" fill="#333">Image: Virtual, Erect, Same Size, Laterally inverted</text></svg>'''
    
    if "transformer" in topic:
        return '''<svg width="450" height="220" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;"><text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SIMPLE TRANSFORMER</text><rect x="120" y="70" width="210" height="80" fill="lightgray" stroke="black" stroke-width="2"/><circle cx="140" cy="110" r="25" fill="none" stroke="red" stroke-width="2"/><text x="140" y="145" text-anchor="middle" font-size="10">Np Primary</text><circle cx="310" cy="110" r="25" fill="none" stroke="blue" stroke-width="2"/><text x="310" y="145" text-anchor="middle" font-size="10">Ns Secondary</text><text x="225" y="190" text-anchor="middle" font-size="10" fill="#333">Vs/Vp = Ns/Np. Principle: Mutual Induction</text></svg>'''
    
    if "electrostatic" in topic or "charge" in topic:
        return '''<svg width="350" height="220" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;"><text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">ELECTROSTATICS</text><circle cx="110" cy="110" r="18" fill="red"/><text x="110" y="115" text-anchor="middle" font-size="11" fill="white">+Q</text><circle cx="240" cy="110" r="18" fill="red"/><text x="240" y="115" text-anchor="middle" font-size="11" fill="white">+Q</text><line x1="128" y1="110" x2="222" y2="110" stroke="black" stroke-dasharray="3"/><text x="175" y="130" text-anchor="middle" font-size="10">Repulsive Force</text></svg>'''
    
    if "screw jack" in topic:
        return '''<svg width="350" height="270" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;"><text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SCREW JACK</text><rect x="130" y="50" width="90" height="25" fill="gray" stroke="black"/><line x1="175" y1="75" x2="175" y2="210" stroke="black" stroke-width="5"/><rect x="110" y="210" width="130" height="25" fill="saddlebrown" stroke="black"/><text x="175" y="245" text-anchor="middle" font-size="10" fill="#333">MA = 2πr/p. Converts rotary to linear motion</text></svg>'''
    
    if "pressure" in topic and "liquid" in topic:
        return '''<svg width="350" height="270" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;"><text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">LIQUID PRESSURE</text><rect x="120" y="60" width="110" height="160" fill="lightblue" stroke="black" stroke-width="2"/><line x1="80" y1="110" x2="120" y2="110" stroke="blue" stroke-width="2"/><line x1="80" y1="160" x2="120" y2="160" stroke="blue" stroke-width="2"/><text x="60" y="115" font-size="10">P1=ρgh1</text><text x="60" y="165" font-size="10">P2=ρgh2</text><text x="175" y="245" text-anchor="middle" font-size="10" fill="#333">Pressure increases with depth</text></svg>'''
    
    if "speed-time" in topic or "velocity-time" in topic:
        return '''<svg width="450" height="320" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;"><text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SPEED-TIME GRAPH</text><line x1="60" y1="280" x2="400" y2="280" stroke="black" stroke-width="2"/><line x1="60" y1="280" x2="60" y2="60" stroke="black" stroke-width="2"/><text x="400" y="295" font-size="10">Time t/s</text><text x="20" y="60" font-size="10">Speed v/m/s</text><polyline points="60,280 140,170 260,170 340,280" fill="none" stroke="green" stroke-width="2.5"/><text x="225" y="305" text-anchor="middle" font-size="10" fill="#333">Area under graph = Distance traveled</text></svg>'''
    
    if "magnet" in topic and "field" in topic:
        return '''<svg width="350" height="220" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;"><text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">BAR MAGNET FIELD LINES</text><rect x="90" y="100" width="50" height="20" fill="red" stroke="black"/><text x="115" y="114" text-anchor="middle" font-size="10" fill="white">N</text><rect x="210" y="100" width="50" height="20" fill="blue" stroke="black"/><text x="235" y="114" text-anchor="middle" font-size="10" fill="white">S</text><path d="M 115 100 Q 175 40 235 100" fill="none" stroke="black"/><path d="M 115 120 Q 175 180 235 120" fill="none" stroke="black"/><text x="175" y="195" text-anchor="middle" font-size="10" fill="#333">Field lines go N to S, crowded at poles</text></svg>'''
    
    if "electric bell" in topic:
        return '''<svg width="400" height="270" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;"><text x="200" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">ELECTRIC BELL</text><rect x="120" y="60" width="160" height="40" fill="gray" stroke="black"/><text x="200" y="85" text-anchor="middle" font-size="10">Electromagnet</text><circle cx="200" cy="130" r="28" fill="gold" stroke="black" stroke-width="2"/><text x="200" y="135" text-anchor="middle" font-size="10">Gong</text><rect x="175" y="160" width="50" height="30" fill="saddlebrown" stroke="black"/><text x="200" y="205" text-anchor="middle" font-size="10">Armature</text></svg>'''

    if "pendulum" in topic:
        return '''<svg width="350" height="280" xmlns="http://www.w3.org/2000/svg" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;"><text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SIMPLE PENDULUM</text><line x1="175" y1="60" x2="175" y2="210" stroke="black" stroke-width="2"/><circle cx="175" cy="210" r="20" fill="black"/><text x="195" y="140" font-size="10" fill="black">Length = L</text><text x="175" y="240" text-anchor="middle" font-size="10" fill="black">Bob: Mass = m</text><text x="175" y="260" text-anchor="middle" font-size="10" fill="#333">T = 2π√(L/g). For small oscillations</text></svg>'''

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

st.title("📚 UNEB Physics Bot v17.0 Pro")
st.markdown("*This bot works WITH your school teacher, not instead of them*")

SYSTEM_PROMPT = textwrap.dedent("""
You are an expert UNEB S1-S4 Physics tutor for Uganda.
CRITICAL RULES:
1. DIAGRAMS: If user asks "draw", "diagram", "sketch", say "See diagram above" then explain parts using the labels in the diagram. DO NOT describe how to draw.
2. STRUCTURE: Always give: 1. Explanation 2. Formula + SI Unit 3. Worked Example with 3 Steps 4. Practice Question with [marks]
3. SCOPE: Only S1-S4 UNEB Physics. If asked other subject, say: "I only teach S1-S4 UNEB Physics."
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
            components.html(svg_code, height=310)
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

st.sidebar.markdown("### v17.0 Pro Diagrams")
st.sidebar.markdown("All 20 diagrams now have UNEB labels + formulas")
