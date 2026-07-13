import streamlit as st
import pytz
from datetime import datetime

# Import the 3 subject files
import subjects.physics as physics
import subjects.chemistry as chemistry
import subjects.biology as biology

st.set_page_config(
    page_title="UNEB AI Tutor - S1 to S4",
    page_icon="📚",
    layout="wide"
)

# HEADER
st.title("📚 UNEB AI Tutor")
st.caption("Physics | Chemistry | Biology | S1 - S4 | Uganda NCDC Syllabus")

# Show Kampala Time
tz = pytz.timezone('Africa/Kampala')
now = datetime.now(tz)
st.write(f"**Current Time in Uganda:** {now.strftime('%I:%M %p')}")
st.divider()

# SIDEBAR
with st.sidebar:
    st.header("Settings")
    subject = st.radio(
        "Choose Subject",
        ["Physics", "Chemistry", "Biology"],
        key="subject_select"
    )
    level = st.selectbox(
        "Choose Class Level",
        ["S1", "S2", "S3", "S4"],
        key="level_select"
    )
    st.divider()
    st.info("Select a topic, click 'Generate Lesson' to get AI explanation + Diagram")

# MAIN AREA - ROUTE TO CORRECT SUBJECT
if subject == "Physics":
    physics.run(level)
elif subject == "Chemistry":
    chemistry.run(level)
elif subject == "Biology":
    biology.run(level)

st.divider()
st.caption("Powered by Groq Llama-3.1 + Inline SVG Diagrams | Built for UNEB Students")
