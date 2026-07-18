import streamlit as st

NAV_ITEMS = [
    ("Home", "🏠", "views/home.py"),
    ("Activities", "🏃", "views/activities.py"),
    ("Progress", "📈", "views/progress.py"),
    ("Coach", "🤖", "views/coach.py"),
    ("Race", "🎯", "views/race.py"),
    ("Profile", "👤", "views/profile.py"),
]

def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #F7F9FA; }
        .block-container {
            max-width: 760px;
            padding-top: 0.55rem;
            padding-bottom: 6.4rem;
        }
        header[data-testid="stHeader"] { background: transparent; }
        [data-testid="stSidebar"] { display: none; }

        .pace-header {
            display:flex; align-items:center; justify-content:space-between;
            margin: 0.1rem 0 0.65rem 0;
        }
        .pace-logo { font-size:1.4rem; font-weight:780; letter-spacing:-0.05em; }
        .pace-badge {
            font-size:0.76rem; padding:0.3rem 0.58rem; border-radius:999px;
            background:#E5F2F2; color:#166A7A; font-weight:680;
        }
        .hero-card, .content-card, .coach-card {
            background:#FFFFFF; border:1px solid #E6EBED; border-radius:20px;
            padding:1.05rem; margin-bottom:0.85rem;
        }
        .hero-card { background:linear-gradient(145deg,#E8F4F4,#F5FAFA); }
        .eyebrow {
            color:#657276; text-transform:uppercase; letter-spacing:.09em;
            font-size:.70rem; font-weight:760; margin-bottom:.28rem;
        }
        .hero-title { font-size:1.55rem; font-weight:770; letter-spacing:-.035em; }
        .hero-subtitle { color:#526064; margin-top:.2rem; }
        .metric-row {
            display:grid; grid-template-columns:repeat(3,1fr); gap:.55rem;
            margin-top:.9rem;
        }
        .metric {
            background:#FFFFFF; border:1px solid #E6EBED; border-radius:15px;
            padding:.72rem;
        }
        .metric-label { color:#6B777A; font-size:.72rem; }
        .metric-value { font-size:1.15rem; font-weight:740; margin-top:.12rem; }
        .status-good { color:#217A50; }
        .status-watch { color:#9A6412; }
        .section-title { font-size:1.05rem; font-weight:730; margin-bottom:.55rem; }
        .coach-card { border-left:5px solid #166A7A; }
        .coach-lead { font-size:1.03rem; font-weight:700; margin-bottom:.4rem; }
        .muted { color:#69777B; font-size:.86rem; }
        .activity-row {
            display:flex; justify-content:space-between; gap:1rem;
            padding:.72rem 0; border-bottom:1px solid #EEF1F2;
        }
        .activity-row:last-child { border-bottom:0; }
        .activity-name { font-weight:680; }
        .activity-meta { color:#6C787B; font-size:.82rem; }
        .activity-value { font-weight:720; white-space:nowrap; }

        .bottom-nav {
            position:fixed; bottom:0; left:0; right:0; z-index:999;
            background:rgba(255,255,255,.98); border-top:1px solid #DDE4E6;
            padding:.34rem .35rem calc(.34rem + env(safe-area-inset-bottom));
            backdrop-filter: blur(10px);
        }
        .bottom-nav-inner {
            width:min(760px,100%); margin:0 auto;
            display:grid; grid-template-columns:repeat(6,1fr); gap:.15rem;
        }
        .bottom-nav form { margin:0; }
        .bottom-nav button {
            width:100%; border:0; background:transparent; color:#647175;
            border-radius:11px; padding:.30rem .04rem .25rem;
            font-size:.66rem; line-height:1rem; cursor:pointer;
        }
        .bottom-nav button:hover { background:#EEF5F5; color:#166A7A; }
        .bottom-nav .nav-icon {
            display:block; font-size:1rem; line-height:1.15rem;
        }

        div[data-testid="stButton"] button {
            border-radius:12px; min-height:2.65rem; font-weight:650;
        }
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stSelectbox"] > div > div,
        div[data-testid="stNumberInput"] input {
            border-radius:12px;
        }
        .profile-summary {
            display:flex; align-items:center; gap:.8rem;
            background:#FFFFFF; border:1px solid #E6EBED; border-radius:20px;
            padding:1rem; margin-bottom:.9rem;
        }
        .profile-avatar {
            width:48px; height:48px; border-radius:50%;
            display:flex; align-items:center; justify-content:center;
            background:#E5F2F2; color:#166A7A; font-weight:800; font-size:1.1rem;
        }
        .profile-name { font-weight:760; font-size:1.05rem; }
        .profile-meta { color:#69777B; font-size:.84rem; }
        @media (max-width:480px){
            .block-container { padding-left:.85rem; padding-right:.85rem; }
            .metric-row { gap:.4rem; }
            .metric { padding:.6rem .5rem; }
            .metric-value { font-size:1rem; }
            .bottom-nav button { font-size:.60rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def render_brand_header() -> None:
    st.markdown(
        '<div class="pace-header"><div class="pace-logo">pace</div>'
        '<div class="pace-badge">HYROX Partner OS</div></div>',
        unsafe_allow_html=True,
    )

def render_bottom_nav(active: str = "") -> None:
    st.markdown('<div style="height:.4rem"></div>', unsafe_allow_html=True)
    cols = st.columns(6, gap="small")
    for col, (label, icon, target) in zip(cols, NAV_ITEMS):
        with col:
            button_type = "primary" if label == active else "secondary"
            if st.button(
                f"{icon}\n{label}",
                key=f"nav_{label}_{active}",
                use_container_width=True,
                type=button_type,
            ):
                st.switch_page(target)

def metric_html(label: str, value: str, css_class: str = "") -> str:
    return (
        f'<div class="metric"><div class="metric-label">{label}</div>'
        f'<div class="metric-value {css_class}">{value}</div></div>'
    )
