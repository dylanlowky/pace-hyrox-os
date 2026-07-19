from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date, timedelta
from typing import Iterable

import pandas as pd


WEEKLY_SESSION_TARGET = 3
WEEKLY_DURATION_TARGET_MIN = 180
SESSION_DURATION_TARGET_MIN = 60

RUN_KEYWORDS = ("run", "running", "jog", "treadmill", "interval")
STRENGTH_KEYWORDS = (
    "strength", "weight", "weights", "gym", "resistance",
    "upper body", "lower body", "full body",
)
HYBRID_KEYWORDS = (
    "hybrid", "hyrox", "sled", "ski", "row", "burpee",
    "wall ball", "lunge", "farmer", "station",
)


@dataclass(frozen=True)
class CoachCard:
    title: str
    message: str
    status: str = "info"
    eyebrow: str = "PACE Coach"

    def to_dict(self) -> dict:
        return asdict(self)


def _empty_activities() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "date", "athlete", "type", "title", "distance_km",
            "duration_min", "avg_hr", "rpe", "pain",
            "pain_location", "training_load", "pace_seconds",
        ]
    )


def _prepare(activities: pd.DataFrame | None) -> pd.DataFrame:
    if activities is None or activities.empty:
        return _empty_activities()

    df = activities.copy()

    if "date" not in df.columns:
        return _empty_activities()

    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df = df[df["date"].notna()].copy()

    numeric_defaults = {
        "distance_km": 0.0,
        "duration_min": 0,
        "avg_hr": 0,
        "rpe": 0,
        "pain": 0,
        "training_load": 0.0,
        "pace_seconds": 0.0,
    }
    for column, default in numeric_defaults.items():
        if column not in df.columns:
            df[column] = default
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(default)

    for column in ("athlete", "type", "title", "pain_location"):
        if column not in df.columns:
            df[column] = ""
        df[column] = df[column].fillna("").astype(str)

    df["category"] = df.apply(
        lambda row: classify_activity(row.get("type", ""), row.get("title", "")),
        axis=1,
    )
    return df


def classify_activity(activity_type: str, title: str = "") -> str:
    text = f"{activity_type} {title}".strip().lower()

    if any(keyword in text for keyword in HYBRID_KEYWORDS):
        return "Hybrid"
    if any(keyword in text for keyword in STRENGTH_KEYWORDS):
        return "Strength"
    if any(keyword in text for keyword in RUN_KEYWORDS):
        return "Run"
    return "Other"


def _filter_athlete(df: pd.DataFrame, athlete_name: str) -> pd.DataFrame:
    if athlete_name == "Team":
        return df
    return df[df["athlete"].str.casefold() == athlete_name.casefold()].copy()


def _week_bounds(today: date) -> tuple[date, date]:
    start = today - timedelta(days=today.weekday())
    return start, start + timedelta(days=6)


def _current_week(df: pd.DataFrame, today: date) -> pd.DataFrame:
    start, end = _week_bounds(today)
    return df[(df["date"] >= start) & (df["date"] <= end)].copy()


def _category_counts(df: pd.DataFrame) -> dict[str, int]:
    counts = df["category"].value_counts().to_dict() if not df.empty else {}
    return {
        "Run": int(counts.get("Run", 0)),
        "Strength": int(counts.get("Strength", 0)),
        "Hybrid": int(counts.get("Hybrid", 0)),
        "Other": int(counts.get("Other", 0)),
    }


def _join_words(items: Iterable[str]) -> str:
    values = list(items)
    if not values:
        return ""
    if len(values) == 1:
        return values[0]
    return ", ".join(values[:-1]) + f" and {values[-1]}"


