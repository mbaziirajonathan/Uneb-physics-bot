import streamlit as st

# ========== S1: 6 ==========
def draw_plant_cell(): 
    svg = """<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Plant Cell</text>
    <rect x="100" y="80" width="200" height="200" fill="#E6FFE6" stroke="black" stroke-width="3"/>
    <rect x="105" y="85" width="190" height="190" fill="none" stroke="green" stroke-width="2"/>
    <circle cx="200" cy="180" r="30" fill="#ADD8E6" stroke="black"/><text x="185" y="185" font-size="10">Nucleus</text>
    <ellipse cx="150" cy="140" rx="15" ry="8" fill="#90EE90"/><text x="125" y="142" font-size="10">Chloroplast</text>
    <rect x="240" y="160" width="40" height="40" fill="lightblue" stroke="black"/><text x="245" y="185" font-size="10">Vacuole</text>
    <text x="200" y="370" text-anchor="middle" font-size="11">Cell Wall gives rigidity</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_animal_cell(): 
    svg = """<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Animal Cell</text>
    <ellipse cx="200" cy="180" rx="100" ry="120" fill="#FFE6E6" stroke="black" stroke-width="2"/>
    <circle cx="200" cy="180" r="30" fill="#ADD8E6" stroke="black"/><text x="185" y="185" font-size="10">Nucleus</text>
    <circle cx="240" cy="220" r="15" fill="orange"/><text x="245" y="225" font-size="10">Mitochondria</text>
    <text x="200" y="370" text-anchor="middle" font-size="11">No cell wall. Has centrioles</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_light_microscope(): 
    svg = """<svg width="300" height="300" xmlns="http://www.w3.org/2000/svg"><text x="150" y="20" text-anchor="middle" font-size="16" font-weight="bold">Light Microscope</text>
    <rect x="120" y="60" width="60" height="180" fill="gray" stroke="black"/><rect x="110" y="240" width="80" height="20" fill="black"/>
    <circle cx="150" cy="100" r="15" fill="white" stroke="black"/><text x="115" y="105" font-size="10">Lens</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_leaf_cross_section(): 
    svg = """<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Leaf Cross Section</text>
    <rect x="100" y="80" width="200" height="60" fill="lightgreen" stroke="black"/>
    <rect x="100" y="75" width="200" height="5" fill="darkgreen"/><rect x="100" y="140" width="200" height="5" fill="darkgreen"/>
    <text x="110" y="110" font-size="10">Palisade</text><text x="110" y="125" font-size="10">Spongy</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_root_hair_cell(): 
    svg = """<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg"><text x="150" y="20" text-anchor="middle" font-size="16" font-weight="bold">Root Hair Cell</text>
    <ellipse cx="150" cy="120" rx="80" ry="20" fill="saddlebrown" stroke="black"/>
    <rect x="145" y="100" width="10" height="40" fill="brown"/><text x="110" y="130" font-size="10">Root Hair</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_food_tests(): 
    svg = """<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Food Tests</text>
    <rect x="80" y="60" width="50" height="40" fill="blue" stroke="black"/><text x="85" y="85" font-size="10">Starch</text>
    <rect x="150" y="60" width="50" height="40" fill="orange" stroke="black"/><text x="155" y="85" font-size="10">Protein</text>
    <rect x="220" y="60" width="50" height="40" fill="red" stroke="black"/><text x="225" y="85" font-size="10">Sugar</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

