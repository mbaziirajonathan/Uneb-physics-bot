def get_topics(level):
    topics_db = {
        "S1": ["Introduction to Physics", "Forces", "Electrostatics"],
        "S2": ["Light - Refraction", "Current Electricity", "Heat"],
        "S3": ["Waves", "Magnetism", "Energy"],
        "S4": ["Electromagnetic Induction", "Transformers", "X-Ray Tube", "Atomic Physics"]
    }
    return topics_db.get(level, [])

def get_content(level, topic):
    content_db = {
        ("S1", "Forces"): {
            "text": "### Forces\nA force is a push or pull on an object. We measure force in Newtons (N).\n\n**Hooke's Law**: Extension is directly proportional to force applied.",
            "diagram": "hookes_law"
        },
        ("S1", "Electrostatics"): {
            "text": "### Electrostatics\nStudy of charges at rest. Like charges repel, unlike charges attract.\n\n**Gold Leaf Electroscope** is used to detect charge.",
            "diagram": "electroscope"
        },
        ("S2", "Light - Refraction"): {
            "text": "### Refraction of Light\nRefraction is the bending of light as it passes from one medium to another.\n\nWe use a glass block and pins to find refractive index.",
            "diagram": "refraction"
        },
        ("S2", "Current Electricity"): {
            "text": "### Current Electricity\nElectric current is flow of electrons. \n\n**Specific Heat Capacity**: Heat energy needed to raise 1kg by 1K.",
            "diagram": "specific_heat"
        },
        ("S4", "Transformers"): {
            "text": "### Transformers\nA transformer steps up or steps down AC voltage. It works on electromagnetic induction.\n\n**Formula**: Vs/Vp = Ns/Np",
            "diagram": "transformer"
        },
        ("S4", "X-Ray Tube"): {
            "text": "### X-Ray Tube\nX-rays are produced when fast electrons hit a metal target.\n\nUsed in medicine and industry.",
            "diagram": "xray_tube"
        },
    }
    
    default = {"text": f"### {topic}\nContent for {topic} at {level} coming soon. Ask the AI below for help.", "diagram": None}
    return content_db.get((level, topic), default)
