import streamlit as st

# ========== S1 PHYSICS: 6 DIAGRAMS ==========
def s1_physics_circuit():
    """S1 Physics 1: Simple Electric Circuit"""
    return """<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
    <line x1="50" y1="100" x2="120" y2="100" stroke="black" stroke-width="2"/>
    <line x1="120" y1="90" x2="120" y2="110" stroke="black" stroke-width="3"/>
    <line x1="130" y1="95" x2="130" y2="105" stroke="black" stroke-width="2"/>
    <text x="115" y="80" font-size="12" font-family="Arial">Cell</text>
    <line x1="130" y1="100" x2="200" y2="100" stroke="black" stroke-width="2"/>
    <rect x="200" y="90" width="40" height="20" fill="none" stroke="black" stroke-width="2"/>
    <text x="205" y="85" font-size="12">Bulb</text>
    <line x1="240" y1="100" x2="310" y2="100" stroke="black" stroke-width="2"/>
    <line x1="310" y1="100" x2="310" y2="150" stroke="black" stroke-width="2"/>
    <line x1="310" y1="150" x2="50" y2="150" stroke="black" stroke-width="2"/>
    <line x1="50" y1="150" x2="50" y2="100" stroke="black" stroke-width="2"/>
    <text x="180" y="170" font-size="14" text-anchor="middle">Simple Electric Circuit</text>
    </svg>"""

def s1_physics_dist_time_graph():
    """S1 Physics 2: Distance-Time Graph"""
    return """<svg width="400" height="250">
    <line x1="50" y1="200" x2="350" y2="200" stroke="black" stroke-width="2"/>
    <line x1="50" y1="200" x2="50" y2="50" stroke="black" stroke-width="2"/>
    <text x="30" y="40" font-size="12">Distance</text>
    <text x="360" y="205" font-size="12">Time</text>
    <line x1="50" y1="200" x2="150" y2="120" stroke="blue" stroke-width="2"/>
    <line x1="150" y1="120" x2="250" y2="120" stroke="red" stroke-width="2"/>
    <line x1="250" y1="120" x2="350" y2="50" stroke="green" stroke-width="2"/>
    <text x="100" y="110" font-size="10" fill="blue">Uniform</text>
    <text x="200" y="110" font-size="10" fill="red">Rest</text>
    <text x="300" y="40" font-size="10" fill="green">Accelerated</text>
    </svg>"""

def s1_physics_wave():
    """S1 Physics 3: Transverse Wave"""
    return """<svg width="400" height="150">
    <path d="M 50 75 Q 75 25 100 75 T 150 75 T 200 75 T 250 75 T 300 75 T 350 75" fill="none" stroke="black" stroke-width="2"/>
    <line x1="100" y1="75" x2="100" y2="25" stroke="black" stroke-dasharray="2,2"/>
    <text x="95" y="20" font-size="12">Amplitude</text>
    <line x1="100" y1="75" x2="200" y2="75" stroke="black"/>
    <text x="145" y="90" font-size="12">Wavelength λ</text>
    <text x="180" y="120" font-size="14" text-anchor="middle">Transverse Wave</text>
    </svg>"""

def s1_physics_reflection():
    """S1 Physics 4: Reflection on Plane Mirror"""
    return """<svg width="400" height="200">
    <line x1="200" y1="50" x2="200" y2="150" stroke="black" stroke-width="3"/>
    <text x="205" y="40" font-size="12">Plane Mirror</text>
    <line x1="100" y1="80" x2="200" y2="100" stroke="black" stroke-width="2" marker-end="url(#a1)"/>
    <line x1="200" y1="100" x2="300" y2="120" stroke="black" stroke-width="2" marker-end="url(#a1)"/>
    <text x="80" y="75" font-size="12">Incident Ray</text>
    <text x="310" y="125" font-size="12">Reflected Ray</text>
    <text x="200" y="180" font-size="14" text-anchor="middle">Law of Reflection</text>
    <defs><marker id="a1"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs>
    </svg>"""

