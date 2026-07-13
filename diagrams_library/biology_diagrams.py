import streamlit as st

# ========== S1 BIOLOGY: 6 DIAGRAMS ==========
def s1_bio_animal_cell():
    """S1 Bio 1: Animal Cell"""
    return """<svg width="300" height="300" xmlns="http://www.w3.org/2000/svg">
    <circle cx="150" cy="150" r="110" fill="none" stroke="black" stroke-width="2"/>
    <circle cx="150" cy="150" r="35" fill="lightblue" stroke="black"/>
    <text x="135" y="155" font-size="12">Nucleus</text>
    <ellipse cx="90" cy="90" rx="12" ry="6" fill="orange" stroke="black"/>
    <text x="105" y="92" font-size="10">Mitochondrion</text>
    <circle cx="180" cy="100" r="8" fill="pink" stroke="black"/>
    <text x="192" y="103" font-size="10">Vacuole</text>
    <text x="100" y="270" font-size="14" text-anchor="middle">Animal Cell</text>
    </svg>"""

def s1_bio_plant_cell():
    """S1 Bio 2: Plant Cell"""
    return """<svg width="300" height="300">
    <rect x="40" y="40" width="220" height="220" fill="none" stroke="black" stroke-width="2"/>
    <rect x="50" y="50" width="200" height="200" fill="lightgreen" stroke="black"/>
    <circle cx="150" cy="150" r="35" fill="lightblue" stroke="black"/>
    <text x="135" y="155" font-size="12">Nucleus</text>
    <rect x="80" y="80" width="20" height="20" fill="green" stroke="black"/>
    <text x="105" y="95" font-size="10">Chloroplast</text>
    <rect x="40" y="40" width="220" height="220" fill="none" stroke="black" stroke-width="3"/>
    <text x="150" y="280" font-size="14" text-anchor="middle">Plant Cell</text>
    </svg>"""

def s1_bio_leaf():
    """S1 Bio 3: Leaf External Structure"""
    return """<svg width="250" height="300">
    <ellipse cx="125" cy="120" rx="80" ry="90" fill="lightgreen" stroke="black" stroke-width="2"/>
    <line x1="125" y1="30" x2="125" y2="210" stroke="black" stroke-width="2"/>
    <line x1="125" y1="80" x2="60" y2="100" stroke="black"/>
    <line x1="125" y1="80" x2="190" y2="100" stroke="black"/>
    <text x="130" y="85" font-size="12">Midrib</text>
    <text x="50" y="105" font-size="12">Vein</text>
    <text x="125" y="270" font-size="14" text-anchor="middle">Leaf</text>
    </svg>"""

def s1_bio_magnifying():
    """S1 Bio 4: Magnifying Glass"""
    return """<svg width="250" height="200">
    <circle cx="100" cy="80" r="50" fill="none" stroke="black" stroke-width="3"/>
    <line x1="135" y1="115" x2="180" y2="160" stroke="brown" stroke-width="8"/>
    <text x="50" y="40" font-size="12">Lens</text>
    <text x="185" y="175" font-size="12">Handle</text>
    <text x="125" y="185" font-size="14">Hand Lens</text>
    </svg>"""

def s1_bio_food_test():
    """S1 Bio 5: Test Tube for Food Tests"""
    return """<svg width="200" height="250">
    <path d="M 70 50 L 60 180 L 140 180 L 130 50 Z" fill="none" stroke="black" stroke-width="2"/>
    <line x1="60" y1="180" x2="140" y2="180" stroke="black" stroke-width="2"/>
    <rect x="80" y="90" width="40" height="30" fill="blue" opacity="0.6"/>
    <text x="85" y="110" font-size="12" fill="white">Solution</text>
    <text x="100" y="220" font-size="14" text-anchor="middle">Test Tube</text>
    </svg>"""

