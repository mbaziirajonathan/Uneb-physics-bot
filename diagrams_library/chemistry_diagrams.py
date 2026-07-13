import streamlit as st

# S1: 6
def draw_bunsen_burner(): 
    svg = """<svg width="300" height="300"><text x="150" y="20" text-anchor="middle" font-size="16" font-weight="bold">Bunsen Burner</text>
    <rect x="120" y="200" width="60" height="60" fill="#A9A9A9" stroke="black"/><rect x="130" y="100" width="40" height="100" fill="#696969" stroke="black"/>
    <circle cx="150" cy="90" r="10" fill="orange"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_filtration_setup(): 
    svg = """<svg width="300" height="300"><text x="150" y="20" text-anchor="middle" font-size="16" font-weight="bold">Filtration</text>
    <rect x="120" y="50" width="60" height="80" fill="lightgray" stroke="black"/><polygon points="150,130 130,180 170,180" fill="white" stroke="black"/>
    <rect x="130" y="200" width="40" height="60" fill="lightblue" stroke="black"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_evaporation_setup(): 
    svg = """<svg width="300" height="250"><text x="150" y="20" text-anchor="middle" font-size="16" font-weight="bold">Evaporation</text>
    <ellipse cx="150" cy="150" rx="60" ry="20" fill="white" stroke="black"/><text x="120" y="155">Solution</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_atom_structure(): 
    svg = """<svg width="300" height="250"><text x="150" y="20" text-anchor="middle" font-size="16" font-weight="bold">Atom Structure</text>
    <circle cx="150" cy="125" r="15" fill="red"/><circle cx="150" cy="125" r="40" stroke="blue" fill="none"/><circle cx="150" cy="125" r="65" stroke="green" fill="none"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_states_of_matter(): 
    svg = """<svg width="400" height="150"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">States of Matter</text>
    <rect x="50" y="60" width="80" height="40" fill="gray"/><text x="60" y="85">Solid</text><ellipse cx="200" cy="80" rx="30" ry="15" fill="blue"/><text x="185" y="85">Liquid</text><circle cx="320" cy="80" r="5" fill="black"/><text x="310" y="85">Gas</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_melting_point(): 
    svg = """<svg width="400" height="200"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Melting Point Curve</text>
    <polyline points="50,150 100,150 150,100 200,100 250,50" stroke="blue" stroke-width="2" fill="none"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

# S2: 6
def draw_water_molecule(): 
    svg = """<svg width="400" height="200"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Water Molecule H2O</text>
    <circle cx="200" cy="100" r="25" fill="red" stroke="black"/><text x="193" y="105" fill="white">O</text>
    <circle cx="140" cy="60" r="18" fill="white" stroke="black"/><text x="134" y="65">H</text><circle cx="260" cy="60" r="18" fill="white" stroke="black"/><text x="254" y="65">H</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_ph_scale(): 
    svg = """<svg width="500" height="100"><text x="250" y="20" text-anchor="middle" font-size="16" font-weight="bold">pH Scale</text>
    <rect x="50" y="40" width="400" height="20" fill="red"/><text x="60" y="35">1 Acid</text><text x="440" y="35">14 Base</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_titration_setup(): 
    svg = """<svg width="400" height="300"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Titration</text>
    <rect x="180" y="40" width="40" height="120" fill="white" stroke="black"/><rect x="170" y="180" width="60" height="40" fill="pink" stroke="black"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_electrolysis_water(): 
    svg = """<svg width="400" height="200"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Electrolysis of Water</text>
    <rect x="150" y="60" width="100" height="80" fill="lightblue" stroke="black"/><rect x="160" y="50" width="10" height="20" fill="black"/><rect x="230" y="50" width="10" height="20" fill="black"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_rusting_iron(): 
    svg = """<svg width="400" height="200"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Rusting of Iron</text>
    <rect x="150" y="100" width="100" height="20" fill="#B87333" stroke="black"/><text x="170" y="115">Fe2O3</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_flame_test(): 
    svg = """<svg width="300" height="200"><text x="150" y="20" text-anchor="middle" font-size="16" font-weight="bold">Flame Test</text>
    <rect x="130" y="100" width="40" height="60" fill="#696969" stroke="black"/><path d="M 150 100 Q 140 70 150 60 Q 160 70 150 100" fill="orange"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

