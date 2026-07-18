import plotly.express as px
import streamlit as st
from core.config import settings
from core.ui import render_bottom_nav
from services.metrics import weekly_volume, personal_bests

if not st.session_state.get("household_id") and not settings.demo_mode:
    st.switch_page("views/setup.py")

st.title("Progress")
st.caption("Volume, training load and milestones.")

activities = st.session_state.activities
if activities.empty:
    st.info("Log activities to begin building progress trends.")
    render_bottom_nav("Progress")
    st.stop()

data = weekly_volume(activities)
athlete_names = sorted(activities["athlete"].dropna().unique().tolist())
options = ["Team"] + athlete_names
athlete = st.segmented_control("View", options, default="Team", label_visibility="collapsed")

chart_data = data if athlete == "Team" else data[data["athlete"] == athlete]
if athlete == "Team":
    chart_data = chart_data.groupby("week", as_index=False).agg(
        distance_km=("distance_km", "sum"),
        training_load=("training_load", "sum"),
        sessions=("sessions", "sum"),
    )

metric_choice = st.segmented_control(
    "Metric",
    ["Distance", "Training load"],
    default="Distance",
    label_visibility="collapsed",
)

y_col = "distance_km" if metric_choice == "Distance" else "training_load"
y_label = "Weekly distance (km)" if metric_choice == "Distance" else "Weekly training load"

fig = px.line(
    chart_data,
    x="week",
    y=y_col,
    markers=True,
    labels={"week": "", y_col: y_label},
)
fig.update_layout(
    height=300,
    margin=dict(l=0, r=0, t=20, b=0),
    showlegend=False,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

pbs = personal_bests(activities, athlete)
c1, c2, c3 = st.columns(3)
c1.metric("Longest distance", f"{pbs['longest_distance']:.1f} km")
c2.metric("Best pace", pbs["best_pace"])
c3.metric("Highest load", pbs["highest_load"])

pain_flags = int((activities["pain"] >= 2).sum())
with st.container(border=True):
    st.markdown("**Data quality and recovery**")
    st.write(f"Recorded sessions: **{len(activities)}**")
    st.write(f"Pain flags at 2/10 or above: **{pain_flags}**")
    st.caption(
        "Trend confidence improves when workout type, distance, duration, RPE and pain are logged consistently."
    )

render_bottom_nav("Progress")