def _weekly_progress_card(week: pd.DataFrame, today: date) -> CoachCard:
    sessions = len(week)
    duration = int(week["duration_min"].sum()) if not week.empty else 0
    counts = _category_counts(week)

    required = ("Run", "Strength", "Hybrid")
    completed = [category for category in required if counts[category] > 0]
    missing = [category.lower() for category in required if counts[category] == 0]
    day_name = today.strftime("%A")

    if sessions == 0:
        message = (
            "A fresh week is ready. Start with the session that is easiest to schedule: "
            "one run, one strength session and one hybrid session."
        )
        status = "info"
    elif sessions >= WEEKLY_SESSION_TARGET and not missing:
        message = (
            f"Weekly target achieved: {sessions} sessions and {duration} minutes completed, "
            "including run, strength and hybrid work. Recover well and carry the consistency forward."
        )
        status = "good"
    elif sessions >= WEEKLY_SESSION_TARGET and missing:
        message = (
            f"You have completed {sessions} sessions, but {_join_words(missing)} is still missing. "
            "For a more balanced HYROX week, make the next session cover that gap."
        )
        status = "watch"
    else:
        remaining = max(WEEKLY_SESSION_TARGET - sessions, 0)
        missing_text = _join_words(missing)
        timing = "this weekend" if today.weekday() >= 4 else "later this week"
        message = (
            f"{sessions} of {WEEKLY_SESSION_TARGET} sessions completed. "
            f"{remaining} more session{'s' if remaining != 1 else ''} to go"
        )
        if missing_text:
            message += f", with {missing_text} still outstanding"
        message += f". Let’s find time {timing} to complete the week."
        status = "good" if sessions == 2 else "info"

    return CoachCard(
        title=f"{sessions} of {WEEKLY_SESSION_TARGET} sessions",
        message=message,
        status=status,
        eyebrow=f"Weekly progress · {day_name}",
    )


def _balance_card(week: pd.DataFrame) -> CoachCard:
    counts = _category_counts(week)
    required = ("Run", "Strength", "Hybrid")
    missing = [category for category in required if counts[category] == 0]

    if week.empty:
        return CoachCard(
            title="Build a balanced week",
            message="PACE will check whether your week includes running, strength and hybrid training.",
        )

    dominant = max(required, key=lambda category: counts[category])

    if not missing:
        return CoachCard(
            title="Training mix is balanced",
            message="You have covered running, strength and hybrid work this week—the core mix for your HYROX plan.",
            status="good",
            eyebrow="Training balance",
        )

    if counts[dominant] >= 3:
        return CoachCard(
            title=f"Too much {dominant.lower()} repetition",
            message=(
                f"You have logged {counts[dominant]} {dominant.lower()} sessions while "
                f"{_join_words(category.lower() for category in missing)} is missing. "
                "Use the next session to restore balance."
            ),
            status="watch",
            eyebrow="Training balance",
        )

    return CoachCard(
        title=f"Next priority: {_join_words(missing)}",
        message=(
            f"Your week already includes {_join_words(category.lower() for category in required if counts[category] > 0) or 'some training'}. "
            f"Add {_join_words(category.lower() for category in missing)} next."
        ),
        status="info",
        eyebrow="Training balance",
    )


def _duration_card(week: pd.DataFrame) -> CoachCard:
    if week.empty:
        return CoachCard(
            title="Aim for purposeful sessions",
            message=f"Your weekly guide is {WEEKLY_DURATION_TARGET_MIN} minutes across three sessions.",
            eyebrow="Training time",
        )

    total = int(week["duration_min"].sum())
    average = int(round(week["duration_min"].mean()))
    remaining = max(WEEKLY_DURATION_TARGET_MIN - total, 0)

    if total >= WEEKLY_DURATION_TARGET_MIN:
        return CoachCard(
            title=f"{total} minutes completed",
            message=(
                f"You have reached the weekly time guide. Average session length is {average} minutes; "
                "focus on recovery and quality rather than adding volume just to exceed the target."
            ),
            status="good",
            eyebrow="Training time",
        )

    if len(week) >= WEEKLY_SESSION_TARGET:
        return CoachCard(
            title=f"{total} of {WEEKLY_DURATION_TARGET_MIN} minutes",
            message=(
                f"Session consistency is good, but average duration is {average} minutes. "
                f"You are {remaining} minutes below the weekly guide. Extend a future session gradually if recovery feels good."
            ),
            status="watch",
            eyebrow="Training time",
        )

    return CoachCard(
        title=f"{total} of {WEEKLY_DURATION_TARGET_MIN} minutes",
        message=(
            f"You have {remaining} minutes remaining against the weekly guide. "
            f"A session near {SESSION_DURATION_TARGET_MIN} minutes would move the week forward well."
        ),
        eyebrow="Training time",
    )


