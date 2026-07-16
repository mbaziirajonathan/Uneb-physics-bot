from typing import Dict, List, Any

# ==========================================
# UNEB BIOLOGY SYLLABUS DATABASE (S1-S4 CBC 2026)
# Aligned to NCDC Uganda
# ==========================================
BIOLOGY_CONTENT: Dict[tuple[str, str], Dict[str, Any]] = {
    # SENIOR 1
    ("S1", "Introduction to Biology"): {
        "text": "### Introduction to Biology\nBiology is the study of living organisms. **Branches:** Botany, Zoology, Ecology.",
        "diagram": None
    },
    ("S1", "Cells"): {
        "text": """### Plant Cell
Cells are the microscopic building blocks of all living organisms.
**Plant Cells:** Have cell wall, large vacuole, chloroplasts.
**Animal Cells:** No cell wall, no chloroplasts.
""",
        "diagram": "assets/diagrams/plant_cell.png"
    },
    ("S1", "Classification"): {
        "text": """### Classification of Living Organisms
Grouping organisms based on shared characteristics.
**Five Kingdoms:** Monera, Protoctista, Fungi, Plantae, Animalia.
""",
        "diagram": None
    },
    ("S1", "Nutrition"): {
        "text": """### Nutrition in Plants
Autotrophic nutrition. Main process is Photosynthesis.
$6CO_2 + 6H_2O \\xrightarrow{light} C_6H_{12}O_6 + 6O_2$
""",
        "diagram": None
    },
    ("S1", "Respiration"): {
        "text": "### Respiration\nBreakdown of glucose to release energy. Occurs in mitochondria.",
        "diagram": None
    },
    ("S1", "Transport"): {
        "text": "### Transport in Plants\n**Xylem:** Transports water and minerals. **Phloem:** Transports food.",
        "diagram": "assets/diagrams/transport_in_plants.png"
    },
    ("S1", "Ecology"): {
        "text": """### Ecosystem
A community of living organisms interacting with their physical environment.
**Components:** Producers, Consumers, Decomposers. **Energy flow:** Sun -> Producer -> Consumer.
""",
        "diagram": "assets/diagrams/ecology.png"
    },

    # SENIOR 2
    ("S2", "Reproduction"): {
        "text": """### Reproduction in Plants
**Asexual:** Budding, cuttings. **Sexual:** Involves flowers. Pollination and fertilization.
""",
        "diagram": None
    },
    ("S2", "Genetics"): {"text": "### Genetics\nStudy of inheritance. **Mendel's Laws.**", "diagram": None},
    ("S2", "Growth"): {"text": "### Growth\nPermanent increase in size and dry mass. Factors: food, water, temperature.", "diagram": "assets/diagrams/growth_cycles.png"},
    ("S2", "Human Body Systems"): {
        "text": """### Human Body Systems
Major systems: Circulatory, Respiratory, Digestive, Nervous, Excretory.
""",
        "diagram": "assets/diagrams/body_systems.png"
    },
    ("S2", "Disease"): {"text": "### Disease\n**Infectious:** Bacteria, Virus. **Non-infectious:** Diabetes, Cancer.", "diagram": None},
    ("S2", "Immunity"): {"text": "### Immunity\nBody's defense against pathogens. **Antibodies, Vaccines.**", "diagram": None},
    ("S2", "Respiratory System"): {
        "text": "### Respiratory System\n**Organs:** Nose, Trachea, Bronchi, Lungs, Alveoli, Diaphragm. Gas exchange occurs in alveoli.",
        "diagram": "assets/diagrams/respiratory_system.png"
    },
    ("S2", "Alveolus"): {
        "text": "### Alveolus\nSite of gas exchange. Thin wall, moist, surrounded by capillaries for diffusion of O2 and CO2.",
        "diagram": "assets/diagrams/alveolus.png"
    },
    ("S2", "Human Ear"): {
        "text": "### Human Ear\n**Functions:** Hearing and Balance. Parts: Pinna, Ear canal, Cochlea, Auditory nerve.",
        "diagram": "assets/diagrams/human_ear.png"
    },
    ("S2", "Human Eye"): {
        "text": "### Human Eye\n**Function:** Sight. Parts: Cornea, Iris, Lens, Retina, Optic nerve.",
        "diagram": "assets/diagrams/human_eye.png"
    },

    # SENIOR 3
    ("S3", "Ecology II"): {"text": "### Ecology\nStudy of interactions between organisms and environment. Energy pyramids, food webs.", "diagram": None},
    ("S3", "Evolution"): {"text": "### Evolution\nChange in characteristics over generations. **Natural Selection.**", "diagram": None},
    ("S3", "Genetics II"): {"text": "### DNA\nDeoxyribonucleic acid. Carrier of genetic information. **Structure:** Double helix.", "diagram": "assets/diagrams/dna.png"},
    ("S3", "Physiology"): {"text": "### Physiology\nStudy of functions of living organisms.", "diagram": None},
    ("S3", "Microbiology"): {"text": "### Microbiology\nStudy of microorganisms: Bacteria, Fungi, Viruses.", "diagram": "assets/diagrams/microbiology_eukaryotic_and_prokaryotic_cells.png"},

    # SENIOR 4
    ("S4", "Molecular Biology"): {"text": "### Molecular Biology\nStudy of DNA, RNA, protein synthesis.", "diagram": None},
    ("S4", "Biotechnology"): {"text": "### Biotechnology\nUse of living organisms to make useful products: yoghurt, beer, insulin.", "diagram": None},
    ("S4", "Conservation"): {"text": "### Conservation\nProtection of environment and biodiversity.", "diagram": None},
    ("S4", "Human Health"): {"text": "### Human Health\n**Brain:** Control center. **Diseases:** HIV, Malaria.", "diagram": "assets/diagrams/human_brain.png"},
}

def get_biology_topics(level: str) -> List[str]:
    """Return list of topics for a given class level"""
    return [topic for (lvl, topic) in BIOLOGY_CONTENT.keys() if lvl == level]

def get_biology_content(level: str, topic: str) -> Dict[str, Any]:
    """Return text and diagram for a topic. NCDC 2026 only"""
    default_response = {
        "text": f"### {topic}\nDetailed UNEB/NCDC 2026 notes are being generated. Please use AI Assistant for more.",
        "diagram": None
    }
    return BIOLOGY_CONTENT.get((level, topic), default_response)
