import streamlit as st

# ========== S1: 6 ==========
def draw_ruler_vernier(): 
    svg = """<svg width="500" height="120"><text x="250" y="20" text-anchor="middle" font-size="16" font-weight="bold">Vernier Calipers</text>
    <rect x="50" y="50" width="400" height="10" fill="gray" stroke="black"/><text x="50" y="90" font-size="12">Main Scale cm</text>
    <rect x="120" y="40" width="100" height="20" fill="white" stroke="black"/><text x="140" y="55" font-size="10">Vernier Scale</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_beam_balance(): 
    svg = """<svg width="400" height="200"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Beam Balance</text>
    <line x1="200" y1="40" x2="200" y2="160" stroke="black" stroke-width="3"/><line x1="100" y1="160" x2="300" y2="160" stroke="black" stroke-width="3"/>
    <circle cx="120" cy="180" r="20" fill="gray"/><circle cx="280" cy="180" r="20" fill="gray"/><text x="150" y="190">Mass</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_spring_balance(): 
    svg = """<svg width="300" height="250"><text x="150" y="20" text-anchor="middle" font-size="16" font-weight="bold">Spring Balance</text>
    <rect x="125" y="60" width="50" height="100" fill="white" stroke="black" stroke-width="2"/><text x="135" y="115">N</text>
    <line x1="150" y1="160" x2="150" y2="210" stroke="black" stroke-width="3"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_area_irregular_shape(): 
    svg = """<svg width="400" height="200"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Area by Graph Paper</text>
    <rect x="50" y="50" width="300" height="100" fill="none" stroke="gray" stroke-width="1"/>
    <path d="M 100 60 Q 200 40 300 80 L 280 120 Q 200 130 120 110 Z" fill="lightblue" stroke="black"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_volume_displacement(): 
    svg = """<svg width="300" height="250"><text x="150" y="20" text-anchor="middle" font-size="16" font-weight="bold">Volume by Displacement</text>
    <rect x="120" y="50" width="60" height="150" fill="lightblue" stroke="black"/><text x="125" y="100">Water</text>
    <rect x="135" y="80" width="30" height="30" fill="gray"/><text x="125" y="40">Stone</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_simple_pendulum(): 
    svg = """<svg width="400" height="250"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Simple Pendulum</text>
    <line x1="200" y1="40" x2="200" y2="150" stroke="black" stroke-width="2"/><circle cx="200" cy="170" r="15" fill="black"/>
    <text x="180" y="200">Bob</text><text x="200" y="230" text-anchor="middle">T = 2π√(L/g)</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

# ========== S2: 6 ==========
def draw_force_triangle(): 
    svg = """<svg width="400" height="200"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Triangle of Forces</text>
    <polygon points="200,50 120,150 280,150" stroke="black" fill="none" stroke-width="2"/>
    <text x="190" y="40">W</text><text x="100" y="160">T1</text><text x="290" y="160">T2</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_lever_classes(): 
    svg = """<svg width="500" height="200"><text x="250" y="20" text-anchor="middle" font-size="16" font-weight="bold">3 Classes of Levers</text>
    <line x1="50" y1="100" x2="450" y2="100" stroke="black" stroke-width="4"/><circle cx="100" cy="100" r="5" fill="red"/><text x="90" y="80">F</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_hydraulic_press(): 
    svg = """<svg width="400" height="200"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Hydraulic Press</text>
    <rect x="80" y="80" width="60" height="80" fill="lightblue" stroke="black"/><rect x="260" y="60" width="60" height="100" fill="lightblue" stroke="black"/>
    <rect x="140" y="100" width="120" height="20" fill="blue"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_manometer(): 
    svg = """<svg width="400" height="200"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">U-tube Manometer</text>
    <path d="M 150 50 L 150 150 Q 200 170 250 150 L 250 50" stroke="black" stroke-width="3" fill="none"/>
    <rect x="150" y="120" width="100" height="30" fill="red"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_fortin_barometer(): 
    svg = """<svg width="300" height="250"><text x="150" y="20" text-anchor="middle" font-size="16" font-weight="bold">Fortin Barometer</text>
    <rect x="130" y="40" width="40" height="160" fill="white" stroke="black"/><rect x="120" y="200" width="60" height="30" fill="gray"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_density_bottle(): 
    svg = """<svg width="300" height="200"><text x="150" y="20" text-anchor="middle" font-size="16" font-weight="bold">Density Bottle</text>
    <ellipse cx="150" cy="120" rx="40" ry="60" fill="white" stroke="black"/><rect x="140" y="50" width="20" height="20" fill="black"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

