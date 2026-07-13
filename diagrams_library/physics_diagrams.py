import streamlit as st
import re

# ========== S1 PHYSICS: 5 DIAGRAMS ==========
def s1_physics_refraction_prism():
    """S1: Refraction through Prism"""
    return """<svg width="450" height="240" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">REFRACTION THROUGH TRIANGULAR PRISM</text>
    <polygon points="100,200 225,40 350,200" fill="lightcyan" stroke="black" stroke-width="2"/>
    <defs><marker id="p1" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="red"/></marker></defs>
    <line x1="40" y1="110" x2="180" y2="115" stroke="red" stroke-width="2" marker-end="url(#p1)"/>
    <line x1="180" y1="115" x2="270" y2="185" stroke="red" stroke-width="2" marker-end="url(#p1)"/>
    <line x1="270" y1="185" x2="400" y2="175" stroke="red" stroke-width="2" marker-end="url(#p1)"/>
    <text x="225" y="220" text-anchor="middle" font-size="10" fill="#333">Principle: Refraction at 2 surfaces. Angle of deviation = i + e - A</text>
    </svg>"""

def s1_physics_convex_lens():
    return """<svg width="500" height="220" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="250" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">CONVEX LENS: REAL IMAGE</text>
    <ellipse cx="250" cy="110" rx="25" ry="80" fill="lightcyan" stroke="black" stroke-width="2"/>
    <line x1="40" y1="110" x2="460" y2="110" stroke="black" stroke-dasharray="4"/>
    <text x="180" y="125" text-anchor="middle" font-size="10">F</text><text x="320" y="125" text-anchor="middle" font-size="10">F</text>
    <text x="250" y="190" text-anchor="middle" font-size="10" fill="#333">Formula: 1/f = 1/u + 1/v. Principle: Refraction</text>
    </svg>"""

def s1_physics_concave_lens():
    return """<svg width="500" height="220" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="250" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">CONCAVE LENS: VIRTUAL IMAGE</text>
    <ellipse cx="250" cy="110" rx="25" ry="80" fill="lightcyan" stroke="black" stroke-width="2"/>
    <line x1="40" y1="110" x2="460" y2="110" stroke="black" stroke-dasharray="4"/>
    <text x="250" y="190" text-anchor="middle" font-size="10" fill="#333">Forms diminished, virtual, upright image</text>
    </svg>"""

def s1_physics_tir():
    return """<svg width="400" height="220" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="200" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">TOTAL INTERNAL REFLECTION</text>
    <rect x="50" y="80" width="300" height="80" fill="lightblue" stroke="black"/>
    <defs><marker id="p2" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="red"/></marker></defs>
    <line x1="200" y1="80" x2="320" y2="40" stroke="red" stroke-width="2" marker-end="url(#p2)"/>
    <text x="200" y="190" text-anchor="middle" font-size="10" fill="#333">Condition: i > Critical Angle. n1 > n2</text>
    </svg>"""

def s1_physics_rainbow():
    return """<svg width="450" height="220" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">RAINBOW FORMATION</text>
    <circle cx="225" cy="120" r="50" fill="none" stroke="black"/>
    <text x="225" y="190" text-anchor="middle" font-size="10" fill="#333">Dispersion + Internal Reflection + Refraction</text>
    </svg>"""

def s1_physics_simple_microscope():
    return """<svg width="300" height="220" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="150" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SIMPLE MICROSCOPE</text>
    <circle cx="150" cy="110" r="40" fill="lightcyan" stroke="black" stroke-width="2"/>
    <text x="150" y="190" text-anchor="middle" font-size="10" fill="#333">M = 1 + D/f. Object between F and 2F</text>
    </svg>"""

def s1_physics_compound_microscope():
    return """<svg width="500" height="220" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="250" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">COMPOUND MICROSCOPE</text>
    <text x="250" y="190" text-anchor="middle" font-size="10" fill="#333">M = Me x Mo. Objective + Eyepiece</text>
    </svg>"""

