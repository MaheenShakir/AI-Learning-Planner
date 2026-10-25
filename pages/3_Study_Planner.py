from datetime import date, datetime

import streamlit as st

from src.database import (
    init_db, get_latest_goal, get_topics, get_sessions,
    save_sessions, delete_sessions, set_session_completed,
)
from src.user import get_user_id
from src.study_planner import build_schedule

init_db()

st.set_page_config(page_title="Study Planner", page_icon="📅", layout="wide")

st.title("📅 Weekly Study Planner")

goal = get_latest_goal(get_user_id())
if not goal:
    st.warning("Please save a learning goal first on the Learning Goal page.")
    st.stop()

topics = get_topics(goal["id"])
if not topics:
    st.warning("Please generate your roadmap first on the My Roadmap page.")
    st.stop()

st.caption(
    f"Goal: **{goal['goal']}** · {goal['hours_per_day']} h/day · "
    f"{goal['days_per_week']} days/week"
)

sessions = get_sessions(goal["id"])


def make_schedule():
    """Build a fresh schedule from the unfinished topics."""
    new_sessions = build_schedule(goal, topics)
    delete_sessions(goal["id"])
    save_sessions(goal["id"], new_sessions)
    return new_sessions


# ---------- No schedule yet ----------
if not sessions:
    st.info("You don't have a study schedule yet.")
    if st.button("📅 Create my schedule", type="primary"):
        if make_schedule():
            st.rerun()
        else:
            st.success("All topics are already completed. Nothing to schedule!")
    st.stop()

# ---------- Summary ----------
done = sum(1 for s in sessions if s["completed"])
hours_total = round(sum(s["duration_hours"] for s in sessions), 1)
hours_done = round(sum(s["duration_hours"] for s in sessions if s["completed"]), 1)

c1, c2, c3 = st.columns(3)
c1.metric("Sessions completed", f"{done} / {len(sessions)}")
c2.metric("Hours done", f"{hours_done} / {hours_total}")
c3.metric("Weeks planned", max(s["week_number"] for s in sessions))
st.progress(done / len(sessions))

# Warn if the plan runs past the target date
last_label = sessions[-1]["day_label"]
target = date.fromisoformat(goal["target_date"])
for year in (target.year, target.year + 1):
    try:
        last_day = datetime.strptime(f"{last_label} {year}", "%a %d %b %Y").date()
    except ValueError:
        continue
    if last_day.weekday() == datetime.strptime(last_label[:3], "%a").weekday():
        if last_day > target and (last_day - target).days < 365:
            st.warning(
                f"Your schedule ends on {last_label}, after your target date. "
                "Consider adding study time on the Learning Goal page."
            )
        break

st.markdown("---")

# ---------- Pick a week ----------
weeks = sorted({s["week_number"] for s in sessions})
week = st.selectbox("Week", weeks, format_func=lambda w: f"Week {w}")
week_sessions = [s for s in sessions if s["week_number"] == week]

w_total = round(sum(s["duration_hours"] for s in week_sessions), 1)
w_done = round(sum(s["duration_hours"] for s in week_sessions if s["completed"]), 1)
st.write(f"**This week:** {w_done} / {w_total} hours done")

current_day = None
for s in week_sessions:
    if s["day_label"] != current_day:
        current_day = s["day_label"]
        st.subheader(current_day)

    with st.container(border=True):
        checked = st.checkbox(
            f"**{s['topic_title']}** · ⏱ {s['duration_hours']} h",
            value=bool(s["completed"]),
            key=f"session_{s['id']}",
        )
        if checked != bool(s["completed"]):
            set_session_completed(s["id"], checked)
            st.rerun()
        st.markdown(f"🎯 **Objective:** {s['objective']}")
        st.markdown(f"✏️ **Practice:** {s['practice_activity']}")

# ---------- Rebuild ----------
st.markdown("---")
if st.button("🔄 Rebuild schedule from today"):
    st.session_state["confirm_rebuild"] = True
if st.session_state.get("confirm_rebuild"):
    st.warning("This replaces the current schedule (unfinished topics only).")
    if st.button("Yes, rebuild it"):
        st.session_state["confirm_rebuild"] = False
        make_schedule()
        st.rerun()
