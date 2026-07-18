import streamlit as st
from core.auth import sign_out
from core.config import settings
from core.ui import render_bottom_nav
from services.repositories import PaceRepository

st.title("Settings")

if settings.demo_mode:
    st.info("Demo mode is active. Set DEMO_MODE=false to use Supabase.")
else:
    user = st.session_state.auth_user
    st.write(f"Signed in as **{user.email}**")

    household_id = st.session_state.get("household_id")
    if household_id:
        repo = PaceRepository()
        invite_code = repo.get_invite_code(household_id)
        st.subheader("Partner invite")
        st.caption("Your partner creates a separate account and enters this code once.")
        st.code(invite_code)
    else:
        st.warning("Complete household setup first.")

    if st.button("Sign out", use_container_width=True):
        sign_out()
        st.rerun()

render_bottom_nav()
