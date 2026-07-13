import streamlit as st

# ========== S1 BIOLOGY: 6 DIAGRAMS ==========
def s1_bio_animal_cell():
    """S1: Animal Cell - UNEB requires 8 parts"""
    return """<svg width="320" height="320">
    <circle cx="160" cy="160" r="110" fill="none" stroke="black" stroke-width="2"/>
    <circle cx="160" cy="160" r="35" fill="#E3F2FD" stroke="black"/>
    <ellipse cx="100" cy="100" rx="12" ry="6" fill="#FFCC80" stroke="black"/>
    <circle cx="200" cy="110" r="15" fill="#F8BBD0" stroke="black" stroke-dasharray="2,2"/>
    <line x1="195" y1="160" x2="250" y2="160" stroke="black"/><text x="255" y="164" font-size="11">Cell Membrane</text>
    <line x1="160" y1="125" x2="160" y2="70" stroke="black"/><text x="165" y="70" font-size="11">Nucleus</text>
    <line x1="100" y1="100" x2="50" y2="80" stroke="black"/><text x="10" y="80" font-size="11">Mitochondrion</text>
    <line x1="200" y1="110" x2="250" y2="90" stroke="black"/><text x="255" y="90" font-size="11">Vacuole</text>
    <line x1="130" y1="190" x2="90" y2="220" stroke="black"/><text x="30" y="225" font-size="11">Cytoplasm</text>
    <text x="160" y="300" font-size="14" text-anchor="middle">Animal Cell</text>
    </svg>"""

def s1_bio_plant_cell():
    """S1: Plant Cell - Cell wall + Chloroplast must be shown"""
    return """<svg width="320" height="320">
    <rect x="50" y="50" width="220" height="220" fill="none" stroke="black" stroke-width="3"/>
    <rect x="60" y="60" width="200" height="200" fill="#E8F5E9" stroke="black"/>
    <circle cx="160" cy="160" r="35" fill="#BBDEFB" stroke="black"/>
    <rect x="90" y="90" width="20" height="20" fill="#4CAF50" stroke="black"/>
    <rect x="200" y="120" width="20" height="20" fill="#4CAF50" stroke="black"/>
    <line x1="50" y1="50" x2="20" y2="30" stroke="black"/><text x="5" y="30" font-size="11">Cell Wall</text>
    <line x1="160" y1="125" x2="160" y2="90" stroke="black"/><text x="165" y="90" font-size="11">Nucleus</text>
    <line x1="90" y1="90" x2="60" y2="70" stroke="black"/><text x="5" y="70" font-size="11">Chloroplast</text>
    <line x1="200" y1="120" x2="230" y2="100" stroke="black"/><text x="235" y="100" font-size="11">Chloroplast</text>
    <text x="160" y="300" font-size="14" text-anchor="middle">Plant Cell</text>
    </svg>"""

def s1_bio_leaf():
    """S1: Leaf - External + Vein pattern"""
    return """<svg width="280" height="320">
    <ellipse cx="140" cy="130" rx="90" ry="100" fill="#A5D6A7" stroke="black" stroke-width="2"/>
    <line x1="140" y1="30" x2="140" y2="230" stroke="#2E7D32" stroke-width="3"/>
    <line x1="140" y1="80" x2="80" y2="100" stroke="#2E7D32"/><line x1="140" y1="80" x2="200" y2="100" stroke="#2E7D32"/>
    <line x1="140" y1="130" x2="70" y2="150" stroke="#2E7D32"/><line x1="140" y1="130" x2="210" y2="150" stroke="#2E7D32"/>
    <line x1="140" y1="230" x2="140" y2="270" stroke="#8D6E63" stroke-width="4"/>
    <text x="145" y="85" font-size="11">Midrib</text><text x="60" y="105" font-size="11">Lateral Vein</text>
    <text x="145" y="270" font-size="11">Petiole</text><text x="140" y="300" font-size="14" text-anchor="middle">Dicot Leaf</text>
    </svg>"""

