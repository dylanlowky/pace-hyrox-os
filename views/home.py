import streamlit as st
from core.config import settings
from core.ui import metric_html, render_bottom_nav
from services.metrics import athlete_summary, personal_bests

if not st.session_state.get("household_id") and not settings.demo_mode:
    st.switch_page("views/setup.py")

race = st.session_state.get("active_race")
activities = st.session_state.activities
brief = st.session_state.weekly_brief

if race:
    st.markdown(
        f"""
        <section class="hero-card">
          <div class="eyebrow">Active goal</div>
          <div class="hero-title">{race['name']}</div>
          <div class="hero-subtitle">{race['category']} · Target {race['target_time']}</div>
          <div class="metric-row">
            {metric_html("Days left", str(race['days_remaining']))}
            {metric_html("Status", brief['status'], "status-good")}
            {metric_html("Phase", "Build")}
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
else:
    st.warning("No active race yet.")
    if st.button("Create active race", type="primary", use_container_width=True):
        st.switch_page("views/race.py")

athlete_names = [
    row.get("display_name", row.get("name", "Athlete"))
    for row in st.session_state.get("athletes", [])
]
options = ["Team"] + athlete_names
selected = st.segmented_control(
    "View",
    options=options,
    default=st.session_state.selected_athlete if st.session_state.selected_athlete in options else "Team",
    label_visibility="collapsed",
)
st.session_state.selected_athlete = selected or "Team"

summary = athlete_summary(activities, st.session_state.selected_athlete)
st.markdown(
    f"""
    <section class="content-card">
      <div class="eyebrow">This week · {st.session_state.selected_athlete}</div>
      <div class="metric-row">
        {metric_html("Sessions", str(summary['sessions']))}
        {metric_html("Distance", f"{summary['distance_km']:.1f} km")}
        {metric_html("Load", f"{int(summary['training_load'])}")}
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <section class="coach-card">
      <div class="eyebrow">Coach insight</div>
      <div class="coach-lead">{brief['headline']}</div>
      <div class="muted">{brief['summary']}</div>
    </section>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)
with col1:
    if st.button("Log workout", use_container_width=True, type="primary"):
        st.switch_page("views/activities.py")
with col2:
    if st.button("Read coach brief", use_container_width=True):
        st.switch_page("views/coach.py")

pbs = personal_bests(activities, st.session_state.selected_athlete)
st.markdown(
    f"""
    <section class="content-card">
      <div class="section-title">Milestones</div>
      <div class="metric-row">
        {metric_html("Longest", f"{pbs['longest_distance']:.1f} km")}
        {metric_html("Best pace", pbs['best_pace'])}
        {metric_html("Highest load", str(pbs['highest_load']))}
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown('<section class="content-card"><div class="section-title">Latest activity</div>', unsafe_allow_html=True)
if activities.empty:
    st.caption("No activities logged yet.")
else:
    for _, row in activities.sort_values("date", ascending=False).head(3).iterrows():
        value = f"{row['distance_km']:.1f} km" if row["distance_km"] > 0 else f"{row['duration_min']} min"
        st.markdown(
            f"""
            <div class="activity-row">
              <div><div class="activity-name">{row['title']}</div>
              <div class="activity-meta">{row['athlete']} · {row['type']} · {row['date']:%d %b}</div></div>
              <div class="activity-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
st.markdown("</section>", unsafe_allow_html=True)

render_bottom_nav("Home")
