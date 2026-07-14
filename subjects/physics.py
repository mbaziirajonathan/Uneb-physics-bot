PHYSICS_CONTENT = {
    "S1": {
        "Introduction to Physics": {
            "content": """**Physics** is the study of matter, energy, and the interaction between them.
            
**Branches of Physics:**
1. **Mechanics** - motion and forces
2. **Heat** - temperature and energy transfer  
3. **Waves** - light, sound
4. **Electricity** - charges and circuits
5. **Modern Physics** - atoms, nuclear

**SI Units**: Meter (m), Kilogram (kg), Second (s), Ampere (A), Kelvin (K)""",
            "diagram": None
        },
        "Measurement": {
            "content": """**Instruments**: Ruler, Vernier calipers, Micrometer screw gauge, Beam balance
            
**Accuracy vs Precision**
**Errors**: Zero error, Random error, Systematic error

Always record to the correct number of decimal places.""",
            "diagram": None
        },
        "Forces": {
            "content": """**Force** is a push or pull that changes motion or shape.

**Hooke's Law**: $F = kx$
Where F = Force, k = spring constant, x = extension

**Verification Experiment**: Load is proportional to extension within elastic limit.

**Types**: Weight, Tension, Friction, Upthrust""",
            "diagram": "hookes_law"
        },
        "Electrostatics": {
            "content": """**Electrostatics** is the study of stationary charges.

**Gold Leaf Electroscope** is used to:
1. Detect presence of charge
2. Test the type of charge  
3. Compare magnitudes of charge

**Charging by**: Friction, Contact, Induction
**Law**: Like charges repel, unlike charges attract""",
            "diagram": "electroscope"
        }
    },

    "S2": {
        "Energy": {
            "content": """**Energy** is the capacity to do work.
            
**Forms**: Kinetic, Potential, Heat, Light, Sound, Electrical, Chemical, Nuclear
**Law of Conservation**: Energy cannot be created or destroyed, only changed from one form to another.

**Work Done**: $W = F \\times d$""",
            "diagram": None
        },
        "Refraction of Light": {
            "content": """**Refraction** is the bending of light as it passes from one medium to another.

**Laws of Refraction**:
1. Incident ray, refracted ray and normal at point of incidence all lie in same plane
2. $n = \\frac{\\sin i}{\\sin r}$ = constant = Snell's Law

**Experiment**: Use glass block and 4 pins P1, P2, P3, P4 to trace rays.""",
            "diagram": "refraction"
        },
        "Current Electricity": {
            "content": """**Electric Current**: $I = \\frac{Q}{t}$
**Ohm's Law**: $V = IR$
**Power**: $P = VI = I^2R = \\frac{V^2}{R}$

**Heating Effect**: $H = I^2Rt$
This principle is used in calorimetry to find specific heat capacity.""",
            "diagram": "specific_heat"
        },
        "Waves": {
            "content": """**Wave**: A disturbance that transfers energy without transferring matter.

**Types**: Transverse and Longitudinal
**Properties**: Wavelength, Frequency, Amplitude, Speed
**Wave Equation**: $v = f \\lambda$

**Examples**: Sound, Light, Water waves""",
            "diagram": None
        }
    },

    "S3": {
        "Magnetism": {
            "content": """**Magnetic materials**: Iron, Steel, Cobalt, Nickel
**Magnetic poles**: North and South. Like poles repel.

**Electromagnet**: Coil + Soft iron core + Current
**Uses**: Electric bell, Relay, Circuit breaker""",
            "diagram": None
        },
        "Electrostatics Advanced": {
            "content": """**Electric field**: Region where a charge experiences force.
**Potential Difference**: $V = \\frac{W}{Q}$
**Capacitance**: $C = \\frac{Q}{V}$""",
            "diagram": None
        }
    },

    "S4": {
        "Transformers": {
            "content": """**Transformer** transfers electrical energy from one circuit to another by electromagnetic induction.

**Step-down transformer**: $N_p > N_s$ so $V_p > V_s$

**Formula**: $\\frac{V_p}{V_s} = \\frac{N_p}{N_s} = \\frac{I_s}{I_p}$

**Parts**:
1. **Laminated Soft Iron Core** - to reduce eddy currents
2. **Primary Coil Np** - AC input
3. **Secondary Coil Ns** - Output load

**Energy Losses**: Copper loss, Hysteresis, Eddy current, Flux leakage""",
            "diagram": "transformer"
        },
        "X-Rays": {
            "content": """**X-Rays** are electromagnetic waves of very short wavelength produced when fast electrons hit a metal target.

**X-Ray Tube Parts**:
1. **Filament/Cathode** - produces electrons by thermionic emission
2. **Tungsten Target** - electrons hit here to produce X-rays
3. **Copper Anode** - conducts heat away
4. **E.H.T. Supply** - 50,000V to accelerate electrons
5. **Evacuated Glass Envelope**

**Properties**: Penetrate matter, Ionizing, Cause fluorescence
**Uses**: Medical, Industrial, Security""",
            "diagram": "xray_tube"
        },
        "Nuclear Physics": {
            "content": """**Radioactivity**: Spontaneous disintegration of unstable nuclei.

**Types of radiation**:
- **Alpha α**: +2 charge, low penetration
- **Beta β**: -1 charge, medium penetration  
- **Gamma γ**: No charge, high penetration

**Half-life**: Time for half the nuclei to decay.
**Applications**: Medicine, Tracers, Carbon dating""",
            "diagram": None
        }
    }
}
