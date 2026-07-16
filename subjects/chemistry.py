from typing import Dict, List, Any

# ==========================================
# UNEB CHEMISTRY SYLLABUS DATABASE (S1-S4 CBC 2026)
# Aligned to NCDC Uganda
# ==========================================
CHEMISTRY_CONTENT: Dict[tuple[str, str], Dict[str, Any]] = {
    # SENIOR 1
    ("S1", "Introduction to Chemistry"): {
        "text": "### Introduction to Chemistry\nChemistry is the study of matter and its changes. **Branches:** Physical, Organic, Inorganic.",
        "diagram": None
    },
    ("S1", "Matter"): {
        "text": "### Matter\nAnything that has mass and occupies space. **States:** Solid, Liquid, Gas. **Changes:** Physical and Chemical.",
        "diagram": None
    },
    ("S1", "Atoms"): {
        "text": """### Structure of an Atom
An atom is the smallest particle of an element that can take part in a chemical reaction.
**Sub-atomic Particles:** Protons, Neutrons, Electrons.
""",
        "diagram": "assets/diagrams/atom.png"
    },
    ("S1", "Molecules"): {
        "text": "### Molecules\nTwo or more atoms chemically bonded. Example: H2O, CO2.",
        "diagram": None
    },
    ("S1", "Acids Bases"): {
        "text": "### Acids, Bases and Salts\n**Acids:** Produce H+ ions. **Bases:** Produce OH- ions. **Neutralization:** Acid + Base -> Salt + Water",
        "diagram": None
    },
    ("S1", "Air"): {
        "text": "### Air and Combustion\nAir: 78% N2, 21% O2. Combustion requires fuel, oxygen and heat. Products: CO2 and H2O",
        "diagram": None
    },
    ("S1", "Water"): {
        "text": "### Water\n**Properties:** Universal solvent. **Hard water vs Soft water.** **Purification:** Filtration, Distillation.",
        "diagram": "assets/diagrams/filtration.png"
    },
    ("S1", "Chemical Reactions"): {
        "text": "### Chemical Reactions\n**Types:** Combination, Decomposition, Displacement. Represented by chemical equations.",
        "diagram": "assets/diagrams/chemical_reaction.png"
    },

    # SENIOR 2
    ("S2", "Periodic Table"): {"text": "### The Periodic Table\nElements arranged in periods and groups based on atomic number.", "diagram": None},
    ("S2", "Chemical Bonding"): {
        "text": """### Chemical Bonding
**Types:** Ionic, Covalent, Metallic. Covalent involves sharing of electrons. Ionic involves transfer of electrons.
""",
        "diagram": "assets/diagrams/chemical_bonding.png"
    },
    ("S2", "Acids Bases Salts"): {"text": "### Acids, Bases and Salts\n**Indicators:** Litmus, Phenolphthalein. **Preparation of salts.**", "diagram": None},
    ("S2", "Carbon"): {"text": "### Carbon and its Compounds\nCarbon forms 4 covalent bonds. Exists as diamond, graphite. **Allotropes.**", "diagram": "assets/diagrams/hydrocarbon.png"},
    ("S2", "Metals"): {
        "text": """### Metals
Metals conduct electricity and heat. **Reactivity Series:** Determines displacement reactions. **Extraction.**
""",
        "diagram": "assets/diagrams/electrical_cell.png"
    },
    ("S2", "Non-metals"): {"text": "### Non-metals\n**Examples:** Oxygen, Hydrogen, Nitrogen. **Properties:** Brittle, poor conductors.", "diagram": None},
    ("S2", "Energy Changes"): {"text": "### Energy Changes\n**Exothermic:** Heat released. **Endothermic:** Heat absorbed.", "diagram": None},

    # SENIOR 3
    ("S3", "Chemical Kinetics"): {"text": "### Rates of Reaction\n**Factors:** Concentration, temperature, surface area, catalyst. Collision theory.", "diagram": "assets/diagrams/chemical_kinetics.png"},
    ("S3", "Equilibrium"): {"text": "### Chemical Equilibrium\nRate of forward = rate of backward. **Le Chatelier's Principle.**", "diagram": None},
    ("S3", "Electrochemistry"): {"text": "### Electrochemistry\nStudy of chemical processes that cause electrons to move. **Electrolysis.**", "diagram": "assets/diagrams/electrolysis.png"},
    ("S3", "Organic Chemistry"): {"text": "### Organic Chemistry\nStudy of carbon compounds. **Functional Groups:** Alkanes, Alkenes, Alcohols.", "diagram": None},
    ("S3", "Industrial Processes"): {"text": "### Industrial Chemistry\nLarge scale production: Haber Process, Contact Process.", "diagram": None},

    # SENIOR 4
    ("S4", "Advanced Organic"): {"text": "### Advanced Organic\nPolymers, Proteins, Fats. Isomerism.", "diagram": "assets/diagrams/polymers.png"},
    ("S4", "Analytical Chemistry"): {"text": "### Analytical Chemistry\nQualitative and Quantitative analysis. Titration techniques.", "diagram": None},
    ("S4", "Environmental Chemistry"): {"text": "### Environmental Chemistry\nPollution: Air, Water, Soil. Acid rain, Global warming.", "diagram": None},
    ("S4", "Polymers"): {"text": "### Polymers\nLarge molecules made from repeating monomer units. **Examples:** Polythene, PVC.", "diagram": None},
}

def get_chemistry_topics(level: str) -> List[str]:
    """Return list of topics for a given class level"""
    return [topic for (lvl, topic) in CHEMISTRY_CONTENT.keys() if lvl == level]

def get_chemistry_content(level: str, topic: str) -> Dict[str, Any]:
    """Return text and diagram for a topic. NCDC 2026 only"""
    default_response = {
        "text": f"### {topic}\nDetailed UNEB/NCDC 2026 notes are being generated. Please use AI Assistant for more.",
        "diagram": None
    }
    return CHEMISTRY_CONTENT.get((level, topic), default_response)
