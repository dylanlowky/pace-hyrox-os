from datetime import date
from html import escape

import pandas as pd
import streamlit as st

from core.config import settings
from core.state import load_remote_state, refresh_brief
from core.ui import icon_svg, render_bottom_nav
from services.metrics import calculate_activity_metrics, format_pace
from services.repositories import PaceRepository


if not st.session_state.get("household_id") and not settings.demo_mode:
    st.switch_page("views/setup.py")


def _page_intro() -> None:
    st.markdown(
        f"""
        <section class="pace-page-intro">
          <div class="pace-page-icon">{icon_svg("log")}</div>
          <div>
            <div class="pace-page-title">Log workout</div>
            <div class="pace-page-subtitle">Capture the essentials. PACE calculates the rest.</div>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _rpe_description(value: int) -> str:
    if value <= 2:
        return "Very easy"
    if value <= 4:
        return "Easy"
    if value <= 6:
        return "Moderate"
    if value <= 8:
        return "Hard"
    return "Max effort"


def _pain_score(level: str) -> int:
    return {
        "🟢 None": 0,
        "🟡 Mild": 2,
        "🟠 Moderate": 5,
        "🔴 Severe": 8,
    }[level]


def _pace_preview(distance_km: float, duration_min: int) -> str:
    if distance_km <= 0 or duration_min <= 0:
        return "—"
    total_seconds = int(duration_min * 60 / distance_km)
    return format_pace(total_seconds)


_page_intro()

activities = st.session_state.activities
athlete_names = [
    row.get("display_name", row.get("name", "Athlete"))
    for row in st.session_state.get("athletes", [])
]

st.markdown('<div class="workout-type-label">Choose workout</div>', unsafe_allow_html=True)
activity_type = st.segmented_control(
    "Workout type",
    ["🏃 Run", "🔥 Hybrid", "🏋 Strength", "🧘 Recovery"],
    default="🏃 Run",
    label_visibility="collapsed",
)

type_map = {
    "🏃 Run": "Run",
    "🔥 Hybrid": "Hybrid",
    "🏋 Strength": "Strength",
    "🧘 Recovery": "Recovery",
}
activity_type_value = type_map.get(activity_type, "Run")

title_defaults = {
    "Run": "Run",
    "Hybrid": "HYROX hybrid",
    "Strength": "Strength training",
    "Recovery": "Recovery session",
}

st.markdown(
    f"""
    <section class="pace-input-card">
      <div class="pace-section-label">{icon_svg("target")} Session details</div>
    </section>
    """,
    unsafe_allow_html=True,
)

c1, c2 = st.columns(2)
workout_date = c1.date_input("Date", value=date.today())
athlete = c2.selectbox(
    "Athlete",
    athlete_names,
    disabled=not athlete_names,
)
title = st.text_input(
    "Workout name",
    value=title_defaults.get(activity_type_value, "Workout"),
)

if activity_type_value in {"Run", "Hybrid"}:
    d1, d2 = st.columns(2)
    distance = d1.number_input(
        "Distance (km)",
        min_value=0.1,
        step=0.1,
        value=5.0,
    )
    duration = d2.number_input(
        "Duration (min)",
        min_value=1,
        step=1,
        value=35,
    )
else:
    distance = 0.0
    duration = st.number_input(
        "Duration (min)",
        min_value=1,
        step=1,
        value=45,
    )

with st.expander("Heart rate and notes", expanded=False):
    avg_hr = st.number_input(
        "Average heart rate",
        min_value=0,
        max_value=230,
        step=1,
        value=0,
    )
    notes = st.text_area(
        "Notes",
        placeholder=(
            "Stations, intervals or conditions"
            if activity_type_value in {"Run", "Hybrid"}
            else "What did you work on?"
        ),
    )

st.markdown(
    f"""
    <section class="pace-input-card">
      <div class="pace-section-label">{icon_svg("phase")} How hard did it feel?</div>
      <div class="rpe-guide">
        <div class="rpe-zone">
          <div class="rpe-zone-icon">😌</div>
          <div class="rpe-zone-name">Very easy</div>
          <div class="rpe-zone-range">RPE 1–2</div>
        </div>
        <div class="rpe-zone">
          <div class="rpe-zone-icon">🙂</div>
          <div class="rpe-zone-name">Easy</div>
          <div class="rpe-zone-range">RPE 3–4</div>
        </div>
        <div class="rpe-zone">
          <div class="rpe-zone-icon">😊</div>
          <div class="rpe-zone-name">Moderate</div>
          <div class="rpe-zone-range">RPE 5–6</div>
        </div>
        <div class="rpe-zone">
          <div class="rpe-zone-icon">😅</div>
          <div class="rpe-zone-name">Hard</div>
          <div class="rpe-zone-range">RPE 7–8</div>
        </div>
        <div class="rpe-zone">
          <div class="rpe-zone-icon">🥵</div>
          <div class="rpe-zone-name">Max effort</div>
          <div class="rpe-zone-range">RPE 9–10</div>
        </div>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

rpe = st.slider(
    "Effort · RPE",
    min_value=1,
    max_value=10,
    value=5,
)
st.caption(f"Selected: **RPE {rpe} · {_rpe_description(rpe)}**")

st.markdown(
    f"""
    <section class="pace-input-card">
      <div class="pace-section-label">{icon_svg("body")} Body check</div>
      <div class="pain-guide">
        <div class="pain-level"><div class="pain-dot pain-none"></div>None</div>
        <div class="pain-level"><div class="pain-dot pain-mild"></div>Mild</div>
        <div class="pain-level"><div class="pain-dot pain-moderate"></div>Moderate</div>
        <div class="pain-level"><div class="pain-dot pain-severe"></div>Severe</div>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

pain_level = st.segmented_control(
    "Pain",
    ["🟢 None", "🟡 Mild", "🟠 Moderate", "🔴 Severe"],
    default="🟢 None",
    label_visibility="collapsed",
)
pain = _pain_score(pain_level or "🟢 None")

pain_location = ""
if pain > 0:
    pain_location = st.text_input(
        "Where do you feel it?",
        placeholder="Example: front of right knee",
    )

trained_together = st.checkbox("👥 Completed together")

pace_preview = (
    _pace_preview(float(distance), int(duration))
    if activity_type_value in {"Run", "Hybrid"}
    else "—"
)
training_load_preview = int(duration) * int(rpe)

st.markdown(
    f"""
    <section class="pace-live-summary">
      <div class="summary-primary">
        <div class="summary-kicker">Workout preview</div>
        <div class="summary-title">{escape(title or activity_type_value)}</div>
      </div>
      <div class="summary-stat">
        <div class="summary-label">Duration</div>
        <div class="summary-value">{int(duration)} min</div>
      </div>
      <div class="summary-stat">
        <div class="summary-label">Distance</div>
        <div class="summary-value">{float(distance):.1f} km</div>
      </div>
      <div class="summary-stat">
        <div class="summary-label">Pace</div>
        <div class="summary-value">{escape(pace_preview)}</div>
      </div>
      <div class="summary-stat">
        <div class="summary-label">Load</div>
        <div class="summary-value">{training_load_preview}</div>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

submitted = st.button(
    "Finish workout",
    type="primary",
    use_container_width=True,
    icon=":material/check_circle:",
    disabled=not athlete_names,
)

if submitted:
    if settings.demo_mode:
        new_activity = calculate_activity_metrics(
            {
                "date": workout_date,
                "athlete": athlete,
                "type": activity_type_value,
                "title": title or activity_type_value,
                "distance_km": distance,
                "duration_min": duration,
                "avg_hr": avg_hr,
                "rpe": rpe,
                "pain": pain,
                "pain_location": pain_location,
                "notes": notes,
                "trained_together": trained_together,
            }
        )
        st.session_state.activities = pd.concat(
            [activities, pd.DataFrame([new_activity])],
            ignore_index=True,
        )
        refresh_brief()
        st.session_state["pace_saved"] = True
        st.rerun()
    else:
        athlete_record = next(
            (
                row
                for row in st.session_state.athletes
                if row.get("display_name") == athlete
                or row.get("name") == athlete
            ),
            None,
        )

        if athlete_record is None:
            st.error("Athlete profile could not be found.")
        else:
            PaceRepository().add_activity(
                athlete_record["id"],
                workout_date,
                activity_type_value,
                title or activity_type_value,
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
            st.session_state["pace_saved"] = True
            st.rerun()

if st.session_state.pop("pace_saved", False):
    st.success("Workout saved. Your briefing and Coach are updated.")
    if st.button(
        "Back to Today",
        type="primary",
        use_container_width=True,
        icon=":material/home:",
    ):
        st.switch_page("views/home.py")

st.markdown("## Recent workouts")

filter_options = ["All"] + athlete_names
athlete_filter = st.segmented_control(
    "Athlete",
    filter_options,
    default="All",
    label_visibility="collapsed",
)
filtered = (
    activities
    if athlete_filter in {None, "All"}
    else activities[activities["athlete"] == athlete_filter]
)

if filtered.empty:
    st.info("No activities logged yet.")
else:
    for _, row in (
        filtered.sort_values("date", ascending=False)
        .head(10)
        .iterrows()
    ):
        pace = (
            format_pace(int(row["pace_seconds"]))
            if pd.notna(row.get("pace_seconds"))
            and row.get("pace_seconds")
            else "—"
        )
        value = (
            f'{row["distance_km"]:.1f} km'
            if row["distance_km"] > 0
            else f'{row["duration_min"]} min'
        )
        together = " · Together" if row.get("trained_together") else ""
        secondary = (
            pace
            if row["distance_km"] > 0
            else f'Load {int(row["training_load"])}'
        )

        st.markdown(
            f"""
            <section class="recent-workout-card">
              <div class="recent-row">
                <div>
                  <div class="recent-title">{escape(str(row["title"]))}</div>
                  <div class="recent-meta">
                    {escape(str(row["athlete"]))} ·
                    {escape(str(row["type"]))} ·
                    {row["date"]:%d %b %Y}{escape(together)}
                  </div>
                </div>
                <div>
                  <div class="recent-value">{escape(value)}</div>
                  <div class="recent-subvalue">{escape(secondary)}</div>
                </div>
              </div>
            </section>
            """,
            unsafe_allow_html=True,
        )

render_bottom_nav("Log")