def s1_bio_magnifying(): return """<svg width="250" height="200"><circle cx="100" cy="80" r="50" fill="none" stroke="black" stroke-width="3"/><line x1="135" y1="115" x2="180" y2="160" stroke="#8D6E63" stroke-width="8"/><text x="50" y="40" font-size="12">Lens</text><text x="185" y="175" font-size="12">Handle</text><text x="125" y="185" font-size="14">Hand Lens</text></svg>"""
def s1_bio_food_test(): return """<svg width="200" height="250"><path d="M 70 50 L 60 180 L 140 180 L 130 50 Z" fill="none" stroke="black" stroke-width="2"/><rect x="80" y="90" width="40" height="30" fill="#2196F3" opacity="0.6"/><text x="85" y="110" font-size="12" fill="white">Solution</text><text x="100" y="220" font-size="14">Test Tube</text></svg>"""
def s1_bio_safety(): return """<svg width="200" height="250"><path d="M 60 50 L 60 200 L 140 200 L 140 50 Q 100 30 60 50" fill="white" stroke="black" stroke-width="2"/><line x1="100" y1="50" x2="100" y2="200" stroke="black" stroke-dasharray="2,2"/><text x="100" y="30" font-size="14">Lab Coat</text></svg>"""

# ========== S2 BIOLOGY: 6 DIAGRAMS ==========
def s2_bio_heart():
    """S2: Human Heart - 4 chambers + major vessels"""
    return """<svg width="320" height="260">
    <path d="M160 190 Q 70 140 70 100 Q 70 70 100 70 Q 120 70 160 90 Q 200 70 220 70 Q 250 70 250 100 Q 250 140 160 190" fill="#EF9A9A" stroke="black" stroke-width="2"/>
    <line x1="160" y1="90" x2="160" y2="190" stroke="black" stroke-width="2"/>
    <ellipse cx="120" cy="120" rx="25" ry="30" fill="none" stroke="black"/><text x="105" y="125" font-size="10">LV</text>
    <ellipse cx="200" cy="120" rx="25" ry="30" fill="none" stroke="black"/><text x="190" y="125" font-size="10">RV</text>
    <line x1="160" y1="70" x2="160" y2="40" stroke="black" stroke-width="3"/><text x="165" y="35" font-size="11">Aorta</text>
    <line x1="130" y1="70" x2="110" y2="45" stroke="black" stroke-width="2"/><text x="80" y="45" font-size="11">Pulmonary Artery</text>
    <text x="160" y="230" font-size="14" text-anchor="middle">Human Heart</text>
    </svg>"""

def s2_bio_respiratory(): return """<svg width="320" height="260"><line x1="160" y1="40" x2="160" y2="80" stroke="black" stroke-width="4"/><ellipse cx="115" cy="140" rx="35" ry="55" fill="#FFCDD2" stroke="black"/><ellipse cx="205" cy="140" rx="35" ry="55" fill="#FFCDD2" stroke="black"/><line x1="160" y1="80" x2="115" y2="100" stroke="black" stroke-width="3"/><line x1="160" y1="80" x2="205" y2="100" stroke="black" stroke-width="3"/><text x="160" y="30" font-size="12">Trachea</text><text x="80" y="150" font-size="11">Left Lung</text><text x="220" y="150" font-size="11">Right Lung</text></svg>"""
def s2_bio_digestive(): return """<svg width="280" height="320"><ellipse cx="140" cy="90" rx="45" ry="30" fill="none" stroke="black"/><path d="M 140 120 Q 100 160 110 210 Q 140 230 170 210 Q 180 160 140 120" fill="none" stroke="black"/><path d="M 170 210 Q 190 240 140 270 Q 90 240 110 210" fill="none" stroke="black"/><text x="140" y="85" font-size="11">Stomach</text><text x="140" y="300" font-size="14">Digestive System</text></svg>"""
def s2_bio_blood(): return """<svg width="320" height="200"><circle cx="90" cy="100" r="12" fill="#F44336" stroke="black"/><circle cx="160" cy="100" r="15" fill="white" stroke="black"/><circle cx="230" cy="100" r="8" fill="#9C27B0" stroke="black"/><text x="75" y="130" font-size="11">RBC</text><text x="145" y="130" font-size="11">WBC</text><text x="215" y="130" font-size="11">Platelet</text></svg>"""
def s2_bio_skeleton(): return """<svg width="220" height="320"><circle cx="110" cy="50" r="20" fill="none" stroke="black"/><line x1="110" y1="70" x2="110" y2="170" stroke="black" stroke-width="3"/><line x1="110" y1="100" x2="70" y2="130" stroke="black" stroke-width="2"/><line x1="110" y1="100" x2="150" y2="130" stroke="black" stroke-width="2"/><line x1="110" y1="170" x2="80" y2="230" stroke="black" stroke-width="2"/><line x1="110" y1="170" x2="140" y2="230" stroke="black" stroke-width="2"/></svg>"""
def s2_bio_microscope(): return """<svg width="220" height="260"><rect x="90" y="210" width="40" height="20" fill="#616161"/><rect x="100" y="60" width="20" height="150" fill="#616161"/><circle cx="110" cy="50" r="15" fill="black"/><rect x="80" y="40" width="60" height="10" fill="black"/></svg>"""

