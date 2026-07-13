import streamlit as st
from diagrams_library.physics_diagrams import *

def run(level):
    st.header(f"Physics - {level}")

    syllabus = {
        "S1": ["Measurement", "Force", "Volume", "Area", "Pendulum", "Balance"],
        "S2": ["Forces", "Levers", "Pressure", "Hydraulics", "Barometer", "Density"],
        "S3": ["Ohm's Law", "Circuits", "Waves", "Light", "Refraction", "Lens"],
        "S4": ["Transformer", "Motor", "Generator", "CRT", "Nuclear", "Logic Gates"]
    }

    topic = st.selectbox("Select Physics Topic", syllabus[level])

    # S1
    if topic == "Measurement": draw_ruler_vernier()
    elif topic == "Force": draw_spring_balance()
    elif topic == "Volume": draw_volume_displacement()
    elif topic == "Area": draw_area_irregular_shape()
    elif topic == "Pendulum": draw_simple_pendulum()
    elif topic == "Balance": draw_beam_balance()

    # S2
    elif topic == "Forces": draw_force_triangle()
    elif topic == "Levers": draw_lever_classes()
    elif topic == "Pressure": draw_manometer()
    elif topic == "Hydraulics": draw_hydraulic_press()
    elif topic == "Barometer": draw_fortin_barometer()
    elif topic == "Density": draw_density_bottle()

    # S3
    elif topic == "Ohm's Law": draw_ohms_circuit()
    elif topic == "Circuits": draw_series_parallel()
    elif topic == "Waves": draw_wave_parts()
    elif topic == "Light": draw_reflection_rays()
    elif topic == "Refraction": draw_refraction_prism()
    elif topic == "Lens": draw_lens_ray_diagram()

    # S4
    elif topic == "Transformer": draw_transformer()
    elif topic == "Motor": draw_dc_motor()
    elif topic == "Generator": draw_ac_generator()
    elif topic == "CRT": draw_cathode_ray_tube()
    elif topic == "Nuclear": draw_nuclear_reactor()
    elif topic == "Logic Gates": draw_logic_gates()
