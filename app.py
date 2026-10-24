import streamlit as st

from src.database import init_db

init_db()

st.set_page_config(
    page_title="AI Learning Planner",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 AI Personalized Learning Planner")
st.caption("Turn your goals into a realistic, trackable learning roadmap.")

st.markdown("---")

col1, col2, col3 = st.columns(3)
col1.metric("Roadmap Topics", "0")
col2.metric("Completed", "0")
col3.metric("Progress", "0%")

st.markdown("---")
st.subheader("How it works")
st.markdown(
    """
1. **Learning Goal**: tell us what you want to learn
2. **My Roadmap**: get a phased, personalized plan
3. **Study Planner**: see a weekly schedule that fits your time
4. **Progress Dashboard**: track how far you've come
"""
)

st.info("Setup complete! Pages will appear in the sidebar as we build them.")
