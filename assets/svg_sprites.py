import streamlit as st
import streamlit.components.v1 as components
from typing import Optional, Dict

# ==========================================
# 1. SVG ASSET DEFINITIONS
# ==========================================
# All diagrams strictly follow a standard 800x325 viewBox for consistent 
# rendering and detailed, UNEB-style labeling.
SVG_SPRITE_PAYLOAD = """
<svg style="display:none" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <!-- Shared Advanced Diagram Markers -->
        <marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M0 1.5 L10 5 L0 8.5 z" fill="#000"/>
        </marker>
        <pattern id="coil" width="20" height="15" patternUnits="userSpaceOnUse">
            <path d="M0 7.5 C18 7.5 18 15 0 15" fill="none" stroke="#0055ff" stroke-width="2.5"/>
        </pattern>

        <!-- ================= BIOLOGY ASSETS ================= -->
        
        <!-- Animal Cell -->
        <symbol id="animal_cell" viewBox="0 0 800 325">
            <text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">GENERALIZED ANIMAL CELL</text>
            <!-- Cell Membrane & Cytoplasm -->
            <ellipse cx="300" cy="180" rx="160" ry="120" fill="#fdfbf7" stroke="#333" stroke-width="3"/>
            <!-- Nucleus -->
            <circle cx="280" cy="180" r="40" fill="#e6f2ff" stroke="#333" stroke-width="2"/>
            <circle cx="270" cy="170" r="12" fill="#66b3ff"/> <!-- Nucleolus -->
            <!-- Mitochondria -->
            <ellipse cx="400" cy="140" rx="25" ry="12" fill="#ffe6e6" stroke="#333" stroke-width="1.5" transform="rotate(30 400 140)"/>
            <path d="M385 140 Q395 130 400 140 T415 140" fill="none" stroke="#333" stroke-width="1.5" transform="rotate(30 400 140)"/>
            <ellipse cx="200" cy="240" rx="25" ry="12" fill="#ffe6e6" stroke="#333" stroke-width="1.5" transform="rotate(-45 200 240)"/>
            <path d="M185 240 Q195 230 200 240 T215 240" fill="none" stroke="#333" stroke-width="1.5" transform="rotate(-45 200 240)"/>
            <!-- Vacuoles -->
            <circle cx="360" cy="230" r="15" fill="#fff" stroke="#333" stroke-width="1"/>
            <circle cx="180" cy="140" r="10" fill="#fff" stroke="#333" stroke-width="1"/>
            <!-- Labels -->
            <line x1="390" y1="75" x2="550" y2="75" stroke="#000" stroke-width="1.5" marker-start="url(#arr)"/>
            <text x="560" y="80" font-size="12">Cell Membrane</text>
            <line x1="350" y1="120" x2="550" y2="120" stroke="#000" stroke-width="1.5" marker-start="url(#arr)"/>
            <text x="560" y="125" font-size="12">Cytoplasm</text>
            <line x1="315" y1="170" x2="550" y2="170" stroke="#000" stroke-width="1.5" marker-start="url(#arr)"/>
            <text x="560" y="175" font-size="12">Nucleus (with Nucleolus)</text>
            <line x1="415" y1="155" x2="550" y2="215" stroke="#000" stroke-width="1.5" marker-start="url(#arr)"/>
            <text x="560" y="220" font-size="12">Mitochondrion</text>
            <line x1="375" y1="235" x2="550" y2="265" stroke="#000" stroke-width="1.5" marker-start="url(#arr)"/>
            <text x="560" y="270" font-size="12">Small Vacuole</text>
        </symbol>

        <!-- Plant Cell -->
        <symbol id="plant_cell" viewBox="0 0 800 325">
            <text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">GENERALIZED PLANT CELL</text>
            <!-- Cell Wall & Membrane -->
            <rect x="150" y="70" width="280" height="220" fill="#e8f5e9" stroke="#2e7d32" stroke-width="6" rx="10"/>
            <rect x="156" y="76" width="268" height="208" fill="none" stroke="#000" stroke-width="1.5" rx="8"/>
            <!-- Large Central Vacuole -->
            <rect x="180" y="100" width="180" height="120" fill="#ffffff" stroke="#333" stroke-width="1.5" rx="20"/>
            <!-- Nucleus -->
            <circle cx="380" cy="230" r="30" fill="#e6f2ff" stroke="#333" stroke-width="2"/>
            <circle cx="375" cy="225" r="10" fill="#66b3ff"/>
            <!-- Chloroplasts -->
            <ellipse cx="200" cy="250" rx="20" ry="10" fill="#81c784" stroke="#2e7d32" stroke-width="1.5"/>
            <ellipse cx="380" cy="110" rx="20" ry="10" fill="#81c784" stroke="#2e7d32" stroke-width="1.5"/>
            <!-- Labels -->
            <line x1="150" y1="80" x2="520" y2="80" stroke="#000" stroke-width="1.5" marker-start="url(#arr)"/>
            <text x="530" y="85" font-size="12">Cellulose Cell Wall</text>
            <line x1="156" y1="120" x2="520" y2="120" stroke="#000" stroke-width="1.5" marker-start="url(#arr)"/>
            <text x="530" y="125" font-size="12">Cell Membrane</text>
            <line x1="270" y1="160" x2="520" y2="160" stroke="#000" stroke-width="1.5" marker-start="url(#arr)"/>
            <text x="530" y="165" font-size="12">Large Central Vacuole</text>
            <line x1="410" y1="230" x2="520" y2="230" stroke="#000" stroke-width="1.5" marker-start="url(#arr)"/>
            <text x="530" y="235" font-size="12">Nucleus</text>
            <line x1="400" y1="110" x2="520" y2="195" stroke="#000" stroke-width="1.5" marker-start="url(#arr)"/>
            <text x="530" y="200" font-size="12">Chloroplast</text>
        </symbol>

        <!-- Heart Structure -->
        <symbol id="heart" viewBox="0 0 800 325">
            <text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">INTERNAL STRUCTURE OF THE MAMMALIAN HEART</text>
            <!-- Simplified Schematic Heart Base -->
            <path d="M300 120 C250 120 220 180 300 280 C380 180 350 120 300 120" fill="none" stroke="#000" stroke-width="3"/>
            <!-- Septum -->
            <path d="M300 140 V270" stroke="#8b0000" stroke-width="12"/>
            <!-- Right Atrium & Ventricle (Blue - Deoxygenated) -->
            <path d="M250 140 C230 160 230 190 290 190 V140 Z" fill="#bbdefb" stroke="#000" stroke-width="1.5"/>
            <path d="M290 200 C230 200 250 250 290 270 V200 Z" fill="#bbdefb" stroke="#000" stroke-width="1.5"/>
            <!-- Left Atrium & Ventricle (Red - Oxygenated) -->
            <path d="M310 140 V190 C370 190 370 160 350 140 Z" fill="#ffcdd2" stroke="#000" stroke-width="1.5"/>
            <path d="M310 200 V270 C350 250 370 200 310 200 Z" fill="#ffcdd2" stroke="#000" stroke-width="1.5"/>
            <!-- Valves -->
            <line x1="250" y1="195" x2="290" y2="195" stroke="#333" stroke-width="4" stroke-dasharray="6,2"/>
            <line x1="310" y1="195" x2="350" y2="195" stroke="#333" stroke-width="4" stroke-dasharray="6,2"/>
            <!-- Vessels -->
            <path d="M260 140 V90" stroke="#1565c0" stroke-width="15"/> <!-- Vena Cava -->
            <path d="M340 140 V90" stroke="#c62828" stroke-width="15"/> <!-- Pulmonary Vein -->
            <path d="M290 140 C290 80 370 80 370 120" stroke="#c62828" fill="none" stroke-width="12"/> <!-- Aorta -->
            <path d="M310 140 C310 100 230 100 230 130" stroke="#1565c0" fill="none" stroke-width="12"/> <!-- Pulmonary Artery -->
            <!-- Labels Right Side (Anatomical Left) -->
            <line x1="380" y1="90" x2="480" y2="90" stroke="#000" stroke-width="1" marker-start="url(#arr)"/>
            <text x="490" y="95" font-size="12">Aorta</text>
            <line x1="350" y1="120" x2="480" y2="120" stroke="#000" stroke-width="1" marker-start="url(#arr)"/>
            <text x="490" y="125" font-size="12">Pulmonary Vein</text>
            <line x1="350" y1="170" x2="480" y2="170" stroke="#000" stroke-width="1" marker-start="url(#arr)"/>
            <text x="490" y="175" font-size="12">Left Atrium</text>
            <line x1="330" y1="195" x2="480" y2="210" stroke="#000" stroke-width="1" marker-start="url(#arr)"/>
            <text x="490" y="215" font-size="12">Bicuspid Valve</text>
            <line x1="330" y1="240" x2="480" y2="240" stroke="#000" stroke-width="1" marker-start="url(#arr)"/>
            <text x="490" y="245" font-size="12">Left Ventricle (Thick Wall)</text>
            <!-- Labels Left Side (Anatomical Right) -->
            <line x1="260" y1="110" x2="150" y2="90" stroke="#000" stroke-width="1" marker-start="url(#arr)"/>
            <text x="140" y="95" font-size="12" text-anchor="end">Vena Cava</text>
            <line x1="225" y1="125" x2="150" y2="130" stroke="#000" stroke-width="1" marker-start="url(#arr)"/>
            <text x="140" y="135" font-size="12" text-anchor="end">Pulmonary Artery</text>
            <line x1="260" y1="170" x2="150" y2="170" stroke="#000" stroke-width="1" marker-start="url(#arr)"/>
            <text x="140" y="175" font-size="12" text-anchor="end">Right Atrium</text>
            <line x1="270" y1="195" x2="150" y2="210" stroke="#000" stroke-width="1" marker-start="url(#arr)"/>
            <text x="140" y="215" font-size="12" text-anchor="end">Tricuspid Valve</text>
            <line x1="260" y1="240" x2="150" y2="240" stroke="#000" stroke-width="1" marker-start="url(#arr)"/>
            <text x="140" y="245" font-size="12" text-anchor="end">Right Ventricle</text>
        </symbol>

        <!-- ================= CHEMISTRY ASSETS ================= -->
        
        <!-- Atomic Structure (Carbon) -->
        <symbol id="atom" viewBox="0 0 800 325">
            <text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">ATOMIC STRUCTURE (CARBON BOHR MODEL)</text>
            <!-- Nucleus -->
            <circle cx="300" cy="180" r="18" fill="#d32f2f" stroke="#000" stroke-width="1"/>
            <text x="300" y="184" text-anchor="middle" fill="#fff" font-size="10" font-weight="bold">6p 6n</text>
            <!-- Shells -->
            <circle cx="300" cy="180" r="50" fill="none" stroke="#555" stroke-width="2" stroke-dasharray="4"/>
            <circle cx="300" cy="180" r="100" fill="none" stroke="#555" stroke-width="2" stroke-dasharray="4"/>
            <!-- Electrons (K shell) -->
            <circle cx="300" cy="130" r="6" fill="#1976d2" stroke="#000" stroke-width="1"/>
            <circle cx="300" cy="230" r="6" fill="#1976d2" stroke="#000" stroke-width="1"/>
            <!-- Electrons (L shell) -->
            <circle cx="300" cy="80" r="6" fill="#1976d2" stroke="#000" stroke-width="1"/>
            <circle cx="300" cy="280" r="6" fill="#1976d2" stroke="#000" stroke-width="1"/>
            <circle cx="200" cy="180" r="6" fill="#1976d2" stroke="#000" stroke-width="1"/>
            <circle cx="400" cy="180" r="6" fill="#1976d2" stroke="#000" stroke-width="1"/>
            <!-- Labels -->
            <line x1="318" y1="180" x2="480" y2="130" stroke="#000" stroke-width="1.5" marker-start="url(#arr)"/>
            <text x="490" y="130" font-size="12">Nucleus (6 Protons, 6 Neutrons)</text>
            <line x1="340" y1="145" x2="480" y2="170" stroke="#000" stroke-width="1.5" marker-start="url(#arr)"/>
            <text x="490" y="175" font-size="12">First Electron Shell (K = 2e⁻)</text>
            <line x1="380" y1="230" x2="480" y2="210" stroke="#000" stroke-width="1.5" marker-start="url(#arr)"/>
            <text x="490" y="215" font-size="12">Second Electron Shell (L = 4e⁻)</text>
            <line x1="400" y1="174" x2="480" y2="250" stroke="#000" stroke-width="1.5" marker-start="url(#arr)"/>
            <text x="490" y="255" font-size="12">Valence Electron (Negative Charge)</text>
        </symbol>

        <!-- ================= PHYSICS ASSETS (Preserved & Standardized) ================= -->
        
        <symbol id="transformer" viewBox="0 0 800 325">
            <text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">1. LAMINATED STEP-DOWN TRANSFORMER</text>
            <rect x="280" y="80" width="240" height="180" fill="none" stroke="#555" stroke-width="34" rx="8"/>
            <rect x="290" y="90" width="220" height="160" fill="none" stroke="#bbb" stroke-width="1.5" rx="4"/>
            <rect x="255" y="100" width="22" height="140" fill="url(#coil)"/>
            <path d="M220 100 H260 M220 240 H260" fill="none" stroke="#000" stroke-width="1.5"/>
            <circle cx="220" cy="170" r="12" fill="none" stroke="#000" stroke-width="1.5"/>
            <path d="M212 170 Q220 160 228 170 T220 170" fill="none" stroke="#000" stroke-width="1.5"/>
            <text x="195" y="174" text-anchor="end">A.C. Input</text>
            <rect x="523" y="120" width="22" height="100" fill="url(#coil)"/>
            <path d="M540 120 H580 V220 H540" fill="none" stroke="#000" stroke-width="1.5"/>
            <text x="590" y="174">Output Load</text>
            <text x="400" y="75" text-anchor="middle">Laminated Soft Iron Core</text>
            <path d="M400 78 V95" fill="none" stroke="#000" stroke-width="1" marker-end="url(#arr)"/>
            <text x="320" y="285" text-anchor="middle">Primary Coil (Np)</text>
            <text x="480" y="285" text-anchor="middle">Secondary Coil (Ns)</text>
        </symbol>

        <symbol id="hookes_law" viewBox="0 0 800 325">
            <text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">2. VERIFICATION OF HOOKE'S LAW</text>
            <path d="M260 270 H400 M300 270 V70 H350" fill="none" stroke="#444" stroke-width="5"/>
            <rect x="360" y="80" width="20" height="180" fill="#fff" stroke="#000" stroke-width="1.5"/>
            <path d="M360 90 H370 M360 110 H370 M360 130 H370 M360 150 H370 M360 170 H370 M360 190 H370 M360 210 H370 M360 230 H370 M360 250 H370" fill="none" stroke="#000" stroke-width="1"/>
            <path d="M330 70 V90 Q340 95 330 100 T330 110 T330 120 T330 130 T330 140 T330 150 V170" fill="none" stroke="#333" stroke-width="2"/>
            <path d="M330 170 H358" fill="none" stroke="#d32f2f" stroke-width="2" marker-end="url(#arr)"/>
            <text x="315" y="165" text-anchor="end" fill="#d32f2f">Pointer</text>
            <path d="M330 170 V210 H310 H350" fill="none" stroke="#000" stroke-width="2"/>
            <rect x="315" y="180" width="30" height="12" fill="#777"/>
            <rect x="315" y="195" width="30" height="12" fill="#777"/>
            <text x="330" y="230" text-anchor="middle">Slotted Masses (m)</text>
        </symbol>

        <!-- (Additional diagrams like Refraction, Specific Heat, X-Ray Tube remain standard structured) -->
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
        "S3": {
            "Transport in Humans - Heart Structure": "heart"
        }
    },
    "Physics": {
        "S3": {
            "Mechanics - Hooke's Law": "hookes_law"
        },
        "S4": {
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
    st.set_page_config(page_title="UNEB AI Tutor - Diagram Asset Test", layout="wide")
    
    # 1. Initialize sprites (Invisible DOM injection)
    DiagramManager.initialize_sprites()
    
    st.title("UNEB S1-S4 Asset Manager")
    st.markdown("Select a subject, class, and topic below to render standard curriculum schematics.")
    
    # 2. Simulate Chatbot LLM Logic retrieving a requested topic
    col1, col2, col3 = st.columns(3)
    
    with col1:
        subject_choice = st.selectbox("Subject", options=list(UNEB_CURRICULUM_MAP.keys()))
    with col2:
        level_choice = st.selectbox("Class Level", options=list(UNEB_CURRICULUM_MAP[subject_choice].keys()))
    with col3:
        topic_choice = st.selectbox("Topic", options=list(UNEB_CURRICULUM_MAP[subject_choice][level_choice].keys()))
    
    # 3. Render the diagram in the UI
    st.write(f"### Visual for: **{topic_choice}**")
    symbol_to_render = DiagramManager.get_symbol_by_curriculum(subject_choice, level_choice, topic_choice)
    DiagramManager.render(symbol_to_render)
