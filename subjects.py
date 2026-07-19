# subjects.py - NCDC 2026 DATA ONLY

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

# PRACTICALS NOW SEPARATED BY LEVEL
PRACTICALS = {
    "Physics": {
        "S1-S4": [
            {"name": "Measuring Length and Time", "aim": "Use rulers and stopwatches", "materials": "Meter rule, Stopwatch", "procedure": "Measure 10 times and average", "graph": "Length vs Time"},
            {"name": "Density of Regular Object", "aim": "Determine density", "materials": "Beam balance, Ruler", "procedure": "Measure Mass and Volume", "graph": "Mass vs Volume"},
            {"name": "Simple Pendulum", "aim": "Investigate period", "materials": "String, Bob", "procedure": "Vary length, time 20 oscillations", "graph": "T^2 vs L"},
            {"name": "Ohm's Law", "aim": "Verify V = IR", "materials": "Battery, Resistor, Ammeter, Voltmeter", "procedure": "Vary V and record I", "graph": "V vs I"},
            {"name": "Focal Length of Lens", "aim": "Find focal length", "materials": "Convex Lens, Screen", "procedure": "Find u and v", "graph": "1/u vs 1/v"},
        ],
        "S5-S6": [
            {"name": "Specific Heat Capacity by Electrical Method", "aim": "Find specific heat capacity of metal", "materials": "Calorimeter, Heater, Ammeter, Voltmeter", "procedure": "Measure electrical energy and temperature rise", "graph": "Temp vs Time"},
            {"name": "Refractive Index by Snell's Law", "aim": "Determine refractive index of glass", "materials": "Glass block, Ray box", "procedure": "Measure angles i and r", "graph": "sin i vs sin r"},
            {"name": "Surface Tension by Capillary Rise", "aim": "Determine surface tension of water", "materials": "Capillary tubes", "procedure": "Measure height of rise", "graph": "h vs 1/r"},
            {"name": "Speed of Sound by Resonance", "aim": "Find velocity of sound in air", "materials": "Resonance tube", "procedure": "Find first and second resonance", "graph": "L vs 1/f"},
            {"name": "Magnetic Field of a Solenoid", "aim": "Investigate B vs Current", "materials": "Solenoid, Power supply", "procedure": "Vary current, measure deflection", "graph": "Deflection vs Current"},
            {"name": "Charging and Discharging of a Capacitor", "aim": "Determine time constant RC", "materials": "Capacitor, Resistor", "procedure": "Record voltage vs time", "graph": "lnV vs Time"}
        ]
    },
    "Chemistry": {
        "S1-S4": [
            {"name": "Testing for Cations", "aim": "Identify metal ions", "materials": "NaOH, NH3", "procedure": "Add reagents and observe ppt", "graph": None},
            {"name": "Testing for Anions", "aim": "Identify acid radicals", "materials": "BaCl2, AgNO3", "procedure": "Add reagents", "graph": None},
            {"name": "Titration - Acid Base", "aim": "Find concentration of acid", "materials": "Burette, Pipette", "procedure": "Titrate with standard base", "graph": "Volume vs pH"},
            {"name": "Rate of Reaction", "aim": "Effect of concentration", "materials": "HCl, Marble chips", "procedure": "Vary conc, collect gas", "graph": "Volume vs Time"},
        ],
        "S5-S6": [
            {"name": "Redox Titration - Permanganate", "aim": "Determine concentration of Fe2+ ions", "materials": "KMnO4, Burette", "procedure": "Titrate in acidic medium", "graph": None},
            {"name": "Enthalpy Change by Calorimetry", "aim": "Find heat of neutralization", "materials": "Calorimeter, NaOH, HCl", "procedure": "Mix and measure temp change", "graph": "Temp vs Time"},
            {"name": "Solubility Curve of KNO3", "aim": "Determine solubility vs temperature", "materials": "KNO3, Water bath", "procedure": "Dissolve at different T", "graph": "Solubility vs T"},
            {"name": "Rate of Reaction - Iodine Clock", "aim": "Determine order of reaction", "materials": "KI, K2S2O8", "procedure": "Vary concentration", "graph": "1/Time vs Concentration"},
            {"name": "Electrolysis - Faraday's Law", "aim": "Verify Faraday's laws", "materials": "Copper electrodes", "procedure": "Electrolyze CuSO4", "graph": "Mass vs Charge"},
            {"name": "Organic Preparation - Ester", "aim": "Prepare and purify ethyl ethanoate", "materials": "Ethanol, Ethanoic acid", "procedure": "Reflux and distill", "graph": None}
        ]
    },
    "Biology": {
        "S1-S4": [
            {"name": "Microscope Use", "aim": "Observe plant and animal cells", "materials": "Microscope, Slides", "procedure": "Prepare wet mount", "graph": None},
            {"name": "Food Tests", "aim": "Test for nutrients", "materials": "Iodine, Benedict's", "procedure": "Add reagents to food", "graph": None},
            {"name": "Osmosis in Potato", "aim": "Investigate osmosis", "materials": "Potato, Sucrose solutions", "procedure": "Soak and measure mass", "graph": "Conc vs % Change"},
            {"name": "Transpiration Rate", "aim": "Measure water loss", "materials": "Potometer", "procedure": "Measure bubble movement", "graph": "Time vs Distance"},
        ],
        "S5-S6": [
            {"name": "Enzyme Activity - Effect of pH", "aim": "Determine optimum pH for amylase", "materials": "Amylase, Starch", "procedure": "Vary pH, test for starch", "graph": "pH vs Rate"},
            {"name": "Photosynthesis - Limiting Factors", "aim": "Investigate effect of light intensity", "materials": "Aquatic plant, Lamp", "procedure": "Count bubbles", "graph": "Light Intensity vs Rate"},
            {"name": "Ecological Sampling - Quadrats", "aim": "Determine population density", "materials": "Quadrat, Tape", "procedure": "Sample area", "graph": "Species vs Frequency"},
            {"name": "Respiration - Gas Exchange", "aim": "Measure CO2 production", "materials": "Yeast, Lime water", "procedure": "Ferment and observe", "graph": "Time vs CO2"},
            {"name": "Chromatography of Plant Pigments", "aim": "Separate leaf pigments", "materials": "Solvent, Filter paper", "procedure": "Spot and develop", "graph": None},
            {"name": "Heart Rate Response to Exercise", "aim": "Investigate recovery time", "materials": "Stopwatch", "procedure": "Measure HR before and after", "graph": "Time vs HR"}
        ]
    },
    "Mathematics": {
        "S1-S4": [
            {"name": "Budgeting Project", "aim": "Use fractions and %", "materials": "Paper", "procedure": "Share money in ratios", "graph": None},
            {"name": "Business Analysis", "aim": "Profit and Loss", "materials": "Receipts", "procedure": "Calculate profit", "graph": "Sales vs Profit"},
            {"name": "Linear Programming", "aim": "Maximize profit", "materials": "Graph paper", "procedure": "Plot feasible region", "graph": "Feasible Region"},
        ],
        "S5-S6": [
            {"name": "Statistical Data Analysis", "aim": "Use mean, median, SD", "materials": "Calculator", "procedure": "Analyze given data", "graph": "Histogram"},
            {"name": "Mechanics - Projectile Motion", "aim": "Model projectile", "materials": "Graph paper", "procedure": "Plot trajectory", "graph": "y vs x"},
            {"name": "Numerical Methods - Newton Raphson", "aim": "Find roots of equation", "materials": "Calculator", "procedure": "Iterate to solution", "graph": "Iteration vs Error"},
            {"name": "Vectors in 3D", "aim": "Find angle between vectors", "materials": "Ruler", "procedure": "Calculate dot product", "graph": None}
        ]
    }
}

def get_topics(subject, level):
    return CURRICULUM.get(subject, {}).get(level, [])

def get_practicals(subject, level):
    """Return correct practicals based on level"""
    level_group = "S5-S6" if level in ["S5", "S6"] else "S1-S4"
    return PRACTICALS.get(subject, {}).get(level_group, [])
