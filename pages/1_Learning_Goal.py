from datetime import date, timedelta

import streamlit as st

from src.database import init_db, save_goal, get_latest_goal

init_db()

st.set_page_config(page_title="Learning Goal", page_icon="🎯", layout="wide")

st.title("🎯 Your Learning Goal")
st.caption("Tell us what you want to learn and how much time you have.")

# ---------- The form ----------
with st.form("goal_form"):
    goal = st.text_input(
        "What do you want to learn?",
        placeholder="e.g. Machine Learning, SQL, Web Development",
    )

    col1, col2 = st.columns(2)
    with col1:
        level = st.selectbox(
            "Current skill level", ["Beginner", "Intermediate", "Advanced"]
        )
        hours_per_day = st.slider(
            "Study hours per day", min_value=0.5, max_value=8.0, value=2.0, step=0.5
        )
        days_per_week = st.slider(
            "Study days per week", min_value=1, max_value=7, value=5
        )
    with col2:
        target_date = st.date_input(
            "Target completion date",
            value=date.today() + timedelta(days=90),
            min_value=date.today() + timedelta(days=7),
        )
        learning_style = st.selectbox(
            "Preferred learning style",
            [
                "Hands-on projects",
                "Video tutorials",
                "Reading & documentation",
                "Mix of everything",
            ],
        )

    submitted = st.form_submit_button("Save my goal", type="primary")

# ---------- What happens on submit ----------
if submitted:
    if not goal.strip():
        st.error("Please enter what you want to learn.")
    else:
        save_goal(
            goal.strip(), level, hours_per_day, days_per_week,
            target_date, learning_style,
        )
        st.success("Goal saved! Your roadmap comes in the next step.")

# ---------- Show the saved goal ----------
saved = get_latest_goal()
if saved:
    st.markdown("---")
    st.subheader("Current saved goal")

    days_left = (date.fromisoformat(saved["target_date"]) - date.today()).days
    weeks_left = max(days_left / 7, 0)
    total_hours = round(
        weeks_left * saved["days_per_week"] * saved["hours_per_day"], 1
    )

    st.markdown(f"**{saved['goal']}** · {saved['level']} · {saved['learning_style']}")

    m1, m2, m3 = st.columns(3)
    m1.metric("Days until target", max(days_left, 0))
    m2.metric("Study hours / week", saved["hours_per_day"] * saved["days_per_week"])
    m3.metric("Total study hours available", total_hours)