def s1_physics_telescope():
    return """<svg width="500" height="220" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="250" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">REFRACTING TELESCOPE</text>
    <text x="250" y="190" text-anchor="middle" font-size="10" fill="#333">M = fo/fe. Objective + Eyepiece</text>
    </svg>"""

def s1_physics_human_eye():
    return """<svg width="400" height="220" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="200" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">HUMAN EYE</text>
    <circle cx="200" cy="110" r="60" fill="white" stroke="black" stroke-width="2"/>
    <circle cx="200" cy="110" r="20" fill="black"/>
    <text x="200" y="190" text-anchor="middle" font-size="10" fill="#333">Lens, Retina, Optic Nerve</text>
    </svg>"""

# ========== S2 PHYSICS: 5 DIAGRAMS ==========
def s2_physics_wave_properties():
    return """<svg width="450" height="170" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">TRANSVERSE WAVE</text>
    <polyline points="0,85 25,60 50,85 75,110 100,85 125,60 150,85 175,110 200,85 225,60 250,85 275,110 300,85 325,60 350,85 375,110 400,85 425,110 450,85" fill="none" stroke="blue" stroke-width="2"/>
    <text x="225" y="145" text-anchor="middle" font-size="10" fill="#333">v = fλ. Amplitude, Wavelength, Frequency</text>
    </svg>"""

def s2_physics_sound_wave():
    return """<svg width="450" height="170" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">LONGITUDINAL SOUND WAVE</text>
    <text x="225" y="145" text-anchor="middle" font-size="10" fill="#333">Compressions and Rarefactions. v = 330 m/s in air</text>
    </svg>"""

def s2_physics_standing_wave():
    return """<svg width="450" height="170" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">STANDING WAVE</text>
    <text x="225" y="145" text-anchor="middle" font-size="10" fill="#333">Nodes and Antinodes. λ = 2L/n</text>
    </svg>"""

def s2_physics_doppler():
    return """<svg width="450" height="170" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">DOPPLER EFFECT</text>
    <text x="225" y="145" text-anchor="middle" font-size="10" fill="#333">f' = f(v±vo)/(v±vs). Pitch changes with motion</text>
    </svg>"""

def s2_physics_echo():
    return """<svg width="450" height="170" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">ECHO</text>
    <text x="225" y="145" text-anchor="middle" font-size="10" fill="#333">d = v*t/2. Reflection of sound</text>
    </svg>"""

# ========== S3 PHYSICS: 6 DIAGRAMS ==========
def s3_physics_electric_field():
    return """<svg width="350" height="220" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">ELECTRIC FIELD LINES</text>
    <circle cx="120" cy="110" r="10" fill="red"/><circle cx="230" cy="110" r="10" fill="blue"/>
    <text x="175" y="190" text-anchor="middle" font-size="10" fill="#333">E = F/Q. Lines N to S</text>
    </svg>"""

def s3_physics_magnetic_field():
    return """<svg width="350" height="220" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="175" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">MAGNETIC FIELD: CURRENT OUT</text>
    <circle cx="175" cy="110" r="6" fill="black"/>
    <circle cx="175" cy="110" r="35" fill="none" stroke="black" stroke-width="1.5"/>
    <circle cx="175" cy="110" r="70" fill="none" stroke="black" stroke-width="1.5"/>
    <text x="175" y="190" text-anchor="middle" font-size="10" fill="#333">Rule: Right Hand Grip Rule. B ∝ I/r</text>
    </svg>"""

def s3_physics_em_wave():
    return """<svg width="450" height="170" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">ELECTROMAGNETIC WAVE</text>
    <text x="225" y="145" text-anchor="middle" font-size="10" fill="#333">E ⊥ B ⊥ Direction. c = 3x10^8 m/s</text>
    </svg>"""