# ========== S3: 6 ==========
def draw_ohms_circuit(): 
    svg = """<svg width="500" height="250"><text x="250" y="20" text-anchor="middle" font-size="16" font-weight="bold">Ohm's Law Circuit</text>
    <rect x="60" y="90" width="70" height="40" fill="#ADD8E6" stroke="black" stroke-width="2"/><text x="75" y="115">Battery V</text>
    <rect x="220" y="90" width="70" height="40" fill="#90EE90" stroke="black" stroke-width="2"/><text x="235" y="115">Resistor R</text>
    <circle cx="360" cy="110" r="20" fill="#FFB6C1" stroke="black" stroke-width="2"/><text x="352" y="115">A</text>
    <line x1="130" y1="110" x2="220" y2="110" stroke="black" stroke-width="2"/><line x1="290" y1="110" x2="340" y2="110" stroke="black" stroke-width="2"/>
    <line x1="360" y1="130" x2="360" y2="170" stroke="black" stroke-width="2"/><line x1="360" y1="170" x2="60" y2="170" stroke="black" stroke-width="2"/>
    <line x1="60" y1="170" x2="60" y2="130" stroke="black" stroke-width="2"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_series_parallel(): 
    svg = """<svg width="500" height="180"><text x="250" y="20" text-anchor="middle" font-size="16" font-weight="bold">Series and Parallel</text>
    <text x="80" y="40">Series</text><rect x="50" y="60" width="40" height="20" fill="green" stroke="black"/><rect x="100" y="60" width="40" height="20" fill="green" stroke="black"/>
    <text x="330" y="40">Parallel</text><rect x="300" y="50" width="40" height="20" fill="green" stroke="black"/><rect x="300" y="80" width="40" height="20" fill="green" stroke="black"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_wave_parts(): 
    svg = """<svg width="500" height="200"><text x="250" y="20" text-anchor="middle" font-size="16" font-weight="bold">Transverse Wave</text>
    <path d="M 20 100 Q 70 40 120 100 T 220 100 T 320 100 T 420 100 T 480 100" stroke="blue" stroke-width="2" fill="none"/>
    <text x="110" y="35" font-size="12" fill="red">Crest</text><text x="210" y="175" font-size="12" fill="red">Trough</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_reflection_rays(): 
    svg = """<svg width="400" height="200"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Reflection of Light</text>
    <line x1="200" y1="50" x2="200" y2="150" stroke="black" stroke-width="3"/><line x1="100" y1="80" x2="200" y2="100" stroke="orange" stroke-width="2"/>
    <line x1="200" y1="100" x2="300" y2="80" stroke="orange" stroke-width="2"/><text x="120" y="70">Incident</text><text x="270" y="70">Reflected</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_refraction_prism(): 
    svg = """<svg width="400" height="200"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Refraction through Prism</text>
    <polygon points="200,50 120,150 280,150" stroke="black" fill="lightblue"/><line x1="80" y1="100" x2="200" y2="100" stroke="red" stroke-width="2"/>
    <line x1="200" y1="100" x2="320" y2="130" stroke="red" stroke-width="2"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_lens_ray_diagram(): 
    svg = """<svg width="500" height="200"><text x="250" y="20" text-anchor="middle" font-size="16" font-weight="bold">Convex Lens</text>
    <line x1="250" y1="40" x2="250" y2="160" stroke="black" stroke-width="2"/><ellipse cx="250" cy="100" rx="20" ry="60" fill="none" stroke="black" stroke-width="2"/>
    <circle cx="100" cy="130" r="8" fill="orange"/><circle cx="400" cy="70" r="8" fill="purple"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

# ========== S4: 6 ==========
def draw_transformer(): 
    svg = """<svg width="500" height="200"><text x="250" y="20" text-anchor="middle" font-size="16" font-weight="bold">Step-down Transformer</text>
    <rect x="100" y="80" width="40" height="80" fill="brown" stroke="black"/><text x="105" y="120">Primary</text>
    <rect x="360" y="80" width="40" height="80" fill="brown" stroke="black"/><text x="365" y="120">Secondary</text>
    <rect x="200" y="60" width="100" height="120" fill="gray" stroke="black"/><text x="225" y="125">Core</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_dc_motor(): 
    svg = """<svg width="400" height="200"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">DC Motor</text>
    <circle cx="200" cy="100" r="50" fill="none" stroke="black" stroke-width="3"/><rect x="190" y="50" width="20" height="20" fill="red"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_ac_generator(): 
    svg = """<svg width="400" height="200"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">AC Generator</text>
    <circle cx="200" cy="100" r="50" fill="none" stroke="black" stroke-width="3"/><text x="180" y="105">Coil</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_cathode_ray_tube(): 
    svg = """<svg width="500" height="200"><text x="250" y="20" text-anchor="middle" font-size="16" font-weight="bold">Cathode Ray Tube</text>
    <ellipse cx="150" cy="100" rx="40" ry="80" fill="black"/><polygon points="190,100 400,50 400,150" fill="black"/><text x="250" y="120" fill="green">Electron Beam</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_nuclear_reactor(): 
    svg = """<svg width="400" height="200"><text x="200" y="20" text-anchor="middle" font-size="16" font-weight="bold">Nuclear Reactor</text>
    <rect x="150" y="60" width="100" height="100" fill="gray" stroke="black"/><text x="170" y="110">Core</text></svg>"""
    st.markdown(svg, unsafe_allow_html=True)

def draw_logic_gates(): 
    svg = """<svg width="500" height="150"><text x="250" y="20" text-anchor="middle" font-size="16" font-weight="bold">Logic Gates</text>
    <text x="60" y="50">AND</text><path d="M 80 40 L 100 40 A 10 10 0 0 1 100 60 L 80 60 Z" stroke="black" fill="none"/>
    <text x="180" y="50">OR</text><path d="M 200 40 Q 220 50 200 60" stroke="black" fill="none"/></svg>"""
    st.markdown(svg, unsafe_allow_html=True)