def s1_physics_force():
    """S1 Physics 5: Balanced Forces"""
    return """<svg width="400" height="150">
    <rect x="180" y="70" width="40" height="40" fill="lightgray" stroke="black"/>
    <line x1="180" y1="90" x2="130" y2="90" stroke="red" stroke-width="3" marker-end="url(#a2)"/>
    <line x1="220" y1="90" x2="270" y2="90" stroke="blue" stroke-width="3" marker-end="url(#a2)"/>
    <text x="100" y="85" font-size="12">5N</text>
    <text x="280" y="85" font-size="12">5N</text>
    <text x="200" y="130" font-size="14" text-anchor="middle">Balanced Forces</text>
    <defs><marker id="a2"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs>
    </svg>"""

def s1_physics_lever():
    """S1 Physics 6: 1st Class Lever"""
    return """<svg width="400" height="180">
    <line x1="50" y1="100" x2="350" y2="100" stroke="black" stroke-width="3"/>
    <polygon points="200,90 210,110 190,110" fill="black"/>
    <text x="195" y="125" font-size="12">Fulcrum</text>
    <circle cx="100" cy="100" r="8" fill="black"/>
    <text x="90" y="85" font-size="12">Effort</text>
    <circle cx="300" cy="100" r="8" fill="black"/>
    <text x="295" y="85" font-size="12">Load</text>
    <text x="200" y="150" font-size="14" text-anchor="middle">1st Class Lever</text>
    </svg>"""

# ========== S2 PHYSICS: 6 DIAGRAMS ==========
def s2_physics_convex_lens():
    """S2 Physics 1: Convex Lens Ray Diagram"""
    return """<svg width="400" height="200">
    <line x1="200" y1="50" x2="200" y2="150" stroke="black" stroke-width="2"/>
    <path d="M 190 50 Q 200 100 190 150" fill="none" stroke="black"/>
    <path d="M 210 50 Q 200 100 210 150" fill="none" stroke="black"/>
    <text x="205" y="40" font-size="12">Convex Lens</text>
    <line x1="50" y1="100" x2="350" y2="100" stroke="gray" stroke-dasharray="2,2"/>
    <circle cx="100" cy="100" r="3" fill="red"/>
    <circle cx="300" cy="100" r="3" fill="red"/>
    <text x="90" y="90" font-size="12">Object</text>
    <text x="310" y="90" font-size="12">Image</text>
    </svg>"""

def s2_physics_pulley():
    """S2 Physics 2: Single Pulley System"""
    return """<svg width="300" height="250">
    <circle cx="150" cy="50" r="30" fill="none" stroke="black" stroke-width="2"/>
    <line x1="150" y1="20" x2="150" y2="10" stroke="black" stroke-width="2"/>
    <line x1="120" y1="50" x2="120" y2="150" stroke="black"/>
    <line x1="180" y1="50" x2="180" y2="150" stroke="black"/>
    <rect x="110" y="150" width="20" height="20" fill="gray"/>
    <rect x="170" y="150" width="20" height="20" fill="gray"/>
    <text x="140" y="30" font-size="12">Fixed Pulley</text>
    </svg>"""

def s2_physics_thermometer():
    """S2 Physics 3: Clinical Thermometer"""
    return """<svg width="100" height="250">
    <rect x="40" y="50" width="20" height="150" fill="none" stroke="black" stroke-width="2"/>
    <circle cx="50" cy="210" r="20" fill="red" stroke="black"/>
    <rect x="45" y="70" width="10" height="130" fill="red"/>
    <text x="65" y="80" font-size="12">°C</text>
    <text x="20" y="220" font-size="12">Mercury</text>
    <text x="50" y="240" font-size="14" text-anchor="middle">Thermometer</text>
    </svg>"""

def s2_physics_magnet():
    """S2 Physics 4: Magnetic Field Lines"""
    return """<svg width="400" height="200">
    <rect x="100" y="90" width="60" height="20" fill="red"/>
    <rect x="240" y="90" width="60" height="20" fill="blue"/>
    <text x="110" y="85" font-size="12">N</text>
    <text x="260" y="85" font-size="12">S</text>
    <path d="M 160 100 Q 200 60 240 100" fill="none" stroke="black"/>
    <path d="M 160 100 Q 200 140 240 100" fill="none" stroke="black"/>
    <text x="180" y="50" font-size="14" text-anchor="middle">Magnetic Field</text>
    </svg>"""

