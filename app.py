import streamlit as st

from core.auth import render_auth_gate
from core.config import settings
from core.state import initialize_state, load_remote_state
from core.ui import apply_global_styles, render_brand_header

st.set_page_config(
    page_title="PACE",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_global_styles()
initialize_state()

if not settings.demo_mode:
    render_auth_gate()
    load_remote_state()

needs_household = not settings.demo_mode and not st.session_state.get("household_id")
needs_profile = False

if not settings.demo_mode and not needs_household:
    user = st.session_state.get("auth_user")
    athletes = st.session_state.get("athletes", [])
    current_athlete = next(
        (athlete for athlete in athletes if str(athlete.get("user_id")) == str(user.id)),
        None,
    )
    needs_profile = bool(
        current_athlete
        and (
            not current_athlete.get("birth_year")
            or not current_athlete.get("height_cm")
            or not current_athlete.get("current_weight_kg")
        )
    )

if needs_household:
    pages = [st.Page("views/setup.py", title="Welcome", icon="👋", default=True)]
elif needs_profile:
    pages = [st.Page("views/onboarding.py", title="Athlete setup", icon="🏃", default=True)]
else:
    pages = [
        st.Page("views/home.py", title="Today", icon="🏠", default=True),
        st.Page("views/activities.py", title="Log", icon="➕"),
        st.Page("views/coach.py", title="Coach", icon="🤖"),
        st.Page("views/profile.py", title="Me", icon="👤"),
        st.Page("views/progress.py", title="Progress", icon="📈"),
        st.Page("views/race.py", title="Race", icon="🎯"),
    ]

navigation = st.navigation({"PACE": pages}, position="hidden")
render_brand_header()
navigation.run()
