from html import escape

import streamlit as st

from core.config import settings
from core.ui import icon_svg, render_bottom_nav
from services.coach import build_coach_cards


if not st.session_state.get("household_id") and not settings.demo_mode:
    st.switch_page("views/setup.py")

activities = st.session_state.activities
athletes = st.session_state.get("athletes", [])

athlete_names = [
    row.get("display_name", row.get("name", "Athlete"))
    for row in athletes
]
options = ["Team"] + athlete_names

selected = st.segmented_control(
    "Coach view",
    options=options,
    default=(
        st.session_state.selected_athlete
        if st.session_state.get("selected_athlete") in options
        else "Team"
    ),
    label_visibility="collapsed",
)
st.session_state.selected_athlete = selected or "Team"

st.markdown("# Coach")
st.caption(
    f"Rule-based coaching for {st.session_state.selected_athlete}. "
    "Only meaningful insights are shown."
)

cards = build_coach_cards(
    activities=activities,
    selected_athlete=st.session_state.selected_athlete,
    athlete_names=athlete_names,
)

ICON_BY_EYEBROW = {
    "Weekly progress": "target",
    "Partner coach": "team",
    "Training balance": "balance",
    "Training time": "clock",
    "Consistency": "trend",
    "Recovery": "heart",
    "Body check": "body",
    "Progress trend": "progress",
    "Progress moment": "trophy",
}

HIDE_PHRASES = (
    "starts after logging",
    "needs history",
    "keep building the data",
    "no pain history yet",
)

visible_cards = []
for index, card in enumerate(cards):
    combined = f"{card.get('title', '')} {card.get('message', '')}".casefold()
    if index != 0 and any(phrase in combined for phrase in HIDE_PHRASES):
        continue
    visible_cards.append(card)

if not visible_cards:
    st.info("Log a workout to unlock your first coach insight.")

for card in visible_cards:
    eyebrow = str(card.get("eyebrow", "PACE Coach"))
    title = str(card.get("title", "Coach insight"))
    message = str(card.get("message", ""))
    status = card.get("status", "info")

    icon_name = next(
        (
            value
            for key, value in ICON_BY_EYEBROW.items()
            if eyebrow.casefold().startswith(key.casefold())
        ),
        "coach",
    )

    status_text = {
        "good": "On track",
        "watch": "Needs attention",
        "alert": "Take care",
        "info": "Coach note",
    }.get(status, "Coach note")

    st.markdown(
        f"""
        <section class="insight-card">
          <div class="insight-row">
            <div class="insight-icon">{icon_svg(icon_name)}</div>
            <div>
              <div class="eyebrow">{escape(eyebrow)}</div>
              <div class="insight-title">
                {escape(title)}
                <span class="insight-status">{escape(status_text)}</span>
              </div>
              <div class="insight-message">{escape(message)}</div>
            </div>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

if st.button("Log workout", type="primary", use_container_width=True, icon=":material/exercise:"):
    st.switch_page("views/activities.py")

render_bottom_nav("Coach")
