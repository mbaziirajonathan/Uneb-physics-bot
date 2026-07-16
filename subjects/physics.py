from typing import Dict, List, Any

# ==========================================
# UNEB PHYSICS SYLLABUS DATABASE (S1-S4 CBC 2026)
# Aligned to NCDC Uganda
# ==========================================
PHYSICS_CONTENT: Dict[tuple[str, str], Dict[str, Any]] = {
    # SENIOR 1
    ("S1", "Introduction to Physics"): {
        "text": "### Introduction to Physics\nBranch of science dealing with matter, energy and their interactions. **Branches:** Mechanics, Optics, Electricity, Modern Physics.",
        "diagram": None
    },
    ("S1", "Measurement"): {
        "text": "### Measurement\n**SI Units:** Length=m, Mass=kg, Time=s. **Instruments:** Ruler, Vernier calipers, Micrometer screw gauge. **Errors:** Systematic and Random.",
        "diagram": "assets/diagrams/vernier.png"
    },
    ("S1", "Matter"): {
        "text": "### Matter\nAnything that has mass and occupies space. **States:** Solid, Liquid, Gas. **Kinetic theory.**",
        "diagram": None
    },
    ("S1", "Force"): {
        "text": "### Force\nA push or pull. **Types:** Gravitational, Frictional, Magnetic. **Unit:** Newton. $F=ma$",
        "diagram": "assets/diagrams/spring_balance.png"
    },
    ("S1", "Work Energy Power"): {
        "text": "### Work, Energy and Power\n**Work:** $W = F \\times d$. **Energy:** Kinetic $KE = \\frac{1}{2}mv^2$ and Potential $PE = mgh$. **Power:** Rate of doing work.",
        "diagram": None
    },
    ("S1", "Pressure"): {
        "text": "### Pressure\nForce per unit area. $P = F/A$. **Applications:** Hydraulic press, Barometer, Manometer.",
        "diagram": None
    },
    ("S1", "Light"): {
        "text": "### Light\n**Properties:** Reflection, Refraction. **Lenses:** Concave and Convex. **Instruments:** Camera, Telescope.",
        "diagram": "assets/diagrams/concave_and_convex_lens.png"
    },
    ("S1", "Sound"): {
        "text": "### Sound\nMechanical wave. **Properties:** Speed, Frequency, Wavelength. $v = f \\lambda$",
        "diagram": None
    },
    ("S1", "Heat"): {
        "text": "### Heat\nForm of energy. **Transfer:** Conduction, Convection, Radiation. **Specific Heat Capacity:** $Q = mc\\theta$",
        "diagram": "assets/diagrams/specific_heat_capacity.png"
    },
    ("S1", "Electricity"): {
        "text": "### Electricity\n**Static:** Electroscope. **Current:** Flow of electrons. **Components:** Cell, Switch, Bulb.",
        "diagram": "assets/diagrams/electrical_cell.png"
    },
    ("S1", "Magnetism"): {
        "text": "### Magnetism\nProperties of magnets. **Poles:** Like repel, unlike attract. **Uses:** Compass, Motor.",
        "diagram": None
    },
    ("S1", "Machines"): {
        "text": "### Machines\nDevices that make work easier. **Examples:** Lever, Pulley, Inclined plane. **MA, VR, Efficiency.**",
        "diagram": None
    },

    # SENIOR 2
    ("S2", "Motion"): {
        "text": "### Motion\n**Types:** Linear, Circular. **Equations of motion:** $v = u + at$, $s = ut + \\frac{1}{2}at^2$",
        "diagram": "assets/diagrams/linear_motion.png"
    },
    ("S2", "Forces"): {
        "text": "### Forces\n**Types:** Tension, Friction, Upthrust. **Newton's Laws of Motion.**",
        "diagram": None
    },
    ("S2", "Work Energy Power"): {
        "text": "### Work Energy Power\n**Conservation of Energy.** **Machines and Efficiency.**",
        "diagram": None
    },
    ("S2", "Pressure"): {
        "text": "### Pressure\n**Liquid Pressure:** $P = \\rho gh$. **Atmospheric pressure.**",
        "diagram": None
    },
    ("S2", "Waves"): {
        "text": "### Waves\nDisturbance that transfers energy. **Types:** Transverse, Longitudinal. $v = f \\lambda$",
        "diagram": "assets/diagrams/longitudinal_and_transverse_waves.png"
    },
    ("S2", "Electrostatics"): {
        "text": "### Electrostatics\nStudy of stationary charges. **Laws of electrostatics.** **Electroscope:** Detects charge.",
        "diagram": "assets/diagrams/electroscope.png"
    },
    ("S2", "Current Electricity"): {
        "text": "### Current Electricity\nFlow of electrons. **Laws:** Ohm's Law $V=IR$. **Series and Parallel circuits.**",
        "diagram": "assets/diagrams/simple_circuit.png"
    },
    ("S2", "Optics"): {
        "text": "### Refraction of Light\nBending of light at interface of 2 media. $n = \\frac{\\sin i}{\\sin r}$. **Total internal reflection.**",
        "diagram": "assets/diagrams/light_refraction.png"
    },

    # SENIOR 3
    ("S3", "Linear Motion"): {
        "text": "### Linear Motion\n**Graphs:** Displacement-time, Velocity-time. **Acceleration.**",
        "diagram": None
    },
    ("S3", "Newton's Laws"): {
        "text": "### Newton's Laws\n1. Inertia. 2. $F=ma$. 3. Action-Reaction. **Applications.**",
        "diagram": None
    },
    ("S3", "Momentum"): {
        "text": "### Momentum\n$P = mv$. **Conservation of momentum.** **Impulse:** $F \\times t$",
        "diagram": None
    },
    ("S3", "Gravitation"): {
        "text": "### Gravitation\n**Newton's Law:** $F = G\\frac{m_1m_2}{r^2}$. **Satellites, Escape velocity.**",
        "diagram": None
    },
    ("S3", "Properties of Matter"): {
        "text": "### Properties of Matter\n**Elasticity:** Hooke's Law $F = ke$. **Surface tension, Viscosity.**",
        "diagram": "assets/diagrams/hookes_law.png"
    },
    ("S3", "Thermal Physics"): {
        "text": "### Thermal Physics\n**Gas laws.** **Specific Heat Capacity:** $Q = mc\\theta$. **Latent heat.**",
        "diagram": "assets/diagrams/colorimeter.png"
    },
    ("S3", "Waves II"): {
        "text": "### Wave Motion\nProperties: Reflection, Refraction, Diffraction, Interference. **Stationary waves.**",
        "diagram": None
    },
    ("S3", "Magnetism"): {
        "text": "### Magnetism\n**Magnetic field patterns.** **Electromagnets.** **Electric bell.**",
        "diagram": None
    },

    # SENIOR 4
    ("S4", "Radioactivity"): {
        "text": "### Radioactivity\nSpontaneous emission of radiation. **Types:** Alpha, Beta, Gamma. **Half-life.**",
        "diagram": "assets/diagrams/radioactivity.png"
    },
    ("S4", "Electronics"): {
        "text": "### Electronics\nStudy of diodes, transistors. **Applications:** Rectification, Amplification. **AC and DC.**",
        "diagram": "assets/diagrams/ac_and_dc_electricity.png"
    },
    ("S4", "AC/DC"): {
        "text": "### AC and DC\n**Alternating Current:** Changes direction. **Direct Current:** One direction. **Transformers.**",
        "diagram": "assets/diagrams/transformer.png"
    },
    ("S4", "Nuclear Physics"): {
        "text": "### Nuclear Physics\n**Fission:** Splitting nucleus. **Fusion:** Joining nuclei. **Applications.**",
        "diagram": None
    },
    ("S4", "Astrophysics"): {
        "text": "### Astrophysics\nStudy of celestial bodies. **Topics:** Stars, Galaxies, Universe.",
        "diagram": None
    },
    ("S4", "Advanced Mechanics"): {
        "text": "### Advanced Mechanics\n**Circular motion.** **Simple Harmonic Motion.**",
        "diagram": None
    },
}

def get_physics_topics(level: str) -> List[str]:
    """Return list of topics for a given class level. NCDC 2026 only"""
    return [topic for (lvl, topic) in PHYSICS_CONTENT.keys() if lvl == level]

def get_physics_content(level: str, topic: str) -> Dict[str, Any]:
    """Return text and diagram for a topic. NCDC 2026 ONLY. No hallucination."""
    default_response = {
        "text": f"### {topic}\nDetailed NCDC 2026 notes are being generated. Please use AI Assistant for more.",
        "diagram": None
    }
    return PHYSICS_CONTENT.get((level, topic), default_response)
