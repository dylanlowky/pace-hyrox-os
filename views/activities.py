from datetime import date
import pandas as pd
import streamlit as st

from core.config import settings
from core.state import load_remote_state, refresh_brief
from core.ui import render_bottom_nav
from services.metrics import calculate_activity_metrics, format_pace
from services.repositories import PaceRepository

if not st.session_state.get("household_id") and not settings.demo_mode:
    st.switch_page("views/setup.py")

st.title("Log workout")
st.caption("Capture the essentials. Pace will calculate the rest.")

activities = st.session_state.activities
athlete_names = [row.get("display_name", row.get("name", "Athlete")) for row in st.session_state.get("athletes", [])]

activity_type = st.segmented_control(
    "Workout type",
    ["Run", "Hybrid", "Strength", "Recovery"],
    default="Run",
    label_visibility="collapsed",
)

with st.form("quick_activity", clear_on_submit=True):
    title_defaults = {
        "Run": "Run",
        "Hybrid": "HYROX hybrid",
        "Strength": "Strength training",
        "Recovery": "Recovery session",
    }
    workout_date = st.date_input("Date", value=date.today())
    athlete = st.selectbox("Athlete", athlete_names)
    title = st.text_input("Workout name", value=title_defaults[activity_type])

    if activity_type in {"Run", "Hybrid"}:
        c1, c2 = st.columns(2)
        distance = c1.number_input("Distance (km)", min_value=0.1, step=0.1, value=5.0)
        duration = c2.number_input("Duration (min)", min_value=1, step=1, value=35)
        with st.expander("Heart rate and notes"):
            avg_hr = st.number_input("Average heart rate", min_value=0, max_value=230, step=1, value=0)
            notes = st.text_area("Notes", placeholder="Stations, intervals or conditions")
    else:
        distance = 0.0
        duration = st.number_input("Duration (min)", min_value=1, step=1, value=45)
        avg_hr = 0
        with st.expander("Notes"):
            notes = st.text_area("Notes", placeholder="What did you work on?")

    c3, c4 = st.columns(2)
    rpe = c3.slider("Effort · RPE", 1, 10, 5)
    pain = c4.slider("Pain", 0, 10, 0)
    pain_location = st.text_input("Pain location", placeholder="Example: front of right knee") if pain > 0 else ""
    trained_together = st.checkbox("Completed together")
    submitted = st.form_submit_button("Save workout", use_container_width=True, type="primary")

if submitted:
    if settings.demo_mode:
        new_activity = calculate_activity_metrics({
            "date": workout_date,
            "athlete": athlete,
            "type": activity_type,
            "title": title or activity_type,
            "distance_km": distance,
            "duration_min": duration,
            "avg_hr": avg_hr,
            "rpe": rpe,
            "pain": pain,
            "pain_location": pain_location,
            "notes": notes,
            "trained_together": trained_together,
        })
        st.session_state.activities = pd.concat([activities, pd.DataFrame([new_activity])], ignore_index=True)
        refresh_brief()
    else:
        athlete_record = next(row for row in st.session_state.athletes if row["display_name"] == athlete)
        PaceRepository().add_activity(
            athlete_record["id"], workout_date, activity_type, title, distance, duration,
            avg_hr, rpe, pain, pain_location, notes, trained_together,
        )
        st.session_state.remote_loaded = False
        load_remote_state(force=True)
    st.session_state["pace_saved"] = True
    st.rerun()

if st.session_state.pop("pace_saved", False):
    st.success("Workout saved. Your briefing and Coach are updated.")
    if st.button("Back to Today", type="primary", use_container_width=True):
        st.switch_page("views/home.py")

st.subheader("Recent workouts")
filter_options = ["All"] + athlete_names
athlete_filter = st.segmented_control("Athlete", filter_options, default="All", label_visibility="collapsed")
filtered = activities if athlete_filter == "All" else activities[activities["athlete"] == athlete_filter]

if filtered.empty:
    st.info("No activities logged yet.")
else:
    for _, row in filtered.sort_values("date", ascending=False).head(10).iterrows():
        pace = format_pace(int(row["pace_seconds"])) if pd.notna(row.get("pace_seconds")) and row.get("pace_seconds") else "—"
        value = f"{row['distance_km']:.1f} km" if row["distance_km"] > 0 else f"{row['duration_min']} min"
        with st.container(border=True):
            left, right = st.columns([3, 1])
            with left:
                st.markdown(f"**{row['title']}**")
                together = " · Together" if row.get("trained_together") else ""
                st.caption(f"{row['athlete']} · {row['type']} · {row['date']:%d %b %Y}{together}")
            with right:
                st.markdown(f"**{value}**")
                st.caption(pace if row["distance_km"] > 0 else f"Load {int(row['training_load'])}")

render_bottom_nav("Log")
