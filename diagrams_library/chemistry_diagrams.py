import streamlit as st
import re

# ========== S1 CHEMISTRY: 6 DIAGRAMS ==========
def s1_chem_bunsen():
    """S1: Bunsen Burner - All parts"""
    return """<svg width="220" height="260"><rect x="90" y="160" width="40" height="80" fill="#757575"/><rect x="95" y="150" width="30" height="10" fill="black"/><path d="M 100 150 Q 110 130 120 150" fill="#FFA726"/><line x1="110" y1="150" x2="110" y2="120" stroke="black" stroke-dasharray="2,2"/><text x="85" y="250" font-size="12">Bunsen Burner</text><text x="130" y="145" font-size="10">Flame</text></svg>"""

def s1_chem_beaker(): return """<svg width="160" height="210"><path d="M 50 60 L 40 160 L 120 160 L 110 60 Z" fill="none" stroke="black" stroke-width="2"/><line x1="40" y1="160" x2="120" y2="160" stroke="black"/><text x="55" y="180" font-size="12">Beaker</text></svg>"""
def s1_chem_water_molecule(): return """<svg width="220" height="160"><circle cx="110" cy="90" r="15" fill="#F44336"/><circle cx="80" cy="120" r="10" fill="white" stroke="black"/><circle cx="140" cy="120" r="10" fill="white" stroke="black"/><line x1="100" y1="100" x2="85" y2="115" stroke="black"/><line x1="120" y1="100" x2="135" y2="115" stroke="black"/><text x="105" y="95" font-size="12">O</text><text x="75" y="125" font-size="12">H</text><text x="135" y="125" font-size="12">H</text></svg>"""
def s1_chem_filtration(): return """<svg width="220" height="260"><polygon points="110,60 70,130 150,130" fill="none" stroke="black"/><rect x="100" y="130" width="20" height="80" fill="none" stroke="black"/><text x="90" y="50" font-size="12">Filter Funnel</text></svg>"""
def s1_chem_flame_test(): return """<svg width="220" height="210"><rect x="90" y="130" width="40" height="60" fill="#757575"/><path d="M 100 130 Q 110 110 120 130" fill="#FFEB3B"/><text x="85" y="200" font-size="12">Flame Test</text></svg>"""
def s1_chem_safety(): return """<svg width="220" height="160"><circle cx="110" cy="80" r="50" fill="none" stroke="#D32F2F" stroke-width="3"/><line x1="75" y1="45" x2="145" y2="115" stroke="#D32F2F" stroke-width="3"/></svg>"""

# ========== S2 CHEMISTRY: 6 DIAGRAMS ==========
def s2_chem_titration(): return """<svg width="220" height="260"><rect x="100" y="40" width="20" height="100" fill="#616161"/><circle cx="110" cy="160" r="40" fill="none" stroke="black"/><line x1="110" y1="140" x2="110" y2="160" stroke="black"/><text x="80" y="30" font-size="12">Burette</text></svg>"""
def s2_chem_co2(): return """<svg width="220" height="110"><circle cx="60" cy="55" r="10" fill="black"/><circle cx="110" cy="55" r="15" fill="#9E9E9E"/><circle cx="160" cy="55" r="10" fill="black"/><line x1="70" y1="55" x2="95" y2="55" stroke="black"/><line x1="125" y1="55" x2="150" y2="55" stroke="black"/></svg>"""
def s2_chem_electrolysis(): return """<svg width="320" height="210"><rect x="60" y="60" width="200" height="100" fill="none" stroke="black"/><rect x="100" y="50" width="10" height="20" fill="black"/><rect x="210" y="50" width="10" height="20" fill="black"/><text x="95" y="40" font-size="12">Cathode</text><text x="205" y="40" font-size="12">Anode</text></svg>"""
def s2_chem_distillation(): return """<svg width="320" height="210"><circle cx="110" cy="110" r="40" fill="none" stroke="black"/><line x1="150" y1="110" x2="210" y2="110" stroke="black"/><rect x="210" y="90" width="60" height="40" fill="none" stroke="black"/></svg>"""
def s2_chem_ph(): return """<svg width="320" height="110"><rect x="30" y="60" width="260" height="20" fill="#F44336"/><rect x="80" y="60" width="40" height="20" fill="#FF9800"/><rect x="140" y="60" width="40" height="20" fill="#4CAF50"/><text x="20" y="55" font-size="12">1</text><text x="270" y="55" font-size="12">14</text></svg>"""
def s2_chem_atom(): return """<svg width="220" height="220"><circle cx="110" cy="110" r="10" fill="black"/><circle cx="110" cy="110" r="40" fill="none" stroke="gray"/><circle cx="110" cy="110" r="70" fill="none" stroke="gray"/><circle cx="150" cy="110" r="3" fill="#2196F3"/><circle cx="110" cy="40" r="3" fill="#2196F3"/></svg>"""