def s1_bio_safety():
    """S1 Bio 6: Lab Safety - Lab Coat"""
    return """<svg width="200" height="250">
    <path d="M 60 50 L 60 200 L 140 200 L 140 50 Q 100 30 60 50" fill="white" stroke="black" stroke-width="2"/>
    <line x1="100" y1="50" x2="100" y2="200" stroke="black" stroke-dasharray="2,2"/>
    <text x="100" y="30" font-size="14" text-anchor="middle">Lab Coat</text>
    </svg>"""

# ========== S2 BIOLOGY: 6 DIAGRAMS ==========
def s2_bio_heart():
    """S2 Bio 1: Human Heart"""
    return """<svg width="300" height="250">
    <path d="M150 180 Q 70 130 70 90 Q 70 60 100 60 Q 120 60 150 80 Q 180 60 200 60 Q 230 60 230 90 Q 230 130 150 180" fill="red" stroke="black" stroke-width="2"/>
    <line x1="150" y1="80" x2="150" y2="180" stroke="black" stroke-width="2"/>
    <text x="150" y="50" font-size="14" text-anchor="middle">Human Heart</text>
    <text x="60" y="100" font-size="12">Left</text>
    <text x="240" y="100" font-size="12">Right</text>
    </svg>"""

def s2_bio_respiratory():
    """S2 Bio 2: Respiratory System"""
    return """<svg width="300" height="250">
    <line x1="150" y1="40" x2="150" y2="80" stroke="black" stroke-width="4"/>
    <ellipse cx="110" cy="130" rx="30" ry="50" fill="pink" stroke="black"/>
    <ellipse cx="190" cy="130" rx="30" ry="50" fill="pink" stroke="black"/>
    <line x1="150" y1="80" x2="110" y2="100" stroke="black" stroke-width="3"/>
    <line x1="150" y1="80" x2="190" y2="100" stroke="black" stroke-width="3"/>
    <text x="150" y="30" font-size="12" text-anchor="middle">Trachea</text>
    <text x="150" y="210" font-size="14" text-anchor="middle">Lungs</text>
    </svg>"""

def s2_bio_digestive():
    """S2 Bio 3: Digestive System"""
    return """<svg width="250" height="300">
    <ellipse cx="125" cy="80" rx="40" ry="25" fill="none" stroke="black"/>
    <path d="M 125 105 Q 90 140 100 190 Q 125 210 150 190 Q 160 140 125 105" fill="none" stroke="black"/>
    <path d="M 150 190 Q 170 220 125 250 Q 80 220 100 190" fill="none" stroke="black"/>
    <text x="125" y="75" font-size="12" text-anchor="middle">Stomach</text>
    <text x="125" y="280" font-size="14" text-anchor="middle">Digestive System</text>
    </svg>"""

def s2_bio_blood():
    """S2 Bio 4: Blood Components"""
    return """<svg width="300" height="200">
    <circle cx="80" cy="100" r="12" fill="red" stroke="black"/>
    <circle cx="150" cy="100" r="15" fill="white" stroke="black"/>
    <circle cx="220" cy="100" r="8" fill="purple" stroke="black"/>
    <text x="65" y="130" font-size="12">RBC</text>
    <text x="135" y="130" font-size="12">WBC</text>
    <text x="210" y="130" font-size="12">Platelet</text>
    <text x="150" y="170" font-size="14" text-anchor="middle">Blood Cells</text>
    </svg>"""

def s2_bio_skeleton():
    """S2 Bio 5: Human Skeleton Outline"""
    return """<svg width="200" height="300">
    <circle cx="100" cy="40" r="20" fill="none" stroke="black"/>
    <line x1="100" y1="60" x2="100" y2="160" stroke="black" stroke-width="3"/>
    <line x1="100" y1="90" x2="60" y2="120" stroke="black" stroke-width="2"/>
    <line x1="100" y1="90" x2="140" y2="120" stroke="black" stroke-width="2"/>
    <line x1="100" y1="160" x2="70" y2="220" stroke="black" stroke-width="2"/>
    <line x1="100" y1="160" x2="130" y2="220" stroke="black" stroke-width="2"/>
    <text x="100" y="270" font-size="14" text-anchor="middle">Skeleton</text>
    </svg>"""

