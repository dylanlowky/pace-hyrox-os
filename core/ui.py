from __future__ import annotations

import base64
from html import escape
from pathlib import Path

import streamlit as st


_ROOT = Path(__file__).resolve().parents[1]
_HERO_ASSET = _ROOT / "assets" / "hyrox_race_hero.jpg"


def _asset_data_uri(path: Path, mime_type: str) -> str:
    try:
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    except OSError:
        return ""
    return f"data:{mime_type};base64,{encoded}"


_HERO_DATA_URI = _asset_data_uri(_HERO_ASSET, "image/jpeg")


# Inline SVGs avoid external icon-library loading failures on Streamlit Cloud.
SVG_ICONS = {
    "home": """
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M3 10.8 12 3l9 7.8v9.7a.5.5 0 0 1-.5.5H15v-6H9v6H3.5a.5.5 0 0 1-.5-.5z"/>
        </svg>
    """,
    "log": """
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M5 3h10a2 2 0 0 1 2 2v14H7a2 2 0 0 1-2-2zm12 5h2v3h3v2h-3v3h-2v-3h-3v-2h3z"/>
        </svg>
    """,
    "coach": """
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="m12 2 1.8 5.2L19 9l-5.2 1.8L12 16l-1.8-5.2L5 9l5.2-1.8zM19 15l.9 2.6 2.6.9-2.6.9L19 22l-.9-2.6-2.6-.9 2.6-.9z"/>
        </svg>
    """,
    "progress": """
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M4 19V9h3v10zm6 0V4h3v15zm6 0v-7h3v7z"/>
        </svg>
    """,
    "profile": """
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 12a4.5 4.5 0 1 0 0-9 4.5 4.5 0 0 0 0 9m-8 9a8 8 0 0 1 16 0z"/>
        </svg>
    """,
    "trend": """
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M4 17 9 12l3 3 6-7h-4V6h8v8h-2v-4l-8 9-3-3-3.5 3.5z"/>
        </svg>
    """,
    "phase": """
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M4 20V10h3v10zm6 0V4h3v16zm6 0v-7h3v7z"/>
        </svg>
    """,
    "team": """
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M8 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8m8-1a3 3 0 1 0 0-6 3 3 0 0 0 0 6M1 21a7 7 0 0 1 14 0zm13.5 0a8.5 8.5 0 0 0-2.1-5.6A6 6 0 0 1 23 19v2z"/>
        </svg>
    """,
    "shoe": """
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M3 15.5 9 18h11a2 2 0 0 1 2 2H9.2a5 5 0 0 1-2-.4L2 17.3zm3-9.8 3 5.2 4.5 2.2 2.1-1.8 1.4 1.4-2 1.8 3 1.5H9.4L4.2 13.8 2.8 8z"/>
        </svg>
    """,
    "target": """
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 2a10 10 0 1 0 10 10h-2a8 8 0 1 1-8-8zm0 4a6 6 0 1 0 6 6h-2a4 4 0 1 1-4-4zm8-4v3h-3v2h3v3h2V7h3V5h-3V2z"/>
        </svg>
    """,
    "clock": """
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2m1 5v4.6l3.2 1.9-1 1.7L11 12.7V7z"/>
        </svg>
    """,
    "heart": """
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 21S3 15.7 3 8.7A5 5 0 0 1 12 5a5 5 0 0 1 9 3.7C21 15.7 12 21 12 21"/>
        </svg>
    """,
    "balance": """
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M11 3h2v3h7v2h-2.1l3.4 6H14l3.4-6H13v11h4v2H7v-2h4V8H6.6l3.4 6H2.7l3.4-6H4V6h7zm-4.9 7L4.9 12h2.4zm11.8 0-1.2 2h2.4z"/>
        </svg>
    """,
    "body": """
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 2a3 3 0 1 0 0 6 3 3 0 0 0 0-6m-5 8 3 2v4l-2 6h3l1-4 1 4h3l-2-6v-4l3-2-1-2-4 2-4-2z"/>
        </svg>
    """,
    "trophy": """
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M7 3h10v2h4v4a5 5 0 0 1-5 5h-.4A5 5 0 0 1 13 16.6V19h4v2H7v-2h4v-2.4A5 5 0 0 1 8.4 14H8a5 5 0 0 1-5-5V5h4zm0 4H5v2a3 3 0 0 0 3 3h.1A8 8 0 0 1 7 8zm10 0v1a8 8 0 0 1-1.1 4h.1a3 3 0 0 0 3-3V7z"/>
        </svg>
    """,
}