# ========== S3 CHEMISTRY: 6 DIAGRAMS ==========
def s3_chem_haber(): return """<svg width="320" height="160"><rect x="60" y="70" width="200" height="40" fill="#757575"/><text x="130" y="95" font-size="12">Fe Catalyst</text><text x="50" y="60" font-size="11">N2 + 3H2</text><text x="240" y="120" font-size="11">2NH3</text></svg>"""
def s3_chem_cell(): return """<svg width="320" height="210"><rect x="60" y="90" width="60" height="60" fill="#E0E0E0"/><rect x="200" y="90" width="60" height="60" fill="#E0E0E0"/><line x1="120" y1="120" x2="200" y2="120" stroke="black" stroke-dasharray="2,2"/><text x="70" y="80" font-size="12">Zn</text><text x="215" y="80" font-size="12">Cu</text></svg>"""
def s3_chem_organic(): return """<svg width="220" height="160"><line x1="60" y1="80" x2="160" y2="80" stroke="black"/><line x1="60" y1="80" x2="60" y2="50" stroke="black"/><line x1="160" y1="80" x2="160" y2="50" stroke="black"/><text x="55" y="45" font-size="12">OH</text><text x="155" y="45" font-size="12">OH</text></svg>"""
def s3_chem_chromatography(): return """<svg width="220" height="260"><rect x="90" y="60" width="40" height="150" fill="#FFFDE7" stroke="black"/><circle cx="110" cy="190" r="3" fill="#F44336"/><circle cx="110" cy="170" r="3" fill="#2196F3"/></svg>"""
def s3_chem_periodic(): return """<svg width="420" height="160"><rect x="30" y="30" width="30" height="30" stroke="black"/><rect x="70" y="30" width="30" height="30" stroke="black"/><rect x="110" y="60" width="30" height="30" stroke="black"/><text x="35" y="50" font-size="12">H</text><text x="75" y="50" font-size="12">He</text><text x="115" y="80" font-size="12">Li</text></svg>"""
def s3_chem_reaction(): return """<svg width="320" height="110"><defs><marker id="c" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs><text x="30" y="55" font-size="12">A + B</text><line x1="90" y1="55" x2="130" y2="55" stroke="black" marker-end="url(#c)"/><text x="150" y="55" font-size="12">C + D</text></svg>"""

# ========== S4 CHEMISTRY: 6 DIAGRAMS ==========
def s4_chem_benzene(): return """<svg width="220" height="220"><polygon points="110,50 150,70 150,110 110,130 70,110 70,70" fill="none" stroke="black"/><polygon points="110,60 140,75 140,105 110,120 80,105 80,75" fill="none" stroke="black"/></svg>"""
def s4_chem_polymer(): return """<svg width="320" height="110"><rect x="60" y="50" width="200" height="20" fill="none" stroke="black"/><line x1="80" y1="50" x2="80" y2="40" stroke="black"/><line x1="120" y1="50" x2="120" y2="40" stroke="black"/><line x1="160" y1="50" x2="160" y2="40" stroke="black"/></svg>"""
def s4_chem_spectrometer(): return """<svg width="320" height="210"><rect x="60" y="60" width="200" height="100" fill="none" stroke="black"/><path d="M 110 60 L 160 30 L 210 60" fill="none" stroke="black"/><text x="130" y="40" font-size="12">Prism</text></svg>"""
def s4_chem_industrial(): return """<svg width="320" height="210"><rect x="60" y="90" width="200" height="60" fill="#9E9E9E"/><rect x="80" y="50" width="20" height="40" fill="#616161"/><rect x="220" y="50" width="20" height="40" fill="#616161"/></svg>"""
def s4_chem_env(): return """<svg width="320" height="210"><circle cx="160" cy="110" r="60" fill="#B3E5FC"/><path d="M 130 80 Q 160 60 190 80" fill="#757575"/></svg>"""
def s4_chem_research(): return """<svg width="220" height="220"><rect x="60" y="60" width="100" height="100" fill="white" stroke="black"/><circle cx="110" cy="110" r="20" fill="none" stroke="#2196F3"/></svg>"""

