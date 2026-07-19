from datetime import date
import streamlit as st
from core.config import settings
from core.state import load_remote_state
from core.ui import metric_html, render_bottom_nav
from services.repositories import PaceRepository

if not st.session_state.get("household_id") and not settings.demo_mode:
    st.switch_page("views/setup.py")

st.title("Race")
st.caption("The target behind every recommendation.")
race = st.session_state.get("active_race")

if race:
    st.markdown(
        f"""
        <section class="hero-card">
          <div class="eyebrow">Active race</div>
          <div class="hero-title">{race['name']}</div>
          <div class="hero-subtitle">{race['category']} · {race['date']:%d %B %Y}</div>
          <div class="metric-row">
            {metric_html("Days left", str(race['days_remaining']))}
            {metric_html("Target", race['target_time'])}
            {metric_html("Status", "Active", "status-good")}
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
else:
    st.info("Create your first active race.")

with st.expander("Edit active race" if race else "Create active race", expanded=not race):
    with st.form("edit_race"):
        name = st.text_input("Race name", value=race["name"] if race else "HYROX Singapore")
        race_date = st.date_input("Race date", value=race["date"] if race else date(2026, 11, 22), min_value=date.today())
        categories = ["Mixed Doubles", "Men's Open", "Women's Open", "Men's Pro", "Women's Pro", "Other"]
        current_category = race["category"] if race and race["category"] in categories else "Mixed Doubles"
        category = st.selectbox("Category", categories, index=categories.index(current_category))
        target_time = st.text_input("Target time", value=race["target_time"] if race else "1:30:00")
        saved = st.form_submit_button("Save race", use_container_width=True, type="primary")
    if saved:
        try:
            if settings.demo_mode:
                st.session_state.active_race = {
                    "id": race.get("id") if race else "demo-race", "name": name, "date": race_date,
                    "category": category, "target_time": target_time, "status": "Active",
                    "days_remaining": max((race_date - date.today()).days, 0),
                }
            else:
                PaceRepository().save_active_race(st.session_state.household_id, name, race_date, category, target_time, race.get("id") if race else None)
                st.session_state.remote_loaded = False
                load_remote_state(force=True)
            st.success("Race saved.")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))

st.subheader("Race history")
if settings.demo_mode:
    st.info("No completed races yet.")
else:
    races = PaceRepository().list_races(st.session_state.household_id)
    completed = [item for item in races if item["status"] == "completed"]
    if not completed:
        st.info("No completed races yet.")
    else:
        for item in completed:
            st.write(f"**{item['name']}** · {item['race_date']}")

render_bottom_nav("Race")