def s3_physics_series_circuit():
    return """<svg width="450" height="200" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SERIES CIRCUIT</text>
    <circle cx="90" cy="100" r="18" fill="yellow" stroke="black" stroke-width="2"/><text x="90" y="105" text-anchor="middle" font-size="10">V</text>
    <rect x="170" y="88" width="50" height="24" fill="white" stroke="black" stroke-width="2"/><text x="195" y="105" text-anchor="middle" font-size="10">R1</text>
    <rect x="270" y="88" width="50" height="24" fill="white" stroke="black" stroke-width="2"/><text x="295" y="105" text-anchor="middle" font-size="10">R2</text>
    <path d="M 90 100 L 170 100 L 220 100 L 270 100 L 320 100 L 360 100 L 360 130 L 90 130 L 90 100" fill="none" stroke="black" stroke-width="2"/>
    <text x="225" y="170" text-anchor="middle" font-size="10" fill="#333">Rule: Same I, Vt = V1 + V2, Rt = R1 + R2</text>
    </svg>"""

def s3_physics_parallel_circuit():
    return """<svg width="450" height="220" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="225" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">PARALLEL CIRCUIT</text>
    <circle cx="90" cy="110" r="18" fill="yellow" stroke="black" stroke-width="2"/><text x="90" y="115" text-anchor="middle" font-size="10">V</text>
    <rect x="170" y="60" width="50" height="24" fill="white" stroke="black" stroke-width="2"/><text x="195" y="77" text-anchor="middle" font-size="10">R1</text>
    <rect x="170" y="140" width="50" height="24" fill="white" stroke="black" stroke-width="2"/><text x="195" y="157" text-anchor="middle" font-size="10">R2</text>
    <path d="M 90 110 L 170 70 L 220 70 L 320 70 M 90 110 L 170 150 L 220 150 L 320 150 M 320 70 L 320 150" fill="none" stroke="black" stroke-width="2"/>
    <text x="225" y="190" text-anchor="middle" font-size="10" fill="#333">Rule: Same V, It = I1 + I2, 1/Rt = 1/R1 + 1/R2</text>
    </svg>"""

def s3_physics_transformer():
    return """<svg width="520" height="300" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="260" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SIMPLE TRANSFORMER</text>
    <rect x="150" y="70" width="220" height="120" fill="lightgray" stroke="black" stroke-width="2"/><text x="260" y="135" text-anchor="middle" font-size="10">Soft Iron Core</text>
    <circle cx="120" cy="130" r="30" fill="none" stroke="red" stroke-width="3"/><circle cx="120" cy="130" r="22" fill="none" stroke="red" stroke-width="2"/>
    <text x="120" y="135" text-anchor="middle" font-size="9">Np=100</text><text x="120" y="165" text-anchor="middle" font-size="9" fill="red">PRIMARY</text>
    <circle cx="400" cy="130" r="30" fill="none" stroke="blue" stroke-width="3"/><circle cx="400" cy="130" r="22" fill="none" stroke="blue" stroke-width="2"/>
    <text x="400" y="135" text-anchor="middle" font-size="9">Ns=400</text><text x="400" y="165" text-anchor="middle" font-size="9" fill="blue">SECONDARY</text>
    <text x="260" y="220" text-anchor="middle" font-size="10" fill="#333">Vs/Vp = Ns/Np = 400/100 = 4. Step-up Transformer</text>
    <text x="260" y="240" text-anchor="middle" font-size="10" fill="#333">Principle: Mutual Induction. VpIp = VsIs</text>
    </svg>"""

# ========== S4 PHYSICS: 4 DIAGRAMS ==========
def s4_physics_nuclear():
    return """<svg width="400" height="220" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="200" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">NUCLEAR FISSION</text>
    <text x="200" y="190" text-anchor="middle" font-size="10" fill="#333">E = mc². Chain Reaction</text>
    </svg>"""

def s4_physics_photoelectric():
    return """<svg width="400" height="220" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="200" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">PHOTOELECTRIC EFFECT</text>
    <text x="200" y="190" text-anchor="middle" font-size="10" fill="#333">hf = φ + KE. Einstein Equation</text>
    </svg>"""