def get_chemistry_diagram(question):
    q = question.lower()

    # S1
    if "bunsen" in q: return s1_chem_bunsen()
    if "beaker" in q: return s1_chem_beaker()
    if "water molecule" in q or "h2o" in q: return s1_chem_water_molecule()
    if "filtration" in q: return s1_chem_filtration()
    if "flame test" in q: return s1_chem_flame_test()

    # S2
    if "titration" in q or "burette" in q: return s2_chem_titration()
    if "co2" in q or "carbon dioxide" in q: return s2_chem_co2()
    if "electrolysis" in q: return s2_chem_electrolysis()
    if "distillation" in q: return s2_chem_distillation()
    if "ph scale" in q: return s2_chem_ph()
    if "atom" in q: return s2_chem_atom()

    # S3
    if "haber" in q or "ammonia" in q: return s3_chem_haber()
    if "voltaic cell" in q or "electrochemical cell" in q: return s3_chem_cell()
    if "organic" in q or "ethane" in q: return s3_chem_organic()
    if "chromatography" in q: return s3_chem_chromatography()
    if "periodic table" in q: return s3_chem_periodic()
    if "reaction" in q: return s3_chem_reaction()

    # S4
    if "benzene" in q: return s4_chem_benzene()
    if "polymer" in q: return s4_chem_polymer()
    if "spectrometer" in q: return s4_chem_spectrometer()
    if "industrial" in q: return s4_chem_industrial()
    if "pollution" in q or "environment" in q: return s4_chem_env()

    return None

import re # <- NOW AT COLUMN 0

def calculate_chemistry(question):
    """UNEB Chemistry calculator S1-S4. Returns formatted string or None"""
    q = question.lower()
    nums = [float(n) for n in re.findall(r'\d+\.?\d*', question)]

    # MOLES = MASS / MR
    if "mole" in q or "moles" in q:
        if "mass" in q and len(nums) >= 2:
            mass, mr = nums[0], nums[1]
            ans = mass / mr
            return f"**Formula**: $n = \\frac{{Mass}}{{Mr}}$\n**Working**: ${mass} / {mr} = {ans:.3f}$\n**Answer**: {ans:.3f} moles"

    # MOLARITY = MOLES / VOLUME
    if "molarity" in q or "concentration" in q:
        if len(nums) >= 2:
            moles, vol_cm3 = nums[0], nums[1]
            vol_dm3 = vol_cm3 / 1000
            ans = moles / vol_dm3
            return f"**Formula**: $C = \\frac{{n}}{{V}}$\n**Working**: ${moles} / {vol_dm3} = {ans:.2f}$\n**Answer**: {ans:.2f} mol/dm³"

    # GAS LAW: P1V1 = P2V2
    if "gas" in q or "boyle" in q or "pressure" in q:
        if len(nums) >= 3:
            p1, v1, p2 = nums[0], nums[1], nums[2]
            v2 = (p1 * v1) / p2
            return f"**Formula**: $P1V1 = P2V2$\n**Working**: ${p1} * {v1} / {p2} = {v2:.2f}$\n**Answer**: {v2:.2f} L"

    # PH = -LOG[H+]
    if "ph" in q:
        if len(nums) >= 1:
            h = nums[0]
            import math
            ph = -math.log10(h)
            return f"**Formula**: $pH = -log[H^+]$ \n**Working**: $-log({h}) = {ph:.2f}$\n**Answer**: {ph:.2f}"

    # TITRATION: C1V1 = C2V2
    if "titration" in q:
        if len(nums) >= 3:
            c1, v1, v2 = nums[0], nums[1], nums[2]
            c2 = (c1 * v1) / v2
            return f"**Formula**: $C1V1 = C2V2$\n**Working**: ${c1} * {v1} / {v2} = {c2:.3f}$\n**Answer**: {c2:.3f} mol/dm³"

    return None