def _consistency_card(df: pd.DataFrame, today: date) -> CoachCard:
    if df.empty:
        return CoachCard(
            title="Start the training history",
            message="Log the first workout and PACE will begin tracking consistency and gaps between sessions.",
            eyebrow="Consistency",
        )

    latest = max(df["date"])
    days_since = (today - latest).days

    recent_start = today - timedelta(days=27)
    active_dates = sorted(set(df[df["date"] >= recent_start]["date"]))
    active_weeks = len(
        {
            activity_date - timedelta(days=activity_date.weekday())
            for activity_date in active_dates
        }
    )

    if days_since == 0:
        message = "Today’s session is logged. Give recovery the same attention as the workout."
        status = "good"
    elif days_since <= 2:
        message = f"Your last session was {days_since} day{'s' if days_since != 1 else ''} ago. Your rhythm is steady."
        status = "good"
    elif days_since <= 5:
        message = f"It has been {days_since} days since your last session. Schedule the next workout before the gap grows."
        status = "info"
    else:
        message = (
            f"It has been {days_since} days since your last session. Restart with an easier workout "
            "rather than trying to recover missed volume in one day."
        )
        status = "watch"

    return CoachCard(
        title=f"Active in {active_weeks} of the last 4 weeks",
        message=message,
        status=status,
        eyebrow="Consistency",
    )


def _recovery_card(df: pd.DataFrame, today: date) -> CoachCard:
    if df.empty:
        return CoachCard(
            title="Recovery check starts after logging",
            message="Effort, pain and session spacing will help PACE flag when an easier day is sensible.",
            eyebrow="Recovery",
        )

    last_7 = df[df["date"] >= today - timedelta(days=6)].copy()
    last_5 = df[df["date"] >= today - timedelta(days=4)].copy()
    hard_sessions = int((last_5["rpe"] >= 8).sum())
    high_load_sessions = int(
        ((last_5["rpe"] >= 7) & (last_5["duration_min"] >= 45)).sum()
    )

    latest = df.sort_values("date", ascending=False).iloc[0]
    latest_rpe = int(latest["rpe"])
    latest_duration = int(latest["duration_min"])

    if hard_sessions >= 3 or high_load_sessions >= 3:
        return CoachCard(
            title="Recovery day recommended",
            message=(
                "You have stacked several demanding sessions within five days. "
                "Choose rest, walking, mobility or easy upper-body work before the next hard session."
            ),
            status="watch",
            eyebrow="Recovery",
        )

    if latest_rpe >= 8 and latest_duration >= 45:
        return CoachCard(
            title="Absorb the hard session",
            message=(
                "Your latest workout was both long and very hard. Keep the next session easy "
                "unless sleep, soreness and energy all feel normal."
            ),
            status="watch",
            eyebrow="Recovery",
        )

    if len(last_7) >= 3:
        return CoachCard(
            title="Training load looks manageable",
            message=(
                f"{len(last_7)} sessions were logged in the last seven days without a cluster of very hard efforts. "
                "Continue alternating demanding and easier days."
            ),
            status="good",
            eyebrow="Recovery",
        )

    return CoachCard(
        title="Room for another quality session",
        message="Recent frequency and effort do not show an obvious overload signal. Increase only if your body feels ready.",
        status="good",
        eyebrow="Recovery",
    )


