# subjects.py - NCDC DATA ONLY

CURRICULUM = {
    "Physics": {
        "S1": ["Intro to Physics", "Measurement", "Force", "Mechanical Properties"],
        "S2": ["Atmospheric/Fluid Pressure", "Work/Energy/Power", "Simple Machines", "Temperature/Heat Transfer"],
        "S3": ["Light/Optics", "Electrostatics", "Current Electricity", "Wave Motion/Sound"],
        "S4": ["Electromagnetism", "Electronics", "Radioactivity/Nuclear Physics"],
        "S5": ["Unit 1: Mechanics/Matter", "Unit 2: Waves/Optics", "Unit 3: Thermal Properties/Thermodynamics I"],
        "S6": ["Unit 4: Thermodynamics II", "Unit 5: Electricity/Magnetism", "Unit 6: Modern Physics/Electronics"],
    },
    "Chemistry": {
        "S1": ["Chemistry/Society", "Experimental Techniques", "States of Matter", "Classification of Matter"],
        "S2": ["Air/Burning/Rusting", "Water/Hydrogen", "Atomic Structure/Bonding", "Acids/Bases/Indicators"],
        "S3": ["Chemical Equations/Formulae", "Mole Concept", "Carbon/Compounds", "Sulfur/Nitrogen Compounds"],
        "S4": ["Periodicity", "Reactivity Series/Metal Extraction", "Organic Chemistry", "Thermochemistry", "Consumable Chemicals"],
        "S5": ["Unit 1: Moles/Equations", "Unit 2: Atomic/Electronic Structure", "Unit 3: Bonding/Crystal Structure", "Unit 4: Periodicity I", "Unit 5: Thermochemistry", "Unit 6: Intro Organic/Hydrocarbons"],
        "S6": ["Unit 7: Physical Equilibria/Kinetics", "Unit 8: Advanced Inorganic", "Unit 9: Advanced Organic", "Unit 10: Industrial/Environmental"],
    },
    "Biology": {
        "S1": ["Intro to Biology", "Cells", "Classification", "Interaction/Interdependence"],
        "S2": ["Nutrition", "Transport", "Gas Exchange/Respiration"],
        "S3": ["Excretion/Homeostasis", "Coordination/Response", "Locomotion/Support", "Reproduction"],
        "S4": ["Growth/Development", "Genetics/Inheritance", "Evolution/Selection"],
        "S5": ["Unit 1: Cell Bio/Biochem", "Unit 2: Nutrition/Autotrophic Systems", "Unit 3: Transport/Gas Exchange", "Unit 4: Cellular Respiration", "Unit 5: Homeostasis/Regulation"],
        "S6": ["Unit 6: Coordination/Response", "Unit 7: Growth/Development/Reproduction", "Unit 8: Inheritance/Genetics/Evolution", "Unit 9: Ecology/Environmental Management"],
    },
    "Mathematics": {
        "S1": ["Unit 1: Number Bases", "Unit 2: Fractions", "Unit 3: Integers", "Unit 4: Sets", "Unit 5: Geometry", "Unit 6: Sequences", "Unit 7: Coordinates"],
        "S2": ["Unit 1: Equations", "Unit 2: Business Math", "Unit 3: Ratios", "Unit 4: Pythagoras", "Unit 5: Area/Volume", "Unit 6: Statistics"],
        "S3": ["Unit 1: Indices", "Unit 2: Quadratics", "Unit 3: Linear Programming", "Unit 4: Vectors", "Unit 5: Transformations", "Unit 6: Taxation"],
        "S4": ["Unit 1: Matrices", "Unit 2: Probability", "Unit 3: 3D Geometry", "Unit 4: Loci", "Unit 5: Functions", "Unit 6: Networks"],
        "S5": ["Paper 1: Advanced Algebra", "Paper 1: Geometry & Vectors", "Paper 1: Calculus I", "Paper 2: Statistics", "Paper 2: Mechanics I", "Paper 2: Numerical Methods"],
        "S6": ["Paper 1: Permutations & Complex", "Paper 1: Conics & 3D", "Paper 1: Calculus II", "Paper 2: Probability", "Paper 2: Mechanics II", "Paper 2: Numerical Methods II"]
    }
}

