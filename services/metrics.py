from datetime import date, timedelta
import math
import pandas as pd

def current_week(df: pd.DataFrame) -> pd.DataFrame:
    start = date.today() - timedelta(days=date.today().weekday())
    return df[df["date"] >= start].copy()

def previous_week(df: pd.DataFrame) -> pd.DataFrame:
    this_start = date.today() - timedelta(days=date.today().weekday())
    last_start = this_start - timedelta(days=7)
    return df[(df["date"] >= last_start) & (df["date"] < this_start)].copy()

def athlete_summary(df: pd.DataFrame, athlete: str) -> dict:
    selected = df if athlete == "Team" else df[df["athlete"] == athlete]
    week = current_week(selected)
    return {
        "sessions": int(len(week)),
        "distance_km": float(week["distance_km"].sum()) if not week.empty else 0.0,
        "minutes": int(week["duration_min"].sum()) if not week.empty else 0,
        "avg_rpe": float(week["rpe"].replace(0, pd.NA).dropna().mean()) if not week.empty and not week["rpe"].replace(0, pd.NA).dropna().empty else 0.0,
        "pain_flags": int((week["pain"] >= 2).sum()) if not week.empty else 0,
        "training_load": float(week["training_load"].sum()) if not week.empty and "training_load" in week else 0.0,
    }

def weekly_volume(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data["date"] = pd.to_datetime(data["date"])
    data["week"] = data["date"].dt.to_period("W").apply(lambda period: period.start_time)
    return (
        data.groupby(["week", "athlete"], as_index=False)
        .agg(
            distance_km=("distance_km", "sum"),
            sessions=("title", "count"),
            training_load=("training_load", "sum"),
        )
        .sort_values("week")
    )

def pace_seconds_per_km(distance_km: float, duration_min: int) -> int | None:
    if distance_km <= 0 or duration_min <= 0:
        return None
    return round((duration_min * 60) / distance_km)

def format_pace(seconds_per_km: int | None) -> str:
    if not seconds_per_km:
        return "—"
    minutes, seconds = divmod(seconds_per_km, 60)
    return f"{minutes}:{seconds:02d}/km"

def calculate_training_load(duration_min: int, rpe: int) -> int:
    return int(duration_min) * int(rpe)

def calculate_activity_metrics(activity: dict) -> dict:
    activity = activity.copy()
    activity["pace_seconds"] = pace_seconds_per_km(
        float(activity.get("distance_km") or 0),
        int(activity.get("duration_min") or 0),
    )
    activity["pace_display"] = format_pace(activity["pace_seconds"])
    activity["training_load"] = calculate_training_load(
        int(activity.get("duration_min") or 0),
        int(activity.get("rpe") or 0),
    )
    return activity

def personal_bests(df: pd.DataFrame, athlete: str | None = None) -> dict:
    data = df.copy()
    if athlete and athlete != "Team":
        data = data[data["athlete"] == athlete]

    run_data = data[(data["distance_km"] > 0) & (data["duration_min"] > 0)].copy()
    if run_data.empty:
        return {"longest_distance": 0.0, "best_pace": "—", "highest_load": 0}

    run_data["pace_seconds"] = (
        run_data["duration_min"] * 60 / run_data["distance_km"]
    )
    best_pace_seconds = int(run_data["pace_seconds"].min())
    return {
        "longest_distance": float(run_data["distance_km"].max()),
        "best_pace": format_pace(best_pace_seconds),
        "highest_load": int(data["training_load"].max()) if "training_load" in data and not data.empty else 0,
    }

def build_dynamic_brief(df: pd.DataFrame, race: dict | None) -> dict:
    if df.empty:
        return {
            "status": "Build the baseline",
            "headline": "Log your first workout to begin receiving useful coaching.",
            "summary": "Pace needs consistent workout data before it can identify trends or make race-specific recommendations.",
            "focus": ["Log each workout within 24 hours.", "Include RPE and pain score.", "Create an active race goal." if not race else "Keep the active race details current."],
            "watch": ["No training baseline is available yet."],
        }

    current = current_week(df)
    previous = previous_week(df)

    current_sessions = len(current)
    previous_sessions = len(previous)
    current_distance = float(current["distance_km"].sum()) if not current.empty else 0
    previous_distance = float(previous["distance_km"].sum()) if not previous.empty else 0
    current_load = float(current["training_load"].sum()) if not current.empty else 0
    previous_load = float(previous["training_load"].sum()) if not previous.empty else 0
    pain_flags = int((current["pain"] >= 2).sum()) if not current.empty else 0
    high_pain = int((current["pain"] >= 5).sum()) if not current.empty else 0

    distance_change = None
    if previous_distance > 0:
        distance_change = ((current_distance - previous_distance) / previous_distance) * 100

    load_change = None
    if previous_load > 0:
        load_change = ((current_load - previous_load) / previous_load) * 100

    if high_pain:
        status = "Needs attention"
        headline = "Reduce intensity and review the pain pattern before the next hard session."
    elif pain_flags >= 2:
        status = "Watch recovery"
        headline = "Training is progressing, but repeated pain entries should limit the next workload increase."
    elif load_change is not None and load_change > 30:
        status = "Watch workload"
        headline = "Training load has increased sharply; consolidate before adding more intensity."
    elif current_sessions >= 3:
        status = "On track"
        headline = "Consistency is good; the next gain should come from repeating quality sessions."
    else:
        status = "Build consistency"
        headline = "The main priority is completing enough sessions to establish a reliable training rhythm."

    summary_parts = [
        f"This week includes {current_sessions} session{'s' if current_sessions != 1 else ''}, "
        f"{current_distance:.1f} km and {int(current_load)} training-load points."
    ]
    if distance_change is not None:
        direction = "higher" if distance_change >= 0 else "lower"
        summary_parts.append(f"Distance is {abs(distance_change):.0f}% {direction} than last week.")
    if load_change is not None:
        direction = "higher" if load_change >= 0 else "lower"
        summary_parts.append(f"Training load is {abs(load_change):.0f}% {direction}.")
    if pain_flags:
        summary_parts.append(f"{pain_flags} workout{'s' if pain_flags != 1 else ''} recorded pain of 2/10 or above.")
    elif not current.empty:
        summary_parts.append("No meaningful pain flags were recorded this week.")

    focus = []
    if current_sessions < 3:
        focus.append("Complete the next planned session before increasing intensity.")
    else:
        focus.append("Keep the next session aligned with the current training pattern.")
    if pain_flags:
        focus.append("Keep the next hard session controlled and reassess pain afterward.")
    else:
        focus.append("Continue recording RPE and pain after every workout.")
    if race:
        focus.append(f"Keep the next block focused on {race['name']} with {race['days_remaining']} days remaining.")
    else:
        focus.append("Create an active race to unlock race-specific coaching.")

    watch = []
    if high_pain:
        watch.append("Pain reached 5/10 or above. Avoid treating this as a normal training signal.")
    elif pain_flags:
        watch.append("Repeated mild pain should not be ignored if it continues or worsens.")
    if load_change is not None and load_change > 30:
        watch.append("Weekly training load increased by more than 30%.")
    if not watch:
        watch.append("No major warning signal is visible in the current data.")

    return {
        "status": status,
        "headline": headline,
        "summary": " ".join(summary_parts),
        "focus": focus,
        "watch": watch,
    }
