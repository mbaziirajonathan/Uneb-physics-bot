import streamlit as st
from groq import Groq
import textwrap

st.set_page_config(page_title="📚 UNEB Physics Bot v16.2", page_icon="📚", layout="wide")

# ========== 1. SVG DIAGRAM ENGINE - TOP 20 UNEB ==========
def generate_svg_diagram(topic):
    if not topic: return None
    topic = topic.lower().strip()

    # 1. DC MOTOR
    if "dc motor" in topic:
        return '''<svg width="420" height="260" xmlns="http://www.w3.org/2000/svg" style="background:white; border:1px solid #ccc; border-radius:8px;"><text x="210" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="black">DC MOTOR</text><rect x="60" y="60" width="300" height="100" fill="#E0E0E0" stroke="black" stroke-width="2"/><circle cx="210" cy="110" r="35" fill="white" stroke="black"/><text x="210" y="115" text-anchor="middle" font-size="10" fill="black">Armature</text><rect x="80" y="45" width="12" height="25" fill="black"/><rect x="328" y="45" width="12" height="25" fill="black"/><text x="65" y="90" font-size="12" font-weight="bold" fill="red">N</text><text x="350" y="90" font-size="12" font-weight="bold" fill="blue">S</text><line x1="210" y1="145" x2="210" y2="175" stroke="orange" stroke-width="3"/><text x="210" y="240" text-anchor="middle" font-size="10" fill="#555">Parts: Armature, Brushes, N/S Magnets, Commutator</text></svg>'''

    # 2. SIMPLE PENDULUM
    if "pendulum" in topic:
        return '''<svg width="300" height="260" xmlns="http://www.w3.org/2000/svg" style="background:white; border:1px solid #ccc; border-radius:8px;"><text x="150" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="black">SIMPLE PENDULUM</text><line x1="150" y1="50" x2="150" y2="200" stroke="black" stroke-width="2"/><circle cx="150" cy="200" r="18" fill="black"/><text x="170" y="130" font-size="10" fill="black">Length = L</text><text x="150" y="230" text-anchor="middle" font-size="10" fill="black">Bob: Mass = m</text><text x="150" y="250" text-anchor="middle" font-size="9" fill="#555">T = 2π√(L/g)</text></svg>'''

    # 3. SERIES CIRCUIT
    if "series" in topic and "circuit" in topic:
        return '''<svg width="400" height="180" xmlns="http://www.w3.org/2000/svg" style="background:white; border:1px solid #ccc; border-radius:8px;"><text x="200" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="black">SERIES CIRCUIT</text><circle cx="80" cy="90" r="15" fill="yellow" stroke="black"/><text x="80" y="95" text-anchor="middle" font-size="9">Cell</text><rect x="150" y="80" width="40" height="20" fill="white" stroke="black"/><text x="170" y="95" text-anchor="middle" font-size="9">R1</text><rect x="240" y="80" width="40" height="20" fill="white" stroke="black"/><text x="260" y="95" text-anchor="middle" font-size="9">R2</text><path d="M 80 90 L 150 90 L 190 90 L 240 90 L 280 90 L 320 90 L 320 120 L 80 120 L 80 90" fill="none" stroke="black" stroke-width="2"/></svg>'''

    # 4. PARALLEL CIRCUIT
    if "parallel" in topic and "circuit" in topic:
        return '''<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg" style="background:white; border:1px solid #ccc; border-radius:8px;"><text x="200" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="black">PARALLEL CIRCUIT</text><circle cx="80" cy="100" r="15" fill="yellow" stroke="black"/><text x="80" y="105" text-anchor="middle" font-size="9">Cell</text><rect x="160" y="50" width="40" height="20" fill="white" stroke="black"/><text x="180" y="65" text-anchor="middle" font-size="9">R1</text><rect x="160" y="130" width="40" height="20" fill="white" stroke="black"/><text x="180" y="145" text-anchor="middle" font-size="9">R2</text><path d="M 80 100 L 160 60 L 200 60 L 280 60 M 80 100 L 160 140 L 200 140 L 280 140 M 280 60 L 280 140" fill="none" stroke="black" stroke-width="2"/></svg>'''

    # 5. REFRACTION THROUGH PRISM
    if "prism" in topic:
        return '''<svg width="400" height="220" xmlns="http://www.w3.org/2000/svg" style="background:white; border:1px solid #ccc; border-radius:8px;"><text x="200" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="black">REFRACTION THROUGH PRISM</text><polygon points="100,180 200,40 300,180" fill="lightblue" stroke="black" stroke-width="2"/><line x1="50" y1="100" x2="180" y2="110" stroke="red" stroke-width="2"/><line x1="180" y1="110" x2="250" y2="170" stroke="red" stroke-width="2"/><line x1="250" y1="170" x2="350" y2="160" stroke="red" stroke-width="2"/></svg>'''

    # 6. CONVEX LENS RAY DIAGRAM
    if "convex lens" in topic or "lens" in topic:
        return '''<svg width="450" height="200" xmlns="http://www.w3.org/2000/svg" style="background:white; border:1px solid #ccc; border-radius:8px;"><text x="225" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="black">CONVEX LENS: REAL IMAGE</text><ellipse cx="225" cy="100" rx="20" ry="70" fill="lightblue" stroke="black"/><line x1="50" y1="100" x2="400" y2="100" stroke="black" stroke-dasharray="3"/><text x="180" y="115" text-anchor="middle" font-size="9">F</text><text x="270" y="115" text-anchor="middle" font-size="9">F</text><line x1="50" y1="50" x2="205" y2="100" stroke="blue" stroke-width="2"/><line x1="205" y1="100" x2="400" y2="100" stroke="blue" stroke-width="2"/></svg>'''

    # 7. MAGNETIC FIELD AROUND WIRE
    if "magnetic field" in topic and "wire" in topic:
        return '''<svg width="300" height="300" xmlns="http://www.w3.org/2000/svg" style="background:white; border:1px solid #ccc; border-radius:8px;"><text x="150" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="black">MAGNETIC FIELD AROUND WIRE</text><circle cx="150" cy="150" r="5" fill="black"/><text x="150" y="170" text-anchor="middle" font-size="10">Current Out</text><circle cx="150" cy="150" r="30" fill="none" stroke="black"/><circle cx="150" cy="150" r="60" fill="none" stroke="black"/><circle cx="150" cy="150" r="90" fill="none" stroke="black"/></svg>'''

    # 8. FIRST CLASS LEVER
    if "lever" in topic:
        return '''<svg width="400" height="150" xmlns="http://www.w3.org/2000/svg" style="background:white; border:1px solid #ccc; border-radius:8px;"><text x="200" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="black">1ST CLASS LEVER</text><line x1="50" y1="80" x2="350" y2="80" stroke="brown" stroke-width="6"/><polygon points="200,70 210,90 190,90" fill="black"/><text x="200" y="105" text-anchor="middle" font-size="10">Fulcrum</text><text x="50" y="70" font-size="10">Effort</text><text x="340" y="70" font-size="10">Load</text></svg>'''

    # 9. SINGLE FIXED PULLEY
    if "pulley" in topic:
        return '''<svg width="300" height="250" xmlns="http://www.w3.org/2000/svg" style="background:white; border:1px solid #ccc; border-radius:8px;"><text x="150" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="black">SINGLE FIXED PULLEY</text><circle cx="150" cy="60" r="25" fill="none" stroke="black" stroke-width="3"/><line x1="150" y1="35" x2="150" y2="10" stroke="black" stroke-width="2"/><line x1="125" y1="60" x2="125" y2="180" stroke="black" stroke-width="2"/><line x1="175" y1="60" x2="175" y2="180" stroke="black" stroke-width="2"/><rect x="110" y="180" width="30" height="20" fill="gray"/><rect x="160" y="180" width="30" height="20" fill="gray"/></svg>'''

    # 10. WAVE DIAGRAM
    if "wave" in topic:
        return '''<svg width="400" height="150" xmlns="http://www.w3.org/2000/svg" style="background:white; border:1px solid #ccc; border-radius:8px;"><text x="200" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="black">TRANSVERSE WAVE</text><polyline points="0,75 20,50 40,75 60,100 80,75 100,50 120,75 140,100 160,75 180,50 200,75 220,100 240,75 260,50 280,75 300,100 320,75 340,50 360,75 380,100 400,75" fill="none" stroke="blue" stroke-width="2"/><line x1="0" y1="75" x2="400" y2="75" stroke="black" stroke-dasharray="3"/><text x="50" y="40" font-size="9">Amplitude</text><text x="150" y="130" font-size="9">Wavelength λ</text></svg>'''

    # 11. AC GENERATOR
    if "ac generator" in topic:
        return '''<svg width="420" height="260" xmlns="http://www.w3.org/2000/svg" style="background:white; border:1px solid #ccc; border-radius:8px;"><text x="210" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="black">AC GENERATOR</text><rect x="60" y="60" width="300" height="100" fill="#E0E0E0" stroke="black" stroke-width="2"/><circle cx="210" cy="110" r="35" fill="white" stroke="black"/><text x="210" y="115" text-anchor="middle" font-size="10" fill="black">Armature</text><rect x="80" y="45" width="12" height="25" fill="black"/><rect x="328" y="45" width="12" height="25" fill="black"/><text x="65" y="90" font-size="12" font-weight="bold" fill="red">N</text><text x="350" y="90" font-size="12" font-weight="bold" fill="blue">S</text><text x="210" y="240" text-anchor="middle" font-size="10" fill="#555">Note: Slip Rings, not Commutator</text></svg>'''

    # 12. I-V GRAPH FOR OHM'S LAW
    if "i-v" in topic or "ohm" in topic:
        return '''<svg width="300" height="300" xmlns="http://www.w3.org/2000/svg" style="background:white; border:1px solid #ccc; border-radius:8px;"><text x="150" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="black">I-V GRAPH: OHM'S LAW</text><line x1="40" y1="260" x2="260" y2="260" stroke="black" stroke-width="2"/><line x1="40" y1="260" x2="40" y2="40" stroke="black" stroke-width="2"/><text x="260" y="275" font-size="10">V</text><text x="20" y="40" font-size="10">I</text><line x1="40" y1="260" x2="260" y2="40" stroke="blue" stroke-width="2"/><text x="150" y="280" text-anchor="middle" font-size="9">Straight line through origin</text></svg>'''

    # 13. PLANE MIRROR RAY DIAGRAM
    if "plane mirror" in topic:
        return '''<svg width="400" height="220" xmlns="http://www.w3.org/2000/svg" style="background:white; border:1px solid #ccc; border-radius:8px;"><text x="200" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="black">PLANE MIRROR</text><line x1="200" y1="40" x2="200" y2="180" stroke="black" stroke-width="4"/><text x="210" y="110" font-size="10">Mirror</text><circle cx="80" cy="110" r="8" fill="black"/><text x="60" y="110" font-size="10">O</text><circle cx="320" cy="110" r="8" fill="gray"/><text x="340" y="110" font-size="10">I</text><line x1="80" y1="110" x2="200" y2="90" stroke="blue" stroke-width="1.5"/><line x1="200" y1="90" x2="320" y2="110" stroke="blue" stroke-width="1.5"/></svg>'''

    # 14. TRANSFORMER
    if "transformer" in topic:
        return '''<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg" style="background:white; border:1px solid #ccc; border-radius:8px;"><text x="200" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="black">SIMPLE TRANSFORMER</text><rect x="100" y="60" width="200" height="80" fill="gray" stroke="black" stroke-width="2"/><circle cx="120" cy="100" r="20" fill="none" stroke="red" stroke-width="2"/><text x="120" y="135" text-anchor="middle" font-size="9">Primary</text><circle cx="280" cy="100" r="20" fill="none" stroke="blue" stroke-width="2"/><text x="280" y="135" text-anchor="middle" font-size="9">Secondary</text></svg>'''

    # 15. ELECTROSTATIC: LIKE CHARGES
    if "electrostatic" in topic or "charge" in topic:
        return '''<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg" style="background:white; border:1px solid #ccc; border-radius:8px;"><text x="150" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="black">LIKE CHARGES REPEL</text><circle cx="90" cy="100" r="15" fill="red"/><text x="90" y="105" text-anchor="middle" font-size="10" fill="white">+</text><circle cx="210" cy="100" r="15" fill="red"/><text x="210" y="105" text-anchor="middle" font-size="10" fill="white">+</text><line x1="105" y1="100" x2="195" y2="100" stroke="black" stroke-dasharray="3"/><text x="150" y="120" text-anchor="middle" font-size="9">Repulsion</text></svg>'''

    # 16. SCREW JACK
    if "screw jack" in topic:
        return '''<svg width="300" height="250" xmlns="http://www.w3.org/2000/svg" style="background:white; border:1px solid #ccc; border-radius:8px;"><text x="150" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="black">SCREW JACK</text><rect x="120" y="40" width="60" height="20" fill="gray" stroke="black"/><line x1="150" y1="60" x2="150" y2="200" stroke="black" stroke-width="4"/><rect x="100" y="200" width="100" height="20" fill="brown" stroke="black"/></svg>'''

    # 17. LIQUID PRESSURE VESSEL
    if "pressure" in topic and "liquid" in topic:
        return '''<svg width="300" height="250" xmlns="http://www.w3.org/2000/svg" style="background:white; border:1px solid #ccc; border-radius:8px;"><text x="150" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="black">LIQUID PRESSURE</text><rect x="100" y="50" width="100" height="150" fill="lightblue" stroke="black" stroke-width="2"/><line x1="70" y1="100" x2="100" y2="100" stroke="blue" stroke-width="2"/><line x1="70" y1="150" x2="100" y2="150" stroke="blue" stroke-width="2"/><text x="50" y="105" font-size="9">P1</text><text x="50" y="155" font-size="9">P2>P1</text></svg>'''

    # 18. SPEED-TIME GRAPH
    if "speed-time" in topic or "velocity-time" in topic:
        return '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg" style="background:white; border:1px solid #ccc; border-radius:8px;"><text x="200" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="black">SPEED-TIME GRAPH</text><line x1="50" y1="260" x2="350" y2="260" stroke="black" stroke-width="2"/><line x1="50" y1="260" x2="50" y2="50" stroke="black" stroke-width="2"/><text x="350" y="275" font-size="10">Time</text><text x="20" y="50" font-size="10">Speed</text><polyline points="50,260 150,150 250,150 350,260" fill="none" stroke="green" stroke-width="2"/></svg>'''

    # 19. BAR MAGNET FIELD LINES
    if "magnet" in topic and "field" in topic:
        return '''<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg" style="background:white; border:1px solid #ccc; border-radius:8px;"><text x="150" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="black">BAR MAGNET FIELD LINES</text><rect x="80" y="90" width="40" height="20" fill="red" stroke="black"/><text x="100" y="104" text-anchor="middle" font-size="10" fill="white">N</text><rect x="180" y="90" width="40" height="20" fill="blue" stroke="black"/><text x="200" y="104" text-anchor="middle" font-size="10" fill="white">S</text><path d="M 100 90 Q 150 40 200 90" fill="none" stroke="black"/><path d="M 100 110 Q 150 160 200 110" fill="none" stroke="black"/></svg>'''

    # 20. SIMPLE ELECTRIC BELL
    if "electric bell" in topic:
        return '''<svg width="350" height="250" xmlns="http://www.w3.org/2000/svg" style="background:white; border:1px solid #ccc; border-radius:8px;"><text x="175" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="black">ELECTRIC BELL</text><rect x="100" y="50" width="150" height="40" fill="gray" stroke="black"/><circle cx="175" cy="120" r="25" fill="yellow" stroke="black"/><text x="175" y="125" text-anchor="middle" font-size="10">Gong</text><rect x="150" y="150" width="50" height="30" fill="brown" stroke="black"/></svg>'''

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

st.title("📚 UNEB Physics Bot v16.2")
st.markdown("*This bot works WITH your school teacher, not instead of them*")

SYSTEM_PROMPT = textwrap.dedent("""
You are an expert UNEB S1-S4 Physics tutor for Uganda.
CRITICAL RULES:
1. DIAGRAMS: If user asks "draw", "diagram", "sketch", say "See diagram above" then explain parts. DO NOT describe how to draw.
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
            try:
                st.markdown(svg_code, unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"Diagram failed to load. Continuing with theory.")
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

st.sidebar.markdown("### v16.2: 20 Diagrams Loaded")
st.sidebar.markdown("Edit any SVG in the code for Premium version")
