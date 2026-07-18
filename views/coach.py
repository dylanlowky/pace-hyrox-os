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
st.caption("Pace reviews the data before waiting for a question.")

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

st.subheader("Focus next")
for item in brief["focus"]:
    st.markdown(f"- {item}")

st.subheader("Watch list")
for item in brief["watch"]:
    st.markdown(f"- {item}")

if race:
    with st.container(border=True):
        st.markdown("**Race context**")
        st.write(
            f"{race['name']} · {race['days_remaining']} days remaining · "
            f"{race['category']} · target {race['target_time']}"
        )
else:
    st.info("Create an active race to enable race-specific coaching.")

st.subheader("Ask Coach")
suggestions = [
    "What should we focus on this weekend?",
    "How are we progressing as a team?",
    "Is there anything in the data we should be cautious about?",
]
for suggestion in suggestions:
    if st.button(suggestion, use_container_width=True):
        st.session_state.pending_question = suggestion

question = st.chat_input("Ask about your training")
if not question:
    question = st.session_state.pop("pending_question", None)

if question:
    context = (
        f"Race: {race}\n"
        f"Coach brief: {brief}\n"
        f"Recent activities:\n{activities.sort_values('date', ascending=False).head(20).to_string(index=False)}"
    )
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        with st.spinner("Reviewing training data..."):
            response = answer_question(question, context)
        st.write(response)

render_bottom_nav("Coach")