def icon_svg(name: str, css_class: str = "") -> str:
    icon = SVG_ICONS.get(name, SVG_ICONS["coach"])
    return f'<span class="pace-svg {escape(css_class)}">{icon}</span>'


PACE_CSS = """
<style>
@property --pace-ring {
  syntax: "<number>";
  inherits: false;
  initial-value: 0;
}

:root {
  --pace-bg: #06080c;
  --pace-surface: #10141b;
  --pace-surface-2: #151a22;
  --pace-border: #29313c;
  --pace-text: #f7f8fa;
  --pace-muted: #9aa4b2;
  --pace-yellow: #ffd400;
  --pace-yellow-soft: rgba(255, 212, 0, .12);
  --pace-green: #39d977;
  --pace-red: #ff4b55;
  --pace-blue: #4d8dff;
}

html, body, [data-testid="stAppViewContainer"], .stApp {
  background:
    radial-gradient(circle at 12% -10%, rgba(255,212,0,.07), transparent 28rem),
    linear-gradient(180deg, #06080c 0%, #090c11 100%) !important;
  color: var(--pace-text) !important;
}

[data-testid="stHeader"] {
  height: 3.25rem;
  background: rgba(6, 8, 12, .88) !important;
  backdrop-filter: blur(18px);
}

[data-testid="stDecoration"] {
  display: none;
}

[data-testid="stMainBlockContainer"] {
  max-width: 1100px;
  padding-top: 4.8rem !important;
  padding-bottom: 8rem !important;
}

h1 {
  font-size: clamp(2.25rem, 5.6vw, 3.65rem) !important;
  line-height: 1.02 !important;
  margin: 2.2rem 0 .45rem !important;
  color: var(--pace-text) !important;
  letter-spacing: -.045em !important;
}

h2 {
  font-size: clamp(1.55rem, 3.5vw, 2.1rem) !important;
  color: var(--pace-text) !important;
  letter-spacing: -.035em !important;
}

[data-testid="stCaptionContainer"],
.stCaption,
.muted {
  color: var(--pace-muted) !important;
  font-size: 1.02rem !important;
  line-height: 1.55 !important;
}

.pace-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: .2rem 0 1.2rem;
  border-bottom: 1px solid var(--pace-border);
  margin-bottom: 1rem;
  animation: paceFadeIn .45s ease-out both;
}

.pace-logo {
  color: #fff;
  font-size: 2rem;
  font-weight: 500;
  letter-spacing: .34em;
  line-height: 1;
  text-transform: lowercase;
}

.pace-tagline {
  color: var(--pace-muted);
  font-size: .82rem;
  margin-top: .55rem;
}

.pace-tagline strong {
  color: var(--pace-yellow);
  font-weight: 750;
}

.pace-os-wrap {
  display: flex;
  align-items: center;
  gap: .8rem;
}

.pace-os-label {
  color: var(--pace-muted);
  font-size: .8rem;
  white-space: nowrap;
}

.pace-avatar {
  display: grid;
  place-items: center;
  width: 2.7rem;
  height: 2.7rem;
  border-radius: 50%;
  background: var(--pace-yellow);
  color: #07090d;
  font-size: 1rem;
  font-weight: 850;
  box-shadow: 0 0 0 5px rgba(255,212,0,.06);
}

.hero-card,
.mission-card,
.content-card,
.insight-card {
  border: 1px solid var(--pace-border);
  border-radius: 24px;
  box-shadow: 0 20px 55px rgba(0,0,0,.26);
  animation: paceRise .5s ease-out both;
}

.hero-card {
  position: relative;
  overflow: hidden;
  min-height: 340px;
  padding: clamp(1.5rem, 4.5vw, 2.5rem);
  margin: 1.25rem 0;
  background-color: #0c1016;
  background-size: cover;
  background-position: center right;
  transition: transform .22s ease, border-color .22s ease, box-shadow .22s ease;
}

.hero-card:hover {
  transform: translateY(-2px);
  border-color: rgba(255,212,0,.32);
  box-shadow: 0 24px 65px rgba(0,0,0,.34);
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, rgba(8,11,16,.99) 0%, rgba(8,11,16,.96) 35%, rgba(8,11,16,.58) 62%, rgba(8,11,16,.18) 100%),
    linear-gradient(180deg, rgba(0,0,0,.04), rgba(0,0,0,.4));
}

.hero-content {
  position: relative;
  z-index: 1;
  width: min(710px, 72%);
}

.eyebrow {
  color: var(--pace-yellow);
  font-size: .78rem;
  font-weight: 850;
  letter-spacing: .13em;
  text-transform: uppercase;
  margin-bottom: .6rem;
}

.hero-title {
  color: var(--pace-text);
  font-size: clamp(2.1rem, 5.5vw, 3.55rem);
  font-weight: 840;
  line-height: 1.01;
  letter-spacing: -.045em;
}

.hero-subtitle {
  color: #b4bdc9;
  font-size: 1.06rem;
  margin-top: .75rem;
}

.countdown-row {
  display: flex;
  gap: .65rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}

.countdown-chip {
  background: rgba(6,8,12,.58);
  border: 1px solid rgba(255,255,255,.09);
  border-radius: 999px;
  color: #c5ccd5;
  font-size: .78rem;
  padding: .35rem .7rem;
  backdrop-filter: blur(8px);
}

.metric-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0,1fr));
  gap: .8rem;
  margin-top: 1.4rem;
}

.metric-box {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: .7rem;
  align-items: center;
  background: rgba(16,20,27,.82);
  border: 1px solid rgba(255,255,255,.075);
  border-radius: 17px;
  padding: .95rem;
  backdrop-filter: blur(10px);
}

.metric-icon {
  width: 1.45rem;
  color: var(--pace-yellow);
}

.metric-copy {
  min-width: 0;
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
  font-weight: 780;
  margin-top: .2rem;
}

.status-good {
  color: var(--pace-green) !important;
}

.mission-link {
  display: block;
  color: inherit !important;
  text-decoration: none !important;
}

.mission-card {
  display: grid;
  grid-template-columns: minmax(0,1fr) 170px;
  gap: 1.5rem;
  align-items: center;
  padding: clamp(1.35rem, 4vw, 2rem);
  margin: 1.15rem 0 .85rem;
  background: linear-gradient(145deg, rgba(17,22,29,.99), rgba(10,14,19,.99));
  transition: transform .2s ease, border-color .2s ease, background .2s ease;
}

.mission-link:hover .mission-card {
  transform: translateY(-2px);
  border-color: rgba(255,212,0,.35);
  background: linear-gradient(145deg, rgba(20,26,34,.99), rgba(11,15,21,.99));
}

.mission-title,
.section-title {
  color: var(--pace-text);
  font-size: clamp(1.4rem, 3.4vw, 1.85rem);
  font-weight: 790;
  line-height: 1.16;
  letter-spacing: -.025em;
}

.mission-meta {
  color: #aab3c0;
  font-size: 1.04rem;
  line-height: 1.58;
  margin-top: .72rem;
  max-width: 660px;
}

.coach-cta {
  color: var(--pace-yellow);
  font-size: .85rem;
  font-weight: 820;
  margin-top: 1rem;
}

.progress-ring {
  --ring-progress: 0;
  position: relative;
  display: grid;
  place-items: center;
  width: 138px;
  height: 138px;
  margin-left: auto;
}

.progress-ring svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.progress-ring .track {
  fill: none;
  stroke: #272e38;
  stroke-width: 11;
}

.progress-ring .value {
  fill: none;
  stroke: var(--pace-yellow);
  stroke-linecap: round;
  stroke-width: 11;
  stroke-dasharray: 339.3;
  stroke-dashoffset: calc(339.3 - (339.3 * var(--ring-progress) / 100));
  animation: ringDraw .9s cubic-bezier(.2,.8,.2,1) both;
}

.progress-ring-copy {
  position: absolute;
  text-align: center;
}

.progress-ring-number {
  color: var(--pace-text);
  font-size: 1.8rem;
  font-weight: 840;
  line-height: 1;
}

.progress-ring-label {
  color: var(--pace-muted);
  font-size: .72rem;
  margin-top: .35rem;
}

.content-card {
  padding: 1.3rem;
  margin: 1rem 0;
  background: linear-gradient(145deg, rgba(17,22,29,.98), rgba(10,14,20,.98));
}

.activity-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding-top: .95rem;
}

.activity-name {
  color: var(--pace-text);
  font-size: 1.08rem;
  font-weight: 740;
}

.activity-meta {
  color: var(--pace-muted);
  font-size: .9rem;
  margin-top: .25rem;
}

.activity-value {
  color: var(--pace-text);
  font-size: 1.15rem;
  font-weight: 790;
  white-space: nowrap;
}

.insight-card {
  position: relative;
  padding: 1.15rem 1.25rem;
  margin: .8rem 0;
  background: linear-gradient(145deg, rgba(17,22,29,.99), rgba(10,14,20,.99));
  transition: transform .2s ease, border-color .2s ease;
}

.insight-card:hover {
  transform: translateY(-2px);
  border-color: rgba(255,212,0,.3);
}

.insight-row {
  display: grid;
  grid-template-columns: 2.8rem minmax(0, 1fr);
  gap: .9rem;
  align-items: start;
}

.insight-icon {
  color: var(--pace-yellow);
}

.insight-title {
  color: var(--pace-text);
  font-size: 1.1rem;
  font-weight: 780;
}

.insight-message {
  color: var(--pace-muted);
  font-size: .99rem;
  line-height: 1.52;
  margin-top: .28rem;
}

.insight-status {
  display: inline-block;
  color: var(--pace-green);
  background: rgba(53,217,120,.09);
  border: 1px solid rgba(53,217,120,.24);
  border-radius: 999px;
  padding: .12rem .5rem;
  font-size: .64rem;
  font-weight: 840;
  letter-spacing: .05em;
  text-transform: uppercase;
  margin-left: .4rem;
}

.pace-svg {
  display: inline-flex;
  width: 1.45rem;
  height: 1.45rem;
}

.pace-svg svg {
  width: 100%;
  height: 100%;
  fill: currentColor;
}

div[data-testid="stButton"] > button,
div[data-testid="stLinkButton"] > a {
  min-height: 3.35rem;
  border-radius: 15px;
  font-size: 1.02rem !important;
  font-weight: 760 !important;
  border: 1px solid var(--pace-border);
  transition: transform .18s ease, box-shadow .18s ease, filter .18s ease;
}

div[data-testid="stButton"] > button:hover,
div[data-testid="stLinkButton"] > a:hover {
  transform: translateY(-1px);
}

div[data-testid="stButton"] > button[kind="primary"] {
  background: linear-gradient(90deg, #ffd400, #ffdf35) !important;
  border-color: #ffd400 !important;
  color: #080a0e !important;
  box-shadow: 0 12px 32px rgba(255,212,0,.14);
}

div[data-testid="stButton"] > button[kind="primary"]:hover {
  filter: brightness(1.04);
  box-shadow: 0 15px 38px rgba(255,212,0,.22);
}

div[data-testid="stButton"] > button[kind="primary"] p,
div[data-testid="stButton"] > button[kind="primary"] span {
  color: #080a0e !important;
  font-weight: 840 !important;
}

div[data-testid="stSegmentedControl"] button {
  min-height: 2.95rem;
  padding-inline: 1.25rem !important;
  font-size: 1rem !important;
  font-weight: 740 !important;
  border-color: var(--pace-border) !important;
  transition: background .18s ease, color .18s ease, border-color .18s ease;
}

div[data-testid="stSegmentedControl"] button[aria-pressed="true"] {
  color: var(--pace-yellow) !important;
  border-color: var(--pace-yellow) !important;
  background: rgba(255,212,0,.075) !important;
}


/* Streamlit-native bottom navigation: avoids hard browser reloads */
.pace-native-nav-marker + div[data-testid="stHorizontalBlock"] {
  position: fixed;
  left: 50%;
  bottom: 0;
  transform: translateX(-50%);
  width: min(100%, 1100px);
  z-index: 999;
  gap: .25rem !important;
  padding: .62rem .75rem calc(.62rem + env(safe-area-inset-bottom));
  background: rgba(8,11,16,.96);
  border-top: 1px solid var(--pace-border);
  backdrop-filter: blur(18px);
  box-shadow: 0 -12px 38px rgba(0,0,0,.26);
}

.pace-native-nav-marker + div[data-testid="stHorizontalBlock"] a {
  min-height: 3.15rem !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
  gap: .12rem !important;
  color: #929baa !important;
  background: transparent !important;
  border: 0 !important;
  border-radius: 12px !important;
  box-shadow: none !important;
  font-size: .72rem !important;
  font-weight: 720 !important;
}

.pace-native-nav-marker + div[data-testid="stHorizontalBlock"] a:hover {
  color: var(--pace-yellow) !important;
  background: rgba(255,212,0,.055) !important;
  transform: translateY(-1px);
}

.pace-native-nav-marker + div[data-testid="stHorizontalBlock"] span[data-testid="stIconMaterial"] {
  font-size: 1.35rem !important;
}

.pace-bottom-nav {
  position: fixed;
  left: 50%;
  bottom: 0;
  transform: translateX(-50%);
  width: min(100%, 1100px);
  z-index: 999;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: .2rem;
  padding: .68rem .8rem calc(.68rem + env(safe-area-inset-bottom));
  background: rgba(8,11,16,.96);
  border-top: 1px solid var(--pace-border);
  backdrop-filter: blur(18px);
  box-shadow: 0 -12px 38px rgba(0,0,0,.26);
}

.pace-nav-item {
  display: grid;
  justify-items: center;
  gap: .18rem;
  color: #8f98a6 !important;
  font-size: .7rem;
  text-decoration: none !important;
  padding: .25rem .12rem;
  transition: color .18s ease, transform .18s ease;
}

.pace-nav-item:hover {
  color: #d8dde5 !important;
  transform: translateY(-1px);
}

.pace-nav-icon {
  display: grid;
  place-items: center;
  width: 1.45rem;
  height: 1.45rem;
}

.pace-nav-icon svg {
  width: 100%;
  height: 100%;
  fill: currentColor;
}

.pace-nav-item.active {
  color: var(--pace-yellow) !important;
  font-weight: 840;
}

@keyframes paceFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes paceRise {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes ringDraw {
  from { stroke-dashoffset: 339.3; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .01ms !important;
    transition-duration: .01ms !important;
  }
}

@media (max-width: 700px) {
  [data-testid="stMainBlockContainer"] {
    padding-top: 4.25rem !important;
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .pace-logo {
    font-size: 1.6rem;
  }

  .pace-os-label {
    display: none;
  }

  .pace-avatar {
    width: 2.35rem;
    height: 2.35rem;
  }

  .hero-card {
    min-height: 430px;
    background-position: 62% center;
  }

  .hero-overlay {
    background:
      linear-gradient(180deg, rgba(8,11,16,.98) 0%, rgba(8,11,16,.91) 55%, rgba(8,11,16,.62) 100%);
  }

  .hero-content {
    width: 100%;
  }

  .metric-row {
    grid-template-columns: 1fr;
  }

  .mission-card {
    grid-template-columns: 1fr 110px;
    gap: .7rem;
  }

  .progress-ring {
    width: 105px;
    height: 105px;
  }

  .progress-ring-number {
    font-size: 1.35rem;
  }
}

@media (max-width: 470px) {
  .mission-card {
    grid-template-columns: 1fr;
  }

  .progress-ring {
    margin: .5rem 0 0;
  }

  
/* Streamlit-native bottom navigation: avoids hard browser reloads */
.pace-native-nav-marker + div[data-testid="stHorizontalBlock"] {
  position: fixed;
  left: 50%;
  bottom: 0;
  transform: translateX(-50%);
  width: min(100%, 1100px);
  z-index: 999;
  gap: .25rem !important;
  padding: .62rem .75rem calc(.62rem + env(safe-area-inset-bottom));
  background: rgba(8,11,16,.96);
  border-top: 1px solid var(--pace-border);
  backdrop-filter: blur(18px);
  box-shadow: 0 -12px 38px rgba(0,0,0,.26);
}

.pace-native-nav-marker + div[data-testid="stHorizontalBlock"] a {
  min-height: 3.15rem !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
  gap: .12rem !important;
  color: #929baa !important;
  background: transparent !important;
  border: 0 !important;
  border-radius: 12px !important;
  box-shadow: none !important;
  font-size: .72rem !important;
  font-weight: 720 !important;
}

.pace-native-nav-marker + div[data-testid="stHorizontalBlock"] a:hover {
  color: var(--pace-yellow) !important;
  background: rgba(255,212,0,.055) !important;
  transform: translateY(-1px);
}

.pace-native-nav-marker + div[data-testid="stHorizontalBlock"] span[data-testid="stIconMaterial"] {
  font-size: 1.35rem !important;
}

.pace-bottom-nav {
    padding-inline: .35rem;
  }
}

/* ---------- PACE v0.7.3 shared page styling ---------- */

[data-testid="stForm"] {
  background: linear-gradient(145deg, rgba(17,22,29,.98), rgba(10,14,20,.98));
  border: 1px solid var(--pace-border);
  border-radius: 22px;
  padding: 1.15rem;
  box-shadow: 0 18px 44px rgba(0,0,0,.20);
}

[data-testid="stExpander"] {
  background: rgba(16,20,27,.72);
  border: 1px solid var(--pace-border) !important;
  border-radius: 16px !important;
  overflow: hidden;
}

[data-testid="stExpander"] summary {
  min-height: 3rem;
  font-size: .98rem;
  font-weight: 720;
}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
textarea {
  background: rgba(13,17,23,.95) !important;
  border-color: var(--pace-border) !important;
  border-radius: 14px !important;
  color: var(--pace-text) !important;
}

input, textarea {
  color: var(--pace-text) !important;
  font-size: 1rem !important;
}

label,
[data-testid="stWidgetLabel"] p {
  color: #dbe0e7 !important;
  font-size: .92rem !important;
  font-weight: 680 !important;
}

[data-testid="stSlider"] {
  padding: .35rem 0 .15rem;
}

[data-testid="stSlider"] [role="slider"] {
  background: var(--pace-yellow) !important;
  border-color: var(--pace-yellow) !important;
  box-shadow: 0 0 0 5px rgba(255,212,0,.12);
}

[data-testid="stAlert"] {
  border-radius: 16px !important;
}

[data-testid="stMetric"] {
  background: linear-gradient(145deg, rgba(17,22,29,.98), rgba(10,14,20,.98));
  border: 1px solid var(--pace-border);
  border-radius: 18px;
  padding: 1rem;
}

[data-testid="stMetricValue"] {
  font-size: 1.65rem !important;
  color: var(--pace-text) !important;
}

[data-testid="stMetricLabel"] {
  color: var(--pace-muted) !important;
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
  gap: .35rem;
  background: rgba(12,16,22,.72);
  border: 1px solid var(--pace-border);
  border-radius: 15px;
  padding: .3rem;
}

[data-testid="stTabs"] button {
  border-radius: 11px;
  min-height: 2.7rem;
  font-weight: 720;
}

[data-testid="stTabs"] button[aria-selected="true"] {
  background: rgba(255,212,0,.09);
  color: var(--pace-yellow) !important;
}

[data-testid="stDataFrame"] {
  border: 1px solid var(--pace-border);
  border-radius: 16px;
  overflow: hidden;
}

.pace-page-intro {
  display: flex;
  align-items: center;
  gap: .9rem;
  margin: .25rem 0 1.25rem;
}

.pace-page-icon {
  display: grid;
  place-items: center;
  width: 3.1rem;
  height: 3.1rem;
  border-radius: 16px;
  background: var(--pace-yellow-soft);
  color: var(--pace-yellow);
}

.pace-page-icon .pace-svg {
  width: 1.65rem;
  height: 1.65rem;
}

.pace-page-title {
  color: var(--pace-text);
  font-size: clamp(1.7rem, 4vw, 2.35rem);
  line-height: 1.08;
  font-weight: 830;
  letter-spacing: -.035em;
}

.pace-page-subtitle {
  color: var(--pace-muted);
  font-size: .98rem;
  margin-top: .2rem;
}

.workout-type-label {
  margin: .25rem 0 .55rem;
  color: var(--pace-muted);
  font-size: .76rem;
  font-weight: 820;
  letter-spacing: .1em;
  text-transform: uppercase;
}

div[data-testid="stSegmentedControl"] {
  margin-bottom: .7rem;
}

div[data-testid="stSegmentedControl"] > div {
  gap: .45rem !important;
  flex-wrap: wrap !important;
}

div[data-testid="stSegmentedControl"] button {
  border-radius: 14px !important;
  padding: .7rem 1rem !important;
}

.pace-input-card {
  background: linear-gradient(145deg, rgba(17,22,29,.98), rgba(10,14,20,.98));
  border: 1px solid var(--pace-border);
  border-radius: 22px;
  padding: 1.2rem;
  margin: .85rem 0;
  box-shadow: 0 18px 45px rgba(0,0,0,.19);
}

.pace-section-label {
  display: flex;
  align-items: center;
  gap: .55rem;
  color: var(--pace-text);
  font-size: 1.05rem;
  font-weight: 770;
  margin-bottom: .75rem;
}

.pace-section-label .pace-svg {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--pace-yellow);
}

.rpe-guide {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: .45rem;
  margin: .6rem 0 .25rem;
}

.rpe-zone {
  border: 1px solid var(--pace-border);
  border-radius: 13px;
  padding: .7rem .35rem;
  text-align: center;
  background: rgba(255,255,255,.025);
}

.rpe-zone-icon {
  font-size: 1.25rem;
}

.rpe-zone-name {
  color: var(--pace-text);
  font-size: .72rem;
  font-weight: 760;
  margin-top: .2rem;
}

.rpe-zone-range {
  color: var(--pace-muted);
  font-size: .64rem;
  margin-top: .08rem;
}

.pain-guide {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: .45rem;
  margin: .5rem 0 .25rem;
}

.pain-level {
  border: 1px solid var(--pace-border);
  border-radius: 13px;
  padding: .7rem .35rem;
  text-align: center;
  background: rgba(255,255,255,.025);
}

.pain-dot {
  width: .7rem;
  height: .7rem;
  margin: 0 auto .35rem;
  border-radius: 50%;
}

.pain-none { background: var(--pace-green); }
.pain-mild { background: var(--pace-yellow); }
.pain-moderate { background: #ff922b; }
.pain-severe { background: var(--pace-red); }

.pace-live-summary {
  display: grid;
  grid-template-columns: 1.1fr repeat(4, minmax(0,.75fr));
  gap: .65rem;
  align-items: stretch;
  background:
    linear-gradient(145deg, rgba(255,212,0,.085), rgba(16,20,27,.98));
  border: 1px solid rgba(255,212,0,.28);
  border-radius: 20px;
  padding: 1rem;
  margin: 1rem 0;
}

.summary-primary,
.summary-stat {
  border-radius: 14px;
  background: rgba(8,11,16,.52);
  padding: .8rem;
}

.summary-kicker {
  color: var(--pace-yellow);
  font-size: .68rem;
  font-weight: 840;
  letter-spacing: .09em;
  text-transform: uppercase;
}

.summary-title {
  color: var(--pace-text);
  font-size: 1.12rem;
  font-weight: 800;
  margin-top: .2rem;
}

.summary-label {
  color: var(--pace-muted);
  font-size: .66rem;
  text-transform: uppercase;
  letter-spacing: .07em;
}

.summary-value {
  color: var(--pace-text);
  font-size: 1.02rem;
  font-weight: 780;
  margin-top: .25rem;
}

.recent-workout-card {
  background: linear-gradient(145deg, rgba(17,22,29,.98), rgba(10,14,20,.98));
  border: 1px solid var(--pace-border);
  border-radius: 18px;
  padding: 1rem 1.05rem;
  margin: .65rem 0;
  transition: transform .18s ease, border-color .18s ease;
}

.recent-workout-card:hover {
  transform: translateY(-1px);
  border-color: rgba(255,212,0,.25);
}

.recent-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.recent-title {
  color: var(--pace-text);
  font-size: 1.03rem;
  font-weight: 760;
}

.recent-meta {
  color: var(--pace-muted);
  font-size: .86rem;
  margin-top: .25rem;
}

.recent-value {
  color: var(--pace-text);
  font-size: 1.08rem;
  font-weight: 790;
  text-align: right;
}

.recent-subvalue {
  color: var(--pace-muted);
  font-size: .78rem;
  text-align: right;
  margin-top: .2rem;
}

@media (max-width: 700px) {
  .rpe-guide {
    grid-template-columns: repeat(3, 1fr);
  }

  .pain-guide {
    grid-template-columns: repeat(2, 1fr);
  }

  .pace-live-summary {
    grid-template-columns: repeat(2, 1fr);
  }

  .summary-primary {
    grid-column: 1 / -1;
  }
}

</style>
"""


