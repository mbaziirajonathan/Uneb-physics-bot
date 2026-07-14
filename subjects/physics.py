SYLLABUS = {
    "S1": ["Introduction to Physics", "Measurement", "Force", "Work, Energy and Power", "Light"],
    "S2": ["Pressure", "Heat", "Sound", "Magnetism", "Electricity I"],
    "S3": ["Waves", "Current Electricity", "Simple Machines", "Density", "Reflection of Light"],
    "S4": ["Radioactivity", "Electronics", "Gravitation", "Electromagnetic Waves", "Nuclear Physics"]
}

CONTENT = {
    ("S1", "Force"): {"text": "## Force\nA push or pull that can change motion. Measured in Newtons. F = ma", "diagram": "forces"},
    ("S2", "Electricity I"): {"text": "## Electricity I\nCovers current, voltage, resistance. Ohm's Law: V = IR", "diagram": "circuit"},
    ("S4", "Radioactivity"): {"text": "## Radioactivity\nSpontaneous decay of unstable nuclei. Types: Alpha, Beta, Gamma.", "diagram": None},
}
def get_topics(level):
    return SYLLABUS.get(level, [])

def get_content(level, topic):
    return CONTENT.get((level, topic), {"text": f"## {topic}\nContent for {topic} is coming soon. Ask the AI below for an explanation.", "diagram": None})
