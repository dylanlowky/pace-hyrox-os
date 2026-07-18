from datetime import date, datetime, timezone
import pandas as pd
from services.supabase_client import get_supabase
from services.metrics import calculate_training_load, pace_seconds_per_km

ACTIVITY_COLUMNS = [
    "id", "date", "athlete", "athlete_id", "type", "title",
    "distance_km", "duration_min", "avg_hr", "rpe", "pain",
    "pain_location", "notes", "trained_together", "training_load",
    "pace_seconds",
]

class PaceRepository:
    def __init__(self):
        self.client = get_supabase(authenticated=True)

    @staticmethod
    def empty_activities() -> pd.DataFrame:
        return pd.DataFrame(columns=ACTIVITY_COLUMNS)

    def get_my_household(self):
        result = (
            self.client.table("household_members")
            .select("household_id,role,households(id,name,invite_code)")
            .limit(1)
            .execute()
        )
        if not result.data:
            return None
        nested = result.data[0].get("households") or {}
        return {
            "id": nested.get("id") or result.data[0]["household_id"],
            "name": nested.get("name") or "Household",
            "invite_code": nested.get("invite_code") or "",
            "role": result.data[0].get("role") or "member",
        }

    def create_household(self, household_name: str, athlete_name: str):
        return self.client.rpc(
            "bootstrap_household",
            {"household_name": household_name, "athlete_name": athlete_name},
        ).execute().data

    def join_household(self, invite_code: str, athlete_name: str):
        return self.client.rpc(
            "join_household_by_code",
            {"provided_invite_code": invite_code.strip().upper(), "athlete_name": athlete_name},
        ).execute().data

    def get_invite_code(self, household_id: str) -> str:
        result = (
            self.client.table("households")
            .select("invite_code")
            .eq("id", household_id)
            .single()
            .execute()
        )
        return result.data["invite_code"]

    def list_athletes(self, household_id: str) -> list[dict]:
        result = (
            self.client.table("athletes")
            .select("id,user_id,display_name,birth_year,height_cm,current_weight_kg,injury_notes")
            .eq("household_id", household_id)
            .order("created_at")
            .execute()
        )
        return result.data or []

    def get_my_athlete(self, household_id: str, user_id: str):
        result = (
            self.client.table("athletes")
            .select("id,user_id,display_name,birth_year,height_cm,current_weight_kg,injury_notes")
            .eq("household_id", household_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None

    def update_athlete_profile(
        self, athlete_id: str, display_name: str, birth_year: int | None,
        height_cm: float | None, current_weight_kg: float | None, injury_notes: str,
    ):
        payload = {
            "display_name": display_name.strip(),
            "birth_year": birth_year,
            "height_cm": height_cm,
            "current_weight_kg": current_weight_kg,
            "injury_notes": injury_notes.strip() or None,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        return (
            self.client.table("athletes")
            .update(payload)
            .eq("id", athlete_id)
            .execute()
            .data
        )

    def list_activities(self, household_id: str) -> pd.DataFrame:
        athletes = self.list_athletes(household_id)
        names = {row["id"]: row["display_name"] for row in athletes}
        athlete_ids = list(names)
        if not athlete_ids:
            return self.empty_activities()

        result = (
            self.client.table("activities")
            .select("*")
            .in_("athlete_id", athlete_ids)
            .order("activity_date", desc=True)
            .limit(500)
            .execute()
        )

        rows = []
        for row in result.data or []:
            distance_km = float(row.get("distance_meters") or 0) / 1000
            duration_min = int((row.get("duration_seconds") or 0) / 60)
            rpe = int(row.get("rpe") or 0)
            rows.append({
                "id": row["id"],
                "date": pd.to_datetime(row["activity_date"]).date(),
                "athlete": names.get(row["athlete_id"], "Athlete"),
                "athlete_id": row["athlete_id"],
                "type": row["activity_type"],
                "title": row.get("title") or row["activity_type"],
                "distance_km": distance_km,
                "duration_min": duration_min,
                "avg_hr": int(row.get("average_hr") or 0),
                "rpe": rpe,
                "pain": int(row.get("pain_score") or 0),
                "pain_location": row.get("pain_location") or "",
                "notes": row.get("notes") or "",
                "trained_together": bool(row.get("trained_together") or False),
                "training_load": calculate_training_load(duration_min, rpe),
                "pace_seconds": pace_seconds_per_km(distance_km, duration_min),
            })
        return pd.DataFrame(rows, columns=ACTIVITY_COLUMNS)

    def add_activity(
        self, athlete_id: str, workout_date: date, activity_type: str,
        title: str, distance_km: float, duration_min: int, avg_hr: int | None,
        rpe: int, pain: int, pain_location: str, notes: str,
        trained_together: bool,
    ):
        dt = datetime.combine(workout_date, datetime.min.time(), tzinfo=timezone.utc)
        payload = {
            "athlete_id": athlete_id,
            "source": "manual",
            "activity_date": dt.isoformat(),
            "activity_type": activity_type,
            "title": title or activity_type,
            "distance_meters": float(distance_km) * 1000,
            "duration_seconds": int(duration_min) * 60,
            "average_hr": int(avg_hr) if avg_hr else None,
            "rpe": int(rpe),
            "pain_score": int(pain),
            "pain_location": pain_location.strip() or None,
            "notes": notes.strip() or None,
            "trained_together": bool(trained_together),
        }
        return self.client.table("activities").insert(payload).execute().data

    def get_active_race(self, household_id: str):
        result = (
            self.client.table("races")
            .select("*")
            .eq("household_id", household_id)
            .eq("status", "active")
            .limit(1)
            .execute()
        )
        if not result.data:
            return None
        row = result.data[0]
        race_date = date.fromisoformat(row["race_date"])
        target_seconds = row.get("target_seconds")
        target_time = ""
        if target_seconds:
            hours, remaining = divmod(target_seconds, 3600)
            minutes, seconds = divmod(remaining, 60)
            target_time = f"{hours}:{minutes:02d}:{seconds:02d}"
        return {
            "id": row["id"],
            "name": row["name"],
            "date": race_date,
            "category": row.get("category") or "",
            "target_time": target_time,
            "status": row["status"].title(),
            "days_remaining": max((race_date - date.today()).days, 0),
        }

    def save_active_race(
        self, household_id: str, name: str, race_date: date,
        category: str, target_time: str, existing_id: str | None = None,
    ):
        parts = [int(part) for part in target_time.split(":")]
        if len(parts) == 2:
            hours, minutes, seconds = 0, parts[0], parts[1]
        elif len(parts) == 3:
            hours, minutes, seconds = parts
        else:
            raise ValueError("Target time must use H:MM:SS or MM:SS.")
        target_seconds = hours * 3600 + minutes * 60 + seconds
        payload = {
            "household_id": household_id,
            "name": name,
            "race_date": race_date.isoformat(),
            "race_type": "HYROX",
            "category": category,
            "target_seconds": target_seconds,
            "status": "active",
        }
        if existing_id:
            return self.client.table("races").update(payload).eq("id", existing_id).execute().data
        self.client.table("races").update({"status": "planned"}).eq(
            "household_id", household_id
        ).eq("status", "active").execute()
        return self.client.table("races").insert(payload).execute().data

    def list_races(self, household_id: str) -> list[dict]:
        return (
            self.client.table("races")
            .select("*")
            .eq("household_id", household_id)
            .order("race_date", desc=True)
            .execute()
            .data or []
        )
