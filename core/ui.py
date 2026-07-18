from __future__ import annotations

import html
import streamlit as st


NAV_ITEMS = [
    ("Today", "⌂", "views/home.py"),
    ("Log", "+", "views/activities.py"),
    ("Coach", "✦", "views/coach.py"),
    ("Me", "○", "views/profile.py"),
]


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
          --pace-bg: #f5f6f8;
          --pace-card: #ffffff;
          --pace-text: #17181b;
          --pace-muted: #737780;
          --pace-line: #e7e9ee;
          --pace-accent: #ff5a36;
          --pace-accent-soft: #fff0eb;
          --pace-success: #1f8a5b;
          --pace-warning: #b96b00;
          --pace-danger: #c53f3f;
          --pace-shadow: 0 8px 28px rgba(18, 22, 33, 0.06);
          --pace-radius: 24px;
        }

        .stApp { background: var(--pace-bg); color: var(--pace-text); }
        [data-testid="stHeader"] { background: rgba(245,246,248,.88); backdrop-filter: blur(12px); }
        [data-testid="stToolbar"], #MainMenu, footer { visibility: hidden; }
        .block-container { max-width: 760px; padding-top: 1.1rem; padding-bottom: 7rem; }

        h1, h2, h3 { letter-spacing: -0.035em; color: var(--pace-text); }
        h1 { font-size: 2rem !important; margin-bottom: .15rem !important; }
        h2 { font-size: 1.35rem !important; margin-top: 1.4rem !important; }
        p, label, .stCaption { color: var(--pace-muted); }

        .pace-brand { display:flex; align-items:flex-end; justify-content:space-between; gap:1rem; padding:.15rem 0 .85rem; margin-bottom:.45rem; border-bottom:1px solid var(--pace-line); }
        .pace-brand-lockup { display:flex; flex-direction:column; gap:.08rem; }
        .pace-wordmark { font-weight:900; letter-spacing:.18em; font-size:1.12rem; line-height:1; color:var(--pace-text); }
        .pace-slogan { font-size:.7rem; font-weight:650; letter-spacing:.02em; color:var(--pace-muted); }
        .pace-tag { font-size:.72rem; color:var(--pace-muted); white-space:nowrap; }

        .pace-card, .hero-card, .content-card, .coach-card, .profile-summary {
          background: var(--pace-card);
          border: 1px solid var(--pace-line);
          border-radius: var(--pace-radius);
          box-shadow: var(--pace-shadow);
          padding: 1.2rem;
          margin: .8rem 0;
        }
        .hero-card { padding: 1.35rem; background: linear-gradient(145deg, #ffffff 0%, #fff7f3 100%); }
        .coach-card { background: linear-gradient(145deg, #1c1f24 0%, #292e36 100%); border:0; color:white; }
        .coach-card .muted, .coach-card .eyebrow { color: rgba(255,255,255,.68); }
        .coach-card .coach-lead { color:white; }

        .eyebrow { font-size:.72rem; text-transform:uppercase; letter-spacing:.12em; font-weight:800; color:var(--pace-muted); }
        .hero-title { font-size:1.85rem; line-height:1.05; font-weight:850; margin:.38rem 0 .28rem; letter-spacing:-.045em; }
        .hero-subtitle { color:var(--pace-muted); font-size:.92rem; }
        .coach-lead { font-size:1.22rem; font-weight:780; line-height:1.25; margin:.5rem 0; letter-spacing:-.025em; }
        .section-title { font-size:1rem; font-weight:800; color:var(--pace-text); margin-bottom:.75rem; }
        .muted { color:var(--pace-muted); font-size:.92rem; line-height:1.5; }

        .metric-row { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.65rem; margin-top:1rem; }
        .metric-box { background:#f7f8fa; border-radius:18px; padding:.8rem .72rem; min-width:0; }
        .metric-label { font-size:.7rem; color:var(--pace-muted); text-transform:uppercase; letter-spacing:.06em; }
        .metric-value { font-size:1.05rem; font-weight:800; margin-top:.15rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
        .status-good .metric-value { color:var(--pace-success); }

        .activity-row { display:flex; justify-content:space-between; align-items:center; gap:1rem; padding:.82rem 0; border-top:1px solid var(--pace-line); }
        .activity-row:first-of-type { border-top:0; }
        .activity-name { font-weight:760; color:var(--pace-text); }
        .activity-meta { font-size:.78rem; color:var(--pace-muted); margin-top:.12rem; }
        .activity-value { font-weight:820; white-space:nowrap; }

        .profile-summary { display:flex; align-items:center; gap:1rem; }
        .profile-avatar { width:54px; height:54px; border-radius:50%; display:grid; place-items:center; background:#191c21; color:white; font-weight:850; }
        .profile-name { font-size:1.2rem; font-weight:820; }
        .profile-meta { font-size:.82rem; color:var(--pace-muted); }

        .mission-card { background:#fff; border:1px solid var(--pace-line); border-radius:var(--pace-radius); padding:1.15rem; box-shadow:var(--pace-shadow); margin:.8rem 0; }
        .mission-title { font-size:1.18rem; font-weight:820; margin:.3rem 0 .15rem; }
        .mission-meta { color:var(--pace-muted); font-size:.9rem; }

        div[data-testid="stButton"] > button, div[data-testid="stFormSubmitButton"] > button {
          border-radius: 16px !important;
          min-height: 3rem;
          font-weight: 760;
          border: 1px solid var(--pace-line);
        }
        div[data-testid="stButton"] > button[kind="primary"], div[data-testid="stFormSubmitButton"] > button[kind="primary"] {
          background: var(--pace-accent) !important;
          border-color: var(--pace-accent) !important;
          color: white !important;
          box-shadow: 0 8px 18px rgba(255,90,54,.22);
        }
        div[data-baseweb="select"] > div, input, textarea, [data-testid="stNumberInput"] input {
          border-radius: 14px !important;
        }
        div[data-testid="stForm"] { background:#fff; border:1px solid var(--pace-line); border-radius:var(--pace-radius); padding:1rem; box-shadow:var(--pace-shadow); }
        div[data-testid="stVerticalBlockBorderWrapper"] { border-radius:var(--pace-radius); }

        .onboarding-shell { max-width:620px; margin:0 auto; }
        .welcome-mark { width:64px; height:64px; display:grid; place-items:center; border-radius:22px; background:var(--pace-accent-soft); font-size:1.75rem; margin:.65rem 0 1.1rem; }
        .welcome-title { font-size:2rem; line-height:1.06; font-weight:880; letter-spacing:-.05em; margin:0 0 .55rem; color:var(--pace-text); }
        .welcome-copy { color:var(--pace-muted); line-height:1.55; font-size:1rem; margin-bottom:1.15rem; }
        .step-pill { display:inline-flex; align-items:center; gap:.35rem; padding:.38rem .65rem; border-radius:999px; background:#f0f1f4; color:var(--pace-muted); font-size:.72rem; font-weight:760; margin-bottom:.8rem; }
        .choice-card { background:#fff; border:1px solid var(--pace-line); border-radius:18px; padding:.9rem 1rem; margin:.45rem 0; }
        .pace-bottom-spacer { height: .4rem; }
        .pace-nav-label { font-size:.68rem; line-height:1; color:var(--pace-muted); margin-top:-.2rem; }
        @media (max-width: 640px) {
          .block-container { padding-left:1rem; padding-right:1rem; padding-top:.7rem; }
          .metric-row { gap:.45rem; }
          .metric-box { padding:.72rem .55rem; }
          .metric-value { font-size:.94rem; }
          .hero-title { font-size:1.62rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand_header() -> None:
    st.markdown(
        '<div class="pace-brand"><div class="pace-brand-lockup"><div class="pace-wordmark">PACE</div><div class="pace-slogan">Train together. Train smarter.</div></div><div class="pace-tag">HYROX Partner OS</div></div>',
        unsafe_allow_html=True,
    )


def metric_html(label: str, value: str, extra_class: str = "") -> str:
    return (
        f'<div class="metric-box {html.escape(extra_class)}">'
        f'<div class="metric-label">{html.escape(str(label))}</div>'
        f'<div class="metric-value">{html.escape(str(value))}</div>'
        '</div>'
    )


def render_bottom_nav(active: str | None = None) -> None:
    st.markdown('<div class="pace-bottom-spacer"></div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for col, (label, icon, path) in zip(cols, NAV_ITEMS):
        with col:
            button_type = "primary" if active == label else "secondary"
            if st.button(icon, key=f"pace_nav_{label}", use_container_width=True, type=button_type):
                st.switch_page(path)
            st.markdown(f'<div class="pace-nav-label" style="text-align:center">{label}</div>', unsafe_allow_html=True)
