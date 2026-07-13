import streamlit as st
import streamlit.components.v1 as components
from groq import Groq

SVG_SPRITE = """<svg style="display:none" xmlns="http://www.w3.org/2000/svg"><defs>
<symbol id="forces" viewBox="0 0 200 120"><rect x="80" y="60" width="40" height="30" fill="#ccc" stroke="black"/><line x1="100" y1="60" x2="100" y2="30" stroke="black" stroke-width="2"/><text x="105" y="35" font-size="10">N</text><line x1="100" y1="90" x2="100" y2="110" stroke="black" stroke-width="2"/><text x="105" y="115" font-size="10">W</text><line x1="120" y1="75" x2="150" y2="75" stroke="red" stroke-width="2"/><text x="152" y="80" font-size="10">F</text></symbol>
<symbol id="convex_lens" viewBox="0 0 200 100"><line x1="0" y1="50" x2="200" y2="50" stroke="black"/><path d="M100,15 Q115,50 100,85 Q85,50 100,15" fill="#add8e6" stroke="blue" stroke-width="2"/><line x1="60" y1="70" x2="140" y2="50" stroke="red" stroke-width="2"/></symbol>
<symbol id="transverse_wave" viewBox="0 0 200 100"><line x1="10" y1="50" x2="190" y2="50" stroke="black"/><path d="M10,50 Q30,20 50,50 T90,50 T130,50 T170,50" fill="none" stroke="blue" stroke-width="2"/><text x="45" y="15" font-size="10">Crest</text></symbol>
<symbol id="gas_law" viewBox="0 0 200 120"><rect x="50" y="30" width="60" height="60" fill="#add8e6" stroke="black"/><line x1="30" y1="100" x2="170" y2="100" stroke="black"/><line x1="30" y1="100" x2="30" y2="20" stroke="black"/><text x="170" y="110" font-size="10">T</text><text x="15" y="25" font-size="10">P</text></symbol>
<symbol id="series_circuit" viewBox="0 0 200 100"><rect x="10" y="40" width="30" height="20" fill="yellow" stroke="black"/><rect x="70" y="40" width="30" height="20" fill="gray" stroke="black"/><rect x="130" y="40" width="30" height="20" fill="gray" stroke="black"/><path d="M40,50 H70 M100,50 H130 M160,50 H180 V70 H10 V50" fill="none" stroke="black" stroke-width="2"/></symbol>
</defs></svg>"""

components.html(SVG_SPRITE, height=0)

def render_svg(symbol_id):
    svg_code = f'<svg width="350" height="180" style="border:1px solid #ddd; background:white;"><use href="#{symbol_id}"/></svg>'
    components.html(svg_code, height=190)

def run(level):
    st.subheader(f"Physics - {level}")
    topics = {
        "S1": ["Select Topic", "Introduction to Physics", "Measurement", "Density", "Forces", "Pressure", "Work, Energy and Power", "Simple Machines", "Light", "Convex Lens", "Sound", "Heat"],
        "S2": ["Select Topic", "Waves", "Transverse Wave", "Sound Waves", "Heat", "Gas Laws", "Magnetism", "Current Electricity", "Static Electricity"],
        "S3": ["Select Topic", "Electric Field", "Series Circuit", "Parallel Circuit", "Magnetic Field", "Electromagnetic Induction", "Cathode Rays", "Radioactivity"],
        "S4": ["Select Topic", "Nuclear Physics", "Electronics", "AC Circuits", "Astrophysics", "Quantum Physics"]
    }
    diagram_map = {"S1": {"Forces": "forces", "Convex Lens": "convex_lens"}, "S2": {"Transverse Wave": "transverse_wave", "Gas Laws": "gas_law"}, "S3": {"Series Circuit": "series_circuit"}}
    topic = st.selectbox("Select Physics Topic", topics[level], key=f"phy_{level}_{st.session_state.get('subject_select')}")
    if topic == "Select Topic": return
    if st.button("Generate Lesson", type="primary", key=f"btn_phy_{level}"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        with st.spinner("AI Teaching..."):
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": f"You are UNEB {level} Physics tutor."}, {"role": "user", "content": f"Teach {topic} for {level}. Definition, Formula, Example, 1 question"}])
            st.markdown("### 📝 EXPLANATION"); st.markdown(res.choices[0].message.content)
    if topic in diagram_map.get(level, {}): st.markdown("### 📊 DIAGRAM"); render_svg(diagram_map[level][topic])
    else: st.info("Diagram coming soon")
