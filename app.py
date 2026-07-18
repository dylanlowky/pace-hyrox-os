import streamlit as st

from core.auth import render_auth_gate
from core.config import settings
from core.state import initialize_state, load_remote_state
from core.ui import apply_global_styles, render_brand_header

st.set_page_config(
    page_title="Pace",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_global_styles()
initialize_state()

if not settings.demo_mode:
    render_auth_gate()
    load_remote_state()

if not settings.demo_mode and not st.session_state.get("household_id"):
    pages = [
        st.Page("views/setup.py", title="Setup", icon="🔗", default=True),
    ]
else:
    pages = [
        st.Page("views/home.py", title="Home", icon="🏠", default=True),
        st.Page("views/activities.py", title="Activities", icon="🏃"),
        st.Page("views/progress.py", title="Progress", icon="📈"),
        st.Page("views/coach.py", title="Coach", icon="🤖"),
        st.Page("views/race.py", title="Race", icon="🎯"),
        st.Page("views/profile.py", title="Profile", icon="👤"),
    ]

navigation = st.navigation({"Pace": pages}, position="hidden")
render_brand_header()
navigation.run()
