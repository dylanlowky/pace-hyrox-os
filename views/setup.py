import streamlit as st
from services.repositories import PaceRepository

st.title("Set up your Pace household")
st.caption("Create the shared training space, or join your partner's existing household.")

repo = PaceRepository()
create_tab, join_tab = st.tabs(["Create household", "Join partner"])

with create_tab:
    with st.form("create_household"):
        household_name = st.text_input("Household name", value="Dylan & Partner")
        athlete_name = st.text_input("Your athlete name", value="Dylan")
        submitted = st.form_submit_button("Create", use_container_width=True, type="primary")
    if submitted:
        try:
            repo.create_household(household_name.strip(), athlete_name.strip())
            st.session_state.remote_loaded = False
            st.success("Household created.")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))

with join_tab:
    with st.form("join_household"):
        invite_code = st.text_input("Invite code").upper()
        athlete_name = st.text_input("Your athlete name", key="join_name")
        submitted = st.form_submit_button("Join", use_container_width=True)
    if submitted:
        try:
            repo.join_household(invite_code, athlete_name.strip())
            st.session_state.remote_loaded = False
            st.success("Household joined.")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))
