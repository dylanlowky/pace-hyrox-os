from __future__ import annotations

from html import escape

import streamlit as st


PACE_CSS = """
<style>
:root {
  --pace-bg: #07090d;
  --pace-surface: #10141b;
  --pace-surface-2: #151a22;
  --pace-border: #282f39;
  --pace-text: #f7f8fa;
  --pace-muted: #9aa3af;
  --pace-yellow: #ffd400;
  --pace-green: #39d977;
  --pace-red: #ff4b55;
  --pace-blue: #4d8dff;
}

html, body, [data-testid="stAppViewContainer"], .stApp {
  background:
    radial-gradient(circle at 12% 0%, rgba(255,212,0,.055), transparent 24rem),
    linear-gradient(180deg, #07090d 0%, #090c11 100%) !important;
  color: var(--pace-text) !important;
}

[data-testid="stHeader"] {
  background: rgba(7, 9, 13, .80) !important;
  backdrop-filter: blur(14px);
}

[data-testid="stMainBlockContainer"] {
  max-width: 920px;
  padding-top: 1rem;
  padding-bottom: 7.5rem;
}

h1 {
  font-size: clamp(2.1rem, 5vw, 3.15rem) !important;
  line-height: 1.04 !important;
  margin: 1.8rem 0 .4rem !important;
  color: var(--pace-text) !important;
}

h2 {
  font-size: clamp(1.5rem, 3.5vw, 2rem) !important;
  line-height: 1.15 !important;
  color: var(--pace-text) !important;
}

[data-testid="stCaptionContainer"],
.stCaption,
.muted {
  color: var(--pace-muted) !important;
  font-size: 1rem !important;
  line-height: 1.55 !important;
}

.pace-topbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  padding: .25rem 0 1.15rem;
  border-bottom: 1px solid var(--pace-border);
  margin-bottom: 1rem;
}

.pace-logo {
  color: #fff;
  font-size: 1.9rem;
  font-weight: 500;
  letter-spacing: .34em;
  line-height: 1;
  text-transform: lowercase;
}

.pace-tagline {
  color: var(--pace-muted);
  font-size: .8rem;
  margin-top: .55rem;
}

.pace-tagline strong {
  color: var(--pace-yellow);
  font-weight: 700;
}

.pace-os-label {
  color: var(--pace-muted);
  font-size: .8rem;
  padding-top: .15rem;
  white-space: nowrap;
}

.hero-card,
.mission-card,
.content-card,
.insight-card {
  background: linear-gradient(145deg, rgba(19,24,32,.98), rgba(10,14,20,.98));
  border: 1px solid var(--pace-border);
  border-radius: 22px;
  box-shadow: 0 18px 46px rgba(0,0,0,.24);
}

.hero-card {
  position: relative;
  overflow: hidden;
  padding: clamp(1.35rem, 4vw, 2.1rem);
  margin: 1rem 0;
}

.hero-card::after {
  content: "";
  position: absolute;
  inset: 0 0 0 48%;
  background:
    linear-gradient(90deg, rgba(10,14,20,1) 0%, rgba(10,14,20,.55) 38%, rgba(10,14,20,.05) 100%),
    repeating-linear-gradient(
      90deg,
      rgba(255,255,255,.025) 0,
      rgba(255,255,255,.025) 1px,
      transparent 1px,
      transparent 22px
    );
  pointer-events: none;
}

.hero-card > * {
  position: relative;
  z-index: 1;
}

.mission-card {
  padding: clamp(1.25rem, 4vw, 1.9rem);
  margin: 1rem 0 .85rem;
}

.content-card {
  padding: 1.25rem;
  margin: 1rem 0;
}

.insight-card {
  padding: 1.15rem 1.2rem;
  margin: .8rem 0;
}

.eyebrow {
  color: var(--pace-yellow);
  font-size: .76rem;
  font-weight: 800;
  letter-spacing: .12em;
  text-transform: uppercase;
  margin-bottom: .55rem;
}

.hero-title {
  color: var(--pace-text);
  font-size: clamp(1.95rem, 5.5vw, 3rem);
  font-weight: 800;
  line-height: 1.02;
  max-width: 70%;
}

.hero-subtitle {
  color: var(--pace-muted);
  font-size: 1.02rem;
  margin-top: .65rem;
}

.mission-title,
.section-title {
  color: var(--pace-text);
  font-size: clamp(1.35rem, 3vw, 1.7rem);
  font-weight: 760;
  line-height: 1.18;
}

.mission-meta {
  color: var(--pace-muted);
  font-size: 1.05rem;
  line-height: 1.58;
  margin-top: .7rem;
  max-width: 78%;
}

.metric-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0,1fr));
  gap: .8rem;
  margin-top: 1.35rem;
  max-width: 75%;
}

.metric-box {
  background: rgba(255,255,255,.035);
  border: 1px solid rgba(255,255,255,.055);
  border-radius: 16px;
  padding: .95rem;
}

.metric-label {
  color: var(--pace-muted);
  font-size: .69rem;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.metric-value {
  color: var(--pace-text);
  font-size: 1rem;
  font-weight: 760;
  margin-top: .28rem;
}

.status-good {
  color: var(--pace-green) !important;
}

.activity-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding-top: .9rem;
}

.activity-name {
  color: var(--pace-text);
  font-size: 1.07rem;
  font-weight: 720;
}

.activity-meta {
  color: var(--pace-muted);
  font-size: .9rem;
  margin-top: .25rem;
}

.activity-value {
  color: var(--pace-text);
  font-size: 1.12rem;
  font-weight: 760;
  white-space: nowrap;
}

.insight-row {
  display: grid;
  grid-template-columns: 2.8rem minmax(0, 1fr);
  gap: .9rem;
  align-items: start;
}

.insight-icon {
  font-size: 1.7rem;
  line-height: 1;
}

.insight-title {
  color: var(--pace-text);
  font-size: 1.08rem;
  font-weight: 760;
}

.insight-message {
  color: var(--pace-muted);
  font-size: .98rem;
  line-height: 1.5;
  margin-top: .25rem;
}

.insight-status {
  display: inline-block;
  color: var(--pace-green);
  background: rgba(53,217,120,.09);
  border: 1px solid rgba(53,217,120,.25);
  border-radius: 999px;
  padding: .12rem .5rem;
  font-size: .65rem;
  font-weight: 800;
  letter-spacing: .05em;
  text-transform: uppercase;
  margin-left: .4rem;
}

div[data-testid="stButton"] > button,
div[data-testid="stLinkButton"] > a {
  min-height: 3.2rem;
  border-radius: 14px;
  font-size: 1rem !important;
  font-weight: 720 !important;
  border: 1px solid var(--pace-border);
}

div[data-testid="stButton"] > button[kind="primary"] {
  background: var(--pace-yellow) !important;
  border-color: var(--pace-yellow) !important;
  color: #090b0f !important;
}

div[data-testid="stButton"] > button[kind="primary"] p,
div[data-testid="stButton"] > button[kind="primary"] span {
  color: #090b0f !important;
  font-weight: 820 !important;
}

div[data-testid="stSegmentedControl"] button {
  min-height: 2.9rem;
  font-size: 1rem !important;
  font-weight: 720 !important;
  border-color: var(--pace-border) !important;
}

div[data-testid="stSegmentedControl"] button[aria-pressed="true"] {
  color: var(--pace-yellow) !important;
  border-color: var(--pace-yellow) !important;
  background: rgba(255,212,0,.08) !important;
}

.pace-bottom-nav {
  position: fixed;
  left: 50%;
  bottom: 0;
  transform: translateX(-50%);
  width: min(100%, 920px);
  z-index: 999;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: .2rem;
  padding: .65rem .7rem calc(.65rem + env(safe-area-inset-bottom));
  background: rgba(9,12,17,.96);
  border-top: 1px solid var(--pace-border);
  backdrop-filter: blur(16px);
}

.pace-nav-item {
  text-align: center;
  color: #8f98a6;
  font-size: .7rem;
  text-decoration: none;
  padding: .28rem .15rem;
}

.pace-nav-icon {
  display: block;
  font-size: 1.28rem;
  line-height: 1.2;
  margin-bottom: .13rem;
}

.pace-nav-item.active {
  color: var(--pace-yellow);
  font-weight: 820;
}

@media (max-width: 640px) {
  [data-testid="stMainBlockContainer"] {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .hero-card::after {
    inset: 0 0 0 58%;
  }

  .hero-title,
  .mission-meta,
  .metric-row {
    max-width: 100%;
  }

  .metric-row {
    grid-template-columns: 1fr;
  }

  .pace-logo {
    font-size: 1.55rem;
  }

  .pace-os-label {
    font-size: .72rem;
  }
}
</style>
"""


