import base64
from pathlib import Path

import pandas as pd
import streamlit as st


# --------------------------------------------------
# Configuration & Page Setup
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PREDICTIONS_FILE = PROJECT_ROOT / "data" / "latest_predictions.csv"

st.set_page_config(
    page_title="NFL Game Predictions | Independent Analytics",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------
# NFL Team Branding (32 Franchises)
# --------------------------------------------------

TEAM_INFO = {
    "ARI": {"name": "Arizona Cardinals", "primary": "#97233F", "secondary": "#FFB612"},
    "ATL": {"name": "Atlanta Falcons", "primary": "#A71930", "secondary": "#000000"},
    "BAL": {"name": "Baltimore Ravens", "primary": "#241773", "secondary": "#9E7C0C"},
    "BUF": {"name": "Buffalo Bills", "primary": "#00338D", "secondary": "#C60C30"},
    "CAR": {"name": "Carolina Panthers", "primary": "#0085CA", "secondary": "#101820"},
    "CHI": {"name": "Chicago Bears", "primary": "#0B162A", "secondary": "#C83803"},
    "CIN": {"name": "Cincinnati Bengals", "primary": "#FB4F14", "secondary": "#000000"},
    "CLE": {"name": "Cleveland Browns", "primary": "#311D00", "secondary": "#FF3C00"},
    "DAL": {"name": "Dallas Cowboys", "primary": "#003594", "secondary": "#869397"},
    "DEN": {"name": "Denver Broncos", "primary": "#FB4F14", "secondary": "#002244"},
    "DET": {"name": "Detroit Lions", "primary": "#0076B6", "secondary": "#B0B7BC"},
    "GB": {"name": "Green Bay Packers", "primary": "#203731", "secondary": "#FFB612"},
    "HOU": {"name": "Houston Texans", "primary": "#03202F", "secondary": "#A71930"},
    "IND": {"name": "Indianapolis Colts", "primary": "#002C5F", "secondary": "#A2AAAD"},
    "JAX": {"name": "Jacksonville Jaguars", "primary": "#006778", "secondary": "#D7A22A"},
    "KC": {"name": "Kansas City Chiefs", "primary": "#E31837", "secondary": "#FFB81C"},
    "LV": {"name": "Las Vegas Raiders", "primary": "#000000", "secondary": "#A5ACAF"},
    "LAC": {"name": "Los Angeles Chargers", "primary": "#0080C6", "secondary": "#FFC20E"},
    "LA": {"name": "Los Angeles Rams", "primary": "#003594", "secondary": "#FFA300"},
    "LAR": {"name": "Los Angeles Rams", "primary": "#003594", "secondary": "#FFA300"},
    "MIA": {"name": "Miami Dolphins", "primary": "#008E97", "secondary": "#FC4C02"},
    "MIN": {"name": "Minnesota Vikings", "primary": "#4F2683", "secondary": "#FFC62F"},
    "NE": {"name": "New England Patriots", "primary": "#002244", "secondary": "#C60C30"},
    "NO": {"name": "New Orleans Saints", "primary": "#D3BC8D", "secondary": "#101820"},
    "NYG": {"name": "New York Giants", "primary": "#0B2265", "secondary": "#A71930"},
    "NYJ": {"name": "New York Jets", "primary": "#125740", "secondary": "#000000"},
    "PHI": {"name": "Philadelphia Eagles", "primary": "#004C54", "secondary": "#A5ACAF"},
    "PIT": {"name": "Pittsburgh Steelers", "primary": "#FFB612", "secondary": "#101820"},
    "SF": {"name": "San Francisco 49ers", "primary": "#AA0000", "secondary": "#B3995D"},
    "SEA": {"name": "Seattle Seahawks", "primary": "#002244", "secondary": "#69BE28"},
    "TB": {"name": "Tampa Bay Buccaneers", "primary": "#D50A0A", "secondary": "#34302B"},
    "TEN": {"name": "Tennessee Titans", "primary": "#0C2340", "secondary": "#4B92DB"},
    "WAS": {"name": "Washington Commanders", "primary": "#5A1414", "secondary": "#FFB612"},
    "WSH": {"name": "Washington Commanders", "primary": "#5A1414", "secondary": "#FFB612"},
}


def get_team_name(abbr: str) -> str:
    """Return full display name for a team abbreviation."""
    return TEAM_INFO.get(abbr, {}).get("name", abbr)


def get_team_accent_color(abbr: str) -> str:
    """Return high-contrast team accent color suitable for dark backgrounds."""
    info = TEAM_INFO.get(abbr, {"primary": "#38bdf8", "secondary": "#94a3b8"})
    dark_primaries = {"#000000", "#0B162A", "#03202F", "#0C2340", "#002244", "#311D00"}
    if info["primary"] in dark_primaries:
        return info["secondary"] if info["secondary"] != "#000000" else "#38bdf8"
    return info["primary"]


def get_team_logo_html(abbr: str, size: int = 24) -> str:
    """
    Check for optional local logo at app/assets/teams/{abbr}.png.
    If available, returns inline base64 image tag.
    If not available, gracefully returns empty string.
    Completely offline: zero network requests or external dependencies.
    """
    logo_path = PROJECT_ROOT / "app" / "assets" / "teams" / f"{abbr}.png"
    if logo_path.exists():
        try:
            b64_data = base64.b64encode(logo_path.read_bytes()).decode("utf-8")
            return (
                f'<img src="data:image/png;base64,{b64_data}" alt="{abbr}" '
                f'style="width:{size}px; height:{size}px; object-fit:contain; '
                f'vertical-align:middle; margin-right:8px; border-radius:4px;" />'
            )
        except Exception:
            return ""
    return ""


# --------------------------------------------------
# Dark Sports-Dashboard Styling
# --------------------------------------------------

st.html(
    """
    <style>
    /* Global Canvas & Base Typography */
    .stApp {
        background-color: #080c18;
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Prevent clipping by Streamlit's fixed header */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    .block-container {
        max-width: 1240px;
        padding-top: 3.25rem !important;
        padding-bottom: 4rem;
        padding-left: 1.25rem;
        padding-right: 1.25rem;
    }

    /* Primary Tab Navigation — High Prominence & Contrast */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.85rem;
        background-color: #0b1325;
        padding: 0.5rem 0.65rem;
        border-radius: 14px;
        border: 1px solid #1e2c47;
        margin-bottom: 2rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.85rem 1.85rem !important;
        font-weight: 700 !important;
        font-size: 1.02rem !important;
        color: #94a3b8 !important;
        background-color: transparent;
        border: 1px solid transparent !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        letter-spacing: 0.015em;
        cursor: pointer;
        box-shadow: none !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #f1f5f9 !important;
        background-color: rgba(30, 44, 71, 0.55) !important;
        border-color: #243452 !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(180deg, #13223d 0%, #0f1a30 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(56, 189, 248, 0.45) !important;
        box-shadow: inset 0 2px 0 #38bdf8, 0 4px 14px rgba(0, 0, 0, 0.3) !important;
    }

    .stTabs [aria-selected="true"] p,
    .stTabs [aria-selected="true"] span,
    .stTabs [aria-selected="true"] div {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    .stTabs [aria-selected="false"] p,
    .stTabs [aria-selected="false"] span,
    .stTabs [aria-selected="false"] div {
        color: #94a3b8 !important;
        font-weight: 650 !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #38bdf8 !important;
        height: 3px !important;
        border-radius: 3px 3px 0 0;
    }

    /* Filter Pills (st.pills / stButtonGroup) — Dark Analytics Styling */
    div[data-testid="stButtonGroup"] {
        background-color: transparent !important;
        gap: 0.5rem !important;
        padding: 0.25rem 0 0.5rem 0 !important;
    }

    div[data-testid="stButtonGroup"] button,
    div[data-testid="stButtonGroup"] [role="button"],
    div[data-testid="stButtonGroup"] div[data-baseweb="button"] {
        background-color: #0f172a !important;
        color: #94a3b8 !important;
        border: 1px solid #1e2c47 !important;
        border-radius: 999px !important;
        padding: 0.45rem 1.15rem !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        transition: all 0.15s ease !important;
        box-shadow: none !important;
        cursor: pointer !important;
    }

    div[data-testid="stButtonGroup"] button:hover,
    div[data-testid="stButtonGroup"] [role="button"]:hover {
        background-color: #1e2c47 !important;
        color: #f8fafc !important;
        border-color: #38bdf8 !important;
    }

    div[data-testid="stButtonGroup"] button[aria-pressed="true"],
    div[data-testid="stButtonGroup"] button[aria-selected="true"],
    div[data-testid="stButtonGroup"] button[data-checked="true"],
    div[data-testid="stButtonGroup"] [aria-pressed="true"],
    div[data-testid="stButtonGroup"] [aria-selected="true"] {
        background: linear-gradient(180deg, #13223d 0%, #0f1a30 100%) !important;
        color: #38bdf8 !important;
        border: 1px solid #38bdf8 !important;
        font-weight: 700 !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.25) !important;
    }

    div[data-testid="stButtonGroup"] button[aria-pressed="true"] *,
    div[data-testid="stButtonGroup"] button[aria-selected="true"] * {
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }

    div[data-testid="stButtonGroup"] button[aria-pressed="false"] *,
    div[data-testid="stButtonGroup"] button[aria-selected="false"] * {
        color: #94a3b8 !important;
    }

    /* Matchup Selector Dropdown (stSelectbox) — Dark Analytics Theme */
    div[data-testid="stSelectbox"] {
        margin-top: 0.25rem;
        margin-bottom: 0.5rem;
    }

    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        border-radius: 12px !important;
    }

    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background-color: #0f172a !important;
        border: 1px solid #1e2c47 !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        min-height: 46px !important;
        height: 46px !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        padding-left: 0.85rem !important;
        transition: all 0.15s ease !important;
        box-shadow: none !important;
    }

    div[data-testid="stSelectbox"] div[data-baseweb="select"]:hover > div {
        border-color: #2e4368 !important;
        background-color: #121c32 !important;
    }

    div[data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within > div {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.25) !important;
    }

    div[data-testid="stSelectbox"] [data-baseweb="select"] * {
        color: #f8fafc !important;
    }

    div[data-testid="stSelectbox"] svg {
        fill: #94a3b8 !important;
        color: #94a3b8 !important;
    }

    /* Virtual Dropdown Popover Menu */
    ul[data-testid="stSelectboxVirtualDropdown"],
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    ul[role="listbox"] {
        background-color: #0c1426 !important;
        border: 1px solid #1e2c47 !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5) !important;
    }

    li[role="option"] {
        background-color: #0c1426 !important;
        color: #cbd5e1 !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        padding: 0.65rem 0.9rem !important;
        transition: background-color 0.1s ease, color 0.1s ease !important;
    }

    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {
        background-color: #162444 !important;
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }

    /* Section Titles */
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        letter-spacing: -0.01em;
        color: #f8fafc;
        margin-top: 1.75rem;
        margin-bottom: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .section-caption {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-bottom: 1rem;
    }

    /* Hero Banner */
    .nfl-hero {
        background: linear-gradient(135deg, #0f172a 0%, #141f36 60%, #162444 100%);
        border: 1px solid #1e2c47;
        border-radius: 16px;
        padding: 1.75rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.4);
    }

    .hero-meta-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 0.6rem;
    }

    .hero-kicker {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        color: #38bdf8;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .hero-timestamp {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        color: #94a3b8;
        font-size: 0.78rem;
        font-weight: 500;
    }

    .live-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: #22c55e;
        display: inline-block;
    }

    .hero-title {
        font-size: 2.15rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        color: #f8fafc;
        margin: 0.2rem 0 0.4rem 0;
        line-height: 1.15;
    }

    .hero-subtitle {
        color: #cbd5e1;
        font-size: 0.95rem;
        line-height: 1.5;
        max-width: 880px;
    }

    /* KPI Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 1.75rem;
    }

    @media (max-width: 900px) {
        .kpi-container {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    @media (max-width: 520px) {
        .kpi-container {
            grid-template-columns: 1fr;
        }
    }

    .kpi-card {
        background-color: #0f172a;
        border: 1px solid #1e2c47;
        border-radius: 12px;
        padding: 1.1rem 1.25rem;
        transition: border-color 0.2s ease;
    }

    .kpi-card:hover {
        border-color: #2e4368;
    }

    .kpi-label {
        color: #94a3b8;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.35rem;
    }

    .kpi-value {
        color: #f8fafc;
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        line-height: 1.1;
        font-variant-numeric: tabular-nums;
    }

    .kpi-subtext {
        color: #64748b;
        font-size: 0.76rem;
        margin-top: 0.35rem;
        font-weight: 500;
    }

    /* Featured Pick Card */
    .pick-card {
        background-color: #0f172a;
        border: 1px solid #1e2c47;
        border-radius: 14px;
        padding: 1.25rem;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
        transition: border-color 0.2s ease, transform 0.15s ease;
    }

    .pick-card:hover {
        border-color: #2e4368;
    }

    .pick-rank-badge {
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #38bdf8;
        margin-bottom: 0.35rem;
    }

    .pick-team-identity {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        margin-bottom: 0.15rem;
    }

    .pick-full-team-name {
        font-size: 0.98rem;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.25;
    }

    .pick-matchup {
        color: #94a3b8;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.65rem;
    }

    .pick-winner-kicker {
        color: #64748b;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .pick-winner-team {
        color: #f8fafc;
        font-size: 2.05rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        line-height: 1.1;
        margin: 0.15rem 0 0.4rem 0;
    }

    .pick-prob-row {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }

    .pick-probability {
        color: #f8fafc;
        font-size: 1.45rem;
        font-weight: 700;
        font-variant-numeric: tabular-nums;
    }

    .pick-prob-label {
        color: #94a3b8;
        font-size: 0.75rem;
        font-weight: 500;
    }

    /* Mini Progress Bar */
    .mini-prob-bar-bg {
        width: 100%;
        height: 6px;
        background-color: #1e293b;
        border-radius: 999px;
        overflow: hidden;
        margin-bottom: 0.85rem;
    }

    .mini-prob-bar-fill {
        height: 100%;
        border-radius: 999px;
    }

    /* Custom Dark Full Week Predictions Table */
    .full-week-table-container {
        background-color: #0f172a;
        border: 1px solid #1e2c47;
        border-radius: 12px;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        margin-top: 0.75rem;
        margin-bottom: 1.5rem;
    }

    .full-week-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.88rem;
        text-align: left;
    }

    .full-week-table thead {
        background-color: #0b1325;
        border-bottom: 1px solid #1e2c47;
    }

    .full-week-table th {
        padding: 0.85rem 1rem;
        color: #94a3b8;
        font-size: 0.74rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        white-space: nowrap;
    }

    .full-week-table td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #16223b;
        color: #e2e8f0;
        vertical-align: middle;
        white-space: nowrap;
    }

    .full-week-table tr:last-child td {
        border-bottom: none;
    }

    .full-week-table tr:hover td {
        background-color: #131e34;
    }

    .table-matchup {
        font-weight: 600;
        color: #cbd5e1;
    }

    .table-kickoff {
        color: #94a3b8;
        font-size: 0.8rem;
    }

    .table-pick-cell {
        display: flex;
        align-items: center;
        gap: 0.45rem;
    }

    .table-pick-pip {
        width: 6px;
        height: 18px;
        border-radius: 2px;
        display: inline-block;
    }

    .table-pick-team {
        font-size: 0.95rem;
        font-weight: 800;
        color: #f8fafc;
    }

    .table-prob-wrapper {
        display: flex;
        align-items: center;
        gap: 0.65rem;
    }

    .table-prob-text {
        font-size: 0.88rem;
        font-weight: 700;
        color: #f8fafc;
        font-variant-numeric: tabular-nums;
        min-width: 48px;
    }

    .table-prob-track {
        flex-grow: 1;
        height: 7px;
        background-color: #1e293b;
        border-radius: 999px;
        overflow: hidden;
        min-width: 70px;
        max-width: 110px;
    }

    .table-prob-fill {
        height: 100%;
        border-radius: 999px;
        transition: width 0.25s ease;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.28rem 0.65rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        border: 1px solid transparent;
        width: fit-content;
    }

    .badge-highest, .badge-high {
        background-color: rgba(34, 197, 94, 0.12);
        color: #4ade80;
        border-color: rgba(34, 197, 94, 0.28);
    }

    .badge-strong {
        background-color: rgba(245, 158, 11, 0.12);
        color: #fbbf24;
        border-color: rgba(245, 158, 11, 0.28);
    }

    .badge-lean {
        background-color: rgba(148, 163, 184, 0.10);
        color: #cbd5e1;
        border-color: rgba(148, 163, 184, 0.22);
    }

    .badge-tossup {
        background-color: rgba(100, 116, 139, 0.10);
        color: #94a3b8;
        border-color: rgba(100, 116, 139, 0.20);
    }

    /* Matchup Board */
    .matchup-board {
        background-color: #0f172a;
        border: 1px solid #1e2c47;
        border-radius: 14px;
        padding: 1.5rem;
        margin-top: 0.5rem;
        margin-bottom: 1.5rem;
    }

    .matchup-teams-row {
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        align-items: center;
        gap: 1.5rem;
        margin-bottom: 1.25rem;
    }

    @media (max-width: 600px) {
        .matchup-teams-row {
            grid-template-columns: 1fr;
            text-align: center;
            gap: 0.75rem;
        }
    }

    .team-cell {
        padding: 1.15rem;
        border-radius: 10px;
        background-color: #080c18;
        border: 1px solid #1e2c47;
    }

    .team-cell-winner {
        border-color: #38bdf8;
        background: linear-gradient(180deg, #101c33 0%, #080c18 100%);
    }

    .team-role {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #64748b;
    }

    .team-role-winner {
        color: #38bdf8;
    }

    .team-header-identity {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        margin-top: 0.25rem;
    }

    .team-full-display-name {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f8fafc;
    }

    .team-code {
        font-size: 2.15rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #f8fafc;
        margin: 0.1rem 0 0.25rem 0;
    }

    .team-prob-large {
        font-size: 1.35rem;
        font-weight: 700;
        font-variant-numeric: tabular-nums;
        color: #f8fafc;
    }

    .vs-separator {
        text-align: center;
        color: #475569;
        font-weight: 800;
        font-size: 1rem;
        letter-spacing: 0.1em;
    }

    /* Head-to-Head Split Probability Bar */
    .split-bar-wrapper {
        margin: 1rem 0 1.25rem 0;
    }

    .split-bar-labels {
        display: flex;
        justify-content: space-between;
        font-size: 0.82rem;
        font-weight: 700;
        color: #cbd5e1;
        margin-bottom: 0.35rem;
        font-variant-numeric: tabular-nums;
    }

    .split-bar-track {
        display: flex;
        width: 100%;
        height: 12px;
        background-color: #1e293b;
        border-radius: 999px;
        overflow: hidden;
    }

    .split-bar-away {
        height: 100%;
        transition: width 0.3s ease;
    }

    .split-bar-home {
        height: 100%;
        transition: width 0.3s ease;
    }

    /* Model Edge Breakdown Section */
    .edge-section {
        background-color: #0c1426;
        border: 1px solid #1e2c47;
        border-radius: 12px;
        padding: 1.25rem;
        margin-top: 1.25rem;
    }

    .edge-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 0.85rem;
    }

    .edge-title {
        font-size: 0.92rem;
        font-weight: 700;
        color: #f8fafc;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    .edge-pill-badge {
        font-size: 0.68rem;
        font-weight: 700;
        color: #38bdf8;
        background-color: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.28);
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .edge-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 0.75rem;
    }

    .edge-item {
        background-color: #080c18;
        border: 1px solid #1e2c47;
        border-radius: 8px;
        padding: 0.75rem 0.9rem;
    }

    .edge-item-name {
        font-size: 0.72rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }

    .edge-item-row {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
    }

    .edge-item-team {
        font-size: 0.92rem;
        font-weight: 800;
        color: #f8fafc;
    }

    .edge-item-val {
        font-size: 0.85rem;
        font-weight: 700;
        color: #38bdf8;
        font-variant-numeric: tabular-nums;
    }

    .edge-footnote {
        font-size: 0.72rem;
        color: #64748b;
        margin-top: 0.75rem;
        line-height: 1.4;
    }

    /* Supplementary Context Box */
    .context-box {
        background-color: #080c18;
        border: 1px dashed #243452;
        border-radius: 10px;
        padding: 1rem 1.15rem;
        margin-top: 1.25rem;
    }

    .context-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 0.75rem;
    }

    .context-badge {
        font-size: 0.68rem;
        font-weight: 700;
        color: #94a3b8;
        background-color: rgba(148, 163, 184, 0.12);
        border: 1px solid rgba(148, 163, 184, 0.25);
        padding: 0.22rem 0.55rem;
        border-radius: 999px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .context-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 0.6rem;
    }

    .context-chip {
        background-color: #0d1527;
        border: 1px solid #1e2c47;
        border-radius: 6px;
        padding: 0.5rem 0.7rem;
    }

    .context-chip-label {
        font-size: 0.68rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .context-chip-val {
        font-size: 0.85rem;
        font-weight: 700;
        color: #cbd5e1;
        margin-top: 0.15rem;
    }

    /* Performance & Validation Cards */
    .perf-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.25rem;
        margin-bottom: 1.75rem;
    }

    .perf-card {
        background-color: #0f172a;
        border: 1px solid #1e2c47;
        border-radius: 12px;
        padding: 1.35rem;
    }

    .perf-card-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #38bdf8;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    .perf-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
    }

    .perf-table th {
        text-align: left;
        color: #64748b;
        font-weight: 600;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid #1e293b;
        text-transform: uppercase;
        font-size: 0.72rem;
        letter-spacing: 0.06em;
    }

    .perf-table td {
        padding: 0.5rem 0;
        border-bottom: 1px solid #141f36;
        color: #e2e8f0;
    }

    .perf-table tr:last-child td {
        border-bottom: none;
        font-weight: 700;
        color: #38bdf8;
        padding-top: 0.6rem;
    }

    .perf-stat-highlight {
        font-variant-numeric: tabular-nums;
        font-weight: 700;
    }

    /* Disclaimer Footer */
    .disclaimer-card {
        background-color: #0a0f1d;
        border: 1px solid #1a2438;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-top: 2.5rem;
        font-size: 0.78rem;
        color: #64748b;
        line-height: 1.5;
        text-align: center;
    }
    </style>
    """
)


# --------------------------------------------------
# Data Helpers
# --------------------------------------------------

@st.cache_data
def load_predictions() -> pd.DataFrame:
    """Load and return the saved model predictions from data/latest_predictions.csv."""
    if not PREDICTIONS_FILE.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(PREDICTIONS_FILE)
    except Exception:
        return pd.DataFrame()


def get_confidence_badge_class(label: str) -> str:
    """Map confidence classification labels to CSS badge classes."""
    mapping = {
        "Highest Confidence": "badge-highest",
        "High Confidence": "badge-high",
        "Strong Lean": "badge-strong",
        "Lean": "badge-lean",
        "Toss-up": "badge-tossup",
    }
    return mapping.get(str(label), "badge-tossup")


def get_confidence_bar_color(label: str) -> str:
    """Return restrained accent colors adhering to sports analytics guidelines."""
    if label in ("Highest Confidence", "High Confidence"):
        return "#22c55e"  # Green only for strongest confidence
    if label == "Strong Lean":
        return "#f59e0b"  # Amber for strong leans
    return "#38bdf8"      # Restrained blue accent for lean / toss-up


# --------------------------------------------------
# Load & Prepare Predictions Data
# --------------------------------------------------

predictions = load_predictions()

if predictions.empty:
    st.warning(
        "No saved predictions were found at data/latest_predictions.csv. "
        "Run `python -m src.run_predictions` to generate the latest picks."
    )
    st.stop()

# Ensure standard sorting by favorite probability descending
predictions = predictions.sort_values(
    "favorite_probability",
    ascending=False,
).reset_index(drop=True)

season = int(predictions["season"].iloc[0])
week = int(predictions["week"].iloc[0])

updated_text = "Recent"
if "predictions_updated" in predictions.columns and not pd.isna(predictions["predictions_updated"].iloc[0]):
    updated = pd.to_datetime(predictions["predictions_updated"].iloc[0])
    updated_text = f"{updated:%b %d, %Y · %I:%M %p}"


# --------------------------------------------------
# 1. Independent Analytics Header (Non-Clipped Hero)
# --------------------------------------------------

st.html(
    f"""
    <div class="nfl-hero">
        <div class="hero-meta-row">
            <div class="hero-kicker">
                <span>🏈 Independent ML Analytics Lab</span>
                <span>&bull;</span>
                <span>{season} Regular Season &bull; Week {week}</span>
            </div>
            <div class="hero-timestamp">
                <span class="live-dot"></span>
                <span>Model Refresh {updated_text}</span>
            </div>
        </div>
        <div class="hero-title">
            NFL Game Predictions
        </div>
        <div class="hero-subtitle">
            Independent Machine Learning Benchmark &bull; Probabilistic game-winner forecasts calibrated on 8-game rolling team efficiency differentials. Not affiliated with or endorsed by the National Football League.
        </div>
    </div>
    """
)


# --------------------------------------------------
# Top-Level Navigation Tabs (High Prominence)
# --------------------------------------------------

tab_predictions, tab_performance = st.tabs(
    ["Weekly Predictions", "Model Performance & Validation"]
)


# ==================================================
# TAB 1: WEEKLY PREDICTIONS
# ==================================================

with tab_predictions:

    # --------------------------------------------------
    # 2. Polished KPI Row
    # --------------------------------------------------

    games_count = len(predictions)
    picks_75 = int((predictions["favorite_probability"] >= 0.75).sum())
    top_confidence = float(predictions["favorite_probability"].max())
    top_game = predictions.iloc[0]
    top_pick_winner = top_game["predicted_winner"]
    top_pick_winner_name = get_team_name(top_pick_winner)
    top_pick_label = f"{top_pick_winner_name} ({top_game['favorite_probability']:.1%})"

    st.html(
        f"""
        <div class="kpi-container">
            <div class="kpi-card">
                <div class="kpi-label">Games This Week</div>
                <div class="kpi-value">{games_count}</div>
                <div class="kpi-subtext">Week {week} active slate</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">75%+ Confidence</div>
                <div class="kpi-value">{picks_75}</div>
                <div class="kpi-subtext">High-conviction projections</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Highest Confidence</div>
                <div class="kpi-value">{top_confidence:.1%}</div>
                <div class="kpi-subtext">{top_pick_label}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Historical Accuracy</div>
                <div class="kpi-value">63.4%</div>
                <div class="kpi-subtext">Walk-forward validation (2022–2025)</div>
            </div>
        </div>
        """
    )

    # --------------------------------------------------
    # 3. Featured Picks (Top 3 Model Predictions)
    # --------------------------------------------------

    st.html(
        f"""
        <div class="section-title">Featured High-Conviction Picks</div>
        <div class="section-caption">The model's three highest-confidence straight-up forecasts for Week {week}.</div>
        """
    )

    featured = predictions.head(3)
    feat_col1, feat_col2, feat_col3 = st.columns(3)

    for rank, (col, (_, game)) in enumerate(zip([feat_col1, feat_col2, feat_col3], featured.iterrows()), start=1):
        label = game["confidence_label"]
        badge_cls = get_confidence_badge_class(label)
        bar_color = get_confidence_bar_color(label)
        away_abbr = str(game["away_team"])
        home_abbr = str(game["home_team"])
        winner_abbr = str(game["predicted_winner"])
        probability = float(game["favorite_probability"])
        prob_percent = probability * 100

        winner_full_name = get_team_name(winner_abbr)
        away_full_name = get_team_name(away_abbr)
        home_full_name = get_team_name(home_abbr)
        winner_accent = get_team_accent_color(winner_abbr)
        winner_logo_html = get_team_logo_html(winner_abbr, size=22)

        time_info = ""
        if "weekday" in game and "gametime" in game and pd.notna(game["weekday"]):
            time_info = f"{game['weekday'][:3]} {game['gametime']}"

        with col:
            st.html(
                f"""
                <div class="pick-card" style="border-top: 3px solid {winner_accent};">
                    <div>
                        <div class="pick-rank-badge">#{rank} Pick &bull; {time_info}</div>
                        <div class="pick-team-identity">
                            {winner_logo_html}
                            <span class="pick-full-team-name">{winner_full_name}</span>
                        </div>
                        <div class="pick-matchup">{away_abbr} @ {home_abbr}</div>
                        <div class="pick-winner-kicker">Model Pick</div>
                        <div class="pick-winner-team">{winner_abbr}</div>
                    </div>
                    <div>
                        <div class="pick-prob-row">
                            <span class="pick-prob-label">Win Probability</span>
                            <span class="pick-probability">{probability:.1%}</span>
                        </div>
                        <div class="mini-prob-bar-bg">
                            <div class="mini-prob-bar-fill" style="width: {prob_percent:.1f}%; background-color: {bar_color};"></div>
                        </div>
                        <span class="badge {badge_cls}">{label}</span>
                    </div>
                </div>
                """
            )

    # --------------------------------------------------
    # 4. Full Week Predictions & Confidence Filtering
    # --------------------------------------------------

    st.html(
        f"""
        <div class="section-title" style="margin-top: 2rem;">Full Week Predictions</div>
        <div class="section-caption">Filter all Week {week} games by confidence rating.</div>
        """
    )

    confidence_filter_options = [
        "All Picks",
        "Highest Confidence",
        "High Confidence",
        "Strong Lean",
        "Lean",
        "Toss-up",
    ]

    selected_filter = st.pills(
        "Filter by Confidence",
        confidence_filter_options,
        default="All Picks",
        label_visibility="collapsed",
    )

    if not selected_filter or selected_filter == "All Picks":
        filtered_df = predictions.copy()
    else:
        filtered_df = predictions[predictions["confidence_label"] == selected_filter].copy()

    if filtered_df.empty:
        st.info(f"No games classified as '{selected_filter}' for Week {week}.")
    else:
        # Build Dark-Theme Sports Analytics Table with Exact 0–100% Probability Bars
        rows_html = ""
        for _, r in filtered_df.iterrows():
            away_code = str(r["away_team"])
            home_code = str(r["home_team"])
            winner_code = str(r["predicted_winner"])
            winner_accent = get_team_accent_color(winner_code)

            prob_val = float(r["favorite_probability"])
            prob_percent = prob_val * 100  # e.g. 0.769376 -> 76.9%

            tier_label = str(r["confidence_label"])
            badge_cls = get_confidence_badge_class(tier_label)
            meter_color = get_confidence_bar_color(tier_label)

            kickoff_str = "—"
            if "weekday" in r and "gametime" in r and pd.notna(r["weekday"]) and pd.notna(r["gametime"]):
                kickoff_str = f"{str(r['weekday'])[:3]} {r['gametime']}"

            rows_html += f"""
            <tr>
                <td class="table-matchup">{away_code} @ {home_code}</td>
                <td class="table-kickoff">{kickoff_str}</td>
                <td>
                    <div class="table-pick-cell">
                        <span class="table-pick-pip" style="background-color: {winner_accent};"></span>
                        <span class="table-pick-team">{winner_code}</span>
                    </div>
                </td>
                <td>
                    <div class="table-prob-wrapper">
                        <span class="table-prob-text">{prob_percent:.1f}%</span>
                        <div class="table-prob-track">
                            <div class="table-prob-fill" style="width: {prob_percent:.1f}%; background-color: {meter_color};"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="badge {badge_cls}">{tier_label}</span>
                </td>
            </tr>
            """

        st.html(
            f"""
            <div class="full-week-table-container">
                <table class="full-week-table">
                    <thead>
                        <tr>
                            <th style="width: 22%;">Matchup</th>
                            <th style="width: 18%;">Kickoff</th>
                            <th style="width: 18%;">Model Pick</th>
                            <th style="width: 24%;">Win Probability</th>
                            <th style="width: 18%;">Confidence Rating</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
            """
        )

    # --------------------------------------------------
    # 5. Matchup Deep Dive
    # --------------------------------------------------

    st.html(
        """
        <div class="section-title" style="margin-top: 2rem;">Matchup Deep Dive</div>
        <div class="section-caption">Comprehensive head-to-head probability split, model feature advantages, and pregame context.</div>
        """
    )

    # Create descriptive matchup selection options with full team names
    matchup_labels = [
        f"{get_team_name(r['away_team'])} @ {get_team_name(r['home_team'])} ({r['away_team']} @ {r['home_team']})"
        for _, r in predictions.iterrows()
    ]

    selected_matchup_label = st.selectbox(
        "Select a matchup for deep-dive analysis",
        matchup_labels,
        label_visibility="collapsed",
    )

    selected_idx = matchup_labels.index(selected_matchup_label)
    selected_game = predictions.iloc[selected_idx]

    away_team = str(selected_game["away_team"])
    home_team = str(selected_game["home_team"])
    away_full_name = get_team_name(away_team)
    home_full_name = get_team_name(home_team)
    away_accent = get_team_accent_color(away_team)
    home_accent = get_team_accent_color(home_team)
    away_logo_html = get_team_logo_html(away_team, size=24)
    home_logo_html = get_team_logo_html(home_team, size=24)

    away_prob = float(selected_game["away_win_probability"])
    home_prob = float(selected_game["home_win_probability"])
    winner = str(selected_game["predicted_winner"])
    winner_full_name = get_team_name(winner)
    fav_prob = float(selected_game["favorite_probability"])
    conf_label = str(selected_game["confidence_label"])
    badge_class = get_confidence_badge_class(conf_label)

    is_away_winner = (winner == away_team)
    away_cell_class = "team-cell team-cell-winner" if is_away_winner else "team-cell"
    home_cell_class = "team-cell team-cell-winner" if not is_away_winner else "team-cell"

    away_role_class = "team-role team-role-winner" if is_away_winner else "team-role"
    home_role_class = "team-role team-role-winner" if not is_away_winner else "team-role"

    away_pick_tag = '<span style="color:#38bdf8; font-weight:700; font-size:0.75rem;"> &bull; MODEL PICK</span>' if is_away_winner else ""
    home_pick_tag = '<span style="color:#38bdf8; font-weight:700; font-size:0.75rem;"> &bull; MODEL PICK</span>' if not is_away_winner else ""

    away_pct = away_prob * 100
    home_pct = home_prob * 100

    # Color the split bar according to model pick and team accents
    away_bar_color = away_accent if is_away_winner else "#2c3b52"
    home_bar_color = home_accent if not is_away_winner else "#2c3b52"

    # --------------------------------------------------
    # 6. Model Edge / Why the Model Likes the Pick
    # --------------------------------------------------

    feature_specs = [
        ("point_diff_diff", "Recent Point Differential", lambda v: f"{v:+.1f} pts/gm"),
        ("win_pct_diff", "Recent Win Percentage", lambda v: f"{v:.1%}"),
        ("def_epa_advantage", "Defensive EPA", lambda v: f"{v:.3f} EPA/play"),
        ("off_success_rate_advantage", "Offensive Success Rate", lambda v: f"{v:.1%}"),
        ("def_success_rate_advantage", "Defensive Success Rate", lambda v: f"{v:.1%}"),
        ("off_ypp_advantage", "Offensive Yards per Play", lambda v: f"{v:+.2f} YPP"),
    ]

    has_features = all(col in selected_game for col, _, _ in feature_specs)

    edge_html = ""
    if has_features:
        edge_items_html = ""
        for col, label, fmt in feature_specs:
            val = float(selected_game[col])
            # Positive values indicate home-team advantage under feature definitions
            if val > 0:
                edge_abbr = home_team
                mag = val
            elif val < 0:
                edge_abbr = away_team
                mag = abs(val)
            else:
                edge_abbr = "Even"
                mag = 0.0

            edge_full = get_team_name(edge_abbr) if edge_abbr != "Even" else "Even"

            edge_items_html += f"""
            <div class="edge-item">
                <div class="edge-item-name">{label}</div>
                <div class="edge-item-row">
                    <span class="edge-item-team">Advantage {edge_full}</span>
                    <span class="edge-item-val">{fmt(mag)}</span>
                </div>
            </div>
            """

        edge_html = f"""
        <div class="edge-section">
            <div class="edge-header">
                <div class="edge-title">
                    <span>⚡ Model Edge &bull; Why the Model Likes {winner_full_name}</span>
                </div>
                <div class="edge-pill-badge">6 Validated Features</div>
            </div>
            <div class="edge-grid">
                {edge_items_html}
            </div>
            <div class="edge-footnote">
                Note: Evaluated across 8-game rolling windows. Positive raw values reflect home advantage under model conventions. These six metrics represent the complete feature space used by the logistic regression engine.
            </div>
        </div>
        """

    # --------------------------------------------------
    # Supplementary Game Context (Explicitly Not Used by Model)
    # --------------------------------------------------

    context_fields_exist = any(
        k in selected_game for k in ["away_qb_name", "home_qb_name", "spread_line", "total_line", "stadium", "gametime"]
    )

    context_html = ""
    if context_fields_exist:
        qb_info = "—"
        if "away_qb_name" in selected_game and "home_qb_name" in selected_game:
            if pd.notna(selected_game["away_qb_name"]) and pd.notna(selected_game["home_qb_name"]):
                qb_info = f"{selected_game['away_qb_name']} vs {selected_game['home_qb_name']}"

        spread_info = "—"
        if "spread_line" in selected_game and pd.notna(selected_game["spread_line"]):
            spread_info = f"{home_team} {selected_game['spread_line']:+.1f}"

        total_info = "—"
        if "total_line" in selected_game and pd.notna(selected_game["total_line"]):
            total_info = f"O/U {selected_game['total_line']:.1f}"

        venue_info = "—"
        if "stadium" in selected_game and pd.notna(selected_game["stadium"]):
            venue_info = str(selected_game["stadium"])

        time_info = "—"
        if "weekday" in selected_game and "gametime" in selected_game:
            if pd.notna(selected_game["weekday"]) and pd.notna(selected_game["gametime"]):
                time_info = f"{selected_game['weekday']} {selected_game['gametime']}"

        context_html = f"""
        <div class="context-box">
            <div class="context-header">
                <span class="context-badge">Game Context &bull; Not Used by Model</span>
                <span style="font-size:0.75rem; color:#64748b;">Market lines and quarterback listings are supplementary reference data only</span>
            </div>
            <div class="context-grid">
                <div class="context-chip">
                    <div class="context-chip-label">Starting QBs</div>
                    <div class="context-chip-val">{qb_info}</div>
                </div>
                <div class="context-chip">
                    <div class="context-chip-label">Market Spread</div>
                    <div class="context-chip-val">{spread_info}</div>
                </div>
                <div class="context-chip">
                    <div class="context-chip-label">Total Line</div>
                    <div class="context-chip-val">{total_info}</div>
                </div>
                <div class="context-chip">
                    <div class="context-chip-label">Venue</div>
                    <div class="context-chip-val">{venue_info}</div>
                </div>
                <div class="context-chip">
                    <div class="context-chip-label">Kickoff</div>
                    <div class="context-chip-val">{time_info}</div>
                </div>
            </div>
        </div>
        """

    # Render Matchup Board with Team Accents
    st.html(
        f"""
        <div class="matchup-board">
            <div class="matchup-teams-row">
                <div class="{away_cell_class}" style="border-left: 4px solid {away_accent};">
                    <div class="{away_role_class}">Away Team{away_pick_tag}</div>
                    <div class="team-header-identity">
                        {away_logo_html}
                        <span class="team-full-display-name">{away_full_name}</span>
                    </div>
                    <div class="team-code">{away_team}</div>
                    <div class="team-prob-large">{away_prob:.1%} Win Prob</div>
                </div>
                <div class="vs-separator">AT</div>
                <div class="{home_cell_class}" style="border-left: 4px solid {home_accent};">
                    <div class="{home_role_class}">Home Team{home_pick_tag}</div>
                    <div class="team-header-identity">
                        {home_logo_html}
                        <span class="team-full-display-name">{home_full_name}</span>
                    </div>
                    <div class="team-code">{home_team}</div>
                    <div class="team-prob-large">{home_prob:.1%} Win Prob</div>
                </div>
            </div>

            <div class="split-bar-wrapper">
                <div class="split-bar-labels">
                    <span>{away_full_name} ({away_team}) {away_pct:.1f}%</span>
                    <span>{home_full_name} ({home_team}) {home_pct:.1f}%</span>
                </div>
                <div class="split-bar-track">
                    <div class="split-bar-away" style="width: {away_pct:.1f}%; background-color: {away_bar_color};"></div>
                    <div class="split-bar-home" style="width: {home_pct:.1f}%; background-color: {home_bar_color};"></div>
                </div>
            </div>

            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem; margin-top:0.75rem;">
                <div>
                    <span style="color:#94a3b8; font-size:0.85rem; font-weight:600;">Model Projection: </span>
                    <strong style="color:#f8fafc; font-size:0.95rem;">{winner_full_name} ({winner})</strong>
                    <span style="color:#38bdf8; font-weight:700; font-size:0.95rem;">({fav_prob:.1%})</span>
                </div>
                <span class="badge {badge_class}">{conf_label}</span>
            </div>

            {edge_html}
            {context_html}
        </div>
        """
    )


# ==================================================
# TAB 2: MODEL PERFORMANCE & VALIDATION
# ==================================================

with tab_performance:

    st.html(
        """
        <div class="section-title" style="margin-top: 0.25rem;">Model Performance & Empirical Validation</div>
        <div class="section-caption">Walk-forward out-of-sample test results, historical calibration tiers, and architecture specifications.</div>
        """
    )

    # --------------------------------------------------
    # 7 & 8. Historical Validation & Calibration Tiers
    # --------------------------------------------------

    st.html(
        """
        <div class="perf-grid">
            <div class="perf-card">
                <div class="perf-card-title">
                    <span>📊 Walk-Forward Accuracy (2022–2025)</span>
                </div>
                <p style="font-size:0.82rem; color:#94a3b8; line-height:1.45; margin-bottom:0.75rem;">
                    Evaluated chronologically out-of-sample: trained solely on past seasons and tested on the upcoming unseen season without lookahead leakage.
                </p>
                <table class="perf-table">
                    <thead>
                        <tr>
                            <th>NFL Season</th>
                            <th>Validation Type</th>
                            <th style="text-align:right;">Win Accuracy</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>2022 Season</td>
                            <td>Walk-Forward Out-of-Sample</td>
                            <td style="text-align:right;" class="perf-stat-highlight">60.3%</td>
                        </tr>
                        <tr>
                            <td>2023 Season</td>
                            <td>Walk-Forward Out-of-Sample</td>
                            <td style="text-align:right;" class="perf-stat-highlight">62.5%</td>
                        </tr>
                        <tr>
                            <td>2024 Season</td>
                            <td>Walk-Forward Out-of-Sample</td>
                            <td style="text-align:right;" class="perf-stat-highlight">67.4%</td>
                        </tr>
                        <tr>
                            <td>2025 Season</td>
                            <td>Walk-Forward Out-of-Sample</td>
                            <td style="text-align:right;" class="perf-stat-highlight">63.4%</td>
                        </tr>
                        <tr>
                            <td>4-Year Average</td>
                            <td>Overall Out-of-Sample</td>
                            <td style="text-align:right;" class="perf-stat-highlight">~63.4%</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="perf-card">
                <div class="perf-card-title">
                    <span>🎯 Historical Confidence Calibration</span>
                </div>
                <p style="font-size:0.82rem; color:#94a3b8; line-height:1.45; margin-bottom:0.75rem;">
                    Empirical win rates stratified by model favorite probability thresholds across all historical walk-forward test slates:
                </p>
                <table class="perf-table">
                    <thead>
                        <tr>
                            <th>Confidence Tier</th>
                            <th>Sample Size</th>
                            <th style="text-align:right;">Empirical Win Rate</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>65%+ Model Picks</td>
                            <td>467 games tested</td>
                            <td style="text-align:right;" class="perf-stat-highlight">70.4%</td>
                        </tr>
                        <tr>
                            <td>70%+ Model Picks</td>
                            <td>286 games tested</td>
                            <td style="text-align:right;" class="perf-stat-highlight">70.6%</td>
                        </tr>
                        <tr>
                            <td>75%+ Model Picks</td>
                            <td>173 games tested</td>
                            <td style="text-align:right;" class="perf-stat-highlight">72.8%</td>
                        </tr>
                        <tr>
                            <td>80%+ Model Picks</td>
                            <td>68 games tested</td>
                            <td style="text-align:right;" class="perf-stat-highlight">88.2%</td>
                        </tr>
                    </tbody>
                </table>
                <p style="font-size:0.74rem; color:#64748b; line-height:1.4; margin-top:0.75rem;">
                    <em>Interview Note:</em> Historically, predictions rated 75%+ won 72.8% of 173 walk-forward-tested games. Model probabilities represent logistic regression point estimates, whereas tier performance reflects empirical historical hit rates across test cohorts. Model probability and historical tier performance remain conceptually distinct.
                </p>
            </div>
        </div>
        """
    )

    # --------------------------------------------------
    # 9. Model Methodology
    # --------------------------------------------------

    with st.expander("Model Architecture, Features & Feature Parity Protocol", expanded=True):
        st.html(
            """
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap:1.25rem;">
                <div style="background-color:#080c18; border:1px solid #1e2c47; border-radius:10px; padding:1.15rem;">
                    <div style="color:#38bdf8; font-weight:700; font-size:0.88rem; text-transform:uppercase; margin-bottom:0.5rem;">
                        1. Algorithm Specification
                    </div>
                    <div style="font-size:0.84rem; color:#cbd5e1; line-height:1.55;">
                        <ul>
                            <li><strong>Model:</strong> L2-regularized Logistic Regression calibrated on binary game outcomes.</li>
                            <li><strong>Feature Scaling:</strong> <code>StandardScaler</code> fit on pregame differential feature metrics.</li>
                            <li><strong>Rolling Window:</strong> 8-game rolling sample window to balance sample size with in-season team efficiency trajectory.</li>
                            <li><strong>Inference:</strong> Produces calibrated win probabilities without ad-hoc manual overrides.</li>
                        </ul>
                    </div>
                </div>

                <div style="background-color:#080c18; border:1px solid #1e2c47; border-radius:10px; padding:1.15rem;">
                    <div style="color:#38bdf8; font-weight:700; font-size:0.88rem; text-transform:uppercase; margin-bottom:0.5rem;">
                        2. Six Validated Matchup Features
                    </div>
                    <div style="font-size:0.84rem; color:#cbd5e1; line-height:1.55;">
                        <ol style="margin:0; padding-left:1.2rem;">
                            <li><strong>Point Differential Advantage:</strong> Rolling net scoring margin per snap.</li>
                            <li><strong>Win Percentage Advantage:</strong> Overall straight-up winning ratio differential.</li>
                            <li><strong>Defensive EPA Advantage:</strong> Expected Points Added allowed efficiency per play.</li>
                            <li><strong>Offensive Success Rate Advantage:</strong> Proportion of plays yielding positive EPA.</li>
                            <li><strong>Defensive Success Rate Advantage:</strong> Opponent offensive success rate prevented.</li>
                            <li><strong>Offensive Yards per Play Advantage:</strong> Explosiveness and snap efficiency.</li>
                        </ol>
                    </div>
                </div>

                <div style="background-color:#080c18; border:1px solid #1e2c47; border-radius:10px; padding:1.15rem;">
                    <div style="color:#38bdf8; font-weight:700; font-size:0.88rem; text-transform:uppercase; margin-bottom:0.5rem;">
                        3. Strict Input & Parity Guarantees
                    </div>
                    <div style="font-size:0.84rem; color:#cbd5e1; line-height:1.55;">
                        <p style="margin-bottom:0.4rem;">
                            <strong>Data Leakage Prevention:</strong> Chronological expanding-window walk-forward testing prevents temporal lookahead bias.
                        </p>
                        <p style="margin-bottom:0.4rem;">
                            <strong>Parity Verification:</strong> Live inference feature calculations were tested for exact mathematical parity against historical training definitions prior to deployment.
                        </p>
                        <p style="margin:0; color:#94a3b8;">
                            <strong>No Market Leakage:</strong> Betting-market spreads, moneyline odds, totals, and quarterback identities are strictly excluded from model features.
                        </p>
                    </div>
                </div>
            </div>
            """
        )


# --------------------------------------------------
# 12. Disclaimer Footer
# --------------------------------------------------

st.html(
    """
    <div class="disclaimer-card">
        <strong>Model Disclaimer:</strong> Model probabilities are statistical estimates based on historical NFL performance and are not guaranteed outcomes. This is an independent machine-learning analytics project developed for empirical modeling and portfolio demonstration. Not intended as financial or wagering advice.
    </div>
    """
)
