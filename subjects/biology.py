import streamlit as st
from groq import Groq

def render_svg(symbol_id): st.markdown(f'<svg width="350" height="180"><use href="assets/biology_sprite.svg#{symbol_id}"/></svg>', unsafe_allow_html=True)

def run(level):
    st.subheader(f"Biology - {level}")
    topics = {"S1": ["Select Topic", "Cell", "Animal Cell", "Photosynthesis"], "S2": ["Select Topic", "Heart", "Circulation", "Nutrition"], "S3": ["Select Topic", "DNA", "Neuron", "Kidney"], "S4": ["Select Topic", "Brain", "Genetics"]}
    diagram_map = {"S1": {"Animal Cell": "animal_cell", "Photosynthesis": "photosynthesis"}, "S2": {"Heart": "heart"}, "S3": {"DNA": "dna", "Neuron": "neuron"}}
    topic = st.selectbox("Select Biology Topic", topics[level], key=f"bio_{level}")
    if topic == "Select Topic": return
    if st.button("Generate Lesson", key=f"btn_bio_{level}"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": f"You are UNEB {level} Biology tutor."}, {"role": "user", "content": f"Teach {topic}"}])
        st.markdown("### EXPLANATION"); st.markdown(res.choices[0].message.content)
    if topic in diagram_map.get(level, {}): st.markdown("### DIAGRAM"); render_svg(diagram_map[level][topic])
