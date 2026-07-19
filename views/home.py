from datetime import datetime
from html import escape

import streamlit as st

from core.config import settings
from core.ui import metric_html, render_bottom_nav
from services.coach import build_coach_cards
from services.metrics import athlete_summary


if not st.session_state.get("household_id") and not settings.demo_mode:
    st.switch_page("views/setup.py")

race = st.session_state.get("active_race")
activities = st.session_state.activities
brief = st.session_state.weekly_brief
athletes = st.session_state.get("athletes", [])

name = "Athlete"
user = st.session_state.get("auth_user")

if athletes:
    current_athlete = None
    if user:
        current_athlete = next(
            (
                athlete
                for athlete in athletes
                if str(athlete.get("user_id")) == str(user.id)
            ),
            None,
        )
    if current_athlete is None and settings.demo_mode:
        current_athlete = athletes[0]
    if current_athlete:
        name = (
            current_athlete.get("display_name")
            or current_athlete.get("name")
            or name
        )

athlete_names = [
    row.get("display_name", row.get("name", "Athlete"))
    for row in athletes
]
options = ["Team"] + athlete_names

selected = st.segmented_control(
    "View",
    options=options,
    default=(
        st.session_state.selected_athlete
        if st.session_state.get("selected_athlete") in options
        else name if name in options else "Team"
    ),
    label_visibility="collapsed",
)
st.session_state.selected_athlete = selected or "Team"

hour = datetime.now().hour
greeting = (
    "Good morning"
    if hour < 12
    else "Good afternoon"
    if hour < 18
    else "Good evening"
)

st.markdown(f"# {greeting}, {escape(name)}")
st.caption("Your training, simplified.")

if race:
    st.markdown(
        f"""
        <section class="hero-card">
          <div class="eyebrow">Race countdown</div>
          <div class="hero-title">{race['days_remaining']} days<br>to {escape(str(race['name']))}</div>
          <div class="hero-subtitle">{escape(str(race['category']))} · Target {escape(str(race['target_time']))}</div>
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
    st.markdown(
        """
        <section class="hero-card">
          <div class="eyebrow">Race countdown</div>
          <div class="hero-title">Set your next race</div>
          <div class="hero-subtitle">Give PACE a clear target to coach toward.</div>
        </section>
        """,
        unsafe_allow_html=True,
    )

coach_cards = build_coach_cards(
    activities=activities,
    selected_athlete=st.session_state.selected_athlete,
    athlete_names=athlete_names,
)
weekly_card = coach_cards[0] if coach_cards else None

if weekly_card:
    status_label = {
        "good": "On track",
        "watch": "Needs attention",
        "alert": "Take care",
        "info": "Coach note",
    }.get(weekly_card.get("status"), "Coach note")

    st.markdown(
        f"""
        <section class="mission-card">
          <div class="eyebrow">{escape(str(weekly_card.get('eyebrow', 'Weekly progress')))}</div>
          <div class="mission-title">{escape(str(weekly_card.get('title', 'Ready when you are')))}</div>
          <div class="mission-meta">{escape(str(weekly_card.get('message', 'Log your next session and PACE will update your coaching.')))}</div>
          <div style="margin-top:.95rem;color:#ffd400;font-size:.82rem;font-weight:820;">
            {escape(status_label)} &nbsp;›
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

if st.button("👟  Log workout", type="primary", use_container_width=True):
    st.switch_page("views/activities.py")

summary = athlete_summary(
    activities,
    st.session_state.selected_athlete,
)

st.markdown(
    f"""
    <section class="content-card">
      <div class="eyebrow">This week · {escape(str(st.session_state.selected_athlete))}</div>
      <div class="metric-row" style="max-width:100%;">
        {metric_html("Sessions", str(summary['sessions']))}
        {metric_html("Distance", f"{summary['distance_km']:.1f} km")}
        {metric_html("Load", f"{int(summary['training_load'])}")}
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<section class="content-card"><div class="section-title">Latest workout</div>',
    unsafe_allow_html=True,
)

selected_activities = activities
if st.session_state.selected_athlete != "Team":
    selected_activities = activities[
        activities["athlete"] == st.session_state.selected_athlete
    ]

if selected_activities.empty:
    st.caption("No activities logged yet.")
else:
    row = selected_activities.sort_values("date", ascending=False).iloc[0]
    value = (
        f"{row['distance_km']:.1f} km"
        if row["distance_km"] > 0
        else f"{row['duration_min']} min"
    )
    st.markdown(
        f"""
        <div class="activity-row">
          <div>
            <div class="activity-name">{escape(str(row['title']))}</div>
            <div class="activity-meta">{escape(str(row['athlete']))} · {escape(str(row['type']))} · {row['date']:%d %b}</div>
          </div>
          <div class="activity-value">{escape(value)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("</section>", unsafe_allow_html=True)

render_bottom_nav("Today")
