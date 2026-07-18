from datetime import datetime
import streamlit as st

from core.config import settings
from core.ui import metric_html, render_bottom_nav
from services.metrics import athlete_summary, personal_bests

if not st.session_state.get("household_id") and not settings.demo_mode:
    st.switch_page("views/setup.py")

race = st.session_state.get("active_race")
activities = st.session_state.activities
brief = st.session_state.weekly_brief
athletes = st.session_state.get("athletes", [])

name = "Athlete"
if athletes:
    name = athletes[0].get("display_name") or athletes[0].get("name") or name
hour = datetime.now().hour
greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"

st.markdown(f"# {greeting}, {name}")
st.caption("Here is what matters for your training today.")

if race:
    st.markdown(
        f"""
        <section class="hero-card">
          <div class="eyebrow">Race countdown</div>
          <div class="hero-title">{race['days_remaining']} days to {race['name']}</div>
          <div class="hero-subtitle">{race['category']} · Target {race['target_time']}</div>
          <div class="metric-row">
            {metric_html("Status", brief['status'], "status-good")}
            {metric_html("Phase", "Build")}
            {metric_html("Team", str(len(athletes)))}
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
else:
    st.info("Add your active race so Pace can coach toward a clear target.")
    if st.button("Set active race", type="primary", use_container_width=True):
        st.switch_page("views/race.py")

st.markdown(
    f"""
    <section class="mission-card">
      <div class="eyebrow">Today</div>
      <div class="mission-title">Keep the next session purposeful</div>
      <div class="mission-meta">{brief['focus'][0] if brief.get('focus') else 'Log your next session and Pace will update the recommendation.'}</div>
    </section>
    """,
    unsafe_allow_html=True,
)

if st.button("Log workout", type="primary", use_container_width=True):
    st.switch_page("views/activities.py")

st.markdown(
    f"""
    <section class="coach-card">
      <div class="eyebrow">Coach noticed</div>
      <div class="coach-lead">{brief['headline']}</div>
      <div class="muted">{brief['summary']}</div>
    </section>
    """,
    unsafe_allow_html=True,
)
if st.button("Open full coach brief", use_container_width=True):
    st.switch_page("views/coach.py")

athlete_names = [row.get("display_name", row.get("name", "Athlete")) for row in athletes]
options = ["Team"] + athlete_names
selected = st.segmented_control(
    "View",
    options=options,
    default=st.session_state.selected_athlete if st.session_state.get("selected_athlete") in options else "Team",
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

st.markdown('<section class="content-card"><div class="section-title">Latest workout</div>', unsafe_allow_html=True)
if activities.empty:
    st.caption("No activities logged yet.")
else:
    row = activities.sort_values("date", ascending=False).iloc[0]
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

c1, c2 = st.columns(2)
with c1:
    if st.button("View progress", use_container_width=True):
        st.switch_page("views/progress.py")
with c2:
    if st.button("Race details", use_container_width=True):
        st.switch_page("views/race.py")

render_bottom_nav("Today")
