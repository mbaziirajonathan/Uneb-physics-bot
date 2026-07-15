from typing import Dict, List, Any

# ==========================================
# UNEB BIOLOGY SYLLABUS DATABASE (S1-S4 CBC)
# ==========================================
BIOLOGY_CONTENT: Dict[tuple[str, str], Dict[str, Any]] = {
    # SENIOR 1
    ("S1", "Plant Cell"): { # Changed from "Cells: The Basic Unit of Life"
        "text": """### Plant Cell
Cells are the microscopic building blocks of all living organisms.

**Comparing Plant and Animal Cells:**
* **Animal Cells:** Contain a nucleus, cell membrane, cytoplasm, and mitochondria.
* **Plant Cells:** Contain all animal cell parts, plus a rigid cellulose cell wall, a large central vacuole, and chloroplasts.
""",
        "diagram": "assets/plant_cell.png" # Added assets/ and.png
    },
    ("S1", "Ecosystem"): { # Changed from "Classification of Living Organisms"
        "text": """### Ecosystem
An ecosystem is a community of living organisms interacting with their physical environment.

**Components:**
* **Producers:** Green plants that make food.
* **Consumers:** Animals that eat producers or other consumers.
* **Decomposers:** Fungi and bacteria that break down dead matter.
""",
        "diagram": "assets/ecosystem.png"
    },

    # SENIOR 2
    ("S2", "Photosynthesis"): { # Changed from "Nutrition in Plants (Photosynthesis)"
        "text": """### Photosynthesis
The process by which autotrophs manufacture glucose using light energy.

**Process Requirements:**
* **Light Energy:** Absorbed by chlorophyll.
* **Carbon Dioxide:** Enters leaves through stomata.
* **Water:** Absorbed by roots and transported via xylem.
* **Equation:** $6CO_2 + 6H_2O \\rightarrow C_6H_{12}O_6 + 6O_2$
""",
        "diagram": "assets/photosynthesis.png"
    },
    ("S2", "Circulatory System"): { # Changed from "Transport in Plants and Animals"
        "text": """### Circulatory System
The system that transports blood, nutrients, and gases around the body.

**In Animals:**
* **Heart:** The central pump.
* **Vessels:** Arteries, Veins, Capillaries.
""",
        "diagram": "assets/circulatory.png"
    },
    ("S2", "Respiration"): { # Changed from "Gaseous Exchange and Respiration"
        "text": """### Respiration
The chemical breakdown of glucose to release energy.

**Aerobic Respiration:**
* Requires oxygen.
* Produces a large amount of energy, water, and carbon dioxide.
* Occurs in the mitochondria.
""",
        "diagram": "assets/alveolus.png"
    },

    # SENIOR 3
    ("S3", "DNA"): { # Changed from "Genetics and Variation"
        "text": """### DNA
Genetics studies inheritance and variation of traits passed from parents to offspring.

**Core Concepts:**
* **DNA:** Deoxyribonucleic acid, arranged in a double helix.
* **Chromosomes:** Thread-like structures of DNA.
* **Genes:** Sections of DNA that code for specific proteins.
""",
        "diagram": "assets/dna.png"
    },

    # SENIOR 4 - Add more later
}

def get_topics(level: str) -> List[str]:
    """Extracts curriculum-mapped topics for a specific class level."""
    return [topic for (lvl, topic) in BIOLOGY_CONTENT.keys() if lvl == level]

def get_content(level: str, topic: str) -> Dict[str, Any]:
    """Retrieves detailed content and diagram path."""
    default_response = {
        "text": f"### {topic}\nDetailed UNEB notes are being generated. Please prompt the AI Assistant below for a complete breakdown.",
        "diagram": None
    }
    return BIOLOGY_CONTENT.get((level, topic), default_response)
