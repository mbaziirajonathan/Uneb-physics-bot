import streamlit as st
from groq import Groq

# ALL BIOLOGY SVG SYMBOLS EMBEDDED. NO EXTERNAL FILES
SVG_SPRITE = """
<svg style="display:none">
  <defs>
    <style>.label{font-size:11px;fill:black;font-family:Arial}</style>

    <symbol id="animal_cell" viewBox="0 0 120 120">
      <ellipse cx="60" cy="60" rx="50" ry="40" fill="#ffffe0" stroke="black" stroke-width="2"/>
      <circle cx="60" cy="60" r="15" fill="#add8e6" stroke="black"/>
      <text x="55" y="65" class="label">N</text>
      <circle cx="35" cy="40" r="5" fill="orange"/>
      <text x="20" y="110" class="label">Animal Cell</text>
    </symbol>

    <symbol id="photosynthesis" viewBox="0 0 150 100">
      <rect x="10" y="40" width="40" height="40" fill="green"/><text x="15" y="65" class="label" fill="white">Leaf</text>
      <path d="M60,60 L90,30" stroke="yellow" stroke-width="4" marker-end="url(#arrow)"/>
      <path d="M60,60 L90,90" stroke="blue" stroke-width="4" marker-end="url(#arrow)"/>
      <text x="95" y="35" class="label">O2</text><text x="95" y="95" class="label">Glucose</text>
      <text x="55" y="20" class="label">CO2 + H2O + Light</text>
      <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs>
    </symbol>

    <symbol id="heart" viewBox="0 0 120 100">
      <path d="M60,80 Q20,60 20,35 Q20,15 40,15 Q50,15 60,25 Q70,15 80,15 Q100,15 100,35 Q100,60 60,80" fill="red" stroke="black" stroke-width="2"/>
      <text x="45" y="50" class="label" fill="white">Heart</text>
    </symbol>

    <symbol id="dna" viewBox="0 0 100 120">
      <path d="M30,10 Q70,30 30,50 Q70,70 30,90 Q70,110 30,110" fill="none" stroke="blue" stroke-width="2"/>
      <path d="M70,10 Q30,30 70,50 Q30,70 70,90 Q30,110 70,110" fill="none" stroke="red" stroke-width="2"/>
      <line x1="30" y1="20" x2="70" y2="20" stroke="black"/><line x1="30" y1="40" x2="70" y2="40" stroke="black"/>
      <text x="30" y="120" class="label">DNA Double Helix</text>
    </symbol>

    <symbol id="neuron" viewBox="0 0 150 80">
      <circle cx="30" cy="40" r="15" fill="yellow" stroke="black" stroke-width="2"/><text x="25" y="45" class="label">N</text>
      <path d="M45,40 Q80,20 120,40" stroke="black" stroke-width="3" fill="none"/>
      <path d="M30,55 Q30,70 50,70" stroke="black" stroke-width="2" fill="none"/>
      <text x="10" y="20" class="label">Neuron</text><text x="50" y="75" class="label">Dendrites</text>
    </symbol>
  </defs>
</svg>
"""

def render_svg(symbol_id):
    st.markdown(SVG_SPRITE + f'<svg width="350" height="180"><use href="#{symbol_id}"/></svg>', unsafe_allow_html=True)

def run(level):
    st.subheader(f"Biology - {level}")

    topics = {
        "S1": ["Select Topic", "Cell", "Animal Cell", "Photosynthesis", "Nutrition"],
        "S2": ["Select Topic", "Heart", "Circulation", "Respiration"],
        "S3": ["Select Topic", "DNA", "Neuron", "Kidney", "Homeostasis"],
        "S4": ["Select Topic", "Brain", "Genetics", "Evolution"]
    }

    diagram_map = {
        "S1": {"Animal Cell": "animal_cell", "Photosynthesis": "photosynthesis"},
        "S2": {"Heart": "heart"},
        "S3": {"DNA": "dna", "Neuron": "neuron"}
    }

    topic = st.selectbox("Select Biology Topic", topics[level], key=f"bio_{level}")
    if topic == "Select Topic": return

    if st.button("Generate Lesson", type="primary", key=f"btn_bio_{level}"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        with st.spinner("AI Teaching..."):
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": f"You are a UNEB {level} Biology tutor for Uganda. Use NCDC syllabus. Give definition, key points, 1 example, 1 practice question."},
                    {"role": "user", "content": f"Teach {topic}"}
                ]
            )
            st.markdown("### EXPLANATION")
            st.markdown(res.choices[0].message.content)

    if topic in diagram_map.get(level, {}):
        st.markdown("### DIAGRAM")
        render_svg(diagram_map[level][topic])
    else:
        st.info("No diagram available for this topic yet")
