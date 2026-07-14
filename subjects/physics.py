from typing import Dict, List, Any

# ==========================================
# UNEB PHYSICS SYLLABUS DATABASE (S1-S4 CBC)
# ==========================================
PHYSICS_CONTENT: Dict[tuple[str, str], Dict[str, Any]] = {
    # SENIOR 1
    ("S1", "Introduction to Measurements"): {
        "text": """### Measurements in Physics
Physics relies heavily on accurate measurements of physical quantities.

**Fundamental Quantities & SI Units:**
*   **Length:** Metre (m) - measured using rulers or Vernier calipers.
*   **Mass:** Kilogram (kg) - measured using a beam balance.
*   **Time:** Second (s) - measured using a stopwatch.
*   **Temperature:** Kelvin (K) - measured using a thermometer.

**Volume and Density:**
*   Density = Mass / Volume.
*   Measured in $kg/m^3$ or $g/cm^3$.
""",
        "diagram": "vernier_caliper"
    },
    ("S1", "States of Matter and Particulate Nature"): {
        "text": """### States of Matter
Matter exists in three primary states: Solid, Liquid, and Gas.

**Kinetic Theory of Matter:**
*   **Solids:** Particles are tightly packed in a regular lattice and vibrate in fixed positions. High density, fixed shape.
*   **Liquids:** Particles are close but can slide past each other. Fixed volume, takes the shape of the container.
*   **Gases:** Particles are far apart and move randomly at high speeds. Low density, highly compressible.
""",
        "diagram": "states_of_matter"
    },

    # SENIOR 2
    ("S2", "Mechanics: Forces and Motion"): {
        "text": """### Forces and Motion
A force is a push or pull that alters an object's state of rest or uniform motion.

**Newton's Laws of Motion:**
1.  **Inertia:** An object remains at rest or in uniform motion unless acted upon by a net external force.
2.  **Acceleration:** Force = Mass × Acceleration ($F = ma$).
3.  **Action/Reaction:** For every action, there is an equal and opposite reaction.

**Types of Forces:** Friction, Gravity, Tension, Upthrust.
""",
        "diagram": "forces_on_block"
    },
    ("S2", "Optics: Reflection and Refraction"): {
        "text": """### Light and Optics
Light travels in straight lines but changes direction when encountering boundaries.

**Reflection:**
*   The bouncing back of light from a surface.
*   Angle of Incidence = Angle of Reflection.

**Refraction:**
*   The bending of light as it passes from one optical medium to another (e.g., air to glass) due to a change in speed.
*   Governed by Snell's Law.
""",
        "diagram": "refraction"
    },

    # SENIOR 3
    ("S3", "Work, Energy, and Power"): {
        "text": """### Work, Energy, and Power
**Work Done:**
*   Work is done when a force moves an object through a distance in the direction of the force.
*   $Work = Force \\times Distance$. Unit: Joules (J).

**Energy:**
*   The capacity to do work.
*   **Potential Energy (PE):** $PE = mgh$ (Energy due to position).
*   **Kinetic Energy (KE):** $KE = \\frac{1}{2}mv^2$ (Energy due to motion).

**Power:**
*   The rate of doing work. $Power = \\frac{Work}{Time}$. Unit: Watts (W).
""",
        "diagram": "pendulum_energy"
    },
    ("S3", "Current Electricity"): {
        "text": """### Current Electricity
The continuous flow of electric charge (electrons) through a conductor.

**Key Terms:**
*   **Voltage (V):** The potential difference pushing electrons. Measured in Volts.
*   **Current (I):** The rate of flow of charge. Measured in Amperes.
*   **Resistance (R):** Opposition to current flow. Measured in Ohms ($\\Omega$).

**Ohm's Law:** 
*   $V = I \\times R$.
""",
        "diagram": "circuit_diagram"
    },

    # SENIOR 4
    ("S4", "Electromagnetism and Induction"): {
        "text": """### Electromagnetism
A magnetic field is created around any conductor carrying an electric current.

**Electromagnetic Induction (Faraday's Law):**
*   An electromotive force (EMF) is induced in a circuit when the magnetic flux linking the circuit changes.
*   **Applications:** Step-up and Step-down Transformers, AC Generators.
""",
        "diagram": "transformer"
    },
    ("S4", "Modern Physics: Cathode Rays and X-Rays"): {
        "text": """### Modern Physics
**Cathode Rays:**
*   Streams of fast-moving electrons emitted from a heated cathode in a vacuum tube.
*   Deflected by both electric and magnetic fields.

**X-Rays:**
*   High-energy electromagnetic radiation produced when fast-moving electrons strike a heavy metal target (like Tungsten).
*   Highly penetrating; used in medical imaging.
""",
        "diagram": "xray_tube"
    }
}

def get_topics(level: str) -> List[str]:
    return [topic for (lvl, topic) in PHYSICS_CONTENT.keys() if lvl == level]

def get_content(level: str, topic: str) -> Dict[str, Any]:
    default_response = {
        "text": f"### {topic}\nCurriculum modules loading. Ask the AI Tutor for the detailed formulation.", 
        "diagram": None
    }
    return PHYSICS_CONTENT.get((level, topic), default_response)
