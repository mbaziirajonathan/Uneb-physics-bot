import streamlit as st
import streamlit.components.v1 as components
from typing import Optional, Dict, List, Any

# ==========================================
# 1. SVG ASSET DEFINITIONS
# ==========================================
# Combined into a single, cohesive payload for DOM injection.
SVG_SPRITE_PAYLOAD = """
<svg style="display:none" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <!-- Biology Assets -->
        <symbol id="animal_cell" viewBox="0 0 120 120"><ellipse cx="60" cy="60" rx="50" ry="40" fill="#ffffe0" stroke="black" stroke-width="2"/><circle cx="60" cy="60" r="15" fill="#add8e6" stroke="black"/><text x="60" y="65" text-anchor="middle" font-size="8">Nucleus</text></symbol>
        <symbol id="plant_cell" viewBox="0 0 120 120"><rect x="20" y="20" width="80" height="80" fill="#90ee90" stroke="black" stroke-width="2"/><circle cx="60" cy="60" r="12" fill="#add8e6" stroke="black"/><text x="60" y="65" text-anchor="middle" font-size="8">Nucleus</text><rect x="22" y="22" width="76" height="76" fill="none" stroke="green" stroke-width="3"/></symbol>
        <symbol id="photosynthesis" viewBox="0 0 150 100"><rect x="10" y="40" width="40" height="40" fill="green"/><text x="30" y="65" text-anchor="middle" fill="white" font-size="8">Leaf</text><path d="M60,60 L90,30" stroke="yellow" stroke-width="4"/><path d="M60,60 L90,90" stroke="blue" stroke-width="4"/><text x="95" y="35" font-size="10">O2</text><text x="95" y="95" font-size="10">Glucose</text></symbol>
        <symbol id="heart" viewBox="0 0 120 100"><path d="M60,80 Q20,60 20,35 Q20,15 40,15 Q50,15 60,25 Q70,15 80,15 Q100,15 100,35 Q100,60 60,80" fill="red" stroke="black" stroke-width="2"/></symbol>
        <symbol id="circulatory" viewBox="0 0 120 100"><path d="M60,80 Q20,60 20,35 Q20,15 40,15 Q50,15 60,25 Q70,15 80,15 Q100,15 100,35 Q100,60 60,80" fill="red" stroke="black" stroke-width="2"/><line x1="60" y1="80" x2="60" y2="95" stroke="blue" stroke-width="3"/></symbol>
        <symbol id="dna" viewBox="0 0 100 120"><path d="M30,10 Q70,30 30,50 Q70,70 30,90 Q70,110 30,110" fill="none" stroke="blue" stroke-width="2"/><path d="M70,10 Q30,30 70,50 Q30,70 70,90 Q30,110 70,110" fill="none" stroke="red" stroke-width="2"/></symbol>
        <symbol id="ecosystem" viewBox="0 0 150 100"><ellipse cx="75" cy="80" rx="70" ry="15" fill="#8b4513"/><circle cx="40" cy="60" r="15" fill="green"/><rect x="70" y="50" width="10" height="20" fill="#8b4513"/><circle cx="75" cy="45" r="12" fill="green"/><text x="75" y="95" text-anchor="middle" font-size="8">Ecosystem</text></symbol>
        <symbol id="neuron" viewBox="0 0 150 80"><circle cx="30" cy="40" r="15" fill="yellow" stroke="black" stroke-width="2"/><path d="M45,40 Q80,20 120,40" stroke="black" stroke-width="3" fill="none"/><text x="125" y="45" font-size="10">Axon</text></symbol>
        
        <!-- Physics & Chemistry Assets -->
        <symbol id="forces" viewBox="0 0 200 120"><rect x="80" y="60" width="40" height="30" fill="#ccc" stroke="black"/><line x1="100" y1="60" x2="100" y2="30" stroke="black" stroke-width="2"/><text x="105" y="35" font-size="10">N</text><line x1="100" y1="90" x2="100" y2="110" stroke="black" stroke-width="2"/><text x="105" y="115" font-size="10">W</text><line x1="120" y1="75" x2="150" y2="75" stroke="red" stroke-width="2"/><text x="152" y="80" font-size="10">F</text></symbol>
        <symbol id="convex_lens" viewBox="0 0 200 100"><line x1="0" y1="50" x2="200" y2="50" stroke="black"/><path d="M100,15 Q115,50 100,85 Q85,50 100,15" fill="#add8e6" stroke="blue" stroke-width="2"/><line x1="60" y1="70" x2="140" y2="50" stroke="red" stroke-width="2"/></symbol>
        <symbol id="atom" viewBox="0 0 120 120"><circle cx="60" cy="60" r="8" fill="red"/><circle cx="60" cy="60" r="25" fill="none" stroke="blue"/><circle cx="60" cy="60" r="40" fill="none" stroke="blue"/><circle cx="60" cy="35" r="4" fill="blue"/></symbol>

        <!-- Advanced Diagram Markers -->
        <marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 1.5 L10 5 L0 8.5 z" fill="#000"/></marker>
        <pattern id="coil" width="20" height="15" patternUnits="userSpaceOnUse"><path d="M0 7.5 C18 7.5 18 15 0 15" fill="none" stroke="#0055ff" stroke-width="2.5"/></pattern>
        
        <!-- Complex Physics Diagrams -->
        <symbol id="transformer" viewBox="0 0 800 325"><text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">1. LAMINATED STEP-DOWN TRANSFORMER</text><rect x="280" y="80" width="240" height="180" fill="none" stroke="#555" stroke-width="34" rx="8"/><rect x="290" y="90" width="220" height="160" fill="none" stroke="#bbb" stroke-width="1.5" rx="4"/><rect x="255" y="100" width="22" height="140" fill="url(#coil)"/><path d="M220 100 H260 M220 240 H260" fill="none" stroke="#000" stroke-width="1.5"/><circle cx="220" cy="170" r="12" fill="none" stroke="#000" stroke-width="1.5"/><path d="M212 170 Q220 160 228 170 T220 170" fill="none" stroke="#000" stroke-width="1.5"/><text x="195" y="174" text-anchor="end">A.C. Input</text><rect x="523" y="120" width="22" height="100" fill="url(#coil)"/><path d="M540 120 H580 V220 H540" fill="none" stroke="#000" stroke-width="1.5"/><text x="590" y="174">Output Load</text><text x="400" y="75" text-anchor="middle">Laminated Soft Iron Core</text><path d="M400 78 V95" fill="none" stroke="#000" stroke-width="1" marker-end="url(#arr)"/><text x="320" y="285" text-anchor="middle">Primary Coil (Np)</text><text x="480" y="285" text-anchor="middle">Secondary Coil (Ns)</text></symbol>
        <symbol id="hookes_law" viewBox="800 0 800 325"><text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">2. VERIFICATION OF HOOKE'S LAW</text><path d="M260 270 H400 M300 270 V70 H350" fill="none" stroke="#444" stroke-width="5"/><rect x="360" y="80" width="20" height="180" fill="#fff" stroke="#000" stroke-width="1.5"/><path d="M360 90 H370 M360 110 H370 M360 130 H370 M360 150 H370 M360 170 H370 M360 190 H370 M360 210 H370 M360 230 H370 M360 250 H370" fill="none" stroke="#000" stroke-width="1"/><path d="M330 70 V90 Q340 95 330 100 T330 110 T330 120 T330 130 T330 140 T330 150 V170" fill="none" stroke="#333" stroke-width="2"/><path d="M330 170 H358" fill="none" stroke="#d32f2f" stroke-width="2" marker-end="url(#arr)"/><text x="315" y="165" text-anchor="end" fill="#d32f2f">Pointer</text><path d="M330 170 V210 H310 H350" fill="none" stroke="#000" stroke-width="2"/><rect x="315" y="180" width="30" height="12" fill="#777"/><rect x="315" y="195" width="30" height="12" fill="#777"/><text x="330" y="230" text-anchor="middle">Slotted Masses (m)</text></symbol>
        <symbol id="refraction" viewBox="0 325 800 325"><text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">3. REFRACTION THROUGH A GLASS BLOCK</text><rect x="250" y="110" width="300" height="120" fill="#f0f8ff" stroke="#000" stroke-width="2"/><text x="400" y="175" fill="#4682b4" font-size="12" text-anchor="middle">Glass Block</text><line x1="350" y1="60" x2="350" y2="280" stroke="#555" stroke-dasharray="4" stroke-width="1.5"/><text x="355" y="75">Normal</text><line x1="230" y1="40" x2="350" y2="110" stroke="#000" stroke-width="2" marker-end="url(#arr)"/><line x1="350" y1="110" x2="390" y2="230" stroke="#000" stroke-width="2" marker-end="url(#arr)"/><line x1="390" y1="230" x2="510" y2="300" stroke="#000" stroke-width="2" marker-end="url(#arr)"/><circle cx="260" cy="57" r="3" fill="#d32f2f"/><text x="265" y="55">P1</text><circle cx="300" cy="81" r="3" fill="#d32f2f"/><text x="305" y="79">P2</text><circle cx="430" cy="253" r="3" fill="#d32f2f"/><text x="435" y="251">P3</text><circle cx="470" cy="277" r="3" fill="#d32f2f"/><text x="475" y="275">P4</text><text x="335" y="100" font-size="12">i</text><text x="360" y="135" font-size="12">r</text></symbol>
        <symbol id="specific_heat" viewBox="800 325 800 325"><text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">4. SPECIFIC HEAT CAPACITY OF A SOLID</text><rect x="230" y="90" width="340" height="190" fill="#fff" stroke="#666" stroke-width="2" stroke-dasharray="3"/><text x="245" y="115" font-size="10" fill="#666">Cotton Wool (Lagging)</text><rect x="290" y="120" width="220" height="140" fill="#eaeaea" stroke="#000" stroke-width="2"/><text x="400" y="250" text-anchor="middle">Metal Block</text><rect x="330" y="50" width="12" height="120" fill="#fff" stroke="#000" stroke-width="1.5" rx="4"/><line x1="336" y1="100" x2="336" y2="165" stroke="#d32f2f" stroke-width="3"/><text x="325" y="45" text-anchor="middle">Thermometer</text><rect x="440" y="130" width="20" height="110" fill="#555"/><path d="M445 130 V70 H400" fill="none" stroke="#000" stroke-width="1.5"/><path d="M455 130 V60 H540 V70" fill="none" stroke="#000" stroke-width="1.5"/><text x="480" y="125">Heater</text><circle cx="400" cy="70" r="10" fill="#fff" stroke="#000" stroke-width="1.5"/><text x="400" y="74" text-anchor="middle" font-size="10">A</text><circle cx="470" cy="40" r="10" fill="#fff" stroke="#000" stroke-width="1.5"/><text x="470" y="44" text-anchor="middle" font-size="10">V</text></symbol>
        <symbol id="xray_tube" viewBox="0 650 800 325"><text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">5. THE X-RAY TUBE</text><rect x="180" y="80" width="440" height="170" fill="none" stroke="#999" stroke-width="12" rx="20"/><rect x="186" y="86" width="428" height="158" fill="#fff" stroke="#000" stroke-width="1.5" rx="15"/><text x="400" y="105" text-anchor="middle" fill="#999">Evacuated Glass Envelope</text><path d="M150 140 H220 L230 150 L220 160 H150" fill="none" stroke="#000" stroke-width="1.5"/><path d="M230 145 Q240 150 230 155" fill="none" stroke="#d32f2f" stroke-width="2"/><text x="210" y="130">Filament (Cathode)</text><path d="M245 148 H390 M245 152 H390" fill="none" stroke="#ffaa00" stroke-dasharray="3" stroke-width="1.5" marker-end="url(#arr)"/><text x="310" y="138" fill="#ffaa00">Electron Beam</text><path d="M400 120 L430 150 L400 180 Z" fill="#777" stroke="#000"/><rect x="430" y="135" width="120" height="30" fill="#d87a64"/><text x="500" y="130">Copper Anode</text><text x="375" y="200" text-anchor="end">Tungsten Target</text><path d="M415 155 L370 280 M420 160 L385 280" fill="none" stroke="#000" stroke-width="1.5" stroke-dasharray="2" marker-end="url(#arr)"/><text x="405" y="275">X-Rays</text><path d="M185 180 H130 V290 H500 V165" fill="none" stroke="#000" stroke-width="1.5"/><rect x="280" y="275" width="80" height="25" fill="#fff" stroke="#000" stroke-width="1.5"/><text x="320" y="291" text-anchor="middle">E.H.T. SUPPLY</text></symbol>
        <symbol id="electroscope" viewBox="800 650 800 325"><text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">6. GOLD LEAF ELECTROSCOPE</text><rect x="280" y="100" width="240" height="180" fill="#fff" stroke="#000" stroke-width="1.5" rx="10"/><rect x="285" y="105" width="230" height="170" fill="none" stroke="#bbb" stroke-width="1" rx="8"/><rect x="260" y="280" width="280" height="20" fill="#8b4513" stroke="#000" stroke-width="1.5"/><ellipse cx="400" cy="90" rx="50" ry="15" fill="#ffd700" stroke="#000" stroke-width="1.5"/><rect x="395" y="90" width="10" height="120" fill="#ffd700" stroke="#000" stroke-width="1"/><ellipse cx="400" cy="205" rx="18" ry="8" fill="#ffd700" stroke="#000" stroke-width="1"/><path d="M400 205 V270" fill="none" stroke="#ffd700" stroke-width="2.5"/><path d="M400 205 V270" fill="none" stroke="#ffd700" stroke-width="2.5" transform="translate(0,0) rotate(-3 400 205)"/><text x="410" y="265" font-size="10" fill="#b8860b">Gold Leaves</text><path d="M410 110 L450 70" fill="none" stroke="#000" stroke-width="1" marker-end="url(#arr)"/><text x="455" y="70">Test Charge</text><text x="400" y="320" text-anchor="middle">Brass Cap and Rod</text><path d="M400 300 V215" fill="none" stroke="#000" stroke-width="1" marker-end="url(#arr)"/><text x="200" y="200" text-anchor="end">Glass Case</text><path d="M270 200 L285 200" fill="none" stroke="#000" stroke-width="1" marker-end="url(#arr)"/><text x="600" y="290" text-anchor="start">Wooden Base</text><path d="M520 290 L540 290" fill="none" stroke="#000" stroke-width="1" marker-end="url(#arr)"/></symbol>
    </defs>
</svg>
"""

