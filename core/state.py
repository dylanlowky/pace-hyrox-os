import streamlit as st
from data.demo import athletes, activities, active_race
from core.config import settings
from services.metrics import build_dynamic_brief, calculate_activity_metrics
from services.repositories import PaceRepository

def _enhance_demo_activities(df):
    if df.empty:
        return df
    enhanced = [calculate_activity_metrics(row) for row in df.to_dict("records")]
    return __import__("pandas").DataFrame(enhanced)

def initialize_state() -> None:
    defaults = {
        "selected_athlete": "Team",
        "chat_messages": [],
        "remote_loaded": False,
    }
    if settings.demo_mode:
        demo_activities = _enhance_demo_activities(activities())
        demo_race = active_race()
        defaults.update({
            "athletes": athletes(),
            "activities": demo_activities,
            "active_race": demo_race,
            "weekly_brief": build_dynamic_brief(demo_activities, demo_race),
            "household_id": "demo",
            "household": {
                "id": "demo",
                "name": "Dylan & Arie",
                "invite_code": "DEMO2026",
                "role": "owner",
            },
        })
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def refresh_brief() -> None:
    st.session_state.weekly_brief = build_dynamic_brief(
        st.session_state.get("activities"),
        st.session_state.get("active_race"),
    )

def load_remote_state(force: bool = False) -> None:
    if st.session_state.get("remote_loaded") and not force:
        return

    repo = PaceRepository()
    household = repo.get_my_household()

    if household is None:
        st.session_state.household_id = None
        st.session_state.household = None
        st.session_state.athletes = []
        st.session_state.activities = repo.empty_activities()
        st.session_state.active_race = None
        st.session_state.weekly_brief = build_dynamic_brief(
            st.session_state.activities, None
        )
        st.session_state.remote_loaded = True
        return

    household_id = household["id"]
    st.session_state.household_id = household_id
    st.session_state.household = household
    st.session_state.athletes = repo.list_athletes(household_id)
    st.session_state.activities = repo.list_activities(household_id)
    st.session_state.active_race = repo.get_active_race(household_id)
    refresh_brief()
    st.session_state.remote_loaded = True
