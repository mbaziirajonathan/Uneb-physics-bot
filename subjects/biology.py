from typing import Dict, List, Any

# ==========================================
# UNEB BIOLOGY SYLLABUS DATABASE (S1-S4 CBC)
# ==========================================
BIOLOGY_CONTENT: Dict[tuple[str, str], Dict[str, Any]] = {
    # SENIOR 1
    ("S1", "Introduction to Biology"): {
        "text": """### Introduction to Biology
Biology is the study of living things and their interactions with the environment.

**Characteristics of Living Things (MRS GREN):**
*   **Movement:** Changing position or location.
*   **Respiration:** Generating energy from food.
*   **Sensitivity:** Responding to environmental stimuli.
*   **Growth:** Permanent increase in size and dry mass.
*   **Reproduction:** Producing offspring.
*   **Excretion:** Removal of metabolic waste.
*   **Nutrition:** Obtaining food for energy and growth.
""",
        "diagram": "living_things"
    },
    ("S1", "Cells: The Basic Unit of Life"): {
        "text": """### Cell Structure and Organization
Cells are the microscopic building blocks of all living organisms.

**Comparing Plant and Animal Cells:**
*   **Animal Cells:** Contain a nucleus (controls activities), cell membrane (selectively permeable), cytoplasm (site of reactions), and mitochondria (respiration).
*   **Plant Cells:** Contain all animal cell parts, plus a rigid cellulose cell wall, a large central vacuole (for turgor pressure), and chloroplasts (for photosynthesis).
""",
        "diagram": "plant_animal_cells"
    },
    ("S1", "Classification of Living Organisms"): {
        "text": """### Classification
Organisms are grouped based on shared characteristics to make studying them easier. 

**The Five Kingdoms:**
1.  **Monera:** Bacteria (prokaryotic).
2.  **Protoctista:** Amoeba, algae (single-celled eukaryotes).
3.  **Fungi:** Mushrooms, molds (saprophytic nutrition).
4.  **Plantae:** Mosses, ferns, flowering plants (photosynthetic).
5.  **Animalia:** Invertebrates and vertebrates (heterotrophic).
""",
        "diagram": "five_kingdoms"
    },

    # SENIOR 2
    ("S2", "Nutrition in Plants (Photosynthesis)"): {
        "text": """### Photosynthesis
The process by which autotrophs (green plants) manufacture glucose using light energy.

**Process Requirements:**
*   **Light Energy:** Absorbed by chlorophyll.
*   **Carbon Dioxide:** Enters leaves through stomata.
*   **Water:** Absorbed by roots and transported via xylem.
*   **Equation:** $6CO_2 + 6H_2O \\rightarrow C_6H_{12}O_6 + 6O_2$
""",
        "diagram": "photosynthesis"
    },
    ("S2", "Transport in Plants and Animals"): {
        "text": """### Transport Systems
Transport systems move necessary substances to cells and remove metabolic wastes.

**In Animals:**
*   **Heart:** The central pump.
*   **Vessels:** Arteries (carry oxygenated blood away), Veins (return deoxygenated blood), Capillaries (exchange site).

**In Plants:**
*   **Xylem:** Transports water and dissolved mineral salts from roots to leaves.
*   **Phloem:** Transports manufactured food (sucrose) from leaves to other parts (translocation).
""",
        "diagram": "heart"
    },
    ("S2", "Gaseous Exchange and Respiration"): {
        "text": """### Gaseous Exchange & Respiration
Respiration is the chemical breakdown of glucose to release energy, while gaseous exchange is the physical swapping of oxygen and carbon dioxide.

**Aerobic Respiration:**
*   Requires oxygen.
*   Produces a large amount of energy, water, and carbon dioxide.
*   Occurs in the mitochondria.
""",
        "diagram": "alveolus"
    },

    # SENIOR 3
    ("S3", "Coordination in Plants and Animals"): {
        "text": """### Coordination
Coordination ensures all body systems work harmoniously in response to stimuli.

**Nervous System (Animals):**
*   Uses electrical impulses transmitted via neurons.
*   Fast-acting, short-lived response.

**Endocrine System (Animals):**
*   Uses chemical hormones transported in blood.
*   Slower acting, longer-lasting response.

**Plant Tropisms:**
*   Phototropism (growth towards light) and Geotropism (growth in response to gravity), regulated by auxins.
""",
        "diagram": "neuron"
    },
    ("S3", "Excretion and Homeostasis"): {
        "text": """### Excretion and Homeostasis
Homeostasis is the maintenance of a constant internal environment. Excretion is the removal of metabolic waste.

**Key Organs:**
*   **Kidneys:** Filter blood to produce urine, regulating water and salt balance (osmoregulation).
*   **Skin:** Regulates body temperature via sweating and vasodilation/vasoconstriction.
*   **Liver:** Deaminates excess amino acids to form urea.
""",
        "diagram": "kidney"
    },

    # SENIOR 4
    ("S4", "Genetics and Variation"): {
        "text": """### Genetics and DNA
Genetics studies inheritance and variation of traits passed from parents to offspring.

**Core Concepts:**
*   **DNA:** Deoxyribonucleic acid, arranged in a double helix.
*   **Chromosomes:** Thread-like structures of DNA.
*   **Genes:** Sections of DNA that code for specific proteins.
*   **Mitosis:** Cell division for growth (produces identical diploid cells).
*   **Meiosis:** Cell division for gamete formation (produces non-identical haploid cells).
""",
        "diagram": "dna"
    },
    ("S4", "Reproduction in Organisms"): {
        "text": """### Reproduction
The biological process by which new individual organisms are produced.

**Asexual vs. Sexual:**
*   **Asexual:** Requires one parent; offspring are genetically identical clones (e.g., binary fission in amoeba).
*   **Sexual:** Involves the fusion of male and female gametes (fertilization) leading to genetic variation.
""",
        "diagram": "flower_structure"
    }
}

def get_topics(level: str) -> List[str]:
    """Extracts curriculum-mapped topics for a specific class level."""
    return [topic for (lvl, topic) in BIOLOGY_CONTENT.keys() if lvl == level]

def get_content(level: str, topic: str) -> Dict[str, Any]:
    """Retrieves detailed content and triggers precise SVG rendering."""
    default_response = {
        "text": f"### {topic}\nDetailed UNEB notes are being generated. Please prompt the AI Assistant below for a complete breakdown.",
        "diagram": None
    }
    return BIOLOGY_CONTENT.get((level, topic), default_response)