def inject_global_styles() -> None:
    st.markdown(PACE_CSS, unsafe_allow_html=True)


def apply_global_styles() -> None:
    inject_global_styles()


def render_brand_header() -> None:
    user = st.session_state.get("auth_user")
    initials = "P"
    if user:
        metadata = getattr(user, "user_metadata", {}) or {}
        display_name = metadata.get("display_name") or metadata.get("name")
        email = getattr(user, "email", "") or ""
        source = display_name or email
        if source:
            initials = source.strip()[0].upper()

    st.markdown(
        f"""
        <header class="pace-topbar">
          <div>
            <div class="pace-logo">pace</div>
            <div class="pace-tagline">Train <strong>together</strong>. Train <strong>smarter</strong>.</div>
          </div>
          <div class="pace-os-wrap">
            <div class="pace-os-label">HYROX Partner OS</div>
            <div class="pace-avatar">{escape(initials)}</div>
          </div>
        </header>
        """,
        unsafe_allow_html=True,
    )


def metric_html(
    label: str,
    value: str,
    value_class: str = "",
    icon: str = "trend",
) -> str:
    return (
        '<div class="metric-box">'
        f'<div class="metric-icon">{icon_svg(icon)}</div>'
        '<div class="metric-copy">'
        f'<div class="metric-label">{escape(str(label))}</div>'
        f'<div class="metric-value {escape(value_class)}">{escape(str(value))}</div>'
        "</div></div>"
    )


