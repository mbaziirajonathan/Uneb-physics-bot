from typing import Dict, List, Any

# ==========================================
# UNEB CHEMISTRY SYLLABUS DATABASE (S1-S4 CBC)
# ==========================================
CHEMISTRY_CONTENT: Dict[tuple[str, str], Dict[str, Any]] = {
    # SENIOR 1
    ("S1", "Introduction to Chemistry and Lab Apparatus"): {
        "text": """### Introduction to Chemistry
Chemistry is the study of the composition, structure, properties, and behavior of matter.

**Common Laboratory Apparatus:**
*   **Beaker & Flasks:** Holding and heating liquids.
*   **Pipette & Burette:** Highly accurate volume measurements for titrations.
*   **Bunsen Burner:** Providing heat. Features a luminous (yellow) and non-luminous (blue, hotter) flame depending on the air-hole configuration.
""",
        "diagram": "bunsen_burner"
    },
    ("S1", "Mixtures, Elements, and Compounds"): {
        "text": """### Classifying Matter
*   **Elements:** Pure substances consisting of only one type of atom (e.g., Oxygen, Iron). Cannot be broken down further chemically.
*   **Compounds:** Two or more elements chemically combined in fixed ratios (e.g., $H_2O$, $CO_2$). Their properties differ entirely from their constituent elements.
*   **Mixtures:** Two or more substances physically combined but not chemically bonded (e.g., Air, Sand and Water). They can be separated by physical means.

**Separation Techniques:** Filtration, Distillation, Chromatography, Evaporation.
""",
        "diagram": "distillation"
    },

    # SENIOR 2
    ("S2", "Atomic Structure and Periodic Table"): {
        "text": """### Atomic Structure
The atom consists of a central, dense nucleus surrounded by orbiting electrons.

**Subatomic Particles:**
*   **Protons:** Positive charge (+1), mass = 1 amu (in nucleus).
*   **Neutrons:** Neutral charge (0), mass = 1 amu (in nucleus).
*   **Electrons:** Negative charge (-1), mass ≈ 0 (in electron shells).

**The Periodic Table:**
*   Elements are arranged by increasing atomic number (number of protons).
*   **Groups:** Vertical columns indicating the number of valence (outermost) electrons.
*   **Periods:** Horizontal rows indicating the number of electron shells.
""",
        "diagram": "atom"
    },
    ("S2", "Acids, Bases, and Salts"): {
        "text": """### Acids, Bases, and Salts
*   **Acids:** Proton ($H^+$) donors in an aqueous solution. They turn blue litmus paper red and have a pH < 7. (e.g., $HCl$, $H_2SO_4$).
*   **Bases/Alkalis:** Proton acceptors. Alkalis release hydroxide ions ($OH^-$) in solution. They turn red litmus paper blue and have a pH > 7. (e.g., $NaOH$).
*   **Salts:** Ionic compounds formed when the hydrogen of an acid is completely or partially replaced by a metal or ammonium ion. Formed via neutralization: Acid + Base $\\rightarrow$ Salt + Water.
""",
        "diagram": "ph_scale"
    },

    # SENIOR 3
    ("S3", "Chemical Bonding and Structure"): {
        "text": """### Chemical Bonding
Atoms bond to achieve a stable, full outer electron shell (octet or duplet).

**Types of Bonding:**
*   **Ionic Bonding:** Transfer of electrons from a metal to a non-metal, forming oppositely charged ions that attract electrostatically (e.g., $NaCl$).
*   **Covalent Bonding:** Sharing of electron pairs between non-metal atoms (e.g., $H_2O$, $CO_2$).
*   **Metallic Bonding:** A lattice of positive metal ions in a "sea" of delocalized electrons, explaining high electrical conductivity.
""",
        "diagram": "ionic_bond"
    },
    ("S3", "Moles and Stoichiometry"): {
        "text": """### The Mole Concept
The mole is the SI unit for the amount of substance. 

**Avogadro's Constant:**
*   One mole contains exactly $6.022 \\times 10^{23}$ particles (atoms, molecules, or ions).

**Key Formulas:**
*   Mass = Moles $\\times$ Molar Mass (RMM/RAM).
*   Molarity = Moles / Volume ($dm^3$).
""",
        "diagram": "mole_triangle"
    },

    # SENIOR 4
    ("S4", "REDOX Reactions"): {
        "text": """### Oxidation and Reduction (REDOX)
Reactions where electrons are transferred between chemical species.

**Definitions (OIL RIG):**
*   **Oxidation:** Is Loss of electrons (or gain of oxygen, loss of hydrogen).
*   **Reduction:** Is Gain of electrons (or loss of oxygen, gain of hydrogen).

**Oxidizing and Reducing Agents:**
*   An oxidizing agent oxidizes another substance and is itself reduced.
*   A reducing agent reduces another substance and is itself oxidized.
""",
        "diagram": "redox_reaction"
    },
    ("S4", "Industrial Chemistry Processes"): {
        "text": """### Industrial Chemistry
Application of chemical principles to manufacture bulk materials safely and profitably.

**Key Processes:**
*   **Haber Process:** Manufacture of Ammonia ($NH_3$) from Nitrogen and Hydrogen. Uses an iron catalyst at 450°C and 200 atm pressure.
*   **Contact Process:** Manufacture of Sulfuric Acid ($H_2SO_4$). Uses a Vanadium(V) oxide ($V_2O_5$) catalyst.
*   **Extraction of Metals:** Using carbon reduction (for Iron in a blast furnace) or electrolysis (for Aluminum).
""",
        "diagram": "blast_furnace"
    }
}

def get_topics(level: str) -> List[str]:
    return [topic for (lvl, topic) in CHEMISTRY_CONTENT.keys() if lvl == level]

def get_content(level: str, topic: str) -> Dict[str, Any]:
    default_response = {
        "text": f"### {topic}\nCurriculum update in progress. Please ask the AI engine to generate the required formulation.", 
        "diagram": None
    }
    return CHEMISTRY_CONTENT.get((level, topic), default_response)
