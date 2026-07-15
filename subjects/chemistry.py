from typing import Dict, List, Any

# ==========================================
# UNEB CHEMISTRY SYLLABUS DATABASE (S1-S4 CBC)
# ==========================================
CHEMISTRY_CONTENT: Dict[tuple[str, str], Dict[str, Any]] = {
    # SENIOR 1
    ("S1", "Structure of an Atom"): {
        "text": """### Structure of an Atom
An atom is the smallest particle of an element that can take part in a chemical reaction.

**Sub-atomic Particles:**
* **Protons:** Positively charged, found in the nucleus.
* **Neutrons:** No charge, found in the nucleus.
* **Electrons:** Negatively charged, found in shells around the nucleus.
""",
        "diagram": "assets/atom.png"
    },
    ("S1", "Periodic Table"): {
        "text": """### The Periodic Table
Elements are arranged in periods and groups based on atomic number and electron configuration.

**Key Features:**
* **Groups:** Vertical columns with similar chemical properties.
* **Periods:** Horizontal rows.
* **Trends:** Reactivity increases down group 1 and decreases across a period.
""",
        "diagram": None
    },
    ("S1", "Chemical Bonding"): {
        "text": """### Chemical Bonding
Atoms combine to achieve a stable electron configuration.

**Types of Bonding:**
* **Ionic Bonding:** Transfer of electrons between metals and non-metals.
* **Covalent Bonding:** Sharing of electrons between non-metals.
* **Metallic Bonding:** Sea of delocalized electrons in metals.
""",
        "diagram": None
    },
    ("S1", "Acids Bases Salts"): {
        "text": """### Acids, Bases and Salts
**Acids:** Produce H+ ions in water. Turn blue litmus red.
**Bases:** Produce OH- ions in water. Turn red litmus blue.
**Salts:** Formed when an acid reacts with a base. Neutralization reaction.
""",
        "diagram": None
    },
    ("S1", "Air and Combustion"): {
        "text": """### Air and Combustion
Air is a mixture of gases: 78% Nitrogen, 21% Oxygen, 1% other gases.
**Combustion:** Rapid reaction with oxygen producing heat and light. Requires fuel, oxygen and heat.
""",
        "diagram": None
    },

    # SENIOR 2
    ("S2", "Water and Hydrogen"): {
        "text": """### Water and Hydrogen
**Properties of Water:** Universal solvent, high specific heat capacity.
**Hydrogen:** Prepared in lab by reacting metals with dilute acids. Used in Haber process.
""",
        "diagram": None
    },
    ("S2", "Oxygen"): {
        "text": """### Oxygen
**Preparation:** Thermal decomposition of potassium manganate VII.
**Properties:** Supports combustion, slightly soluble in water.
""",
        "diagram": None
    },
    ("S2", "Carbon and its Compounds"): {
        "text": """### Carbon and its Compounds
Carbon forms 4 covalent bonds. Exists as diamond, graphite, and amorphous forms.
**Organic Compounds:** Alkanes, Alkenes, Alcohols, Carboxylic acids.
""",
        "diagram": None
    },
    ("S2", "Fertilizers"): {
        "text": """### Fertilizers
Chemicals added to soil to improve fertility.
**Types:** NPK fertilizers. Provide Nitrogen for leaf growth, Phosphorus for roots, Potassium for fruits.
""",
        "diagram": None
    },
    ("S2", "Metals"): {
        "text": """### Metals
Metals conduct electricity and heat. Form positive ions.
**Reactivity Series:** Determines displacement reactions and extraction methods.
""",
        "diagram": None
    },

    # SENIOR 3
    ("S3", "Rates of Reaction"): {
        "text": """### Rates of Reaction
The speed at which reactants are converted to products.
**Factors:** Concentration, temperature, surface area, catalyst, pressure.
""",
        "diagram": None
    },
    ("S3", "Energy Changes"): {
        "text": """### Energy Changes in Chemical Reactions
**Exothermic:** Heat is released. e.g. combustion.
**Endothermic:** Heat is absorbed. e.g. photosynthesis.
""",
        "diagram": None
    },
    ("S3", "Chemical Equilibrium"): {
        "text": """### Chemical Equilibrium
A state where rate of forward reaction equals rate of backward reaction.
**Le Chatelier's Principle:** System adjusts to counteract changes in concentration, temperature, pressure.
""",
        "diagram": None
    },
    ("S3", "Acids and Bases"): {
        "text": """### Acids and Bases
**Strength vs Concentration:** Strong acids fully ionize.
**pH Scale:** Measures acidity. pH 0-6 acidic, 7 neutral, 8-14 alkaline.
""",
        "diagram": None
    },
    ("S3", "Organic Chemistry"): {
        "text": """### Organic Chemistry
Study of carbon compounds.
**Functional Groups:** Alkanes, Alkenes, Alkynes, Alcohols, Acids.
""",
        "diagram": None
    },

    # SENIOR 4
    ("S4", "Electrochemistry"): {
        "text": """### Electrochemistry
Study of chemical processes that cause electrons to move.
**Electrolysis:** Decomposition using electricity. Used in extraction and purification of metals.
""",
        "diagram": None
    },
    ("S4", "Nitrogen and Compounds"): {
        "text": """### Nitrogen and its Compounds
**Haber Process:** $N_2 + 3H_2 \\leftrightarrow 2NH_3$
**Uses:** Ammonia for fertilizers, nitric acid for explosives.
""",
        "diagram": None
    },
    ("S4", "Sulphur and Compounds"): {
        "text": """### Sulphur and its Compounds
**Contact Process:** Used to manufacture Sulphuric acid.
**Uses:** Fertilizers, detergents, batteries.
""",
        "diagram": None
    },
    ("S4", "Industrial Chemistry"): {
        "text": """### Industrial Chemistry
Large scale production of chemicals.
**Examples:** Haber Process, Contact Process, Solvay Process.
""",
        "diagram": None
    },
    ("S4", "Polymers"): {
        "text": """### Polymers
Large molecules made from repeating monomer units.
**Examples:** Polyethene, PVC, Proteins, Starch.
""",
        "diagram": None
    },
}

def get_topics(level: str) -> List[str]:
    """Extracts curriculum-mapped topics for a specific class level."""
    return [topic for (lvl, topic) in CHEMISTRY_CONTENT.keys() if lvl == level]

def get_content(level: str, topic: str) -> Dict[str, Any]:
    """Retrieves detailed content and diagram path."""
    default_response = {
        "text": f"### {topic}\nDetailed UNEB notes are being generated. Please prompt the AI Assistant below for a complete breakdown.",
        "diagram": None
    }
    return CHEMISTRY_CONTENT.get((level, topic), default_response)
