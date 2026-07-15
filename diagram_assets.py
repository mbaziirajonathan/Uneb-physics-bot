import streamlit as st
import base64
from pathlib import Path
from typing import Optional, Dict

# ==========================================
# 1. UNEB 2026 CURRICULUM MAPPING - S1 TO S4
# BIOLOGY + CHEMISTRY + PHYSICS
# ==========================================
UNEB_CURRICULUM_MAP: Dict[str, Dict[str, Dict[str, str]]] = {
    "Biology": {
        "S1": {"Cell Biology - Animal": "animal_cell", "Cell Biology - Plant": "plant_cell"},
        "S2": {"Plant Nutrition - Transverse Section of Leaf": "leaf_ts", "Human Anatomy - Alveolus": "alveolus"},
        "S3": {"Transport in Humans - Heart Structure": "heart", "Excretion - Kidney Nephron": "nephron"},
        "S4": {"Coordination - Motor Neurone": "neurone"}
    },
    "Chemistry": {
        "S1": {"Atomic Structure": "atom", "Separation Techniques - Filtration": "filtration", "Separation Techniques - Chromatography": "chromatography"},
        "S2": {"Bonding - Covalent Water Molecule": "covalent_water", "Oxygen Preparation": "gas_prep"},
        "S3": {"Moles & Volumetric Analysis - Titration Setup": "titration"},
        "S4": {"Organic Chemistry - Fractional Distillation": "fractional_distillation"}
    },
    "Physics": { # ADDED FOR UNEB 2026
        "S1": {"Measurements - Vernier Calipers": "vernier", "Force - Spring Balance": "spring_balance"},
        "S2": {"Electricity - Simple Electric Circuit": "simple_circuit", "Waves - Ripple Tank": "ripple_tank"},
        "S3": {"Magnetism - Bar Magnet Field Lines": "bar_magnet", "Heat - Calorimeter": "calorimeter"},
        "S4": {"Electronics - Diode I-V Curve": "diode_iv", "Nuclear Physics - Alpha Scattering": "alpha_scattering"}
    }
}

# ==========================================
# 2. HELPER: CONVERT PNG TO BASE64 - CACHED
# ==========================================
@st.cache_data(show_spinner=False)
def img_to_base64(img_path: Path) -> str:
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# ==========================================
# 3. DIAGRAM MANAGER CLASS - CLIENT SIDE RENDER
# ==========================================
class DiagramManager:
    @staticmethod
    def initialize_sprites() -> None:
        assets_path = Path("assets")
        if not assets_path.exists():
            st.error("FATAL: 'assets' folder not found. Upload PNGs to /assets/")
            st.stop()

    @classmethod
    def get_symbol_by_curriculum(cls, subject: str, level: str, topic: str) -> Optional[str]:
        return UNEB_CURRICULUM_MAP.get(subject, {}).get(level, {}).get(topic)

    @staticmethod
    def render(symbol_id: Optional[str]) -> None:
        if not symbol_id:
            st.warning("⚠️ No diagram is currently available for this specific UNEB 2026 topic.")
            return
            
        img_path = Path(f"assets/{symbol_id}.png")
        
        if img_path.exists():
            img_b64 = img_to_base64(img_path)
            st.markdown(
                f'<img src="data:image/png;base64,{img_b64}" style="width:100%; max-width:800px; border:1px solid #e2e8f0; border-radius:8px; background:#f8fafc; display:block; margin:auto;">', 
                unsafe_allow_html=True
            )
        else:
            st.error(f"Diagram file 'assets/{symbol_id}.png' not found. Check filename spelling.")

# ==========================================
# 4. STANDALONE TEST BLOCK
# ==========================================
if __name__ == "__main__":
    st.set_page_config(page_title="UNEB 2026 AI Tutor", layout="wide")
    DiagramManager.initialize_sprites()
    st.title("UNEB 2026 S1-S4 Asset Manager")
    col1, col2, col3 = st.columns(3)
    with col1: subject_choice = st.selectbox("Subject", options=list(UNEB_CURRICULUM_MAP.keys()))
    with col2: level_choice = st.selectbox("Class Level", options=list(UNEB_CURRICULUM_MAP[subject_choice].keys()))
    with col3: topic_choice = st.selectbox("Topic", options=list(UNEB_CURRICULUM_MAP[subject_choice][level_choice].keys()))
    st.write(f"### Visual for: **{topic_choice}**")
    symbol_to_render = DiagramManager.get_symbol_by_curriculum(subject_choice, level_choice, topic_choice)
    DiagramManager.render(symbol_to_render)