# S3: 6
def draw_gas_laws_apparatus(): 
    svg = """<svg width="400" height="200"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Boyle's Law Apparatus</text>
    <rect x="180" y="60" width="40" height="100" fill="white" stroke="black"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_periodic_trends(): 
    svg = """<svg width="500" height="200"><text x="250" y="20" text-anchor="middle" font-size="16" font-weight="bold">Periodic Trends</text>
    <polyline points="50,150 150,100 250,120 350,80 450,90" stroke="blue" stroke-width="2" fill="none"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_ionic_bonding(): 
    svg = """<svg width="400" height="200"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Ionic Bond NaCl</text>
    <circle cx="120" cy="100" r="25" fill="blue" stroke="black"/><text x="112" y="105" fill="white">Na+</text>
    <circle cx="280" cy="100" r="25" fill="green" stroke="black"/><text x="272" y="105" fill="white">Cl-</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_covalent_bonding(): 
    svg = """<svg width="400" height="200"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Covalent Bond H2</text>
    <circle cx="160" cy="100" r="20" fill="white" stroke="black"/><circle cx="240" cy="100" r="20" fill="white" stroke="black"/><line x1="180" y1="100" x2="220" y2="100" stroke="black" stroke-width="3"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_reaction_rate_graph(): 
    svg = """<svg width="400" height="200"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Reaction Rate</text>
    <polyline points="50,150 150,100 250,70 350,60" stroke="red" stroke-width="2" fill="none"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_chromatography(): 
    svg = """<svg width="300" height="250"><text x="150" y="20" text-anchor="middle" font-size="16" font-weight="bold">Paper Chromatography</text>
    <rect x="120" y="50" width="60" height="150" fill="white" stroke="black"/><circle cx="150" cy="100" r="5" fill="purple"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

# S4: 6
def draw_fractional_distillation(): 
    svg = """<svg width="500" height="300"><text x="250" y="20" text-anchor="middle" font-size="16" font-weight="bold">Fractional Distillation</text>
    <rect x="200" y="200" width="100" height="60" fill="orange" stroke="black"/><rect x="220" y="80" width="60" height="120" fill="lightgray" stroke="black"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_haber_process(): 
    svg = """<svg width="400" height="200"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Haber Process</text>
    <rect x="150" y="80" width="100" height="60" fill="gray" stroke="black"/><text x="170" y="115">Fe Catalyst</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_contact_process(): 
    svg = """<svg width="400" height="200"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Contact Process</text>
    <rect x="150" y="80" width="100" height="60" fill="gray" stroke="black"/><text x="165" y="115">V2O5</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_esterification(): 
    svg = """<svg width="500" height="200"><text x="250" y="20" text-anchor="middle" font-size="16" font-weight="bold">Esterification</text>
    <text x="100" y="100">Acid + Alcohol</text><text x="300" y="100">-> Ester + Water</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_polymerization(): 
    svg = """<svg width="500" height="150"><text x="250" y="20" text-anchor="middle" font-size="16" font-weight="bold">Polymerization</text>
    <circle cx="100" cy="80" r="10" fill="blue"/><circle cx="130" cy="80" r="10" fill="blue"/><circle cx="160" cy="80" r="10" fill="blue"/><text x="200" y="85">-> Chain</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_galvanic_cell(): 
    svg = """<svg width="500" height="250"><text x="250" y="20" text-anchor="middle" font-size="16" font-weight="bold">Daniell Cell</text>
    <rect x="60" y="80" width="80" height="100" fill="lightblue" stroke="black"/><text x="75" y="135">ZnSO4</text>
    <rect x="360" y="80" width="80" height="100" fill="lightgreen" stroke="black"/><text x="375" y="135">CuSO4</text>
    <rect x="220" y="100" width="60" height="60" fill="white" stroke="black"/><text x="225" y="135">Salt Bridge</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)
