import streamlit as st
import streamlit.components.v1 as components
from typing import Optional, Dict

# ==========================================
# 1. SVG DICTIONARY - ON-DEMAND, NO SPRITE BANK
# ==========================================
# Each diagram is a full standalone <svg>. Fixes Streamlit Cloud 100KB limit
SVG_DICTIONARY = {

    "animal_cell": """
    <svg width="100%" height="350" viewBox="0 0 800 325" style="border:1px solid #e2e8f0; border-radius: 8px; background:#f8fafc;">
    <defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 1.5 L10 5 L0 8.5 z" fill="#000"/></marker></defs>
    <text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">1. GENERALIZED ANIMAL CELL</text>
    <ellipse cx="300" cy="180" rx="160" ry="120" fill="#fdfbf7" stroke="#333" stroke-width="3"/>
    <circle cx="280" cy="180" r="40" fill="#e6f2ff" stroke="#333" stroke-width="2"/>
    <circle cx="270" cy="170" r="12" fill="#66b3ff"/> 
    <ellipse cx="400" cy="140" rx="25" ry="12" fill="#ffe6e6" stroke="#333" stroke-width="1.5" transform="rotate(30 400 140)"/>
    <path d="M385 140 Q395 130 400 140 T415 140" fill="none" stroke="#333" stroke-width="1.5" transform="rotate(30 400 140)"/>
    <ellipse cx="200" cy="240" rx="25" ry="12" fill="#ffe6e6" stroke="#333" stroke-width="1.5" transform="rotate(-45 200 240)"/>
    <path d="M185 240 Q195 230 200 240 T215 240" fill="none" stroke="#333" stroke-width="1.5" transform="rotate(-45 200 240)"/>
    <circle cx="360" cy="230" r="15" fill="#fff" stroke="#333" stroke-width="1"/>
    <circle cx="180" cy="140" r="10" fill="#fff" stroke="#333" stroke-width="1"/>
    <line x1="390" y1="75" x2="550" y2="75" stroke="#000" stroke-width="1.5" marker-end="url(#arr)"/>
    <text x="560" y="80" font-size="14">Cell Membrane</text>
    <line x1="350" y1="120" x2="550" y2="120" stroke="#000" stroke-width="1.5" marker-end="url(#arr)"/>
    <text x="560" y="125" font-size="14">Cytoplasm</text>
    <line x1="315" y1="170" x2="550" y2="170" stroke="#000" stroke-width="1.5" marker-end="url(#arr)"/>
    <text x="560" y="175" font-size="14">Nucleus (with Nucleolus)</text>
    <line x1="415" y1="155" x2="550" y2="215" stroke="#000" stroke-width="1.5" marker-end="url(#arr)"/>
    <text x="560" y="220" font-size="14">Mitochondrion</text>
    <line x1="375" y1="235" x2="550" y2="265" stroke="#000" stroke-width="1.5" marker-end="url(#arr)"/>
    <text x="560" y="270" font-size="14">Small Vacuole</text>
    </svg>
    """,

    "plant_cell": """
    <svg width="100%" height="350" viewBox="0 0 800 325" style="border:1px solid #e2e8f0; border-radius: 8px; background:#f8fafc;">
    <defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 1.5 L10 5 L0 8.5 z" fill="#000"/></marker></defs>
    <text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">2. GENERALIZED PLANT CELL</text>
    <rect x="150" y="70" width="280" height="220" fill="#e8f5e9" stroke="#2e7d32" stroke-width="6" rx="10"/>
    <rect x="156" y="76" width="268" height="208" fill="none" stroke="#000" stroke-width="1.5" rx="8"/>
    <rect x="180" y="100" width="180" height="120" fill="#ffffff" stroke="#333" stroke-width="1.5" rx="20"/>
    <circle cx="380" cy="230" r="30" fill="#e6f2ff" stroke="#333" stroke-width="2"/>
    <circle cx="375" cy="225" r="10" fill="#66b3ff"/>
    <ellipse cx="200" cy="250" rx="20" ry="10" fill="#81c784" stroke="#2e7d32" stroke-width="1.5"/>
    <ellipse cx="380" cy="110" rx="20" ry="10" fill="#81c784" stroke="#2e7d32" stroke-width="1.5"/>
    <line x1="150" y1="80" x2="520" y2="80" stroke="#000" stroke-width="1.5" marker-end="url(#arr)"/>
    <text x="530" y="85" font-size="14">Cellulose Cell Wall</text>
    <line x1="156" y1="120" x2="520" y2="120" stroke="#000" stroke-width="1.5" marker-end="url(#arr)"/>
    <text x="530" y="125" font-size="14">Cell Membrane</text>
    <line x1="270" y1="160" x2="520" y2="160" stroke="#000" stroke-width="1.5" marker-end="url(#arr)"/>
    <text x="530" y="165" font-size="14">Large Central Vacuole</text>
    <line x1="410" y1="230" x2="520" y2="230" stroke="#000" stroke-width="1.5" marker-end="url(#arr)"/>
    <text x="530" y="235" font-size="14">Nucleus</text>
    <line x1="400" y1="110" x2="520" y2="195" stroke="#000" stroke-width="1.5" marker-end="url(#arr)"/>
    <text x="530" y="200" font-size="14">Chloroplast</text>
    </svg>
    """,

    "heart": """
    <svg width="100%" height="350" viewBox="0 0 800 325" style="border:1px solid #e2e8f0; border-radius: 8px; background:#f8fafc;">
    <defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 1.5 L10 5 L0 8.5 z" fill="#000"/></marker></defs>
    <text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">3. INTERNAL STRUCTURE OF THE MAMMALIAN HEART</text>
    <path d="M300 120 C250 120 220 180 300 280 C380 180 350 120 300 120" fill="none" stroke="#000" stroke-width="3"/>
    <path d="M300 140 V270" stroke="#8b0000" stroke-width="12"/>
    <path d="M250 140 C230 160 230 190 290 190 V140 Z" fill="#bbdefb" stroke="#000" stroke-width="1.5"/>
    <path d="M290 200 C230 200 250 250 290 270 V200 Z" fill="#bbdefb" stroke="#000" stroke-width="1.5"/>
    <path d="M310 140 V190 C370 190 370 160 350 140 Z" fill="#ffcdd2" stroke="#000" stroke-width="1.5"/>
    <path d="M310 200 V270 C350 250 370 200 310 200 Z" fill="#ffcdd2" stroke="#000" stroke-width="1.5"/>
    <line x1="250" y1="195" x2="290" y2="195" stroke="#333" stroke-width="4" stroke-dasharray="6,2"/>
    <line x1="310" y1="195" x2="350" y2="195" stroke="#333" stroke-width="4" stroke-dasharray="6,2"/>
    <path d="M260 140 V90" stroke="#1565c0" stroke-width="15"/>
    <path d="M340 140 V90" stroke="#c62828" stroke-width="15"/>
    <path d="M290 140 C290 80 370 80 370 120" stroke="#c62828" fill="none" stroke-width="12"/>
    <path d="M310 140 C310 100 230 100 230 130" stroke="#1565c0" fill="none" stroke-width="12"/>
    <line x1="380" y1="90" x2="480" y2="90" stroke="#000" stroke-width="1" marker-end="url(#arr)"/><text x="490" y="95" font-size="14">Aorta</text>
    <line x1="350" y1="120" x2="480" y2="120" stroke="#000" stroke-width="1" marker-end="url(#arr)"/><text x="490" y="125" font-size="14">Pulmonary Vein</text>
    <line x1="350" y1="170" x2="480" y2="170" stroke="#000" stroke-width="1" marker-end="url(#arr)"/><text x="490" y="175" font-size="14">Left Atrium</text>
    <line x1="330" y1="195" x2="480" y2="210" stroke="#000" stroke-width="1" marker-end="url(#arr)"/><text x="490" y="215" font-size="14">Bicuspid Valve</text>
    <line x1="330" y1="240" x2="480" y2="240" stroke="#000" stroke-width="1" marker-end="url(#arr)"/><text x="490" y="245" font-size="14">Left Ventricle (Thick Wall)</text>
    <line x1="260" y1="110" x2="150" y2="90" stroke="#000" stroke-width="1" marker-end="url(#arr)"/><text x="140" y="95" font-size="14" text-anchor="end">Vena Cava</text>
    <line x1="225" y1="125" x2="150" y2="130" stroke="#000" stroke-width="1" marker-end="url(#arr)"/><text x="140" y="135" font-size="14" text-anchor="end">Pulmonary Artery</text>
    <line x1="260" y1="170" x2="150" y2="170" stroke="#000" stroke-width="1" marker-end="url(#arr)"/><text x="140" y="175" font-size="14" text-anchor="end">Right Atrium</text>
    <line x1="270" y1="195" x2="150" y2="210" stroke="#000" stroke-width="1" marker-end="url(#arr)"/><text x="140" y="215" font-size="14" text-anchor="end">Tricuspid Valve</text>
    <line x1="260" y1="240" x2="150" y2="240" stroke="#000" stroke-width="1" marker-end="url(#arr)"/><text x="140" y="245" font-size="14" text-anchor="end">Right Ventricle</text>
    </svg>
    """,

    "leaf_ts": """
    <svg width="100%" height="350" viewBox="0 0 800 325" style="border:1px solid #e2e8f0; border-radius: 8px; background:#f8fafc;">
    <defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 1.5 L10 5 L0 8.5 z" fill="#000"/></marker></defs>
    <text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">4. TRANSVERSE SECTION OF A DICOTYLEDONOUS LEAF</text>
    <rect x="200" y="80" width="200" height="15" fill="#e0f2f1" stroke="#00695c"/>
    <rect x="200" y="95" width="200" height="25" fill="#b2dfdb" stroke="#00695c"/>
    <rect x="200" y="120" width="30" height="60" fill="#81c784" stroke="#2e7d32"/>
    <rect x="235" y="120" width="30" height="60" fill="#81c784" stroke="#2e7d32"/>
    <rect x="270" y="120" width="30" height="60" fill="#81c784" stroke="#2e7d32"/>
    <rect x="305" y="120" width="30" height="60" fill="#81c784" stroke="#2e7d32"/>
    <rect x="340" y="120" width="30" height="60" fill="#81c784" stroke="#2e7d32"/>
    <circle cx="230" cy="210" r="15" fill="#aed581" stroke="#33691e"/>
    <circle cx="270" cy="195" r="15" fill="#aed581" stroke="#33691e"/>
    <circle cx="310" cy="215" r="15" fill="#aed581" stroke="#33691e"/>
    <circle cx="360" cy="200" r="15" fill="#aed581" stroke="#33691e"/>
    <rect x="200" y="250" width="80" height="25" fill="#b2dfdb" stroke="#00695c"/>
    <rect x="320" y="250" width="80" height="25" fill="#b2dfdb" stroke="#00695c"/>
    <path d="M 280 275 C 290 250 310 250 320 275" fill="none" stroke="#2e7d32" stroke-width="3"/>
    <line x1="300" y1="87" x2="450" y2="87" stroke="#000" marker-end="url(#arr)"/><text x="460" y="90" font-size="14">Waxy Cuticle</text>
    <line x1="400" y1="107" x2="450" y2="107" stroke="#000" marker-end="url(#arr)"/><text x="460" y="110" font-size="14">Upper Epidermis</text>
    <line x1="370" y1="150" x2="450" y2="150" stroke="#000" marker-end="url(#arr)"/><text x="460" y="153" font-size="14">Palisade Mesophyll</text>
    <line x1="375" y1="205" x2="450" y2="205" stroke="#000" marker-end="url(#arr)"/><text x="460" y="208" font-size="14">Spongy Mesophyll Layer</text>
    <line x1="400" y1="262" x2="450" y2="262" stroke="#000" marker-end="url(#arr)"/><text x="460" y="265" font-size="14">Lower Epidermis</text>
    <line x1="300" y1="265" x2="450" y2="295" stroke="#000" marker-end="url(#arr)"/><text x="460" y="300" font-size="14">Stoma (Guard Cells)</text>
    </svg>
    """,

    "nephron": """
    <svg width="100%" height="350" viewBox="0 0 800 325" style="border:1px solid #e2e8f0; border-radius: 8px; background:#f8fafc;">
    <defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 1.5 L10 5 L0 8.5 z" fill="#000"/></marker></defs>
    <text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">5. STRUCTURE OF A NEPHRON (KIDNEY TUBULE)</text>
    <path d="M 120 120 C 150 70 200 70 220 120 C 230 140 210 160 190 140 C 170 120 150 120 140 140" fill="none" stroke="#b71c1c" stroke-width="8"/>
    <path d="M 170 130 C 140 80 250 80 250 150 V 170 C 250 200 270 200 270 170 V 150 C 270 100 330 100 330 150 V 260 C 330 290 370 290 370 260 V 150 C 370 110 420 110 420 150 H 460 V 280" fill="none" stroke="#fbc02d" stroke-width="12"/>
    <line x1="180" y1="100" x2="280" y2="70" stroke="#000" marker-end="url(#arr)"/><text x="290" y="75" font-size="14">Glomerulus (Capillary Knot)</text>
    <line x1="210" y1="120" x2="280" y2="105" stroke="#000" marker-end="url(#arr)"/><text x="290" y="110" font-size="14">Bowman's Capsule</text>
    <line x1="260" y1="180" x2="160" y2="180" stroke="#000" marker-end="url(#arr)"/><text x="150" y="185" font-size="14" text-anchor="end">Proximal Convoluted Tubule</text>
    <line x1="350" y1="280" x2="450" y2="280" stroke="#000" marker-end="url(#arr)"/><text x="460" y="285" font-size="14">Loop of Henle</text>
    <line x1="400" y1="120" x2="480" y2="100" stroke="#000" marker-end="url(#arr)"/><text x="490" y="105" font-size="14">Distal Convoluted Tubule</text>
    <line x1="460" y1="200" x2="520" y2="200" stroke="#000" marker-end="url(#arr)"/><text x="530" y="205" font-size="14">Collecting Duct</text>
    </svg>
    """,

    "neurone": """
    <svg width="100%" height="350" viewBox="0 0 800 325" style="border:1px solid #e2e8f0; border-radius: 8px; background:#f8fafc;">
    <defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 1.5 L10 5 L0 8.5 z" fill="#000"/></marker></defs>
    <text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">6. STRUCTURE OF A MOTOR NEURONE</text>
    <circle cx="150" cy="160" r="40" fill="#e1bee7" stroke="#4a148c" stroke-width="2"/>
    <circle cx="150" cy="160" r="10" fill="#4a148c"/>
    <path d="M 110 160 L 60 140 M 120 130 L 80 80 M 150 120 L 150 70 M 180 130 L 210 90 M 180 180 L 220 220 M 130 190 L 90 230" stroke="#4a148c" stroke-width="4"/>
    <line x1="190" y1="160" x2="500" y2="160" stroke="#4a148c" stroke-width="6"/>
    <rect x="220" y="152" width="60" height="16" fill="#fff9c4" stroke="#fbc02d" stroke-width="2" rx="4"/>
    <rect x="290" y="152" width="60" height="16" fill="#fff9c4" stroke="#fbc02d" stroke-width="2" rx="4"/>
    <rect x="360" y="152" width="60" height="16" fill="#fff9c4" stroke="#fbc02d" stroke-width="2" rx="4"/>
    <rect x="430" y="152" width="60" height="16" fill="#fff9c4" stroke="#fbc02d" stroke-width="2" rx="4"/>
    <path d="M 500 160 L 550 120 M 500 160 L 560 160 M 500 160 L 550 200" stroke="#4a148c" stroke-width="3"/>
    <line x1="150" y1="160" x2="220" y2="80" stroke="#000" marker-end="url(#arr)"/><text x="230" y="75" font-size="14">Cell Body (Soma) & Nucleus</text>
    <line x1="90" y1="140" x2="220" y2="110" stroke="#000" marker-end="url(#arr)"/><text x="230" y="115" font-size="14">Dendrites</text>
    <line x1="250" y1="152" x2="250" y2="100" stroke="#000" marker-end="url(#arr)"/><text x="240" y="95" font-size="14" text-anchor="middle">Myelin Sheath</text>
    <line x1="355" y1="160" x2="355" y2="220" stroke="#000" marker-end="url(#arr)"/><text x="355" y="235" font-size="14" text-anchor="middle">Node of Ranvier</text>
    <line x1="550" y1="160" x2="620" y2="160" stroke="#000" marker-end="url(#arr)"/><text x="630" y="165" font-size="14">Motor End Plates (To Effector)</text>
    </svg>
    """,

    "alveolus": """
    <svg width="100%" height="350" viewBox="0 0 800 325" style="border:1px solid #e2e8f0; border-radius: 8px; background:#f8fafc;">
    <defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 1.5 L10 5 L0 8.5 z" fill="#000"/></marker></defs>
    <text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">7. GASEOUS EXCHANGE AT THE ALVEOLUS</text>
    <path d="M 350 70 V 120 C 300 120 250 170 250 220 C 250 270 320 310 400 310 C 480 310 550 270 550 220 C 550 170 500 120 450 120 V 70" fill="#e3f2fd" stroke="#1565c0" stroke-width="3"/>
    <path d="M 230 250 C 230 320 570 320 570 250" fill="none" stroke="#c62828" stroke-width="15"/>
    <circle cx="300" cy="275" r="5" fill="#fff" stroke="#c62828" stroke-width="2"/>
    <circle cx="350" cy="290" r="5" fill="#fff" stroke="#c62828" stroke-width="2"/>
    <circle cx="400" cy="295" r="5" fill="#ffcdd2" stroke="#c62828" stroke-width="2"/>
    <circle cx="450" cy="290" r="5" fill="#ffcdd2" stroke="#c62828" stroke-width="2"/>
    <path d="M 370 200 L 370 270" stroke="#000" stroke-width="2" marker-end="url(#arr)" stroke-dasharray="4"/><text x="360" y="240" font-size="14" text-anchor="end">O2</text>
    <path d="M 430 270 L 430 200" stroke="#000" stroke-width="2" marker-end="url(#arr)" stroke-dasharray="4"/><text x="440" y="240" font-size="14">CO2</text>
    <line x1="450" y1="90" x2="520" y2="90" stroke="#000" marker-end="url(#arr)"/><text x="530" y="95" font-size="14">Bronchiole</text>
    <line x1="550" y1="210" x2="620" y2="210" stroke="#000" marker-end="url(#arr)"/><text x="630" y="215" font-size="14">Thin Alveolar Wall (One Cell Thick)</text>
    <line x1="565" y1="260" x2="620" y2="260" stroke="#000" marker-end="url(#arr)"/><text x="630" y="265" font-size="14">Blood Capillary Network</text>
    <line x1="400" y1="295" x2="400" y2="320" stroke="#000" marker-end="url(#arr)"/><text x="400" y="335" font-size="14" text-anchor="middle">Red Blood Cell</text>
    </svg>
    """,

    "atom": """
    <svg width="100%" height="350" viewBox="0 0 800 325" style="border:1px solid #e2e8f0; border-radius: 8px; background:#f8fafc;">
    <defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 1.5 L10 5 L0 8.5 z" fill="#000"/></marker></defs>
    <text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">1. ATOMIC STRUCTURE (CARBON BOHR MODEL)</text>
    <circle cx="300" cy="180" r="18" fill="#d32f2f" stroke="#000" stroke-width="1"/><text x="300" y="184" text-anchor="middle" fill="#fff" font-size="10" font-weight="bold">6p 6n</text>
    <circle cx="300" cy="180" r="50" fill="none" stroke="#555" stroke-width="2" stroke-dasharray="4"/>
    <circle cx="300" cy="180" r="100" fill="none" stroke="#555" stroke-width="2" stroke-dasharray="4"/>
    <circle cx="300" cy="130" r="6" fill="#1976d2" stroke="#000" stroke-width="1"/>
    <circle cx="300" cy="230" r="6" fill="#1976d2" stroke="#000" stroke-width="1"/>
    <circle cx="300" cy="80" r="6" fill="#1976d2" stroke="#000" stroke-width="1"/>
    <circle cx="300" cy="280" r="6" fill="#1976d2" stroke="#000" stroke-width="1"/>
    <circle cx="200" cy="180" r="6" fill="#1976d2" stroke="#000" stroke-width="1"/>
    <circle cx="400" cy="180" r="6" fill="#1976d2" stroke="#000" stroke-width="1"/>
    <line x1="318" y1="180" x2="480" y2="130" stroke="#000" stroke-width="1.5" marker-end="url(#arr)"/><text x="490" y="130" font-size="14">Nucleus (6 Protons, 6 Neutrons)</text>
    <line x1="340" y1="145" x2="480" y2="170" stroke="#000" stroke-width="1.5" marker-end="url(#arr)"/><text x="490" y="175" font-size="14">First Electron Shell (K = 2e⁻)</text>
    <line x1="380" y1="230" x2="480" y2="210" stroke="#000" stroke-width="1.5" marker-end="url(#arr)"/><text x="490" y="215" font-size="14">Second Electron Shell (L = 4e⁻)</text>
    <line x1="400" y1="174" x2="480" y2="250" stroke="#000" stroke-width="1.5" marker-end="url(#arr)"/><text x="490" y="255" font-size="14">Valence Electron (Negative Charge)</text>
    </svg>
    """
}

    "chromatography": """
    <svg width="100%" height="350" viewBox="0 0 800 325" style="border:1px solid #e2e8f0; border-radius: 8px; background:#f8fafc;">
    <defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 1.5 L10 5 L0 8.5 z" fill="#000"/></marker></defs>
    <text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">3. ASCENDING PAPER CHROMATOGRAPHY</text>
    <path d="M 250 250 H 350 V 100 H 250 Z" fill="none" stroke="#444" stroke-width="3"/>
    <rect x="252" y="210" width="96" height="38" fill="#e0f7fa"/>
    <line x1="280" y1="80" x2="320" y2="80" stroke="#000" stroke-width="5"/>
    <rect x="290" y="80" width="20" height="150" fill="#fff" stroke="#9e9e9e" stroke-width="1.5"/>
    <line x1="290" y1="200" x2="310" y2="200" stroke="#000" stroke-dasharray="2" stroke-width="1"/>
    <circle cx="300" cy="180" r="3" fill="#d32f2f"/>
    <circle cx="300" cy="140" r="3" fill="#1976d2"/>
    <circle cx="300" cy="110" r="3" fill="#388e3c"/>
    <line x1="320" y1="80" x2="440" y2="80" stroke="#000" marker-end="url(#arr)"/><text x="450" y="85" font-size="14">Glass Rod / Support</text>
    <line x1="310" y1="125" x2="440" y2="125" stroke="#000" marker-end="url(#arr)"/><text x="450" y="130" font-size="14">Chromatography Paper</text>
    <line x1="305" y1="180" x2="440" y2="170" stroke="#000" marker-end="url(#arr)"/><text x="450" y="175" font-size="14">Separated Components (Dyes)</text>
    <line x1="300" y1="200" x2="440" y2="200" stroke="#000" marker-end="url(#arr)"/><text x="450" y="205" font-size="14">Origin (Pencil Line)</text>
    <line x1="340" y1="230" x2="440" y2="230" stroke="#000" marker-end="url(#arr)"/><text x="450" y="235" font-size="14">Solvent (Mobile Phase)</text>
    </svg>
    """,

    "titration": """
    <svg width="100%" height="350" viewBox="0 0 800 325" style="border:1px solid #e2e8f0; border-radius: 8px; background:#f8fafc;">
    <defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 1.5 L10 5 L0 8.5 z" fill="#000"/></marker></defs>
    <text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">4. ACID-BASE TITRATION APPARATUS</text>
    <path d="M 280 270 H 350 M 315 270 V 70 H 330" fill="none" stroke="#444" stroke-width="5"/>
    <rect x="250" y="60" width="10" height="150" fill="none" stroke="#000" stroke-width="1.5"/>
    <path d="M 250 210 L 255 230 L 260 210 Z" fill="none" stroke="#000" stroke-width="1.5"/>
    <rect x="245" y="220" width="20" height="5" fill="#424242"/>
    <path d="M 240 235 H 270 L 290 270 H 220 Z" fill="none" stroke="#000" stroke-width="2"/>
    <rect x="251" y="100" width="8" height="110" fill="#fce4ec"/>
    <path d="M 230 260 H 280 L 285 270 H 225 Z" fill="#e8eaf6"/>
    <path d="M 260 140 H 315" fill="none" stroke="#444" stroke-width="3"/>
    <line x1="260" y1="120" x2="400" y2="100" stroke="#000" marker-end="url(#arr)"/><text x="410" y="105" font-size="14">Burette containing Titrant (Acid)</text>
    <line x1="265" y1="222" x2="400" y2="200" stroke="#000" marker-end="url(#arr)"/><text x="410" y="205" font-size="14">Tap / Stopcock</text>
    <line x1="270" y1="250" x2="400" y2="250" stroke="#000" marker-end="url(#arr)"/><text x="410" y="255" font-size="14">Conical Flask containing Analyte & Indicator</text>
    <line x1="315" y1="170" x2="400" y2="170" stroke="#000" marker-end="url(#arr)"/><text x="410" y="175" font-size="14">Retort Stand and Clamp</text>
    </svg>
    """,

    "gas_prep": """
    <svg width="100%" height="350" viewBox="0 0 800 325" style="border:1px solid #e2e8f0; border-radius: 8px; background:#f8fafc;">
    <defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 1.5 L10 5 L0 8.5 z" fill="#000"/></marker><pattern id="dots" width="10" height="10" patternUnits="userSpaceOnUse"><circle cx="5" cy="5" r="1.5" fill="#555"/></pattern></defs>
    <text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">5. LAB PREPARATION OF OXYGEN GAS (H2O2 + MnO2)</text>
    <path d="M 170 240 H 230 V 160 H 170 Z" fill="none" stroke="#000" stroke-width="2"/>
    <rect x="172" y="200" width="56" height="40" fill="#fff9c4"/>
    <rect x="180" y="230" width="40" height="10" fill="url(#dots)"/>
    <path d="M 190 70 V 180" fill="none" stroke="#000" stroke-width="4"/>
    <path d="M 180 70 L 190 90 L 200 70" fill="none" stroke="#000" stroke-width="2"/>
    <path d="M 210 170 H 215 V 100 H 350 V 260 H 370" fill="none" stroke="#000" stroke-width="3"/>
    <rect x="300" y="220" width="150" height="60" fill="none" stroke="#444" stroke-width="3"/>
    <rect x="302" y="240" width="146" height="40" fill="#e3f2fd"/>
    <path d="M 360 270 H 380 V 250 H 360 Z" fill="none" stroke="#000" stroke-width="2"/>
    <rect x="360" y="130" width="30" height="120" fill="none" stroke="#000" stroke-width="2"/>
    <rect x="362" y="180" width="26" height="70" fill="#e3f2fd"/>
    <circle cx="375" cy="160" r="2" fill="#000"/><circle cx="370" cy="150" r="2" fill="#000"/><circle cx="380" cy="140" r="2" fill="#000"/>
    <line x1="185" y1="80" x2="110" y2="80" stroke="#000" marker-end="url(#arr)"/><text x="100" y="85" font-size="14" text-anchor="end">Thistle Funnel (Adds H2O2)</text>
    <line x1="200" y1="235" x2="110" y2="235" stroke="#000" marker-end="url(#arr)"/><text x="100" y="240" font-size="14" text-anchor="end">Manganese(IV) Oxide Catalyst</text>
    <line x1="280" y1="100" x2="280" y2="70" stroke="#000" marker-end="url(#arr)"/><text x="280" y="60" font-size="14" text-anchor="middle">Delivery Tube</text>
    <line x1="375" y1="150" x2="450" y2="150" stroke="#000" marker-end="url(#arr)"/><text x="460" y="155" font-size="14">Oxygen Gas (O2)</text>
    <line x1="390" y1="210" x2="450" y2="210" stroke="#000" marker-end="url(#arr)"/><text x="460" y="215" font-size="14">Inverted Gas Jar</text>
    <line x1="420" y1="260" x2="450" y2="260" stroke="#000" marker-end="url(#arr)"/><text x="460" y="265" font-size="14">Water Trough</text>
    </svg>
    """,

    "fractional_distillation": """
    <svg width="100%" height="350" viewBox="0 0 800 325" style="border:1px solid #e2e8f0; border-radius: 8px; background:#f8fafc;">
    <defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 1.5 L10 5 L0 8.5 z" fill="#000"/></marker></defs>
    <text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">6. FRACTIONAL DISTILLATION</text>
    <circle cx="200" cy="230" r="30" fill="none" stroke="#000" stroke-width="2"/>
    <rect x="190" y="180" width="20" height="25" fill="none" stroke="#000" stroke-width="2"/>
    <path d="M 200 240 Q 210 250 200 260 Q 190 250 200 240" fill="#ff5722"/>
    <rect x="190" y="90" width="20" height="90" fill="none" stroke="#000" stroke-width="2"/>
    <circle cx="200" cy="110" r="4" fill="#616161"/><circle cx="200" cy="130" r="4" fill="#616161"/><circle cx="200" cy="150" r="4" fill="#616161"/>
    <line x1="200" y1="90" x2="200" y2="60" stroke="#d32f2f" stroke-width="3"/>
    <path d="M 210 100 L 320 150" fill="none" stroke="#000" stroke-width="4"/>
    <path d="M 230 110 L 300 145" fill="none" stroke="#1976d2" stroke-width="12" opacity="0.3"/>
    <rect x="310" y="160" width="30" height="50" fill="none" stroke="#000" stroke-width="2"/>
    <line x1="170" y1="230" x2="100" y2="230" stroke="#000" marker-end="url(#arr)"/><text x="90" y="235" font-size="14" text-anchor="end">Round Bottom Flask (Mixture)</text>
    <line x1="190" y1="130" x2="100" y2="130" stroke="#000" marker-end="url(#arr)"/><text x="90" y="135" font-size="14" text-anchor="end">Fractionating Column (Glass Beads)</text>
    <line x1="200" y1="65" x2="280" y2="65" stroke="#000" marker-end="url(#arr)"/><text x="290" y="70" font-size="14">Thermometer</text>
    <line x1="265" y1="125" x2="350" y2="110" stroke="#000" marker-end="url(#arr)"/><text x="360" y="115" font-size="14">Liebig Condenser</text>
    <line x1="340" y1="185" x2="400" y2="185" stroke="#000" marker-end="url(#arr)"/><text x="410" y="190" font-size="14">Distillate (Pure Fraction)</text>
    </svg>
    """,

    "covalent_water": """
    <svg width="100%" height="350" viewBox="0 0 800 325" style="border:1px solid #e2e8f0; border-radius: 8px; background:#f8fafc;">
    <defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 1.5 L10 5 L0 8.5 z" fill="#000"/></marker></defs>
    <text x="400" y="30" font-size="14" text-anchor="middle" font-weight="bold">7. COVALENT BONDING IN WATER (H2O DOT AND CROSS)</text>
    <circle cx="400" cy="180" r="60" fill="none" stroke="#d32f2f" stroke-width="2"/>
    <circle cx="330" cy="140" r="40" fill="none" stroke="#1976d2" stroke-width="2"/>
    <circle cx="470" cy="140" r="40" fill="none" stroke="#1976d2" stroke-width="2"/>
    <text x="400" y="185" font-size="20" font-weight="bold" fill="#d32f2f" text-anchor="middle">O</text>
    <text x="315" y="145" font-size="20" font-weight="bold" fill="#1976d2" text-anchor="middle">H</text>
    <text x="485" y="145" font-size="20" font-weight="bold" fill="#1976d2" text-anchor="middle">H</text>
    <text x="400" y="130" font-size="16" font-weight="bold" fill="#000" text-anchor="middle">x x</text>
    <text x="400" y="235" font-size="16" font-weight="bold" fill="#000" text-anchor="middle">x x</text>
    <circle cx="360" cy="145" r="3" fill="#000"/>
    <text x="350" y="152" font-size="16" font-weight="bold" fill="#000" text-anchor="middle">x</text>
    <circle cx="440" cy="145" r="3" fill="#000"/>
    <text x="450" y="152" font-size="16" font-weight="bold" fill="#000" text-anchor="middle">x</text>
    <line x1="420" y1="220" x2="520" y2="250" stroke="#000" marker-end="url(#arr)"/><text x="530" y="255" font-size="14">Oxygen Outer Shell (6 Electrons)</text>
    <line x1="360" y1="140" x2="250" y2="100" stroke="#000" marker-end="url(#arr)"/><text x="240" y="95" font-size="14" text-anchor="end">Shared Pair (Single Covalent Bond)</text>
    <line x1="470" y1="100" x2="520" y2="80" stroke="#000" marker-end="url(#arr)"/><text x="530" y="85" font-size="14">Hydrogen Shell (1 Electron)</text>
    </svg>
    """
}

