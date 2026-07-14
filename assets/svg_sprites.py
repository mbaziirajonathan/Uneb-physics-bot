import streamlit.components.v1 as components

SVG_SPRITE = """<svg style="display:none" xmlns="http://www.w3.org/2000/svg"><defs>
<symbol id="animal_cell" viewBox="0 0 120 120"><ellipse cx="60" cy="60" rx="50" ry="40" fill="#ffffe0" stroke="black" stroke-width="2"/><circle cx="60" cy="60" r="15" fill="#add8e6" stroke="black"/><text x="60" y="65" text-anchor="middle" font-size="8">Nucleus</text></symbol>
<symbol id="photosynthesis" viewBox="0 0 150 100"><rect x="10" y="40" width="40" height="40" fill="green"/><text x="30" y="65" text-anchor="middle" fill="white" font-size="8">Leaf</text><path d="M60,60 L90,30" stroke="yellow" stroke-width="4"/><path d="M60,60 L90,90" stroke="blue" stroke-width="4"/><text x="95" y="35" font-size="10">O2</text><text x="95" y="95" font-size="10">Glucose</text></symbol>
<symbol id="heart" viewBox="0 0 120 100"><path d="M60,80 Q20,60 20,35 Q20,15 40,15 Q50,15 60,25 Q70,15 80,15 Q100,15 100,35 Q100,60 60,80" fill="red" stroke="black" stroke-width="2"/></symbol>
<symbol id="dna" viewBox="0 0 100 120"><path d="M30,10 Q70,30 30,50 Q70,70 30,90 Q70,110 30,110" fill="none" stroke="blue" stroke-width="2"/><path d="M70,10 Q30,30 70,50 Q30,70 70,90 Q30,110 70,110" fill="none" stroke="red" stroke-width="2"/></symbol>
<symbol id="neuron" viewBox="0 0 150 80"><circle cx="30" cy="40" r="15" fill="yellow" stroke="black" stroke-width="2"/><path d="M45,40 Q80,20 120,40" stroke="black" stroke-width="3" fill="none"/><text x="125" y="45" font-size="10">Axon</text></symbol>
<symbol id="forces" viewBox="0 0 200 120"><rect x="80" y="60" width="40" height="30" fill="#ccc" stroke="black"/><line x1="100" y1="60" x2="100" y2="30" stroke="black" stroke-width="2"/><text x="105" y="35" font-size="10">N</text><line x1="100" y1="90" x2="100" y2="110" stroke="black" stroke-width="2"/><text x="105" y="115" font-size="10">W</text><line x1="120" y1="75" x2="150" y2="75" stroke="red" stroke-width="2"/><text x="152" y="80" font-size="10">F</text></symbol>
<symbol id="convex_lens" viewBox="0 0 200 100"><line x1="0" y1="50" x2="200" y2="50" stroke="black"/><path d="M100,15 Q115,50 100,85 Q85,50 100,15" fill="#add8e6" stroke="blue" stroke-width="2"/><line x1="60" y1="70" x2="140" y2="50" stroke="red" stroke-width="2"/></symbol>
<symbol id="atom" viewBox="0 0 120 120"><circle cx="60" cy="60" r="8" fill="red"/><circle cx="60" cy="60" r="25" fill="none" stroke="blue"/><circle cx="60" cy="60" r="40" fill="none" stroke="blue"/><circle cx="60" cy="35" r="4" fill="blue"/></symbol>
</defs></svg>"""

def load_svg_sprite():
    # Load the sprite sheet once at app start. height=0 hides it
    components.html(SVG_SPRITE, height=0, scrolling=False)

def render_svg(symbol_id):
    # Renders one diagram from the sprite
    if symbol_id is None:
        st.info("No diagram available for this topic.")
        return
    svg_code = f'<svg width="350" height="180" style="border:1px solid #ddd; background:white;"><use href="#{symbol_id}"/></svg>'
    components.html(svg_code, height=190, scrolling=False)
