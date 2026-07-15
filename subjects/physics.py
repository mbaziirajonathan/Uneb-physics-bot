from typing import Dict, List, Any

# ==========================================
# UNEB PHYSICS SYLLABUS DATABASE (S1-S4 CBC)
# ==========================================
PHYSICS_CONTENT: Dict[tuple[str, str], Dict[str, Any]] = {
    # SENIOR 1
    ("S1", "Introduction to Physics"): {"text": "### Introduction to Physics\nBranch of science dealing with matter, energy and their interactions.", "diagram": None},
    ("S1", "Measurement"): {"text": "### Measurement\n**SI Units:** Length=m, Mass=kg, Time=s. **Instruments:** Ruler, Vernier calipers.", "diagram": "assets/vernier.png"},
    ("S1", "Force"): {"text": "### Force\nA push or pull. **Types:** Gravitational, Frictional. **Unit:** Newton. $F=ma$", "diagram": "assets/spring_balance.png"},
    ("S1", "Work Energy Power"): {"text": "### Work, Energy and Power\n**Work:** $W = F x d$. **Energy:** Kinetic and Potential. **Power:** Rate of doing work.", "diagram": None},
    ("S1", "Pressure"): {"text": "### Pressure\nForce per unit area. $P = F/A$. **Applications:** Hydraulic press, Barometer.", "diagram": None},

    # SENIOR 2
    ("S2", "Electroscope"): {"text": "### Electroscope\nDetects electric charge. Like charges repel causing gold leaves to diverge.", "diagram": "assets/electroscope.png"},
    ("S2", "Current Electricity"): {"text": "### Current Electricity\nFlow of electrons. **Laws:** Ohm's Law $V=IR$.", "diagram": "assets/simple_circuit.png"},
    ("S2", "Refraction"): {"text": "### Refraction of Light\nBending of light at interface of 2 media. $n = \\frac{\\sin i}{\\sin r}$", "diagram": "assets/refraction.png"},
    ("S2", "Heat"): {"text": "### Heat\nForm of energy. **Transfer:** Conduction, Convection, Radiation.", "diagram": None},
    ("S2", "Waves"): {"text": "### Waves\nDisturbance that transfers energy. **Types:** Transverse, Longitudinal. $v = f \\lambda$", "diagram": "assets/cro.png"},

    # SENIOR 3
    ("S3", "Hookes Law"): {"text": "### Hooke's Law\nExtension is proportional to force. $F = ke$", "diagram": "assets/hookes_law.png"},
    ("S3", "Specific Heat Capacity"): {"text": "### Specific Heat Capacity\nHeat to raise 1kg by 1°C. $Q = mc\\theta$", "diagram": "assets/colorimeter.png"},
    ("S3", "Magnetism"): {"text": "### Magnetism\nProperties of magnets. **Poles:** Like repel, unlike attract.", "diagram": None},
    ("S3", "Wave Motion"): {"text": "### Wave Motion\nProperties: Reflection, Refraction, Diffraction, Interference.", "diagram": None},
    ("S3", "Radioactivity"): {"text": "### Radioactivity\nSpontaneous emission of radiation. **Types:** Alpha, Beta, Gamma.", "diagram": None},

    # SENIOR 4
    ("S4", "Transformers"): {"text": "### Transformers\nStep up or step down AC voltage. $\\frac{V_p}{V_s} = \\frac{N_p}{N_s}$", "diagram": "assets/ac_transformer.png"},
    ("S4", "X-Ray Production"): {"text": "### X-Ray Production\nProduced by bombarding metal target with high speed electrons.", "diagram": "assets/xray_tube.png"},
    ("S4", "Electronics"): {"text": "### Electronics\nStudy of diodes, transistors. **Applications:** Rectification.", "diagram": None},
    ("S4", "Nuclear Physics"): {"text": "### Nuclear Physics\n**Fission:** Splitting nucleus. **Fusion:** Joining nuclei.", "diagram": None},
    ("S4", "Astrophysics"): {"text": "### Astrophysics\nStudy of celestial bodies. **Topics:** Stars, Galaxies.", "diagram": None},
}

def get_topics(level: str) -> List[str]:
    return [topic for (lvl, topic) in PHYSICS_CONTENT.keys() if lvl == level]

def get_content(level: str, topic: str) -> Dict[str, Any]:
    default_response = {"text": f"### {topic}\nDetailed UNEB notes are being generated. Please prompt the AI Assistant below.", "diagram": None}
    return PHYSICS_CONTENT.get((level, topic), default_response)