# ==========================================
# 2. UNEB CURRICULUM MAPPING (S1 - S4)
# ==========================================
# Acts as a queryable database for the LLM Dialogue Manager
UNEB_CURRICULUM_MAP: Dict[str, Dict[str, Dict[str, str]]] = {
    "Biology": {
        "S1": {
            "Cell Biology - Animal": "animal_cell",
            "Cell Biology - Plant": "plant_cell"
        },
        "S2": {
            "Nutrition - Photosynthesis": "photosynthesis",
            "Ecology - Ecosystems": "ecosystem"
        },
        "S3": {
            "Transport in Humans - Heart Structure": "heart",
            "Circulatory System": "circulatory"
        },
        "S4": {
            "Genetics - DNA Structure": "dna",
            "Nervous System - Neuron": "neuron"
        }
    },
    "Physics": {
        "S1": {
            "Basic Mechanics - Forces": "forces"
        },
        "S2": {
            "Optics - Refraction & Lenses": "convex_lens",
            "Light - Refraction through Glass": "refraction"
        },
        "S3": {
            "Mechanics - Hooke's Law": "hookes_law",
            "Heat - Specific Heat Capacity": "specific_heat"
        },
        "S4": {
            "Modern Physics - X-Ray Tube": "xray_tube",
            "Electrostatics - Gold Leaf Electroscope": "electroscope",
            "Electricity - Step-Down Transformer": "transformer"
        }
    },
    "Chemistry": {
        "S1": {
            "Atomic Structure": "atom"
        }
    }
}