def _pain_card(df: pd.DataFrame, today: date) -> CoachCard:
    if df.empty:
        return CoachCard(
            title="No pain history yet",
            message="Log discomfort honestly. Repeated pain matters more than one isolated score.",
            eyebrow="Body check",
        )

    last_21 = df[df["date"] >= today - timedelta(days=20)].sort_values("date", ascending=False)
    painful = last_21[last_21["pain"] > 0]
    recent_three = df.sort_values("date", ascending=False).head(3)
    consecutive = int((recent_three["pain"] > 0).sum())

    if consecutive == 3:
        locations = [
            value.strip() for value in recent_three["pain_location"].tolist()
            if value.strip()
        ]
        location_text = f" around {_join_words(sorted(set(locations)))}" if locations else ""
        return CoachCard(
            title="Pain repeated across 3 sessions",
            message=(
                f"Discomfort has been logged in three consecutive workouts{location_text}. "
                "Reduce running intensity and volume, and seek medical assessment if pain persists, worsens or affects normal movement."
            ),
            status="alert",
            eyebrow="Body check",
        )

    if len(painful) >= 3:
        return CoachCard(
            title=f"Pain logged {len(painful)} times in 3 weeks",
            message=(
                "The pattern is recurring rather than isolated. Review which session types trigger it "
                "and avoid progressing load until the pattern settles."
            ),
            status="watch",
            eyebrow="Body check",
        )

    if painful.empty:
        return CoachCard(
            title="No pain logged in 3 weeks",
            message="That is encouraging. Keep progressing gradually and continue recording even mild discomfort.",
            status="good",
            eyebrow="Body check",
        )

    latest_pain = painful.iloc[0]
    return CoachCard(
        title="Monitor recent discomfort",
        message=(
            f"Pain was recorded on {latest_pain['date']:%d %b}"
            + (
                f" at {latest_pain['pain_location']}."
                if latest_pain["pain_location"]
                else "."
            )
            + " Keep the next increase in running or hybrid load conservative."
        ),
        status="watch",
        eyebrow="Body check",
    )


def _trend_card(df: pd.DataFrame, today: date) -> CoachCard:
    if df.empty:
        return CoachCard(
            title="Trend analysis needs history",
            message="After several weeks of logging, PACE will compare volume, pace and training frequency.",
            eyebrow="Progress trend",
        )

    current_start = today - timedelta(days=27)
    previous_start = today - timedelta(days=55)

    current = df[(df["date"] >= current_start) & (df["date"] <= today)]
    previous = df[(df["date"] >= previous_start) & (df["date"] < current_start)]

    if len(current) < 3 or len(previous) < 3:
        return CoachCard(
            title="Keep building the data",
            message=(
                f"{len(current)} sessions are available in the latest four-week window. "
                "PACE needs at least three sessions in both comparison periods before calling a trend."
            ),
            eyebrow="Progress trend",
        )

    current_sessions = len(current)
    previous_sessions = len(previous)
    current_minutes = float(current["duration_min"].sum())
    previous_minutes = float(previous["duration_min"].sum())

    session_change = (
        (current_sessions - previous_sessions) / previous_sessions * 100
        if previous_sessions else 0
    )
    minute_change = (
        (current_minutes - previous_minutes) / previous_minutes * 100
        if previous_minutes else 0
    )

    current_runs = current[
        (current["category"] == "Run")
        & (current["distance_km"] > 0)
        & (current["pace_seconds"] > 0)
    ]
    previous_runs = previous[
        (previous["category"] == "Run")
        & (previous["distance_km"] > 0)
        & (previous["pace_seconds"] > 0)
    ]

    trend_bits = []
    status = "info"

    if abs(session_change) >= 10:
        direction = "up" if session_change > 0 else "down"
        trend_bits.append(f"session frequency is {abs(session_change):.0f}% {direction}")

    if abs(minute_change) >= 10:
        direction = "up" if minute_change > 0 else "down"
        trend_bits.append(f"training time is {abs(minute_change):.0f}% {direction}")

    if len(current_runs) >= 2 and len(previous_runs) >= 2:
        current_pace = float(current_runs["pace_seconds"].mean())
        previous_pace = float(previous_runs["pace_seconds"].mean())
        pace_change = previous_pace - current_pace
        if abs(pace_change) >= 5:
            if pace_change > 0:
                trend_bits.append(f"average running pace is {pace_change:.0f} sec/km faster")
                status = "good"
            else:
                trend_bits.append(f"average running pace is {abs(pace_change):.0f} sec/km slower")

    if not trend_bits:
        return CoachCard(
            title="Training is broadly stable",
            message="The latest four weeks are similar to the previous four in frequency, duration and recorded running pace.",
            status="good",
            eyebrow="Progress trend",
        )

    if minute_change > 25:
        status = "watch"

    return CoachCard(
        title="Four-week trend detected",
        message=(
            "Compared with the previous four weeks, "
            + _join_words(trend_bits)
            + ". "
            + (
                "The increase is sizeable, so monitor recovery and pain."
                if minute_change > 25
                else "Keep the progression gradual and repeatable."
            )
        ),
        status=status,
        eyebrow="Progress trend",
    )