# ==========================================
# 2. UNEB CURRICULUM MAPPING (S1 - S4)
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
    }
}

# ==========================================
# 3. CHATBOT DIAGRAM MANAGER CLASS - FIXED FOR CLOUD
# ==========================================
class DiagramManager:
    @staticmethod
    def initialize_sprites() -> None:
        pass # No longer needed

    @classmethod
    def get_symbol_by_curriculum(cls, subject: str, level: str, topic: str) -> Optional[str]:
        return UNEB_CURRICULUM_MAP.get(subject, {}).get(level, {}).get(topic)

    @staticmethod
    def render(symbol_id: Optional[str]) -> None:
        if not symbol_id:
            st.warning("⚠️ No diagram is currently available for this specific UNEB topic.")
            return
        svg_code = SVG_DICTIONARY.get(symbol_id)
        if svg_code:
            components.html(svg_code, height=370, scrolling=False)
        else:
            st.error(f"Diagram '{symbol_id}' not found in SVG_DICTIONARY")

# ==========================================
# 4. EXAMPLE USAGE / TESTING
# ==========================================
if __name__ == "__main__":
    st.set_page_config(page_title="UNEB AI Tutor", layout="wide")
    DiagramManager.initialize_sprites()
    st.title("UNEB S1-S4 Asset Manager")
    col1, col2, col3 = st.columns(3)
    with col1: subject_choice = st.selectbox("Subject", options=list(UNEB_CURRICULUM_MAP.keys()))
    with col2: level_choice = st.selectbox("Class Level", options=list(UNEB_CURRICULUM_MAP[subject_choice].keys()))
    with col3: topic_choice = st.selectbox("Topic", options=list(UNEB_CURRICULUM_MAP[subject_choice][level_choice].keys()))
    st.write(f"### Visual for: **{topic_choice}**")
    symbol_to_render = DiagramManager.get_symbol_by_curriculum(subject_choice, level_choice, topic_choice)
    DiagramManager.render(symbol_to_render)