PRACTICALS = {
    "Physics": [
        {"name": "Measuring Length and Time", "aim": "Use rulers and stopwatches", "materials": "Meter rule", "procedure": "Measure 10 times", "graph": "Length vs Time"},
        {"name": "Density of Regular Object", "aim": "Determine density", "materials": "Beam balance", "procedure": "Mass and Volume", "graph": "Mass vs Volume"},
        {"name": "Simple Pendulum", "aim": "Investigate period", "materials": "String", "procedure": "Vary length", "graph": "T^2 vs L"},
        {"name": "Ohm's Law", "aim": "Verify V = IR", "materials": "Battery", "procedure": "Vary V", "graph": "V vs I"},
        {"name": "Focal Length of Lens", "aim": "Find focal length", "materials": "Lens", "procedure": "u and v", "graph": "1/u vs 1/v"},
        {"name": "Specific Heat Capacity", "aim": "Find specific heat", "materials": "Calorimeter", "procedure": "Heat transfer", "graph": "Temp vs Time"},
        {"name": "Refraction of Light", "aim": "Find refractive index", "materials": "Glass block", "procedure": "Snell's Law", "graph": "sin i vs sin r"},
        {"name": "Surface Tension", "aim": "Capillary rise", "materials": "Tube", "procedure": "Measure h", "graph": "h vs 1/r"},
        {"name": "Resonance in Air Column", "aim": "Speed of sound", "materials": "Tube", "procedure": "Find resonance", "graph": "L vs 1/f"},
        {"name": "Magnetic Field of Coil", "aim": "Field strength", "materials": "Coil", "procedure": "Vary current", "graph": "Deflection vs Current"}
    ],
    "Chemistry": [
        {"name": "Testing for Cations", "aim": "Identify metal ions", "materials": "NaOH", "procedure": "Add reagents", "graph": None},
        {"name": "Testing for Anions", "aim": "Identify acid radicals", "materials": "BaCl2", "procedure": "Add reagents", "graph": None},
        {"name": "Titration - Acid Base", "aim": "Find concentration", "materials": "Burette", "procedure": "Titrate", "graph": "Volume vs pH"},
        {"name": "Rate of Reaction", "aim": "Effect of concentration", "materials": "HCl", "procedure": "Vary conc", "graph": "Volume vs Time"},
        {"name": "Electrolysis of Water", "aim": "Decompose water", "materials": "Apparatus", "procedure": "Electrolyze", "graph": "H2 vs O2"},
        {"name": "Solubility Curve", "aim": "Solubility vs T", "materials": "KNO3", "procedure": "Dissolve", "graph": "Solubility vs T"},
        {"name": "Organic Preparation - Ethene", "aim": "Prepare ethene", "materials": "Ethanol", "procedure": "Heat", "graph": None},
        {"name": "Chromatography", "aim": "Separate ink", "materials": "Paper", "procedure": "Spot", "graph": None},
        {"name": "Enthalpy Change", "aim": "Heat of reaction", "materials": "Calorimeter", "procedure": "Mix", "graph": "Temp vs Time"},
        {"name": "Redox Titration", "aim": "Find Fe2+", "materials": "KMnO4", "procedure": "Titrate", "graph": None}
    ],
    "Biology": [
        {"name": "Microscope Use", "aim": "Observe cells", "materials": "Microscope", "procedure": "Prepare slide", "graph": None},
        {"name": "Food Tests", "aim": "Test nutrients", "materials": "Iodine", "procedure": "Add reagents", "graph": None},
        {"name": "Osmosis in Potato", "aim": "Investigate osmosis", "materials": "Potato", "procedure": "Soak", "graph": "Conc vs % Change"},
        {"name": "Transpiration Rate", "aim": "Measure water loss", "materials": "Potometer", "procedure": "Measure bubble", "graph": "Time vs Distance"},
        {"name": "Photosynthesis", "aim": "Test for starch", "materials": "Leaf", "procedure": "Destarch", "graph": None},
        {"name": "Heart Rate Response", "aim": "Effect of exercise", "materials": "Stopwatch", "procedure": "Measure", "graph": "Time vs HR"},
        {"name": "Germination Factors", "aim": "Effect of water", "materials": "Seeds", "procedure": "Set conditions", "graph": "% vs Days"},
        {"name": "Enzyme Activity", "aim": "Effect of pH", "materials": "Amylase", "procedure": "Vary pH", "graph": "pH vs Time"},
        {"name": "Ecological Sampling", "aim": "Quadrat method", "materials": "Quadrat", "procedure": "Sample", "graph": "Species vs Freq"},
        {"name": "Blood Smear", "aim": "Identify blood cells", "materials": "Slide", "procedure": "Observe", "graph": None}
    ],
    "Mathematics": [
        {"name": "Budgeting Project", "aim": "Use fractions and %", "materials": "Paper", "procedure": "Share money", "graph": None},
        {"name": "Business Analysis", "aim": "Profit and Loss", "materials": "Receipts", "procedure": "Calculate profit", "graph": "Sales vs Profit"},
        {"name": "Linear Programming", "aim": "Maximize profit", "materials": "Graph paper", "procedure": "Plot feasible region", "graph": "Feasible Region"},
        {"name": "Network Project", "aim": "Critical path", "materials": "Paper", "procedure": "Draw network", "graph": "Network Graph"}
    ]
}

def get_topics(subject, level):
    return CURRICULUM.get(subject, {}).get(level, [])
