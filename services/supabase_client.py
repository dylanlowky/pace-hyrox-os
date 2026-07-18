from core.config import settings
import streamlit as st
from supabase import create_client, ClientOptions

def reset_supabase_client() -> None:
    st.session_state.pop("_supabase_anon", None)
    st.session_state.pop("_supabase_auth", None)

def get_supabase(authenticated: bool = True):
    if not settings.supabase_ready:
        return None

    key = "_supabase_auth" if authenticated else "_supabase_anon"
    if key not in st.session_state:
        options = ClientOptions(
            persist_session=False,
            auto_refresh_token=False,
        )
        client = create_client(settings.supabase_url, settings.supabase_anon_key, options=options)

        if authenticated:
            access = st.session_state.get("access_token")
            refresh = st.session_state.get("refresh_token")
            if not access or not refresh:
                raise RuntimeError("Authentication session is missing.")
            client.auth.set_session(access, refresh)

        st.session_state[key] = client

    return st.session_state[key]