# ==========================================
# 3. CHATBOT DIAGRAM MANAGER CLASS
# ==========================================
class DiagramManager:
    """
    Handles the initialization, querying, and rendering of SVG diagrams 
    based on the UNEB S1-S4 Competence-Based Curriculum.
    """

    @staticmethod
    def initialize_sprites() -> None:
        """
        Injects the hidden SVG sprites into the Streamlit DOM. 
        Must be called once at the top of the app layout.
        """
        components.html(SVG_SPRITE_PAYLOAD, height=0, scrolling=False)

    @classmethod
    def get_symbol_by_curriculum(cls, subject: str, level: str, topic: str) -> Optional[str]:
        """
        Retrieves the SVG symbol ID mapped to a specific curriculum node.
        Used by the LLM agent to fetch relevant visuals.
        """
        try:
            return UNEB_CURRICULUM_MAP.get(subject, {}).get(level, {}).get(topic)
        except KeyError:
            return None

    @staticmethod
    def render(symbol_id: Optional[str]) -> None:
        """
        Renders the retrieved SVG sprite in the Streamlit UI chat flow.
        """
        if not symbol_id:
            st.warning("⚠️ No diagram is currently available for this specific UNEB topic.")
            return
            
        svg_code = f"""
        <svg width="100%" height="350" style="border:1px solid #e2e8f0; border-radius: 8px; background:#f8fafc; margin-top: 10px;">
            <use href="#{symbol_id}"/>
        </svg>
        """
        components.html(svg_code, height=370, scrolling=False)


# ==========================================
# 4. EXAMPLE USAGE / TESTING
# ==========================================
if __name__ == "__main__":
    st.set_page_config(page_title="UNEB AI Tutor - Diagram Asset Test")
    
    # 1. Initialize sprites (Invisible DOM injection)
    DiagramManager.initialize_sprites()
    
    st.title("UNEB S1-S4 Asset Manager")
    
    # 2. Simulate Chatbot LLM Logic retrieving a requested topic
    subject_choice = st.selectbox("Subject", options=list(UNEB_CURRICULUM_MAP.keys()))
    level_choice = st.selectbox("Class Level", options=list(UNEB_CURRICULUM_MAP[subject_choice].keys()))
    topic_choice = st.selectbox("Topic", options=list(UNEB_CURRICULUM_MAP[subject_choice][level_choice].keys()))
    
    # 3. Render the diagram in the UI
    st.write(f"### Visual for: {topic_choice}")
    symbol_to_render = DiagramManager.get_symbol_by_curriculum(subject_choice, level_choice, topic_choice)
    DiagramManager.render(symbol_to_render)