# ========== S2: 6 ==========
def draw_amoeba(): 
    svg = """<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg"><text x="150" y="20" text-anchor="middle" font-size="16" font-weight="bold">Amoeba</text>
    <ellipse cx="150" cy="100" rx="60" ry="40" fill="lightpink" stroke="black"/>
    <circle cx="150" cy="100" r="10" fill="purple"/><text x="140" y="105" font-size="10">N</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_paramecium(): 
    svg = """<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg"><text x="150" y="20" text-anchor="middle" font-size="16" font-weight="bold">Paramecium</text>
    <ellipse cx="150" cy="100" rx="70" ry="30" fill="lightblue" stroke="black"/>
    <circle cx="150" cy="100" r="8" fill="purple"/><text x="100" y="110" font-size="10">Cilia</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_spirogyra(): 
    svg = """<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Spirogyra</text>
    <rect x="100" y="80" width="200" height="40" fill="lightgreen" stroke="black"/>
    <path d="M 110 90 Q 150 100 190 90 T 270 90" stroke="darkgreen" stroke-width="2"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_human_heart(): 
    svg = """<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Human Heart</text>
    <ellipse cx="200" cy="150" rx="80" ry="100" fill="#FF7F7F" stroke="black" stroke-width="2"/>
    <line x1="200" y1="60" x2="200" y2="240" stroke="black" stroke-width="2"/>
    <text x="120" y="120" font-size="12">RA</text><text x="260" y="120" font-size="12">LA</text>
    <text x="120" y="190" font-size="12">RV</text><text x="260" y="190" font-size="12">LV</text>
    <text x="50" y="280" font-size="11">RA=Right Atrium, RV=Right Ventricle, LA=Left Atrium, LV=Left Ventricle</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_blood_circulation(): 
    svg = """<svg width="400" height="250" xmlns="http://www.w3.org/2000/svg"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Blood Circulation</text>
    <circle cx="200" cy="125" r="40" fill="#FF7F7F" stroke="black"/><text x="180" y="130">Heart</text>
    <path d="M 240 125 Q 300 80 320 125" stroke="red" stroke-width="3" fill="none"/>
    <path d="M 160 125 Q 100 170 180 125" stroke="blue" stroke-width="3" fill="none"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_respiratory_system(): 
    svg = """<svg width="400" height="250" xmlns="http://www.w3.org/2000/svg"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Respiratory System</text>
    <path d="M 200 60 L 170 120 L 230 120 Z" fill="pink" stroke="black"/>
    <ellipse cx="170" cy="150" rx="20" ry="30" fill="pink" stroke="black"/><ellipse cx="230" cy="150" rx="20" ry="30" fill="pink" stroke="black"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

# ========== S3: 6 ==========
def draw_digestive_system(): 
    svg = """<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Digestive System</text>
    <rect x="180" y="50" width="40" height="20" fill="pink" stroke="black"/><text x="185" y="65">Mouth</text>
    <rect x="185" y="70" width="30" height="100" fill="pink" stroke="black"/><text x="190" y="120">Esophagus</text>
    <ellipse cx="200" cy="200" rx="50" ry="30" fill="pink" stroke="black"/><text x="175" y="205">Stomach</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_nephron(): 
    svg = """<svg width="400" height="250" xmlns="http://www.w3.org/2000/svg"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Nephron</text>
    <circle cx="150" cy="80" r="20" fill="red" stroke="black"/><path d="M 150 100 Q 200 150 250 100" stroke="blue" stroke-width="3" fill="none"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_flower_parts(): 
    svg = """<svg width="400" height="250" xmlns="http://www.w3.org/2000/svg"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Flower Parts</text>
    <circle cx="200" cy="120" r="30" fill="yellow" stroke="black"/><text x="190" y="125">Anther</text>
    <rect x="195" y="150" width="10" height="50" fill="green"/><text x="210" y="180">Stalk</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_pollination(): 
    svg = """<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Pollination</text>
    <circle cx="120" cy="100" r="30" fill="pink" stroke="black"/><circle cx="280" cy="100" r="30" fill="pink" stroke="black"/>
    <path d="M 150 100 Q 200 60 250 100" stroke="orange" stroke-width="3"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_dna_double_helix(): 
    svg = """<svg width="400" height="250" xmlns="http://www.w3.org/2000/svg"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">DNA Double Helix</text>
    <path d="M 100 50 Q 200 100 100 150 Q 200 200 100 250" stroke="blue" stroke-width="3" fill="none"/>
    <path d="M 300 50 Q 200 100 300 150 Q 200 200 300 250" stroke="blue" stroke-width="3" fill="none"/>
    <line x1="100" y1="80" x2="300" y2="80" stroke="red"/><line x1="100" y1="120" x2="300" y2="120" stroke="red"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_mitosis(): 
    svg = """<svg width="500" height="150" xmlns="http://www.w3.org/2000/svg"><text x="250" y="20" text-anchor="middle" font-size="16" font-weight="bold">Mitosis Stages</text>
    <circle cx="80" cy="80" r="20" fill="lightblue" stroke="black"/><text x="70" y="85">1</text>
    <circle cx="180" cy="80" r="20" fill="lightblue" stroke="black"/><text x="170" y="85">2</text>
    <circle cx="280" cy="80" r="20" fill="lightblue" stroke="black"/><text x="270" y="85">3</text>
    <circle cx="380" cy="80" r="20" fill="lightblue" stroke="black"/><text x="370" y="85">4</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

