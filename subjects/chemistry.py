from typing import Dict, List, Any

# ==========================================
# UNEB CHEMISTRY SYLLABUS DATABASE (S1-S4 CBC)
# ==========================================
CHEMISTRY_CONTENT: Dict[tuple[str, str], Dict[str, Any]] = {
    # SENIOR 1
    ("S1", "Structure of an Atom"): {
        "text": """### Structure of an Atom
An atom is the smallest particle of an element that can take part in a chemical reaction.
**Sub-atomic Particles:** Protons, Neutrons, Electrons.
""",
        "diagram": "assets/atom.png"
    },
    ("S1", "Periodic Table"): {"text": "### The Periodic Table\nElements arranged in periods and groups based on atomic number.", "diagram": None},
    ("S1", "Chemical Bonding"): {
        "text": """### Chemical Bonding
**Types:** Ionic, Covalent, Metallic. Covalent involves sharing of electrons.
""",
        "diagram": "assets/covalent_water.png"
    },
    ("S1", "Acids Bases Salts"): {"text": "### Acids, Bases and Salts\n**Acids:** Produce H+ ions. **Bases:** Produce OH- ions. **Neutralization.**", "diagram": None},
    ("S1", "Air and Combustion"): {"text": "### Air and Combustion\nAir: 78% N2, 21% O2. Combustion requires fuel, oxygen and heat.", "diagram": None},

    # SENIOR 2
    ("S2", "Water and Hydrogen"): {"text": "### Water and Hydrogen\n**Properties of Water:** Universal solvent. **Hydrogen:** Prepared by reacting metals with acids.", "diagram": "assets/filtration.png"},
    ("S2", "Oxygen"): {"text": "### Oxygen\n**Preparation:** Thermal decomposition of potassium manganate VII.", "diagram": None},
    ("S2", "Carbon and its Compounds"): {"text": "### Carbon and its Compounds\nCarbon forms 4 covalent bonds. Exists as diamond, graphite.", "diagram": None},
    ("S2", "Fertilizers"): {"text": "### Fertilizers\nChemicals added to soil to improve fertility. **Types:** NPK fertilizers.", "diagram": None},
    ("S2", "Metals"): {
        "text": """### Metals
Metals conduct electricity and heat. **Reactivity Series:** Determines displacement reactions.
""",
        "diagram": "assets/fractional_distillation.png"
    },

    # SENIOR 3
    ("S3", "Rates of Reaction"): {"text": "### Rates of Reaction\n**Factors:** Concentration, temperature, surface area, catalyst.", "diagram": None},
    ("S3", "Energy Changes"): {"text": "### Energy Changes\n**Exothermic:** Heat released. **Endothermic:** Heat absorbed.", "diagram": None},
    ("S3", "Chemical Equilibrium"): {"text": "### Chemical Equilibrium\nRate of forward = rate of backward. **Le Chatelier's Principle.**", "diagram": None},
    ("S3", "Acids and Bases"): {"text": "### Acids and Bases\n**pH Scale:** 0-6 acidic, 7 neutral, 8-14 alkaline.", "diagram": None},
    ("S3", "Organic Chemistry"): {"text": "### Organic Chemistry\nStudy of carbon compounds. **Functional Groups.**", "diagram": None},

    # SENIOR 4
    ("S4", "Electrochemistry"): {"text": "### Electrochemistry\nStudy of chemical processes that cause electrons to move.", "diagram": None},
    ("S4", "Nitrogen and Compounds"): {"text": "### Nitrogen and its Compounds\n**Haber Process:** $N_2 + 3H_2 \\leftrightarrow 2NH_3$", "diagram": None},
    ("S4", "Sulphur and Compounds"): {"text": "### Sulphur and its Compounds\n**Contact Process:** Used to manufacture Sulphuric acid.", "diagram": None},
    ("S4", "Industrial Chemistry"): {"text": "### Industrial Chemistry\nLarge scale production of chemicals.", "diagram": None},
    ("S4", "Polymers"): {"text": "### Polymers\nLarge molecules made from repeating monomer units.", "diagram": None},
}

def get_topics(level: str) -> List[str]:
    return [topic for (lvl, topic) in CHEMISTRY_CONTENT.keys() if lvl == level]

def get_content(level: str, topic: str) -> Dict[str, Any]:
    default_response = {"text": f"### {topic}\nDetailed UNEB notes are being generated. Please prompt the AI Assistant below.", "diagram": None}
    return CHEMISTRY_CONTENT.get((level, topic), default_response)
