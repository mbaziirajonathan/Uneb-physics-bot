import streamlit as st
from groq import Groq

SVG_SPRITE = """<svg style="display:none" xmlns="http://www.w3.org/2000/svg"><defs>
<symbol id="bunsen_burner" viewBox="0 0 100 120"><rect x="40" y="20" width="20" height="80" fill="#888" stroke="black"/><ellipse cx="50" cy="100" rx="20" ry="10" fill="#333"/><path d="M50,20 Q60,5 50,0 Q40,5 50,20" fill="orange"/></symbol>
<symbol id="atom" viewBox="0 0 120 120"><circle cx="60" cy="60" r="8" fill="red"/><circle cx="60" cy="60" r="25" fill="none" stroke="blue"/><circle cx="60" cy="60" r="40" fill="none" stroke="blue"/><circle cx="60" cy="35" r="4" fill="blue"/></symbol>
<symbol id="titration" viewBox="0 0 120 140"><rect x="50" y="10" width="5" height="80" fill="gray"/><ellipse cx="50" cy="50" rx="15" ry="40" fill="none" stroke="black" stroke-width="2"/><rect x="20" y="90" width="60" height="30" fill="white" stroke="black" stroke-width="2"/></symbol>
<symbol id="water_molecule" viewBox="0 0 120 80"><circle cx="60" cy="40" r="12" fill="red"/><circle cx="30" cy="20" r="8" fill="#ccc"/><circle cx="90" cy="20" r="8" fill="#ccc"/><line x1="38" y1="28" x2="52" y2="35" stroke="black" stroke-width="2"/><line x1="82" y1="28" x2="68" y2="35" stroke="black" stroke-width="2"/></symbol>
<symbol id="alkane" viewBox="0 0 150 60"><circle cx="20" cy="30" r="8" fill="black"/><circle cx="50" cy="30" r="8" fill="black"/><circle cx="80" cy="30" r="8" fill="black"/><circle cx="110" cy="30" r="8" fill="black"/><line x1="28" y1="30" x2="42" y2="30" stroke="black" stroke-width="3"/><line x1="58" y1="30" x2="72" y2="30" stroke="black" stroke-width="3"/><line x1="88" y1="30" x2="102" y2="30" stroke="black" stroke-width="3"/></symbol>
</defs></svg>"""

st.markdown(SVG_SPRITE, unsafe_allow_html=True)

def render_svg(symbol_id):
    st.markdown(f'<svg width="350" height="180" style="border:1px solid #ddd; background:white;"><use href="#{symbol_id}"/></svg>', unsafe_allow_html=True)

def run(level):
    st.subheader(f"Chemistry - {level}")
    topics = {
        "S1": ["Select Topic", "Introduction to Chemistry", "Lab Apparatus", "Bunsen Burner", "States of Matter", "Mixtures", "Compounds", "Elements", "Chemical Reactions"],
        "S2": ["Select Topic", "Atomic Structure", "The Periodic Table", "Titration", "Acids, Bases and Salts", "Air and Combustion", "Water", "Carbon"],
        "S3": ["Select Topic", "Chemical Bonding", "Water Molecule", "Rates of Reaction", "Carbonates", "Extraction of Metals", "Organic Chemistry Intro", "Fertilizers"],
        "S4": ["Select Topic", "Organic Chemistry", "Alkane", "Alkenes", "Alcohols", "Electrochemistry", "Nitrogen and Fertilizers", "Industrial Chemistry"]
    }
    diagram_map = {"S1": {"Bunsen Burner": "bunsen_burner"}, "S2": {"Atomic Structure": "atom", "Titration": "titration"}, "S3": {"Water Molecule": "water_molecule"}, "S4": {"Alkane": "alkane"}}
    topic = st.selectbox("Select Chemistry Topic", topics[level], key=f"chem_{level}")
    if topic == "Select Topic": return
    if st.button("Generate Lesson", type="primary", key=f"btn_chem_{level}"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        with st.spinner("AI Teaching..."):
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": f"You are UNEB {level} Chemistry tutor. Use NCDC syllabus."}, {"role": "user", "content": f"Teach {topic} for {level}. Definition, Example, 1 question"}])
            st.markdown("### 📝 EXPLANATION"); st.markdown(res.choices[0].message.content)
    if topic in diagram_map.get(level, {}): st.markdown("### 📊 DIAGRAM"); render_svg(diagram_map[level][topic])
    else: st.info("Diagram coming soon")