# ========== S3 BIOLOGY: 6 DIAGRAMS ==========
def s3_bio_neuron(): return """<svg width="360" height="220"><circle cx="90" cy="110" r="25" fill="#FFF9C4" stroke="black"/><path d="M 115 110 Q 190 90 260 110" fill="none" stroke="black" stroke-width="3"/><line x1="260" y1="110" x2="280" y2="100" stroke="black" stroke-width="2"/><line x1="260" y1="110" x2="280" y2="120" stroke="black" stroke-width="2"/><text x="80" y="115" font-size="11">Cell Body</text><text x="260" y="95" font-size="11">Axon</text></svg>"""
def s3_bio_kidney(): return """<svg width="260" height="220"><path d="M 90 60 Q 50 110 90 160 Q 140 180 190 160 Q 230 110 190 60 Q 140 40 90 60" fill="#EF5350" stroke="black"/><path d="M 140 70 Q 120 110 140 150" fill="none" stroke="black" stroke-width="2"/><text x="140" y="200" font-size="14">Kidney</text></svg>"""
def s3_bio_photosynthesis(): return """<svg width="360" height="220"><rect x="60" y="90" width="70" height="40" fill="#C8E6C9" stroke="black"/><text x="65" y="115" font-size="10">CO2 + H2O</text><line x1="130" y1="110" x2="180" y2="110" stroke="black" marker-end="url(#a)"/><rect x="180" y="90" width="70" height="40" fill="#FFF9C4" stroke="black"/><text x="185" y="115" font-size="10">C6H12O6 + O2</text><text x="135" y="70" font-size="12">Sunlight + Chlorophyll</text></svg>"""
def s3_bio_dna(): return """<svg width="220" height="260"><path d="M 90 30 Q 130 50 90 70 Q 50 90 90 110 Q 130 130 90 150 Q 50 170 90 190 Q 130 210 90 230" fill="none" stroke="#3F51B5" stroke-width="2"/><path d="M 130 30 Q 90 50 130 70 Q 170 90 130 110 Q 90 130 130 150 Q 170 170 130 190 Q 90 210 130 230" fill="none" stroke="#E91E63" stroke-width="2"/></svg>"""
def s3_bio_ecosystem(): return """<svg width="360" height="160"><rect x="30" y="70" width="60" height="30" fill="#66BB6A"/><rect x="130" y="70" width="60" height="30" fill="#FFA726"/><rect x="230" y="70" width="60" height="30" fill="#8D6E63"/><line x1="90" y1="85" x2="130" y2="85" stroke="black" marker-end="url(#b)"/><line x1="190" y1="85" x2="230" y2="85" stroke="black" marker-end="url(#b)"/><text x="40" y="65" font-size="11">Producer</text><text x="135" y="65" font-size="11">Consumer</text><text x="235" y="65" font-size="11">Top Consumer</text></svg>"""
def s3_bio_bacteria(): return """<svg width="320" height="160"><circle cx="70" cy="80" r="10" fill="#7B1FA2"/><rect x="110" y="70" width="30" height="20" fill="#7B1FA2"/><path d="M 180 80 Q 190 70 200 80 Q 190 90 180 80" fill="#7B1FA2"/><text x="60" y="105" font-size="11">Coccus</text><text x="105" y="105" font-size="11">Bacillus</text><text x="175" y="105" font-size="11">Spirillum</text></svg>"""