def s2_physics_density():
    """S2 Physics 5: Density Column"""
    return """<svg width="200" height="250">
    <rect x="50" y="50" width="100" height="150" fill="none" stroke="black" stroke-width="2"/>
    <rect x="50" y="150" width="100" height="50" fill="blue"/>
    <rect x="50" y="100" width="100" height="50" fill="yellow"/>
    <rect x="50" y="50" width="100" height="50" fill="red"/>
    <text x="10" y="75" font-size="12">Oil</text>
    <text x="10" y="125" font-size="12">Water</text>
    <text x="10" y="175" font-size="12">Mercury</text>
    </svg>"""

def s2_physics_oscillation():
    """S2 Physics 6: Simple Pendulum"""
    return """<svg width="400" height="150">
    <line x1="200" y1="50" x2="200" y2="100" stroke="black" stroke-width="2"/>
    <circle cx="200" cy="120" r="10" fill="black"/>
    <path d="M 150 120 Q 200 70 250 120" fill="none" stroke="black" stroke-dasharray="2,2"/>
    <text x="190" y="140" font-size="14" text-anchor="middle">Simple Pendulum</text>
    </svg>"""

# ========== S3 PHYSICS: 6 DIAGRAMS ==========
def s3_physics_transformer():
    """S3 Physics 1: Simple Transformer"""
    return """<svg width="400" height="200">
    <rect x="100" y="70" width="40" height="60" fill="none" stroke="black"/>
    <rect x="260" y="70" width="40" height="60" fill="none" stroke="black"/>
    <text x="105" y="65" font-size="12">Primary</text>
    <text x="265" y="65" font-size="12">Secondary</text>
    <line x1="50" y1="100" x2="100" y2="100" stroke="black"/>
    <line x1="300" y1="100" x2="350" y2="100" stroke="black"/>
    <text x="20" y="105" font-size="12">AC Input</text>
    <text x="355" y="105" font-size="12">AC Output</text>
    </svg>"""

def s3_physics_cathode_ray():
    """S3 Physics 2: Cathode Ray Tube"""
    return """<svg width="400" height="200">
    <ellipse cx="100" cy="100" rx="80" ry="40" fill="none" stroke="black" stroke-width="2"/>
    <line x1="180" y1="100" x2="320" y2="100" stroke="black"/>
    <rect x="320" y="80" width="30" height="40" fill="lightgreen" stroke="black"/>
    <circle cx="40" cy="100" r="3" fill="black"/>
    <text x="35" y="115" font-size="12">Cathode</text>
    <text x="90" y="40" font-size="14">Cathode Ray Tube</text>
    <text x="325" y="75" font-size="12">Screen</text>
    </svg>"""

def s3_physics_radioactive():
    """S3 Physics 3: Alpha, Beta, Gamma Rays"""
    return """<svg width="400" height="200">
    <rect x="50" y="50" width="300" height="100" fill="none" stroke="black"/>
    <line x1="80" y1="50" x2="80" y2="150" stroke="red" stroke-width="2"/>
    <line x1="120" y1="50" x2="120" y2="150" stroke="green" stroke-width="2"/>
    <line x1="160" y1="50" x2="160" y2="150" stroke="blue" stroke-width="2"/>
    <text x="70" y="40" font-size="12" fill="red">Alpha</text>
    <text x="105" y="40" font-size="12" fill="green">Beta</text>
    <text x="150" y="40" font-size="12" fill="blue">Gamma</text>
    <text x="200" y="180" font-size="14" text-anchor="middle">Penetrating Power</text>
    </svg>"""

def s3_physics_generator():
    """S3 Physics 4: AC Generator"""
    return """<svg width="400" height="200">
    <circle cx="200" cy="100" r="50" fill="none" stroke="black" stroke-width="2"/>
    <line x1="150" y1="100" x2="250" y2="100" stroke="black" stroke-width="3"/>
    <rect x="190" y="40" width="20" height="20" fill="red"/>
    <rect x="190" y="140" width="20" height="20" fill="blue"/>
    <text x="185" y="35" font-size="12">N</text>
    <text x="185" y="165" font-size="12">S</text>
    <line x1="100" y1="100" x2="70" y2="100" stroke="black"/>
    <line x1="300" y1="100" x2="330" y2="100" stroke="black"/>
    <text x="60" y="105" font-size="12">Slip Rings</text>
    <text x="200" y="180" font-size="14" text-anchor="middle">AC Generator</text>
    </svg>"""

