from collections import defaultdict
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.database import init_db, get_latest_goal, get_topics, get_sessions
from src.user import get_user_id

init_db()

st.set_page_config(page_title="Progress Dashboard", page_icon="📊", layout="wide")

# Chart colors: blue = done, gray = still to do (same meaning on every chart)
DONE = "#3987e5"
TODO = "#5c5b57"
TEXT = "#c3c2b7"
GRID = "rgba(195,194,183,0.15)"
SURFACE = "#0e1117"


def style(fig, height=320):
    """Shared look for every chart."""
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT),
        legend=dict(orientation="h", y=1.12, x=0),
        bargap=0.35,
    )
    fig.update_xaxes(showgrid=False, linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zeroline=False)
    return fig


st.title("📊 Progress Dashboard")

goal = get_latest_goal(get_user_id())
if not goal:
    st.warning("Please save a learning goal first on the Learning Goal page.")
    st.stop()

topics = get_topics(goal["id"])
if not topics:
    st.warning("Please generate your roadmap first on the My Roadmap page.")
    st.stop()

sessions = get_sessions(goal["id"])

# ---------- Numbers ----------
total = len(topics)
done = sum(1 for t in topics if t["completed"])
percent = round(done / total * 100)
weekly_hours = goal["hours_per_day"] * goal["days_per_week"]

st.markdown(
    f"### {goal['goal']}  \n"
    f"{goal['level']} · {goal['learning_style']} · target {goal['target_date']}"
)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Skill level", goal["level"])
c2.metric("Roadmap topics", total)
c3.metric("Completed", done)
c4.metric("Overall progress", f"{percent}%")
c5.metric("Study hours / week", weekly_hours)
st.progress(done / total)

st.markdown("---")

# ---------- Charts row 1 ----------
left, right = st.columns(2)

with left:
    st.subheader("Topics by phase")
    by_phase = defaultdict(lambda: [0, 0])  # phase -> [done, remaining]
    for t in topics:
        by_phase[t["phase"]][0 if t["completed"] else 1] += 1
    phases = list(by_phase.keys())

    fig = go.Figure()
    fig.add_bar(
        y=phases, x=[by_phase[p][0] for p in phases], name="Completed",
        orientation="h", marker=dict(color=DONE, line=dict(color=SURFACE, width=2)),
        hovertemplate="%{y}<br>Completed: %{x}<extra></extra>",
    )
    fig.add_bar(
        y=phases, x=[by_phase[p][1] for p in phases], name="Remaining",
        orientation="h", marker=dict(color=TODO, line=dict(color=SURFACE, width=2)),
        hovertemplate="%{y}<br>Remaining: %{x}<extra></extra>",
    )
    fig.update_layout(barmode="stack")
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(title="Topics", dtick=1, showgrid=True, gridcolor=GRID)
    st.plotly_chart(style(fig), use_container_width=True)

with right:
    st.subheader("Study hours by week")
    if sessions:
        planned, finished = defaultdict(float), defaultdict(float)
        for s in sessions:
            planned[s["week_number"]] += s["duration_hours"]
            if s["completed"]:
                finished[s["week_number"]] += s["duration_hours"]
        weeks = sorted(planned)
        labels = [f"Week {w}" for w in weeks]

        fig = go.Figure()
        fig.add_bar(
            x=labels, y=[round(planned[w], 1) for w in weeks], name="Planned",
            marker=dict(color=TODO, line=dict(color=SURFACE, width=2)),
            hovertemplate="%{x}<br>Planned: %{y} h<extra></extra>",
        )
        fig.add_bar(
            x=labels, y=[round(finished[w], 1) for w in weeks], name="Done",
            marker=dict(color=DONE, line=dict(color=SURFACE, width=2)),
            hovertemplate="%{x}<br>Done: %{y} h<extra></extra>",
        )
        fig.update_layout(barmode="group")
        fig.update_yaxes(title="Hours")
        st.plotly_chart(style(fig), use_container_width=True)
    else:
        st.info("Create your schedule on the Study Planner page to see weekly hours.")

# ---------- Charts row 2: activity ----------
if sessions:
    per_day = defaultdict(float)
    for s in sessions:
        if s["completed"] and s["completed_at"]:
            day = datetime.fromisoformat(s["completed_at"]).date()
            per_day[day] += s["duration_hours"]
    if per_day:
        st.subheader("Hours completed per day")
        days = sorted(per_day)
        fig = go.Figure()
        fig.add_bar(
            x=days, y=[round(per_day[d], 1) for d in days], name="Hours",
            marker=dict(color=DONE),
            hovertemplate="%{x|%a %d %b}<br>%{y} h<extra></extra>",
        )
        fig.update_yaxes(title="Hours")
        fig.update_layout(showlegend=False)
        st.plotly_chart(style(fig, 260), use_container_width=True)

st.markdown("---")

# ---------- Upcoming tasks and remaining topics ----------
a, b = st.columns(2)

with a:
    st.subheader("Upcoming tasks")
    upcoming = [s for s in sessions if not s["completed"]][:6]
    if upcoming:
        table = pd.DataFrame({
            "Day": [s["day_label"] for s in upcoming],
            "Topic": [s["topic_title"] for s in upcoming],
            "Hours": [s["duration_hours"] for s in upcoming],
        })
        st.dataframe(table, hide_index=True, use_container_width=True)
    elif sessions:
        st.success("All study sessions are completed. 🎉")
    else:
        st.info("No schedule yet. Create one on the Study Planner page.")

with b:
    st.subheader("Remaining topics")
    remaining = [t for t in topics if not t["completed"]]
    if remaining:
        for t in remaining:
            st.markdown(f"- {t['title']} · {t['estimated_hours']} h")
    else:
        st.success("You finished every topic on your roadmap! 🎓")