def s2_bio_microscope():
    """S2 Bio 6: Simple Microscope"""
    return """<svg width="200" height="250">
    <rect x="80" y="200" width="40" height="20" fill="gray"/>
    <rect x="90" y="50" width="20" height="150" fill="gray"/>
    <circle cx="100" cy="40" r="15" fill="black"/>
    <rect x="70" y="30" width="60" height="10" fill="black"/>
    <text x="100" y="240" font-size="14" text-anchor="middle">Microscope</text>
    </svg>"""

# ========== S3 BIOLOGY: 6 DIAGRAMS ==========
def s3_bio_neuron():
    """S3 Bio 1: Neuron"""
    return """<svg width="350" height="200">
    <circle cx="80" cy="100" r="25" fill="yellow" stroke="black"/>
    <path d="M 105 100 Q 180 80 250 100" fill="none" stroke="black" stroke-width="3"/>
    <line x1="250" y1="100" x2="270" y2="90" stroke="black" stroke-width="2"/>
    <line x1="250" y1="100" x2="270" y2="110" stroke="black" stroke-width="2"/>
    <text x="70" y="105" font-size="12">Cell Body</text>
    <text x="250" y="85" font-size="12">Axon</text>
    </svg>"""

def s3_bio_kidney():
    """S3 Bio 2: Kidney"""
    return """<svg width="250" height="200">
    <path d="M 80 50 Q 50 100 80 150 Q 125 170 170 150 Q 200 100 170 50 Q 125 30 80 50" fill="red" stroke="black"/>
    <path d="M 125 60 Q 110 100 125 140" fill="none" stroke="black" stroke-width="2"/>
    <text x="125" y="180" font-size="14" text-anchor="middle">Kidney</text>
    </svg>"""

def s3_bio_photosynthesis():
    """S3 Bio 3: Photosynthesis Equation Diagram"""
    return """<svg width="350" height="200">
    <rect x="50" y="80" width="60" height="40" fill="lightgreen" stroke="black"/>
    <text x="55" y="105" font-size="10">CO2 + H2O</text>
    <line x1="110" y1="100" x2="160" y2="100" stroke="black" marker-end="url(#a)"/>
    <rect x="160" y="80" width="60" height="40" fill="lightyellow" stroke="black"/>
    <text x="165" y="105" font-size="10">Glucose + O2</text>
    <text x="125" y="60" font-size="12">Sunlight</text>
    <defs><marker id="a"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs>
    </svg>"""

def s3_bio_dna():
    """S3 Bio 4: DNA Double Helix"""
    return """<svg width="200" height="250">
    <path d="M 80 20 Q 120 40 80 60 Q 40 80 80 100 Q 120 120 80 140 Q 40 160 80 180 Q 120 200 80 220" fill="none" stroke="blue" stroke-width="2"/>
    <path d="M 120 20 Q 80 40 120 60 Q 160 80 120 100 Q 80 120 120 140 Q 160 160 120 180 Q 80 200 120 220" fill="none" stroke="red" stroke-width="2"/>
    <text x="100" y="240" font-size="14" text-anchor="middle">DNA</text>
    </svg>"""

def s3_bio_ecosystem():
    """S3 Bio 5: Food Chain"""
    return """<svg width="350" height="150">
    <rect x="20" y="60" width="60" height="30" fill="green"/>
    <rect x="120" y="60" width="60" height="30" fill="orange"/>
    <rect x="220" y="60" width="60" height="30" fill="brown"/>
    <line x1="80" y1="75" x2="120" y2="75" stroke="black" marker-end="url(#b)"/>
    <line x1="180" y1="75" x2="220" y2="75" stroke="black" marker-end="url(#b)"/>
    <text x="30" y="55" font-size="12">Plant</text>
    <text x="125" y="55" font-size="12">Rabbit</text>
    <text x="225" y="55" font-size="12">Fox</text>
    <defs><marker id="b"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs>
    </svg>"""

