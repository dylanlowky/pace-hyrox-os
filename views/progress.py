import plotly.express as px
import streamlit as st
from core.config import settings
from core.ui import metric_html, render_bottom_nav
from services.metrics import weekly_volume, personal_bests

if not st.session_state.get("household_id") and not settings.demo_mode:
    st.switch_page("views/setup.py")

st.title("Progress")
st.caption("A simple view of consistency, volume and milestones.")
activities = st.session_state.activities
if activities.empty:
    st.info("Log activities to begin building progress trends.")
    render_bottom_nav()
    st.stop()

data = weekly_volume(activities)
athlete_names = sorted(activities["athlete"].dropna().unique().tolist())
athlete = st.segmented_control("View", ["Team"] + athlete_names, default="Team", label_visibility="collapsed")
chart_data = data if athlete == "Team" else data[data["athlete"] == athlete]
if athlete == "Team":
    chart_data = chart_data.groupby("week", as_index=False).agg(
        distance_km=("distance_km", "sum"), training_load=("training_load", "sum"), sessions=("sessions", "sum")
    )

latest = chart_data.sort_values("week").tail(2)
trend = "Building consistency"
if len(latest) == 2:
    current = float(latest.iloc[-1]["training_load"])
    previous = float(latest.iloc[-2]["training_load"])
    if current > previous * 1.2:
        trend = "Load increased meaningfully"
    elif current < previous * 0.8:
        trend = "Training eased this week"

st.markdown(f'<section class="content-card"><div class="eyebrow">Current story</div><div class="coach-lead">{trend}</div><div class="muted">Use the chart to confirm the pattern, not to chase a perfect line.</div></section>', unsafe_allow_html=True)

metric_choice = st.segmented_control("Metric", ["Distance", "Training load"], default="Distance", label_visibility="collapsed")
y_col = "distance_km" if metric_choice == "Distance" else "training_load"
y_label = "Weekly distance (km)" if metric_choice == "Distance" else "Weekly training load"
fig = px.line(chart_data, x="week", y=y_col, markers=True, labels={"week": "", y_col: y_label})
fig.update_layout(height=290, margin=dict(l=0, r=0, t=20, b=0), showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

pbs = personal_bests(activities, athlete)
st.markdown(
    f"""
    <section class="content-card">
      <div class="eyebrow">Milestones</div>
      <div class="metric-row">
        {metric_html("Longest", f"{pbs['longest_distance']:.1f} km")}
        {metric_html("Best pace", pbs['best_pace'])}
        {metric_html("Highest load", str(pbs['highest_load']))}
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

render_bottom_nav()
