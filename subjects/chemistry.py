def get_topics(level):
    topics_db = {
        "S1": ["Introduction to Chemistry", "Structure of an Atom", "Elements, Compounds and Mixtures"],
        "S2": ["Chemical Bonding", "Acids, Bases and Salts", "Air and Combustion"],
        "S3": ["Mole Concept", "Rates of Reaction", "Energy Changes"],
        "S4": ["Organic Chemistry", "Metals", "Electrochemistry"]
    }
    return topics_db.get(level, [])

def get_content(level, topic):
    content_db = {
        ("S1", "Structure of an Atom"): {
            "text": "### Structure of an Atom\nAn atom has a nucleus with protons and neutrons. Electrons orbit in shells.\n\n**Parts**: Nucleus, Electrons, Protons, Neutrons.",
            "diagram": "atom"
        },
        ("S1", "Elements, Compounds and Mixtures"): {
            "text": "### Elements, Compounds and Mixtures\n**Element**: 1 type of atom. **Compound**: 2+ elements chemically joined. **Mixture**: 2+ substances physically mixed.",
            "diagram": None
        },
        ("S2", "Chemical Bonding"): {
            "text": "### Chemical Bonding\nAtoms bond to become stable. 3 types: Ionic, Covalent, Metallic.",
            "diagram": None
        },
        ("S4", "Organic Chemistry"): {
            "text": "### Organic Chemistry\nStudy of carbon compounds. Main groups: Alkanes, Alkenes, Alcohols, Acids.",
            "diagram": None
        },
    }
    
    default = {"text": f"### {topic}\nContent for {topic} at {level} coming soon. Ask the AI below for help.", "diagram": None}
    return content_db.get((level, topic), default)
