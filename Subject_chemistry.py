import streamlit as st
from diagrams_library.chemistry_diagrams import *

def run(level):
    st.header(f"Chemistry - {level}")

    syllabus = {
        "S1": ["Bunsen Burner", "Filtration", "Evaporation", "Atom", "States", "Melting"],
        "S2": ["Water Molecule", "pH Scale", "Titration", "Electrolysis", "Rusting", "Flame Test"],
        "S3": ["Gas Laws", "Periodic Trends", "Ionic Bond", "Covalent Bond", "Reaction Rate", "Chromatography"],
        "S4": ["Distillation", "Haber Process", "Contact Process", "Esterification", "Polymerization", "Galvanic Cell"]
    }

    topic = st.selectbox("Select Chemistry Topic", syllabus[level])

    if topic == "Bunsen Burner": draw_bunsen_burner()
    elif topic == "Filtration": draw_filtration_setup()
    elif topic == "Evaporation": draw_evaporation_setup()
    elif topic == "Atom": draw_atom_structure()
    elif topic == "States": draw_states_of_matter()
    elif topic == "Melting": draw_melting_point()
    elif topic == "Water Molecule": draw_water_molecule()
    elif topic == "pH Scale": draw_ph_scale()
    elif topic == "Titration": draw_titration_setup()
    elif topic == "Electrolysis": draw_electrolysis_water()
    elif topic == "Rusting": draw_rusting_iron()
    elif topic == "Flame Test": draw_flame_test()
    elif topic == "Gas Laws": draw_gas_laws_apparatus()
    elif topic == "Periodic Trends": draw_periodic_trends()
    elif topic == "Ionic Bond": draw_ionic_bonding()
    elif topic == "Covalent Bond": draw_covalent_bonding()
    elif topic == "Reaction Rate": draw_reaction_rate_graph()
    elif topic == "Chromatography": draw_chromatography()
    elif topic == "Distillation": draw_fractional_distillation()
    elif topic == "Haber Process": draw_haber_process()
    elif topic == "Contact Process": draw_contact_process()
    elif topic == "Esterification": draw_esterification()
    elif topic == "Polymerization": draw_polymerization()
    elif topic == "Galvanic Cell": draw_galvanic_cell()
