from datetime import date

import streamlit as st

from core.auth import sign_out
from core.config import settings
from core.state import load_remote_state
from core.ui import render_bottom_nav
from services.repositories import PaceRepository

if not st.session_state.get("household_id") and not settings.demo_mode:
    st.switch_page("views/setup.py")

household = st.session_state.get("household") or {}
athletes = st.session_state.get("athletes", [])

if settings.demo_mode:
    current_athlete = athletes[0] if athletes else {
        "display_name": "Dylan",
        "birth_year": 1989,
        "height_cm": 176,
        "current_weight_kg": 75,
        "injury_notes": "",
    }
    user_email = "demo@pace.local"
else:
    repo = PaceRepository()
    user = st.session_state.auth_user
    user_email = user.email
    current_athlete = repo.get_my_athlete(st.session_state.household_id, str(user.id))

initials = "".join(
    part[0].upper()
    for part in current_athlete.get("display_name", "Athlete").split()[:2]
)

st.markdown(
    f"""
    <section class="profile-summary">
      <div class="profile-avatar">{initials or 'A'}</div>
      <div>
        <div class="profile-name">{current_athlete.get('display_name', 'Athlete')}</div>
        <div class="profile-meta">{user_email}</div>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown("### Your team")
with st.container(border=True):
    st.markdown(f"**{household.get('name', 'PACE Team')}**")
    st.caption(
        f"{len(athletes)} athlete{'s' if len(athletes) != 1 else ''} training together"
    )
    st.markdown("**Invite your partner**")
    st.code(household.get("invite_code", "Unavailable"))
    st.caption(
        "Share this one-time team code. Your partner creates a separate login, chooses ‘Join my partner’, and completes their own athlete profile."
    )

st.markdown("### Athlete profile")
profile_bits = []
if current_athlete.get("birth_year"):
    profile_bits.append(f"Born {int(current_athlete['birth_year'])}")
if current_athlete.get("height_cm"):
    profile_bits.append(f"{float(current_athlete['height_cm']):.0f} cm")
if current_athlete.get("current_weight_kg"):
    profile_bits.append(f"{float(current_athlete['current_weight_kg']):.1f} kg")

with st.container(border=True):
    st.markdown(f"**{current_athlete.get('display_name', 'Athlete')}**")
    st.caption(" · ".join(profile_bits) if profile_bits else "Profile not completed")
    if current_athlete.get("injury_notes"):
        st.caption(f"Coach context: {current_athlete['injury_notes']}")

with st.expander("Edit my athlete profile"):
    with st.form("athlete_profile"):
        display_name = st.text_input(
            "Display name",
            value=current_athlete.get("display_name") or "",
        )
        current_year = date.today().year
        birth_year = st.number_input(
            "Birth year",
            min_value=1940,
            max_value=current_year,
            value=int(current_athlete.get("birth_year") or 1989),
            step=1,
        )
        c1, c2 = st.columns(2)
        height_cm = c1.number_input(
            "Height (cm)",
            min_value=100.0,
            max_value=230.0,
            value=float(current_athlete.get("height_cm") or 176.0),
            step=0.5,
        )
        weight_kg = c2.number_input(
            "Weight (kg)",
            min_value=30.0,
            max_value=250.0,
            value=float(current_athlete.get("current_weight_kg") or 75.0),
            step=0.1,
        )
        injury_notes = st.text_area(
            "Coaching context",
            value=current_athlete.get("injury_notes") or "",
            placeholder="Example: Monitor knee discomfort after hybrid sessions.",
        )
        saved = st.form_submit_button(
            "Save profile",
            use_container_width=True,
            type="primary",
        )

    if saved:
        if settings.demo_mode:
            st.success("Profile saved in demo mode.")
        else:
            try:
                repo.update_athlete_profile(
                    current_athlete["id"],
                    display_name,
                    int(birth_year),
                    float(height_cm),
                    float(weight_kg),
                    injury_notes,
                )
                st.session_state.remote_loaded = False
                load_remote_state(force=True)
                st.success("Profile updated.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

c1, c2 = st.columns(2)
with c1:
    if st.button("Progress", use_container_width=True):
        st.switch_page("views/progress.py")
with c2:
    if st.button("Race", use_container_width=True):
        st.switch_page("views/race.py")

st.markdown("### Team athletes")
for athlete in athletes:
    athlete_name = athlete.get("display_name") or "Athlete"
    details = []
    if athlete.get("height_cm"):
        details.append(f"{float(athlete['height_cm']):.0f} cm")
    if athlete.get("current_weight_kg"):
        details.append(f"{float(athlete['current_weight_kg']):.1f} kg")
    with st.container(border=True):
        st.markdown(f"**{athlete_name}**")
        st.caption(" · ".join(details) if details else "Profile not completed")

if not settings.demo_mode:
    if st.button("Sign out", use_container_width=True):
        sign_out()
        st.rerun()

render_bottom_nav("Me")
