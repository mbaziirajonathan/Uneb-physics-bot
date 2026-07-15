from typing import Dict, List, Any

# ==========================================
# UNEB PHYSICS SYLLABUS DATABASE (S1-S4 CBC)
# ==========================================
PHYSICS_CONTENT: Dict[tuple[str, str], Dict[str, Any]] = {
    # SENIOR 2
    ("S2", "Electroscope"): {
        "text": """### Electroscope
An instrument used to detect electric charge and to determine its type.

**How it works:**
* Like charges repel. The gold leaves diverge when charged.
* Used to test for presence and type of charge.
""",
        "diagram": "assets/electroscope.png"
    },
    ("S2", "Refraction"): {
        "text": """### Refraction of Light
The bending of light as it passes from one medium to another of different optical density.

**Laws of Refraction:**
* The incident ray, refracted ray and normal all lie in the same plane.
* $n = \\frac{\\sin i}{\\sin r}$
""",
        "diagram": "assets/refraction.png"
    },
    ("S2", "Waves"): {
        "text": """### Wave Motion
A wave is a disturbance that transfers energy from one point to another without transfer of matter.

**Wave Types:**
* **Transverse:** Vibration perpendicular to wave motion. e.g. light.
* **Longitudinal:** Vibration parallel to wave motion. e.g. sound.
""",
        "diagram": "assets/wave.png"
    },

    # SENIOR 3
    ("S3", "Hookes Law"): {
        "text": """### Hooke's Law
States that extension of a spring is directly proportional to the applied force, provided elastic limit is not exceeded.
$$F = ke$$
Where k = spring constant, e = extension.
""",
        "diagram": "assets/hookes_law.png"
    },
    ("S3", "Specific Heat Capacity"): {
        "text": """### Specific Heat Capacity
The amount of heat required to raise the temperature of 1kg of a substance by 1°C.
$$Q = mc\\theta$$
""",
        "diagram": "assets/specific_heat.png"
    },

    # SENIOR 4
    ("S4", "Transformers"): {
        "text": """### Transformers
A device used to step up or step down AC voltage.

**Principle:** Electromagnetic Induction.
$$\\frac{V_p}{V_s} = \\frac{N_p}{N_s}$$
""",
        "diagram": "assets/ac_transformer.png"
    },
    ("S4", "X-Ray Production"): {
        "text": """### X-Ray Production
X-rays are produced when fast moving electrons are suddenly stopped by a metal target.

**X-Ray Tube:** Contains cathode and anode in a vacuum tube.
""",
        "diagram": "assets/xray_tube.png"
    },
}

def get_topics(level: str) -> List[str]:
    """Extracts curriculum-mapped topics for a specific class level."""
    return [topic for (lvl, topic) in PHYSICS_CONTENT.keys() if lvl == level]

def get_content(level: str, topic: str) -> Dict[str, Any]:
    """Retrieves detailed content and diagram path."""
    default_response = {
        "text": f"### {topic}\nDetailed UNEB notes are being generated. Please prompt the AI Assistant below for a complete breakdown.",
        "diagram": None
    }
    return PHYSICS_CONTENT.get((level, topic), default_response)