def s3_physics_refraction():
    """S3 Physics 5: Refraction of Light"""
    return """<svg width="400" height="200">
    <line x1="0" y1="100" x2="400" y2="100" stroke="black"/>
    <text x="190" y="95" font-size="12">Air</text>
    <text x="190" y="120" font-size="12">Water</text>
    <line x1="100" y1="50" x2="200" y2="100" stroke="black" marker-end="url(#a3)"/>
    <line x1="200" y1="100" x2="250" y2="150" stroke="black" marker-end="url(#a3)"/>
    <text x="90" y="40" font-size="12">Incident</text>
    <text x="255" y="170" font-size="12">Refracted</text>
    <defs><marker id="a3"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs>
    </svg>"""

def s3_physics_solar_system():
    """S3 Physics 6: Solar System Inner Planets"""
    return """<svg width="400" height="200">
    <circle cx="200" cy="100" r="20" fill="yellow"/>
    <circle cx="260" cy="100" r="5" fill="blue"/>
    <circle cx="310" cy="100" r="8" fill="red"/>
    <circle cx="350" cy="100" r="6" fill="gray"/>
    <text x="195" y="50" font-size="12">Sun</text>
    <text x="255" y="85" font-size="12">Earth</text>
    <text x="305" y="85" font-size="12">Mars</text>
    </svg>"""

# ========== S4 PHYSICS: 6 DIAGRAMS - UPDATED ==========
def s4_physics_nuclear():
    """S4 Physics 1: Atomic Nucleus"""
    return """<svg width="400" height="200">
    <circle cx="200" cy="100" r="30" fill="none" stroke="black" stroke-width="2"/>
    <circle cx="185" cy="90" r="3" fill="blue"/>
    <circle cx="215" cy="90" r="3" fill="red"/>
    <circle cx="190" cy="110" r="3" fill="red"/>
    <circle cx="210" cy="110" r="3" fill="blue"/>
    <text x="180" y="110" font-size="12">n</text>
    <text x="210" y="110" font-size="12">p</text>
    <text x="200" y="150" font-size="14" text-anchor="middle">Atomic Nucleus</text>
    </svg>"""

def s4_physics_diode():
    """S4 Physics 2: Diode Circuit Symbol"""
    return """<svg width="300" height="150">
    <polygon points="120,50 180,75 120,100" fill="black"/>
    <line x1="180" y1="50" x2="180" y2="100" stroke="black" stroke-width="3"/>
    <line x1="80" y1="75" x2="120" y2="75" stroke="black" stroke-width="2"/>
    <line x1="180" y1="75" x2="220" y2="75" stroke="black" stroke-width="2"/>
    <text x="110" y="110" font-size="14" text-anchor="middle">Diode</text>
    </svg>"""

def s4_physics_cro():
    """S4 Physics 3: Cathode Ray Oscilloscope"""
    return """<svg width="400" height="200">
    <rect x="50" y="50" width="300" height="100" fill="black" stroke="gray" stroke-width="2"/>
    <path d="M 60 100 Q 100 50 140 100 T 220 100 T 300 100 T 340 100" fill="none" stroke="green" stroke-width="2"/>
    <rect x="360" y="70" width="20" height="60" fill="gray"/>
    <text x="200" y="170" font-size="14" text-anchor="middle">CRO Waveform Display</text>
    <text x="365" y="65" font-size="10">Controls</text>
    </svg>"""

def s4_physics_solar_eclipse():
    """S4 Physics 4: Solar Eclipse"""
    return """<svg width="400" height="200">
    <circle cx="80" cy="100" r="30" fill="yellow" stroke="orange" stroke-width="2"/>
    <circle cx="200" cy="100" r="10" fill="gray" stroke="black"/>
    <circle cx="320" cy="100" r="20" fill="blue" stroke="black"/>
    <line x1="110" y1="100" x2="190" y2="100" stroke="black" stroke-dasharray="2,2"/>
    <line x1="210" y1="100" x2="300" y2="100" stroke="black" stroke-dasharray="2,2"/>
    <text x="70" y="50" font-size="12">Sun</text>
    <text x="190" y="85" font-size="12">Moon</text>
    <text x="315" y="70" font-size="12">Earth</text>
    <text x="200" y="170" font-size="14" text-anchor="middle">Solar Eclipse</text>
    </svg>"""

