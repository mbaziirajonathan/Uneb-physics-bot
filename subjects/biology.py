from typing import Dict, List, Any

# ==========================================
# UNEB BIOLOGY SYLLABUS DATABASE (S1-S4 CBC)
# ==========================================
BIOLOGY_CONTENT: Dict[tuple[str, str], Dict[str, Any]] = {
    # SENIOR 1
    ("S1", "Plant Cell"): {
        "text": """### Plant Cell
Cells are the microscopic building blocks of all living organisms.
**Plant Cells:** Have cell wall, large vacuole, chloroplasts.
**Animal Cells:** No cell wall, no chloroplasts.
""",
        "diagram": "assets/plant_cell.png"
    },
    ("S1", "Ecosystem"): {
        "text": """### Ecosystem
A community of living organisms interacting with their physical environment.
**Components:** Producers, Consumers, Decomposers. **Energy flow:** Sun -> Producer -> Consumer.
""",
        "diagram": "assets/ecosystem.png"
    },
    ("S1", "Classification"): {
        "text": """### Classification of Living Organisms
Grouping organisms based on shared characteristics.
**Five Kingdoms:** Monera, Protoctista, Fungi, Plantae, Animalia.
""",
        "diagram": None
    },
    ("S1", "Nutrition in Plants"): {
        "text": """### Nutrition in Plants
Autotrophic nutrition. Main process is Photosynthesis.
$6CO_2 + 6H_2O \\xrightarrow{light} C_6H_{12}O_6 + 6O_2$
""",
        "diagram": None
    },
    ("S1", "Nutrition in Animals"): {
        "text": """### Nutrition in Animals
Heterotrophic nutrition. Types: Holozoic, Parasitic, Saprophytic.
**Human Digestive System:** Mouth -> Oesophagus -> Stomach -> Small Intestine -> Large Intestine.
""",
        "diagram": None
    },

    # SENIOR 2
    ("S2", "Circulatory System"): {
        "text": """### Circulatory System
Transport system in animals. **Components:** Heart, Blood, Blood vessels.
**Functions:** Transport of nutrients, gases, waste.
""",
        "diagram": "assets/circulatory.png"
    },
    ("S2", "Photosynthesis"): {
        "text": """### Photosynthesis
Process by which green plants manufacture food using light energy.
**Factors:** Light, CO2, Water, Chlorophyll, Temperature.
""",
        "diagram": "assets/photosynthesis.png"
    },
    ("S2", "Respiration"): {
        "text": """### Respiration
Breakdown of glucose to release energy.
**Aerobic:** With oxygen. **Anaerobic:** Without oxygen. Occurs in mitochondria.
""",
        "diagram": None
    },
    ("S2", "Excretion"): {
        "text": """### Excretion
Removal of metabolic waste. 
**Organs:** Kidneys, Skin, Lungs, Liver. **Kidney function:** Osmoregulation.
""",
        "diagram": None
    },
    ("S2", "Reproduction in Plants"): {
        "text": """### Reproduction in Plants
**Asexual:** Budding, cuttings. **Sexual:** Involves flowers. Pollination and fertilization.
""",
        "diagram": None
    },

    # SENIOR 3
    ("S3", "DNA"): {
        "text": """### DNA
Deoxyribonucleic acid. Carrier of genetic information.
**Structure:** Double helix. **Units:** Nucleotides with base pairs A-T, C-G.
""",
        "diagram": "assets/dna.png"
    },
    ("S3", "Cell Division"): {
        "text": """### Cell Division
**Mitosis:** For growth, 2 identical diploid cells.
**Meiosis:** For gametes, 4 non-identical haploid cells.
""",
        "diagram": None
    },
    ("S3", "Genetics"): {
        "text": """### Genetics
Study of inheritance. **Mendel's Laws.** **Terms:** Gene, Allele, Dominant, Recessive, Genotype, Phenotype.
""",
        "diagram": None
    },
    ("S3", "Evolution"): {
        "text": """### Evolution
Change in characteristics of species over generations.
**Theories:** Lamarckism, Darwin's Natural Selection.
""",
        "diagram": None
    },
    ("S3", "Ecology"): {
        "text": """### Ecology
Study of interactions between organisms and environment.
**Concepts:** Food chains, Food webs, Energy pyramids, Conservation.
""",
        "diagram": None
    },

    # SENIOR 4
    ("S4", "Human Reproduction"): {
        "text": """### Human Reproduction
**Male:** Testes produce sperm. **Female:** Ovaries produce ova.
**Menstrual Cycle:** 28 days. Fertilization in fallopian tube.
""",
        "diagram": None
    },
    ("S4", "Nervous System"): {
        "text": """### Nervous System
**Central:** Brain and Spinal cord. **Peripheral:** Nerves.
**Neuron:** Sensory, Relay, Motor. Transmission via electrical impulses.
""",
        "diagram": None
    },
    ("S4", "Homeostasis"): {
        "text": """### Homeostasis
Maintenance of constant internal environment.
**Examples:** Temperature regulation, Osmoregulation, Blood glucose regulation.
""",
        "diagram": None
    },
    ("S4", "Immunity"): {
        "text": """### Immunity
Body's defense against pathogens.
**Types:** Natural, Artificial. **Cells:** Lymphocytes, Antibodies.
""",
        "diagram": None
    },
    ("S4", "Biotechnology"): {
        "text": """### Biotechnology
Use of living organisms to make useful products.
**Examples:** Brewing, Baking, Genetic engineering, IVF.
""",
        "diagram": None
    },
}

def get_topics(level: str) -> List[str]:
    return [topic for (lvl, topic) in BIOLOGY_CONTENT.keys() if lvl == level]

def get_content(level: str, topic: str) -> Dict[str, Any]:
    default_response = {"text": f"### {topic}\nDetailed UNEB notes are being generated. Please prompt the AI Assistant below.", "diagram": None}
    return BIOLOGY_CONTENT.get((level, topic), default_response)
