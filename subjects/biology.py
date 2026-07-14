SYLLABUS = {
    "S1": ["Introduction to Biology", "Animal Cell", "Plant Cell", "Classification of Living Things", "Safety in the Laboratory"],
    "S2": ["Nutrition in Animals", "Nutrition in Plants", "Respiration", "Transport in Animals", "Transport in Plants"],
    "S3": ["Excretion", "Reproduction in Plants", "Reproduction in Humans", "Ecology", "Genetics I"],
    "S4": ["Genetics II", "Evolution", "Human Diseases", "Environmental Conservation", "Biotechnology"]
}

CONTENT = {
    ("S1", "Animal Cell"): {"text": "## Animal Cell\nThe basic unit of animal life. Contains nucleus, cytoplasm, cell membrane, mitochondria.\n**Key Functions:**\n- Nucleus: Controls cell activities\n- Mitochondria: Powerhouse for respiration", "diagram": "animal_cell"},
    ("S1", "Plant Cell"): {"text": "## Plant Cell\nSimilar to animal cell but has cell wall, chloroplasts, and large vacuole.", "diagram": "plant_cell"},
    ("S4", "Genetics II"): {"text": "## Genetics II\nStudy of DNA, RNA, and protein synthesis. DNA carries genetic information.", "diagram": "dna"},
    ("S3", "Reproduction in Humans"): {"text": "## Reproduction in Humans\nCovers male and female reproductive systems and fertilization.", "diagram": "human_reproduction"},
}
# Fill others with default
def get_topics(level):
    return SYLLABUS.get(level, [])

def get_content(level, topic):
    return CONTENT.get((level, topic), {"text": f"## {topic}\nContent for {topic} is coming soon. Ask the AI below for an explanation.", "diagram": None})