def inject_global_styles() -> None:
    st.markdown(PACE_CSS, unsafe_allow_html=True)


def apply_global_styles() -> None:
    """Backward-compatible entry point used by app.py."""
    inject_global_styles()


def render_brand_header() -> None:
    st.markdown(
        """
        <header class="pace-topbar">
          <div>
            <div class="pace-logo">pace</div>
            <div class="pace-tagline">Train <strong>together</strong>. Train <strong>smarter</strong>.</div>
          </div>
          <div class="pace-os-label">HYROX Partner OS</div>
        </header>
        """,
        unsafe_allow_html=True,
    )


def metric_html(label: str, value: str, value_class: str = "") -> str:
    return (
        '<div class="metric-box">'
        f'<div class="metric-label">{escape(str(label))}</div>'
        f'<div class="metric-value {escape(value_class)}">{escape(str(value))}</div>'
        "</div>"
    )


def render_bottom_nav(active: str) -> None:
    items = [
        ("Today", "⌂", "views/home.py"),
        ("Log", "▣", "views/activities.py"),
        ("Coach", "✦", "views/coach.py"),
        ("Progress", "▥", "views/progress.py"),
        ("Me", "◎", "views/profile.py"),
    ]

    links = []
    for label, icon, page in items:
        active_class = " active" if label.casefold() == active.casefold() else ""
        links.append(
            f'<a class="pace-nav-item{active_class}" href="/{page}" target="_self">'
            f'<span class="pace-nav-icon">{icon}</span>{escape(label)}</a>'
        )

    st.markdown(
        '<nav class="pace-bottom-nav">' + "".join(links) + "</nav>",
        unsafe_allow_html=True,
    )
