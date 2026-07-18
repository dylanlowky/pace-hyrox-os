import streamlit as st
from core.config import settings
from services.supabase_client import get_supabase, reset_supabase_client

def _save_session(auth_response) -> None:
    session = getattr(auth_response, "session", None)
    user = getattr(auth_response, "user", None)
    if session is None or user is None:
        raise RuntimeError("No session was returned. Confirm your email if email confirmation is enabled.")
    st.session_state.auth_user = user
    st.session_state.auth_session = session
    st.session_state.access_token = session.access_token
    st.session_state.refresh_token = session.refresh_token
    reset_supabase_client()

def sign_in(email: str, password: str) -> None:
    client = get_supabase(authenticated=False)
    response = client.auth.sign_in_with_password({"email": email, "password": password})
    _save_session(response)

def sign_up(email: str, password: str) -> str:
    client = get_supabase(authenticated=False)
    response = client.auth.sign_up({"email": email, "password": password})
    if getattr(response, "session", None):
        _save_session(response)
        return "Account created."
    return "Account created. Check your email, confirm the address, then sign in."

def sign_out() -> None:
    try:
        client = get_supabase(authenticated=True)
        client.auth.sign_out()
    except Exception:
        pass
    for key in [
        "auth_user", "auth_session", "access_token", "refresh_token",
        "household_id", "athletes", "activities", "active_race", "remote_loaded"
    ]:
        st.session_state.pop(key, None)
    reset_supabase_client()

def render_auth_gate() -> None:
    if not settings.supabase_ready:
        st.error("Supabase is not configured. Add SUPABASE_URL and SUPABASE_ANON_KEY to .env.")
        st.stop()

    if st.session_state.get("auth_user"):
        return

    st.markdown("## Sign in to Pace")
    st.caption("Use one account for each athlete. Both accounts can belong to the same household.")

    sign_in_tab, create_tab = st.tabs(["Sign in", "Create account"])

    with sign_in_tab:
        with st.form("sign_in_form"):
            email = st.text_input("Email", key="signin_email")
            password = st.text_input("Password", type="password", key="signin_password")
            submit = st.form_submit_button("Sign in", use_container_width=True, type="primary")
        if submit:
            try:
                sign_in(email.strip(), password)
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

    with create_tab:
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            confirm = st.text_input("Confirm password", type="password")
            submit = st.form_submit_button("Create account", use_container_width=True)
        if submit:
            if len(password) < 8:
                st.error("Use at least 8 characters.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                try:
                    message = sign_up(email.strip(), password)
                    st.success(message)
                    if st.session_state.get("auth_user"):
                        st.rerun()
                except Exception as exc:
                    st.error(str(exc))

    st.stop()