def s4_physics_photoelectric():
    """S4 Physics 5: Photoelectric Effect"""
    return """<svg width="400" height="200">
    <rect x="100" y="80" width="60" height="40" fill="yellow" stroke="black"/>
    <line x1="50" y1="100" x2="100" y2="100" stroke="black" marker-end="url(#a4)"/>
    <circle cx="200" cy="100" r="5" fill="black"/>
    <line x1="160" y1="100" x2="195" y2="100" stroke="black" stroke-dasharray="2,2"/>
    <text x="95" y="70" font-size="12">Metal Plate</text>
    <text x="40" y="90" font-size="12">Light</text>
    <text x="210" y="105" font-size="12">e-</text>
    <text x="200" y="170" font-size="14" text-anchor="middle">Photoelectric Effect</text>
    <defs><marker id="a4"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs>
    </svg>"""

def s4_physics_transformer_detail():
    """S4 Physics 6: Step-up Transformer Coils"""
    return """<svg width="400" height="200">
    <rect x="120" y="60" width="160" height="80" fill="none" stroke="black"/>
    <path d="M 130 60 Q 130 40 150 40 Q 170 40 170 60" fill="none" stroke="black"/>
    <path d="M 130 140 Q 130 160 150 160 Q 170 160 170 140" fill="none" stroke="black"/>
    <path d="M 230 60 Q 230 30 250 30 Q 270 30 270 60 Q 270 90 250 90 Q 230 90 230 60" fill="none" stroke="black"/>
    <path d="M 230 140 Q 230 170 250 170 Q 270 170 270 140 Q 270 110 250 110 Q 230 110 230 140" fill="none" stroke="black"/>
    <text x="115" y="50" font-size="12">Few Turns</text>
    <text x="275" y="50" font-size="12">Many Turns</text>
    <text x="200" y="180" font-size="14" text-anchor="middle">Step-up Transformer</text>
    </svg>"""
     from . import physics_diagrams as pd

def get_physics_diagram(question):
    """Auto-pick SVG based on keywords. Returns SVG string or None"""
    q = question.lower()
    
    # S1
    if "circuit" in q or "bulb" in q or "cell" in q: 
        return pd.s1_physics_circuit()
    if "distance time" in q or "speed graph" in q: 
        return pd.s1_physics_dist_time_graph()
    if "wave" in q or "amplitude" in q or "wavelength" in q: 
        return pd.s1_physics_wave()
    if "reflection" in q or "mirror" in q or "incident ray" in q: 
        return pd.s1_physics_reflection()
    if "force" in q or "balanced" in q or "5n" in q: 
        return pd.s1_physics_force()
    if "lever" in q or "fulcrum" in q: 
        return pd.s1_physics_lever()
    
    # S2
    if "lens" in q or "convex" in q or "image" in q: 
        return pd.s2_physics_convex_lens()
    if "pulley" in q: 
        return pd.s2_physics_pulley()
    if "thermometer" in q or "temperature" in q: 
        return pd.s2_physics_thermometer()
    if "magnet" in q or "magnetic field" in q: 
        return pd.s2_physics_magnet()
    if "density" in q: 
        return pd.s2_physics_density()
    if "pendulum" in q or "oscillation" in q: 
        return pd.s2_physics_oscillation()
    
    # S3
    if "transformer" in q: 
        return pd.s3_physics_transformer()
    if "cathode ray tube" in q or "crt" in q: 
        return pd.s3_physics_cathode_ray()
    if "alpha" in q or "beta" in q or "gamma" in q: 
        return pd.s3_physics_radioactive()
    if "generator" in q or "ac generator" in q: 
        return pd.s3_physics_generator()
    if "refraction" in q: 
        return pd.s3_physics_refraction()
    if "solar system" in q or "planet" in q: 
        return pd.s3_physics_solar_system()
    
    # S4
    if "nucleus" in q or "proton neutron" in q: 
        return pd.s4_physics_nuclear()
    if "diode" in q: 
        return pd.s4_physics_diode()
    if "cro" in q or "oscilloscope" in q or "waveform" in q: 
        return pd.s4_physics_cro()
    if "solar eclipse" in q or "moon between sun" in q: 
        return pd.s4_physics_solar_eclipse()
    if "photoelectric" in q: 
        return pd.s4_physics_photoelectric()
    if "step up transformer" in q: 
        return pd.s4_physics_transformer_detail()
    
    return None
