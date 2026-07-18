import streamlit as st

from services.repositories import PaceRepository

st.markdown('<div class="onboarding-shell">', unsafe_allow_html=True)
st.markdown('<div class="welcome-mark">🏃</div>', unsafe_allow_html=True)
st.markdown('<div class="welcome-title">Your shared road to race day.</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="welcome-copy">Create a training space for you and your partner, or join one that already exists. Each athlete keeps a personal profile while PACE coaches the team.</div>',
    unsafe_allow_html=True,
)

repo = PaceRepository()
create_tab, join_tab = st.tabs(["Create our team", "Join my partner"])

with create_tab:
    st.markdown("#### Start a new PACE team")
    st.caption("You will receive a private invite code to share with your partner.")
    with st.form("create_household"):
        household_name = st.text_input(
            "Team name",
            placeholder="Example: Dylan & Arie",
        )
        athlete_name = st.text_input(
            "What should PACE call you?",
            placeholder="Your first name",
        )
        submitted = st.form_submit_button(
            "Create our team",
            use_container_width=True,
            type="primary",
        )
    if submitted:
        if not household_name.strip() or not athlete_name.strip():
            st.error("Please enter both your team name and athlete name.")
        else:
            try:
                repo.create_household(household_name.strip(), athlete_name.strip())
                st.session_state.remote_loaded = False
                st.success("Team created. Let's complete your athlete profile.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

with join_tab:
    st.markdown("#### Join your partner")
    st.caption("Ask your partner for the invite code shown in PACE under Me.")
    with st.form("join_household"):
        invite_code = st.text_input(
            "Invite code",
            placeholder="Example: A1B2C3D4",
        ).upper()
        athlete_name = st.text_input(
            "What should PACE call you?",
            placeholder="Your first name",
            key="join_name",
        )
        submitted = st.form_submit_button(
            "Join our team",
            use_container_width=True,
            type="primary",
        )
    if submitted:
        if not invite_code.strip() or not athlete_name.strip():
            st.error("Please enter the invite code and your athlete name.")
        else:
            try:
                repo.join_household(invite_code, athlete_name.strip())
                st.session_state.remote_loaded = False
                st.success("You joined the team. Let's complete your athlete profile.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

st.markdown('</div>', unsafe_allow_html=True)
