from datetime import datetime
from html import escape

import streamlit as st

from core.config import settings
from core.ui import (
    metric_html,
    progress_ring_html,
    race_hero_style,
    render_bottom_nav,
)
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
    days = int(race["days_remaining"])

    hero_html = (
        f'<section class="hero-card" style="{race_hero_style()}">'
        '<div class="hero-overlay"></div>'
        '<div class="hero-content">'
        '<div class="eyebrow">Race countdown</div>'
        f'<div class="hero-title">{days} days<br>to {escape(str(race["name"]))}</div>'
        f'<div class="hero-subtitle">{escape(str(race["category"]))} · '
        f'Target {escape(str(race["target_time"]))}</div>'
        '<div class="metric-row">'
        f'{metric_html("Status", brief["status"], "status-good", "trend")}'
        f'{metric_html("Phase", "Build", "", "phase")}'
        f'{metric_html("Team", str(len(athletes)), "", "team")}'
        '</div>'
        '</div>'
        '</section>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)

else:
    st.markdown(
        (
            '<section class="hero-card">'
            '<div class="hero-overlay"></div>'
            '<div class="hero-content">'
            '<div class="eyebrow">Race countdown</div>'
            '<div class="hero-title">Set your next race</div>'
            '<div class="hero-subtitle">'
            'Give PACE a clear target to coach toward.'
            '</div>'
            '</div>'
            '</section>'
        ),
        unsafe_allow_html=True,
    )

coach_cards = build_coach_cards(
    activities=activities,
    selected_athlete=st.session_state.selected_athlete,
    athlete_names=athlete_names,
)
weekly_card = coach_cards[0] if coach_cards else None

summary = athlete_summary(
    activities,
    st.session_state.selected_athlete,
)
weekly_sessions = int(summary["sessions"])
weekly_progress = min(round(weekly_sessions / 3 * 100), 100)

if weekly_card:
    status_label = {
        "good": "On track",
        "watch": "Needs attention",
        "alert": "Take care",
        "info": "Coach note",
    }.get(weekly_card.get("status"), "Coach note")

    mission_html = (
        '<a class="mission-link" href="/Coach" target="_self">'
        '<section class="mission-card">'
        '<div>'
        f'<div class="eyebrow">{escape(str(weekly_card.get("eyebrow", "Weekly progress")))}</div>'
        f'<div class="mission-title">{escape(str(weekly_card.get("title", "Ready when you are")))}</div>'
        f'<div class="mission-meta">{escape(str(weekly_card.get("message", "Log your next session and PACE will update your coaching.")))}</div>'
        f'<div class="coach-cta">{escape(status_label)} &nbsp;›</div>'
        '</div>'
        f'{progress_ring_html(weekly_progress)}'
        '</section>'
        '</a>'
    )
    st.markdown(mission_html, unsafe_allow_html=True)

if st.button(
    "Log workout",
    type="primary",
    use_container_width=True,
    icon=":material/exercise:",
):
    st.switch_page("views/activities.py")

week_html = (
    '<section class="content-card">'
    f'<div class="eyebrow">This week · {escape(str(st.session_state.selected_athlete))}</div>'
    '<div class="metric-row">'
    f'{metric_html("Sessions", str(summary["sessions"]), "", "target")}'
    f'{metric_html("Distance", f"{summary["distance_km"]:.1f} km", "", "progress")}'
    f'{metric_html("Load", f"{int(summary["training_load"])}", "", "phase")}'
    '</div>'
    '</section>'
)
st.markdown(week_html, unsafe_allow_html=True)

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
        f'{row["distance_km"]:.1f} km'
        if row["distance_km"] > 0
        else f'{row["duration_min"]} min'
    )

    latest_html = (
        '<div class="activity-row">'
        '<div>'
        f'<div class="activity-name">{escape(str(row["title"]))}</div>'
        f'<div class="activity-meta">{escape(str(row["athlete"]))} · '
        f'{escape(str(row["type"]))} · {row["date"]:%d %b}</div>'
        '</div>'
        f'<div class="activity-value">{escape(value)}</div>'
        '</div>'
    )
    st.markdown(latest_html, unsafe_allow_html=True)

st.markdown("</section>", unsafe_allow_html=True)

render_bottom_nav("Today")