def s3_bio_bacteria():
    """S3 Bio 6: Bacteria Shapes"""
    return """<svg width="300" height="150">
    <circle cx="60" cy="75" r="10" fill="purple"/>
    <rect x="100" y="65" width="30" height="20" fill="purple"/>
    <path d="M 170 75 Q 180 65 190 75 Q 180 85 170 75" fill="purple"/>
    <text x="50" y="100" font-size="12">Coccus</text>
    <text x="100" y="100" font-size="12">Bacillus</text>
    <text x="170" y="100" font-size="12">Spirillum</text>
    </svg>"""

# ========== S4 BIOLOGY: 6 DIAGRAMS ==========
def s4_bio_brain():
    """S4 Bio 1: Human Brain"""
    return """<svg width="300" height="200">
    <ellipse cx="150" cy="100" rx="80" ry="60" fill="pink" stroke="black" stroke-width="2"/>
    <path d="M 100 100 Q 150 70 200 100" fill="none" stroke="black"/>
    <text x="150" y="105" font-size="14" text-anchor="middle">Brain</text>
    </svg>"""

def s4_bio_eye():
    """S4 Bio 2: Eye Cross Section"""
    return """<svg width="300" height="200">
    <circle cx="150" cy="100" r="60" fill="white" stroke="black" stroke-width="2"/>
    <circle cx="150" cy="100" r="20" fill="black"/>
    <circle cx="150" cy="100" r="10" fill="white"/>
    <text x="150" y="170" font-size="14" text-anchor="middle">Eye</text>
    <text x="155" y="105" font-size="12">Pupil</text>
    </svg>"""

def s4_bio_ear():
    """S4 Bio 3: Human Ear"""
    return """<svg width="250" height="200">
    <path d="M 50 100 Q 80 50 120 70 Q 160 90 180 100 Q 160 110 120 130 Q 80 150 50 100" fill="pink" stroke="black"/>
    <circle cx="140" cy="100" r="10" fill="none" stroke="black"/>
    <text x="125" y="170" font-size="14">Ear</text>
    </svg>"""

def s4_bio_meiosis():
    """S4 Bio 4: Meiosis Stages"""
    return """<svg width="350" height="150">
    <circle cx="50" cy="75" r="20" stroke="black" fill="none"/>
    <line x1="70" y1="75" x2="100" y2="75" stroke="black"/>
    <circle cx="120" cy="75" r="15" stroke="black" fill="none"/>
    <circle cx="140" cy="75" r="15" stroke="black" fill="none"/>
    <line x1="160" y1="75" x2="190" y2="75" stroke="black"/>
    <circle cx="210" cy="60" r="10" stroke="black" fill="none"/>
    <circle cx="210" cy="90" r="10" stroke="black" fill="none"/>
    <text x="175" y="110" font-size="12">4 Cells</text>
    </svg>"""

def s4_bio_genetics():
    """S4 Bio 5: Punnett Square"""
    return """<svg width="250" height="200">
    <rect x="50" y="50" width="100" height="100" fill="none" stroke="black" stroke-width="2"/>
    <line x1="100" y1="50" x2="100" y2="150" stroke="black"/>
    <line x1="50" y1="100" x2="150" y2="100" stroke="black"/>
    <text x="70" y="80" font-size="12">TT</text>
    <text x="120" y="80" font-size="12">Tt</text>
    <text x="70" y="130" font-size="12">Tt</text>
    <text x="120" y="130" font-size="12">tt</text>
    </svg>"""

def s4_bio_immune():
    """S4 Bio 6: Antibody Binding Antigen"""
    return """<svg width="300" height="200">
    <circle cx="100" cy="100" r="20" fill="red" stroke="black"/>
    <path d="M 150 70 L 150 130 L 170 130 L 170 70 Z" fill="blue" stroke="black"/>
    <path d="M 150 100 L 120 100" stroke="black" stroke-width="2"/>
    <text x="90" y="140" font-size="12">Antigen</text>
    <text x="150" y="150" font-size="12">Antibody</text>
    </svg>"""
