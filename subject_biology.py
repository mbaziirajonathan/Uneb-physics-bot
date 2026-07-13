import streamlit as st
from diagrams_library.biology_diagrams import *

def run(level):
    st.header(f"Biology - {level}")

    syllabus = {
        "S1": ["Plant Cell", "Animal Cell", "Microscope", "Leaf", "Root Hair", "Food Tests"],
        "S2": ["Amoeba", "Paramecium", "Spirogyra", "Heart", "Circulation", "Respiration"],
        "S3": ["Digestion", "Nephron", "Flower", "Pollination", "DNA", "Mitosis"],
        "S4": ["Brain", "Eye", "Ear", "Skeleton", "Photosynthesis", "Genetics"]
    }

    topic = st.selectbox("Select Biology Topic", syllabus[level])

    if topic == "Plant Cell": draw_plant_cell()
    elif topic == "Animal Cell": draw_animal_cell()
    elif topic == "Microscope": draw_light_microscope()
    elif topic == "Leaf": draw_leaf_cross_section()
    elif topic == "Root Hair": draw_root_hair_cell()
    elif topic == "Food Tests": draw_food_tests()
    elif topic == "Amoeba": draw_amoeba()
    elif topic == "Paramecium": draw_paramecium()
    elif topic == "Spirogyra": draw_spirogyra()
    elif topic == "Heart": draw_human_heart()
    elif topic == "Circulation": draw_blood_circulation()
    elif topic == "Respiration": draw_respiratory_system()
    elif topic == "Digestion": draw_digestive_system()
    elif topic == "Nephron": draw_nephron()
    elif topic == "Flower": draw_flower_parts()
    elif topic == "Pollination": draw_pollination()
    elif topic == "DNA": draw_dna_double_helix()
    elif topic == "Mitosis": draw_mitosis()
    elif topic == "Brain": draw_human_brain()
    elif topic == "Eye": draw_human_eye()
    elif topic == "Ear": draw_human_ear()
    elif topic == "Skeleton": draw_human_skeleton()
    elif topic == "Photosynthesis": draw_photosynthesis()
    elif topic == "Genetics": draw_genetics_punnett()
