from datetime import date

import streamlit as st

from core.state import load_remote_state
from services.repositories import PaceRepository

repo = PaceRepository()
user = st.session_state.auth_user
current_athlete = repo.get_my_athlete(st.session_state.household_id, str(user.id))

if not current_athlete:
    st.error("We could not find your athlete profile. Please sign out and try again.")
    st.stop()

name = current_athlete.get("display_name") or "Athlete"
current_year = date.today().year

st.markdown('<div class="onboarding-shell">', unsafe_allow_html=True)
st.markdown('<div class="step-pill">ATHLETE SETUP · ABOUT 30 SECONDS</div>', unsafe_allow_html=True)
st.markdown(f'<div class="welcome-title">Welcome to PACE, {name}.</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="welcome-copy">A few basics help PACE interpret training load and give more relevant coaching. You can change these later under Me.</div>',
    unsafe_allow_html=True,
)

with st.form("complete_athlete_profile"):
    display_name = st.text_input(
        "Your name",
        value=name,
        help="This is how your partner and PACE will see you.",
    )

    birth_year = st.number_input(
        "Birth year",
        min_value=1940,
        max_value=current_year,
        value=int(current_athlete.get("birth_year") or 1990),
        step=1,
    )

    c1, c2 = st.columns(2)
    height_cm = c1.number_input(
        "Height (cm)",
        min_value=100.0,
        max_value=230.0,
        value=float(current_athlete.get("height_cm") or 165.0),
        step=0.5,
    )
    weight_kg = c2.number_input(
        "Weight (kg)",
        min_value=30.0,
        max_value=250.0,
        value=float(current_athlete.get("current_weight_kg") or 60.0),
        step=0.1,
    )

    injury_notes = st.text_area(
        "Anything your coach should know? (optional)",
        value=current_athlete.get("injury_notes") or "",
        placeholder="Example: Monitor my left knee after running sessions.",
        help="Use this for injuries, recurring discomfort or other useful coaching context.",
    )

    consent = st.checkbox(
        "I understand this is training guidance, not medical advice.",
        value=False,
    )

    submitted = st.form_submit_button(
        "Enter PACE",
        use_container_width=True,
        type="primary",
    )

if submitted:
    if not display_name.strip():
        st.error("Please enter your name.")
    elif not consent:
        st.error("Please confirm the guidance notice before continuing.")
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
            st.success("Profile complete. Welcome to your team.")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))

st.caption("PACE stores this profile in your private household workspace.")
st.markdown('</div>', unsafe_allow_html=True)
