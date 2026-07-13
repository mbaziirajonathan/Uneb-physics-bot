import streamlit as st
from groq import Groq

# ALL SVG SYMBOLS EMBEDDED HERE. NO EXTERNAL FILES
SVG_SPRITE = """
<svg style="display:none">
  <defs>
    <style>.axis{stroke:black;stroke-width:1.5}.label{font-size:11px;fill:black;font-family:Arial}.ray{stroke:red;stroke-width:2}</style>

    <symbol id="forces" viewBox="0 0 200 120">
      <rect x="80" y="60" width="40" height="30" fill="#cccccc" stroke="black"/>
      <text x="88" y="80" class="label">Block</text>
      <line x1="100" y1="60" x2="100" y2="30" class="axis"/><text x="105" y="35" class="label">N</text>
      <line x1="100" y1="90" x2="100" y2="110" class="axis"/><text x="105" y="115" class="label">W</text>
      <line x1="120" y1="75" x2="150" y2="75" class="axis"/><text x="152" y="80" class="label">F</text>
    </symbol>

    <symbol id="gas_law" viewBox="0 0 200 120">
      <rect x="50" y="30" width="60" height="60" fill="#add8e6" stroke="black"/><text x="65" y="65" class="label">Gas</text>
      <line x1="30" y1="100" x2="170" y2="100" class="axis"/><line x1="30" y1="100" x2="30" y2="20" class="axis"/>
      <text x="170" y="110" class="label">T</text><text x="15" y="25" class="label">P</text>
      <path d="M40,90 Q100,50 160,30" fill="none" stroke="red" stroke-width="2"/>
    </symbol>

    <symbol id="convex_lens" viewBox="0 0 200 100">
      <line x1="0" y1="50" x2="200" y2="50" class="axis"/>
      <path d="M100,15 Q115,50 100,85 Q85,50 100,15" fill="#add8e6" stroke="blue" stroke-width="2"/>
      <line x1="60" y1="70" x2="100" y2="50" class="ray"/><line x1="60" y1="30" x2="100" y2="50" class="ray"/><line x1="100" y1="50" x2="140" y2="50" class="ray"/>
      <text x="55" y="25" class="label">O</text><text x="135" y="25" class="label">I</text><text x="95" y="65" class="label">F</text>
    </symbol>

    <symbol id="transverse_wave" viewBox="0 0 200 100">
      <line x1="10" y1="50" x2="190" y2="50" class="axis"/>
      <path d="M10,50 Q30,20 50,50 T90,50 T130,50 T170,50" fill="none" stroke="blue" stroke-width="2"/>
      <text x="45" y="15" class="label">Crest</text><text x="85" y="95" class="label">Trough</text><text x="80" y="65" class="label">λ</text>
    </symbol>

    <symbol id="series_circuit" viewBox="0 0 200 100">
      <rect x="10" y="40" width="30" height="20" fill="yellow" stroke="black"/><text x="15" y="54" class="label">V</text>
      <rect x="70" y="40" width="30" height="20" fill="gray" stroke="black"/><text x="75" y="54" class="label">R1</text>
      <rect x="130" y="40" width="30" height="20" fill="gray" stroke="black"/><text x="135" y="54" class="label">R2</text>
      <path d="M40,50 H70 M100,50 H130 M160,50 H180 V70 H10 V50" fill="none" stroke="black" stroke-width="2"/>
    </symbol>
  </defs>
</svg>
"""

def render_svg(symbol_id):
    # 1. First render the hidden sprite definitions
    # 2. Then render the <use> tag that calls it
    st.markdown(SVG_SPRITE + f'<svg width="350" height="180"><use href="#{symbol_id}"/></svg>', unsafe_allow_html=True)

def run(level):
    st.subheader(f"Physics - {level}")
    topics = {"S1": ["Select Topic", "Measurement", "Density", "Forces", "Pressure", "Energy", "Convex Lens"], "S2": ["Select Topic", "Waves", "Transverse Wave", "Sound", "Heat", "Gas Laws"], "S3": ["Select Topic", "Electric Field", "Series Circuit", "Magnetic Field"], "S4": ["Select Topic", "Nuclear Physics"]}
    diagram_map = {"S1": {"Forces": "forces", "Convex Lens": "convex_lens"}, "S2": {"Transverse Wave": "transverse_wave", "Gas Laws": "gas_law"}, "S3": {"Series Circuit": "series_circuit"}}
    topic = st.selectbox("Select Physics Topic", topics[level], key=f"phy_{level}")
    if topic == "Select Topic": return

    col1, col2 = st.columns([3,1])
    with col1:
        if st.button("Generate Lesson", type="primary", key=f"btn_phy_{level}"):
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            with st.spinner("AI Teaching..."):
                res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": f"You are UNEB {level} Physics tutor."}, {"role": "user", "content": f"Teach {topic} with definition, formula, example"}])
                st.markdown("### EXPLANATION"); st.markdown(res.choices[0].message.content)

    with col2:
        if topic in diagram_map.get(level, {}):
            st.markdown("### DIAGRAM"); render_svg(diagram_map[level][topic])
