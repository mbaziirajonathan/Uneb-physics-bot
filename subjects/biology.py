import streamlit as st
import streamlit.components.v1 as components
from groq import Groq

SVG_SPRITE = """<svg style="display:none" xmlns="http://www.w3.org/2000/svg"><defs>
<symbol id="animal_cell" viewBox="0 0 120 120"><ellipse cx="60" cy="60" rx="50" ry="40" fill="#ffffe0" stroke="black" stroke-width="2"/><circle cx="60" cy="60" r="15" fill="#add8e6" stroke="black"/><text x="60" y="65" text-anchor="middle" font-size="8">Nucleus</text></symbol>
<symbol id="photosynthesis" viewBox="0 0 150 100"><rect x="10" y="40" width="40" height="40" fill="green"/><text x="30" y="65" text-anchor="middle" fill="white" font-size="8">Leaf</text><path d="M60,60 L90,30" stroke="yellow" stroke-width="4"/><path d="M60,60 L90,90" stroke="blue" stroke-width="4"/><text x="95" y="35" font-size="10">O2</text><text x="95" y="95" font-size="10">Glucose</text></symbol>
<symbol id="heart" viewBox="0 0 120 100"><path d="M60,80 Q20,60 20,35 Q20,15 40,15 Q50,15 60,25 Q70,15 80,15 Q100,15 100,35 Q100,60 60,80" fill="red" stroke="black" stroke-width="2"/></symbol>
<symbol id="dna" viewBox="0 0 100 120"><path d="M30,10 Q70,30 30,50 Q70,70 30,90 Q70,110 30,110" fill="none" stroke="blue" stroke-width="2"/><path d="M70,10 Q30,30 70,50 Q30,70 70,90 Q30,110 70,110" fill="none" stroke="red" stroke-width="2"/></symbol>
<symbol id="neuron" viewBox="0 0 150 80"><circle cx="30" cy="40" r="15" fill="yellow" stroke="black" stroke-width="2"/><path d="M45,40 Q80,20 120,40" stroke="black" stroke-width="3" fill="none"/><text x="125" y="45" font-size="10">Axon</text></symbol>
</defs></svg>"""

# RENDER SVG ONCE SO IT WORKS
components.html(SVG_SPRITE, height=0)

def render_svg(symbol_id):
    svg_code = f'<svg width="350" height="180" style="border:1px solid #ddd; background:white;"><use href="#{symbol_id}"/></svg>'
    components.html(svg_code, height=190)

def run(level): # BUG FIX: level is now received correctly
    st.subheader(f"Biology - {level}")
    topics = {
        "S1": ["Select Topic", "Introduction to Biology", "Cell Structure", "Animal Cell", "Plant Cell", "Photosynthesis", "Nutrition", "Respiration", "Transport in Plants"],
        "S2": ["Select Topic", "Heart and Circulation", "Respiration in Humans", "Excretion", "Reproduction in Plants", "Reproduction in Humans", "Growth and Development"],
        "S3": ["Select Topic", "DNA and Genetics", "Neuron and Nervous System", "Kidney and Excretion", "Homeostasis", "Ecology", "Pollution"],
        "S4": ["Select Topic", "Brain", "Human Genetics", "Evolution", "Immunity and Disease", "Biotechnology", "Applied Biology"]
    }
    diagram_map = {
        "S1": {"Animal Cell": "animal_cell", "Photosynthesis": "photosynthesis"},
        "S2": {"Heart and Circulation": "heart"},
        "S3": {"DNA and Genetics": "dna", "Neuron and Nervous System": "neuron"}
    }

    topic = st.selectbox("Select Biology Topic", topics[level], key=f"bio_{level}_{st.session_state.get('subject_select')}")
    if topic == "Select Topic": return

    if st.button("Generate Lesson", type="primary", key=f"btn_bio_{level}"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        with st.spinner("AI Teaching..."):
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": f"You are UNEB {level} Biology tutor. Use Uganda NCDC syllabus. Be clear and short."},
                    {"role": "user", "content": f"Teach {topic} for {level}. Give: 1.Definition 2.Key points 3.Example 4.One practice question with answer"}
                ]
            )
            st.markdown("### 📝 EXPLANATION")
            st.markdown(res.choices[0].message.content)

    if topic in diagram_map.get(level, {}):
        st.markdown("### 📊 DIAGRAM")
        render_svg(diagram_map[level][topic])
    else:
        st.info("Diagram coming soon for this topic")
