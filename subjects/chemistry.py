SYLLABUS = {
    "S1": ["Introduction to Chemistry", "Matter", "Atoms and Molecules", "Chemical Symbols", "Laboratory Apparatus"],
    "S2": ["Air and Combustion", "Water", "Acids, Bases and Salts", "Chemical Reactions", "Atomic Structure"],
    "S3": ["The Periodic Table", "Chemical Bonding", "Mole Concept", "Energy Changes", "Rates of Reaction"],
    "S4": ["Organic Chemistry", "Electrochemistry", "Metals", "Non-Metals", "Chemical Equations"]
}

CONTENT = {
    ("S1", "Atoms and Molecules"): {"text": "## Atoms and Molecules\nAn atom is the smallest particle of an element. Molecules are 2+ atoms bonded together.", "diagram": "atom"},
    ("S3", "Chemical Bonding"): {"text": "## Chemical Bonding\nTypes: Ionic, Covalent, Metallic bonding. Determines properties of compounds.", "diagram": "chemical_bond"},
    ("S4", "Organic Chemistry"): {"text": "## Organic Chemistry\nStudy of carbon compounds. Includes alkanes, alkenes, alcohols.", "diagram": None},
}
def get_topics(level):
    return SYLLABUS.get(level, [])

def get_content(level, topic):
    return CONTENT.get((level, topic), {"text": f"## {topic}\nContent for {topic} is coming soon. Ask the AI below for an explanation.", "diagram": None})
