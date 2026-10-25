import streamlit as st

from src.database import (
    init_db, get_latest_goal, get_topics, save_topics,
    delete_topics, set_topic_completed,
)
from src.roadmap_generator import generate_roadmap

init_db()

st.set_page_config(page_title="My Roadmap", page_icon="🗺️", layout="wide")

st.title("🗺️ My Roadmap")

goal = get_latest_goal()
if not goal:
    st.warning("Please save a learning goal first on the Learning Goal page.")
    st.stop()

st.caption(f"Goal: **{goal['goal']}** · {goal['level']} · {goal['learning_style']}")

topics = get_topics(goal["id"])


def make_roadmap():
    """Generate a roadmap with AI and save it."""
    with st.spinner("Building your roadmap... this can take up to a minute."):
        try:
            new_topics = generate_roadmap(goal)
            delete_topics(goal["id"])
            save_topics(goal["id"], new_topics)
        except Exception as e:
            st.error(f"Could not create the roadmap: {e}")
            return False
    return True


# ---------- No roadmap yet ----------
if not topics:
    st.info("You don't have a roadmap for this goal yet.")
    if st.button("✨ Generate my roadmap", type="primary"):
        if make_roadmap():
            st.rerun()
    st.stop()

# ---------- Progress summary ----------
done = sum(1 for t in topics if t["completed"])
total = len(topics)
hours_total = round(sum(t["estimated_hours"] or 0 for t in topics), 1)
hours_done = round(
    sum(t["estimated_hours"] or 0 for t in topics if t["completed"]), 1
)

c1, c2, c3 = st.columns(3)
c1.metric("Topics completed", f"{done} / {total}")
c2.metric("Hours done", f"{hours_done} / {hours_total}")
c3.metric("Progress", f"{round(done / total * 100)}%")
st.progress(done / total)

st.markdown("---")

# ---------- Topics grouped by phase ----------
current_phase = None
for t in topics:
    if t["phase"] != current_phase:
        current_phase = t["phase"]
        st.subheader(current_phase)

    with st.container(border=True):
        checked = st.checkbox(
            f"**{t['title']}** · ⏱ {t['estimated_hours']} h",
            value=bool(t["completed"]),
            key=f"topic_{t['id']}",
        )
        if checked != bool(t["completed"]):
            set_topic_completed(t["id"], checked)
            st.rerun()

        st.write(t["description"])
        with st.expander("Practice, mini-project and resources"):
            st.markdown(f"**✏️ Practice:** {t['practice']}")
            st.markdown(f"**🛠️ Mini-project:** {t['mini_project']}")
            st.markdown("**📚 Resources:**")
            for line in (t["resources"] or "").splitlines():
                if line.strip():
                    st.markdown(f"- {line.strip().lstrip('-• ')}")

# ---------- Regenerate ----------
st.markdown("---")
if st.button("🔄 Regenerate roadmap"):
    st.session_state["confirm_regen"] = True
if st.session_state.get("confirm_regen"):
    st.warning("This replaces your current roadmap and its progress.")
    if st.button("Yes, replace it"):
        st.session_state["confirm_regen"] = False
        if make_roadmap():
            st.rerun()