# ========== S4 BIOLOGY: 6 DIAGRAMS ==========
def s4_bio_brain(): return """<svg width="320" height="220"><ellipse cx="160" cy="110" rx="85" ry="65" fill="#F8BBD0" stroke="black" stroke-width="2"/><path d="M 110 110 Q 160 80 210 110" fill="none" stroke="black"/><text x="160" y="115" font-size="14">Cerebrum</text></svg>"""
def s4_bio_eye(): return """<svg width="320" height="220"><circle cx="160" cy="110" r="60" fill="white" stroke="black" stroke-width="2"/><circle cx="160" cy="110" r="20" fill="black"/><circle cx="160" cy="110" r="10" fill="white"/><text x="160" y="180" font-size="14">Human Eye</text></svg>"""
def s4_bio_ear(): return """<svg width="260" height="220"><path d="M 60 110 Q 90 60 130 80 Q 170 100 190 110 Q 170 120 130 140 Q 90 160 60 110" fill="#F8BBD0" stroke="black"/><circle cx="150" cy="110" r="10" fill="none" stroke="black"/></svg>"""
def s4_bio_meiosis(): return """<svg width="360" height="160"><circle cx="60" cy="80" r="20" stroke="black" fill="none"/><line x1="80" y1="80" x2="110" y2="80" stroke="black"/><circle cx="130" cy="80" r="15" stroke="black" fill="none"/><circle cx="150" cy="80" r="15" stroke="black" fill="none"/><line x1="170" y1="80" x2="200" y2="80" stroke="black"/><circle cx="220" cy="65" r="10" stroke="black" fill="none"/><circle cx="220" cy="95" r="10" stroke="black" fill="none"/></svg>"""
def s4_bio_genetics(): return """<svg width="260" height="220"><rect x="60" y="60" width="100" height="100" fill="none" stroke="black" stroke-width="2"/><line x1="110" y1="60" x2="110" y2="160" stroke="black"/><line x1="60" y1="110" x2="160" y2="110" stroke="black"/><text x="80" y="90" font-size="12">TT</text><text x="130" y="90" font-size="12">Tt</text><text x="80" y="140" font-size="12">Tt</text><text x="130" y="140" font-size="12">tt</text></svg>"""
def s4_bio_immune(): return """<svg width="320" height="220"><circle cx="110" cy="110" r="20" fill="#F44336" stroke="black"/><path d="M 160 80 L 160 140 L 180 140 L 180 80 Z" fill="#3F51B5" stroke="black"/><line x1="160" y1="110" x2="130" y2="110" stroke="black" stroke-width="2"/><text x="100" y="150" font-size="11">Antigen</text><text x="155" y="160" font-size="11">Antibody</text></svg>"""

 from . import biology_diagrams as bd

def get_biology_diagram(question):
    q = question.lower()
    
    # S1
    if "animal cell" in q: return bd.s1_bio_animal_cell()
    if "plant cell" in q: return bd.s1_bio_plant_cell()
    if "leaf" in q: return bd.s1_bio_leaf()
    if "hand lens" in q or "magnifying" in q: return bd.s1_bio_magnifying()
    if "test tube" in q or "food test" in q: return bd.s1_bio_food_test()
    if "lab coat" in q or "safety" in q: return bd.s1_bio_safety()
    
    # S2
    if "heart" in q: return bd.s2_bio_heart()
    if "respiratory" in q or "lung" in q or "trachea" in q: return bd.s2_bio_respiratory()
    if "digestive" in q or "stomach" in q: return bd.s2_bio_digestive()
    if "blood cell" in q or "rbc" in q: return bd.s2_bio_blood()
    if "skeleton" in q: return bd.s2_bio_skeleton()
    if "microscope" in q: return bd.s2_bio_microscope()
    
    # S3
    if "neuron" in q or "nerve cell" in q: return bd.s3_bio_neuron()
    if "kidney" in q: return bd.s3_bio_kidney()
    if "photosynthesis" in q: return bd.s3_bio_photosynthesis()
    if "dna" in q: return bd.s3_bio_dna()
    if "food chain" in q or "ecosystem" in q: return bd.s3_bio_ecosystem()
    if "bacteria" in q: return bd.s3_bio_bacteria()
    
    # S4
    if "brain" in q: return bd.s4_bio_brain()
    if "eye" in q: return bd.s4_bio_eye()
    if "ear" in q: return bd.s4_bio_ear()
    if "meiosis" in q: return bd.s4_bio_meiosis()
    if "punnett" in q or "genetics" in q: return bd.s4_bio_genetics()
    if "antibody" in q or "immune" in q: return bd.s4_bio_immune()
    
    return None