def progress_ring_html(progress: int) -> str:
    bounded = max(0, min(int(progress), 100))
    return f"""
        <div class="progress-ring" style="--ring-progress:{bounded};">
          <svg viewBox="0 0 120 120" aria-hidden="true">
            <circle class="track" cx="60" cy="60" r="54"></circle>
            <circle class="value" cx="60" cy="60" r="54"></circle>
          </svg>
          <div class="progress-ring-copy">
            <div class="progress-ring-number">{bounded}%</div>
            <div class="progress-ring-label">of weekly goal</div>
          </div>
        </div>
    """


def race_hero_style() -> str:
    if not _HERO_DATA_URI:
        return ""
    return f"background-image:url('{_HERO_DATA_URI}');"


def render_bottom_nav(active: str) -> None:
    """
    Render navigation with Streamlit-native page links.

    Native page links preserve Streamlit session state and the authenticated
    Supabase session. Raw HTML href links trigger a full browser reload and can
    send the user back through the login gate.
    """
    items = [
        ("Today", "views/home.py", ":material/home:"),
        ("Log", "views/activities.py", ":material/add_box:"),
        ("Coach", "views/coach.py", ":material/auto_awesome:"),
        ("Progress", "views/progress.py", ":material/bar_chart:"),
        ("Me", "views/profile.py", ":material/person:"),
    ]

    st.markdown('<div class="pace-native-nav-marker"></div>', unsafe_allow_html=True)

    columns = st.columns(len(items), gap="small")
    for column, (label, page, icon) in zip(columns, items):
        with column:
            st.page_link(
                page,
                label=label,
                icon=icon,
                use_container_width=True,
            )
