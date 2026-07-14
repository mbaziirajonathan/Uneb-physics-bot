def get_topics(level):
    topics_db = {
        "S1": ["Cell Biology", "Animal Cell", "Plant Cell"],
        "S2": ["Nutrition", "Photosynthesis", "Circulatory System"],
        "S3": ["Respiration", "Excretion", "Ecology"],
        "S4": ["Genetics", "DNA", "Evolution", "Reproduction"]
    }
    return topics_db.get(level, [])

def get_content(level, topic):
    content_db = {
        ("S1", "Animal Cell"): {
            "text": "### Animal Cell\nAnimal cells have no cell wall. Main parts: Nucleus, Cytoplasm, Cell Membrane, Mitochondria.",
            "diagram": "animal_cell"
        },
        ("S1", "Plant Cell"): {
            "text": "### Plant Cell\nPlant cells have a cell wall and chloroplasts for photosynthesis.",
            "diagram": "plant_cell"
        },
        ("S2", "Photosynthesis"): {
            "text": "### Photosynthesis\nProcess by which green plants make food using sunlight.\n\n**Equation**: 6CO2 + 6H2O + Light -> C6H12O6 + 6O2",
            "diagram": "photosynthesis"
        },
        ("S2", "Circulatory System"): {
            "text": "### Circulatory System\nSystem that transports blood, nutrients and oxygen around the body. Main organ: Heart.",
            "diagram": "circulatory"
        },
        ("S3", "Ecology"): {
            "text": "### Ecology\nStudy of interactions between organisms and their environment.",
            "diagram": "ecosystem"
        },
        ("S4", "DNA"): {
            "text": "### DNA\nDeoxyribonucleic Acid. Carries genetic information. Double helix structure.",
            "diagram": "dna"
        },
    }
    
    default = {"text": f"### {topic}\nContent for {topic} at {level} coming soon. Ask the AI below for help.", "diagram": None}
    return content_db.get((level, topic), default)
