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

st.title("Activities")
st.caption("Log a workout in under 30 seconds, then let Pace update the rest.")

activities = st.session_state.activities
athlete_names = [
    row.get("display_name", row.get("name", "Athlete"))
    for row in st.session_state.get("athletes", [])
]

with st.container(border=True):
    st.markdown("### Quick log")
    activity_type = st.segmented_control(
        "Workout type",
        ["Run", "Hybrid", "Strength", "Recovery"],
        default="Run",
        label_visibility="collapsed",
    )

    with st.form("quick_activity", clear_on_submit=True):
        c1, c2 = st.columns(2)
        workout_date = c1.date_input("Date", value=date.today())
        athlete = c2.selectbox("Athlete", athlete_names)

        title_defaults = {
            "Run": "Run",
            "Hybrid": "HYROX hybrid",
            "Strength": "Strength training",
            "Recovery": "Recovery session",
        }
        title = st.text_input("Workout name", value=title_defaults[activity_type])

        if activity_type in {"Run", "Hybrid"}:
            c3, c4 = st.columns(2)
            distance = c3.number_input("Distance (km)", min_value=0.1, step=0.1, value=5.0)
            duration = c4.number_input("Duration (min)", min_value=1, step=1, value=35)
            avg_hr = st.number_input("Average heart rate (optional)", min_value=0, max_value=230, step=1, value=0)
        else:
            distance = 0.0
            duration = st.number_input("Duration (min)", min_value=1, step=1, value=45)
            avg_hr = 0

        c5, c6 = st.columns(2)
        rpe = c5.slider("RPE", 1, 10, 5)
        pain = c6.slider("Pain", 0, 10, 0)

        pain_location = ""
        if pain > 0:
            pain_location = st.text_input("Pain location", placeholder="Example: front of right knee")

        trained_together = st.checkbox("Trained together")
        notes = st.text_area("Notes (optional)", placeholder="Stations, intervals, conditions or anything worth remembering.")

        submitted = st.form_submit_button(
            "Save workout",
            use_container_width=True,
            type="primary",
        )

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
            st.session_state.activities = pd.concat(
                [activities, pd.DataFrame([new_activity])],
                ignore_index=True,
            )
            refresh_brief()
        else:
            athlete_record = next(
                row for row in st.session_state.athletes
                if row["display_name"] == athlete
            )
            PaceRepository().add_activity(
                athlete_record["id"],
                workout_date,
                activity_type,
                title,
                distance,
                duration,
                avg_hr,
                rpe,
                pain,
                pain_location,
                notes,
                trained_together,
            )
            st.session_state.remote_loaded = False
            load_remote_state(force=True)
        st.success("Workout saved. Dashboard and Coach updated.")
        st.rerun()

st.subheader("Recent workouts")
filter_options = ["All"] + athlete_names
athlete_filter = st.segmented_control(
    "Athlete",
    filter_options,
    default="All",
    label_visibility="collapsed",
)
filtered = activities if athlete_filter == "All" else activities[activities["athlete"] == athlete_filter]

if filtered.empty:
    st.info("No activities logged yet.")
else:
    for _, row in filtered.sort_values("date", ascending=False).head(20).iterrows():
        pace = format_pace(int(row["pace_seconds"])) if pd.notna(row.get("pace_seconds")) and row.get("pace_seconds") else "—"
        pain_text = "No pain" if row["pain"] == 0 else f"Pain {row['pain']}/10"
        with st.container(border=True):
            left, right = st.columns([3, 1])
            with left:
                st.markdown(f"**{row['title']}**")
                together = " · Together" if row.get("trained_together") else ""
                st.caption(f"{row['athlete']} · {row['type']} · {row['date']:%d %b %Y}{together}")
            with right:
                if row["distance_km"] > 0:
                    st.markdown(f"**{row['distance_km']:.1f} km**")
                else:
                    st.markdown(f"**{row['duration_min']} min**")
                st.caption(pace if row["distance_km"] > 0 else f"Load {int(row['training_load'])}")
            hr_text = f"Avg HR {row['avg_hr']} · " if row["avg_hr"] else ""
            st.caption(f"{hr_text}RPE {row['rpe']}/10 · Load {int(row['training_load'])} · {pain_text}")
            if row.get("notes"):
                st.caption(row["notes"])

render_bottom_nav("Activities")
