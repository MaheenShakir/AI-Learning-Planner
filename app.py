import streamlit as st

from src.database import init_db, get_latest_goal, get_topics
from src.user import get_user_id

init_db()

st.set_page_config(
    page_title="AI Learning Planner",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 AI Personalized Learning Planner")
st.caption("Turn your goals into a realistic, trackable learning roadmap.")

st.markdown("---")

goal = get_latest_goal(get_user_id())
topics = get_topics(goal["id"]) if goal else []
total = len(topics)
done = sum(1 for t in topics if t["completed"])

if goal:
    st.markdown(f"**Current goal:** {goal['goal']} · {goal['level']}")

col1, col2, col3 = st.columns(3)
col1.metric("Roadmap Topics", total)
col2.metric("Completed", done)
col3.metric("Progress", f"{round(done / total * 100) if total else 0}%")

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

st.caption("🔒 Your goal and progress are private to your browser link. Bookmark this page to come back to them.")
st.info("Use the sidebar to move between pages: set a goal, build your roadmap, plan your week, and track your progress.")