# ========== S4: 6 ==========
def draw_human_brain(): 
    svg = """<svg width="400" height="250" xmlns="http://www.w3.org/2000/svg"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Human Brain</text>
    <ellipse cx="200" cy="120" rx="100" ry="60" fill="pink" stroke="black"/>
    <text x="120" y="110" font-size="10">Cerebrum</text><text x="170" y="160" font-size="10">Cerebellum</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_human_eye(): 
    svg = """<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Human Eye</text>
    <circle cx="200" cy="100" r="60" fill="white" stroke="black" stroke-width="2"/>
    <circle cx="200" cy="100" r="20" fill="black"/><text x="180" y="105" fill="white">Pupil</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_human_ear(): 
    svg = """<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Human Ear</text>
    <path d="M 100 100 Q 150 50 200 100 Q 150 150 100 100" fill="pink" stroke="black"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_human_skeleton(): 
    svg = """<svg width="300" height="300" xmlns="http://www.w3.org/2000/svg"><text x="150" y="20" text-anchor="middle" font-size="16" font-weight="bold">Human Skeleton</text>
    <line x1="150" y1="40" x2="150" y2="260" stroke="gray" stroke-width="4"/>
    <circle cx="150" cy="30" r="15" fill="gray"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_photosynthesis(): 
    svg = """<svg width="500" height="250" xmlns="http://www.w3.org/2000/svg"><text x="250" y="20" text-anchor="middle" font-size="16" font-weight="bold">Photosynthesis</text>
    <circle cx="250" cy="125" r="50" fill="green" stroke="black"/><text x="215" y="130" fill="white">Plant</text>
    <text x="50" y="100" font-size="12">CO2</text><path d="M 80 100 L 200 120" stroke="black" stroke-width="2"/>
    <text x="400" y="100" font-size="12">O2</text><path d="M 300 120 L 380 100" stroke="black" stroke-width="2"/>
    <text x="200" y="220" text-anchor="middle" font-size="12">6CO2 + 6H2O + Light -> C6H12O6 + 6O2</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_genetics_punnett(): 
    svg = """<svg width="400" height="250" xmlns="http://www.w3.org/2000/svg"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Punnett Square</text>
    <rect x="150" y="60" width="40" height="40" stroke="black" fill="white"/><text x="165" y="85">A</text>
    <rect x="190" y="60" width="40" height="40" stroke="black" fill="white"/><text x="205" y="85">a</text>
    <rect x="110" y="100" width="40" height="40" stroke="black" fill="white"/><text x="125" y="125">A</text>
    <rect x="110" y="140" width="40" height="40" stroke="black" fill="white"/><text x="125" y="165">a</text>
    <text x="200" y="220" text-anchor="middle" font-size="11">Ratio: 3:1 Phenotypic</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)
