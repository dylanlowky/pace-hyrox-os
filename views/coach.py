import streamlit as st
from core.config import settings
from core.ui import render_bottom_nav
from services.ai_coach import answer_question

if not st.session_state.get("household_id") and not settings.demo_mode:
    st.switch_page("views/setup.py")

brief = st.session_state.weekly_brief
race = st.session_state.get("active_race")
activities = st.session_state.activities

st.title("Coach")
st.caption("Pace has already reviewed the data.")

st.markdown(
    f"""
    <section class="coach-card">
      <div class="eyebrow">Current status · {brief['status']}</div>
      <div class="coach-lead">{brief['headline']}</div>
      <div class="muted">{brief['summary']}</div>
    </section>
    """,
    unsafe_allow_html=True,
)

with st.container(border=True):
    st.markdown("### Do next")
    for item in brief.get("focus", []):
        st.markdown(f"**→** {item}")

with st.container(border=True):
    st.markdown("### Keep an eye on")
    for item in brief.get("watch", []):
        st.markdown(f"**•** {item}")

if race:
    st.caption(f"Race context: {race['name']} · {race['days_remaining']} days · {race['category']} · target {race['target_time']}")

st.subheader("Ask Coach")
suggestions = [
    "What should we focus on this weekend?",
    "How are we progressing as a team?",
    "Is there anything we should be cautious about?",
]
for suggestion in suggestions:
    if st.button(suggestion, use_container_width=True):
        st.session_state.pending_question = suggestion

question = st.chat_input("Ask about your training")
if not question:
    question = st.session_state.pop("pending_question", None)

if question:
    context = (
        f"Race: {race}\nCoach brief: {brief}\nRecent activities:\n"
        f"{activities.sort_values('date', ascending=False).head(20).to_string(index=False)}"
    )
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        with st.spinner("Reviewing your training..."):
            response = answer_question(question, context)
        st.write(response)

render_bottom_nav("Coach")