def _personal_best_card(df: pd.DataFrame) -> CoachCard | None:
    if len(df) < 2:
        return None

    ordered = df.sort_values("date")
    latest = ordered.iloc[-1]
    previous = ordered.iloc[:-1]

    achievements = []

    if latest["distance_km"] > 0 and latest["distance_km"] > previous["distance_km"].max():
        achievements.append(f"longest recorded distance at {latest['distance_km']:.1f} km")

    if latest["duration_min"] > previous["duration_min"].max():
        achievements.append(f"longest recorded session at {int(latest['duration_min'])} minutes")

    latest_category = latest["category"]
    if latest_category == "Run" and latest["pace_seconds"] > 0:
        comparable = previous[
            (previous["category"] == "Run")
            & (previous["pace_seconds"] > 0)
            & (previous["distance_km"] >= max(latest["distance_km"] * 0.8, 1))
            & (previous["distance_km"] <= latest["distance_km"] * 1.2)
        ]
        if not comparable.empty and latest["pace_seconds"] < comparable["pace_seconds"].min():
            achievements.append("fastest comparable run pace")

    if not achievements:
        return None

    return CoachCard(
        title="New personal milestone",
        message=f"Your latest session delivered your {_join_words(achievements)}. Celebrate it, then recover before chasing the next one.",
        status="good",
        eyebrow="Progress moment",
    )


def _partner_card(df: pd.DataFrame, athlete_names: list[str], today: date) -> CoachCard | None:
    names = [name for name in athlete_names if name]
    if len(names) < 2:
        return None

    week = _current_week(df, today)
    details = []
    missing_by_name: dict[str, list[str]] = {}

    for name in names:
        athlete_week = week[week["athlete"].str.casefold() == name.casefold()]
        counts = _category_counts(athlete_week)
        missing = [
            category for category in ("Run", "Strength", "Hybrid")
            if counts[category] == 0
        ]
        missing_by_name[name] = missing
        details.append(f"{name}: {len(athlete_week)}/3")

    shared_missing = set(missing_by_name[names[0]])
    for name in names[1:]:
        shared_missing &= set(missing_by_name[name])

    if shared_missing:
        session = sorted(shared_missing)[0]
        message = (
            f"Both partners still need a {session.lower()} session. "
            f"One shared {session.lower()} workout would move both weekly plans forward."
        )
        status = "info"
    elif all(not missing_by_name[name] for name in names):
        message = "Both partners have completed the run-strength-hybrid mix. Plan recovery together and protect next week’s consistency."
        status = "good"
    else:
        trailing_name = min(
            names,
            key=lambda person: len(
                week[week["athlete"].str.casefold() == person.casefold()]
            ),
        )
        missing = missing_by_name[trailing_name]
        message = (
            f"{trailing_name} still needs {_join_words(category.lower() for category in missing) or 'no specific category'}. "
            "Choose a shared session that helps close that gap without adding unnecessary load for the other partner."
        )
        status = "info"

    return CoachCard(
        title=" · ".join(details),
        message=message,
        status=status,
        eyebrow="Partner coach",
    )


def build_coach_cards(
    activities: pd.DataFrame | None,
    selected_athlete: str = "Team",
    athlete_names: list[str] | None = None,
    today: date | None = None,
) -> list[dict]:
    """
    Build deterministic coaching cards from logged activity data.

    No API or database changes are required. The function accepts the existing
    activity DataFrame already loaded into Streamlit session state.
    """
    today = today or date.today()
    athlete_names = athlete_names or []

    all_activities = _prepare(activities)
    selected = _filter_athlete(all_activities, selected_athlete)
    week = _current_week(selected, today)

    cards: list[CoachCard] = [
        _weekly_progress_card(week, today),
        _balance_card(week),
        _duration_card(week),
        _consistency_card(selected, today),
        _recovery_card(selected, today),
        _pain_card(selected, today),
        _trend_card(selected, today),
    ]

    personal_best = _personal_best_card(selected)
    if personal_best:
        cards.insert(3, personal_best)

    if selected_athlete == "Team":
        partner = _partner_card(all_activities, athlete_names, today)
        if partner:
            cards.insert(1, partner)

    return [card.to_dict() for card in cards]
