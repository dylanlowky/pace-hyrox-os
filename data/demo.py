from datetime import date, timedelta
import pandas as pd

def athletes() -> list[dict]:
    return [
        {"id": "dylan", "name": "Dylan", "role": "Athlete 1"},
        {"id": "partner", "name": "Partner", "role": "Athlete 2"},
    ]

def active_race() -> dict:
    race_date = date(2026, 11, 22)
    return {
        "name": "HYROX Singapore",
        "date": race_date,
        "category": "Mixed Doubles",
        "target_time": "1:30:00",
        "status": "Active",
        "days_remaining": max((race_date - date.today()).days, 0),
    }

def activities() -> pd.DataFrame:
    today = date.today()
    rows = [
        {"date": today - timedelta(days=1), "athlete": "Dylan", "type": "Hybrid", "title": "4 × 1 km + stations", "distance_km": 5.1, "duration_min": 56, "avg_hr": 154, "rpe": 7, "pain": 2},
        {"date": today - timedelta(days=2), "athlete": "Partner", "type": "Run", "title": "Easy aerobic run", "distance_km": 4.6, "duration_min": 34, "avg_hr": 146, "rpe": 5, "pain": 0},
        {"date": today - timedelta(days=4), "athlete": "Dylan", "type": "Run", "title": "Steady 6 km", "distance_km": 6.0, "duration_min": 38, "avg_hr": 149, "rpe": 6, "pain": 1},
        {"date": today - timedelta(days=5), "athlete": "Partner", "type": "Strength", "title": "Lower body strength", "distance_km": 0.0, "duration_min": 48, "avg_hr": 128, "rpe": 6, "pain": 0},
        {"date": today - timedelta(days=8), "athlete": "Dylan", "type": "Hybrid", "title": "3 × 1 km + stations", "distance_km": 4.2, "duration_min": 49, "avg_hr": 157, "rpe": 8, "pain": 2},
        {"date": today - timedelta(days=9), "athlete": "Partner", "type": "Run", "title": "Progression run", "distance_km": 5.0, "duration_min": 36, "avg_hr": 151, "rpe": 7, "pain": 0},
    ]
    return pd.DataFrame(rows)

def weekly_brief() -> dict:
    return {
        "status": "On track",
        "headline": "Keep building running consistency; do not increase intensity this week.",
        "summary": (
            "Combined training volume is moving in the right direction. Dylan's knee discomfort "
            "remains mild but has appeared after recent hybrid sessions, so the next gain should "
            "come from consistency rather than another workload jump."
        ),
        "focus": [
            "Complete one easy aerobic session each.",
            "Keep Dylan's next hybrid session controlled.",
            "Log soreness after every workout.",
        ],
        "watch": [
            "Dylan: recurring knee discomfort after hybrid sessions.",
            "Partner: running frequency remains the main opportunity.",
        ],
    }