def s4_physics_solar_eclipse():
    return """<svg width="500" height="220" style="background:white; border:2px solid #333; border-radius:8px; font-family:Arial;">
    <text x="250" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="black">SOLAR ECLIPSE</text>
    <text x="250" y="190" text-anchor="middle" font-size="10" fill="#333">Sun - Moon - Earth in straight line</text>
    </svg>"""

def get_physics_diagram(question):
    q = question.lower()

    # S1
    if "refraction" in q and "prism" in q: return s1_physics_refraction_prism()
    if "convex lens" in q: return s1_physics_convex_lens()
    if "concave lens" in q: return s1_physics_concave_lens()
    if "total internal reflection" in q or "tir" in q: return s1_physics_tir()
    if "rainbow" in q: return s1_physics_rainbow()
    if "simple microscope" in q: return s1_physics_simple_microscope()
    if "compound microscope" in q: return s1_physics_compound_microscope()
    if "telescope" in q: return s1_physics_telescope()
    if "eye" in q and "diagram" in q: return s1_physics_human_eye()

    # S2
    if "wave" in q and "properties" in q: return s2_physics_wave_properties()
    if "sound wave" in q: return s2_physics_sound_wave()
    if "standing wave" in q: return s2_physics_standing_wave()
    if "doppler" in q: return s2_physics_doppler()
    if "echo" in q: return s2_physics_echo()

    # S3
    if "electric field" in q: return s3_physics_electric_field()
    if "magnetic field" in q: return s3_physics_magnetic_field()
    if "em wave" in q or "electromagnetic" in q: return s3_physics_em_wave()
    if "circuit" in q and "series" in q: return s3_physics_series_circuit()
    if "circuit" in q and "parallel" in q: return s3_physics_parallel_circuit()
    if "transformer" in q: return s3_physics_transformer()

    # S4
    if "nuclear" in q or "atom" in q: return s4_physics_nuclear()
    if "photoelectric" in q: return s4_physics_photoelectric()
    if "solar eclipse" in q: return s4_physics_solar_eclipse()

    return None

import re # COLUMN 0

def calculate_physics(question):
    """UNEB Physics calculator S1-S4. Returns formatted string or None"""
    q = question.lower()
    nums = [float(n) for n in re.findall(r"[-+]?\d*\.?\d+", question)]

    # SPEED = DIST/TIME
    if "speed" in q or "velocity" in q:
        if len(nums) >= 2:
            d, t = nums[0], nums[1]
            ans = d / t
            return f"**Formula**: $v = d/t$\n**Working**: ${d} / {t} = {ans:.2f}$\n**Answer**: {ans:.2f} m/s"

    # FORCE = MA
    if "force" in q:
        if len(nums) >= 2:
            m, a = nums[0], nums[1]
            ans = m * a
            return f"**Formula**: $F = ma$\n**Working**: ${m} * {a} = {ans:.2f}$\n**Answer**: {ans:.2f} N"

    # OHM'S LAW
    if "current" in q or "voltage" in q or "resistance" in q:
        if len(nums) >= 2:
            if "voltage" in q and "current" in q:
                v, i = nums[0], nums[1]
                r = v / i
                return f"**Formula**: $R = V/I$\n**Working**: ${v} / {i} = {r:.2f}$\n**Answer**: {r:.2f} Ω"

    # WORK = F*D
    if "work" in q:
        if len(nums) >= 2:
            f, d = nums[0], nums[1]
            w = f * d
            return f"**Formula**: $W = Fd$\n**Working**: ${f} * {d} = {w:.2f}$\n**Answer**: {w:.2f} J"

    # POWER = W/T
    if "power" in q:
        if len(nums) >= 2:
            w, t = nums[0], nums[1]
            p = w / t
            return f"**Formula**: $P = W/t$\n**Working**: ${w} / {t} = {p:.2f}$\n**Answer**: {p:.2f} W"

    return None
