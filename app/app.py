from pathlib import Path

import pandas as pd
import streamlit as st


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PREDICTIONS_FILE = (
    PROJECT_ROOT
    / "data"
    / "latest_predictions.csv"
)


st.set_page_config(
    page_title="NFL Game Predictions",
    page_icon="🏈",
    layout="wide",
)


# --------------------------------------------------
# Styling
# --------------------------------------------------

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .hero {
        padding: 2rem 2.25rem;
        border-radius: 18px;
        background:
            linear-gradient(
                135deg,
                #101827 0%,
                #172554 100%
            );
        margin-bottom: 1.5rem;
        color: white;
    }

    .hero-kicker {
        color: #93c5fd;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .hero-title {
        margin-top: 0.25rem;
        margin-bottom: 0.25rem;
        font-size: 2.6rem;
        font-weight: 800;
    }

    .hero-subtitle {
        color: #cbd5e1;
        font-size: 1rem;
    }

    .prediction-card {
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 16px;
        padding: 1.25rem;
        height: 100%;
        background-color: rgba(30, 41, 59, 0.35);
    }

    .matchup {
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 600;
    }

    .pick {
        font-size: 2rem;
        font-weight: 800;
        margin-top: 0.3rem;
    }

    .probability {
        color: #60a5fa;
        font-size: 1.5rem;
        font-weight: 700;
    }

    .badge {
        display: inline-block;
        margin-top: 0.65rem;
        padding: 0.3rem 0.65rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
    }

    .highest {
        background-color: rgba(34, 197, 94, 0.20);
        color: #4ade80;
    }

    .high {
        background-color: rgba(59, 130, 246, 0.20);
        color: #60a5fa;
    }

    .strong {
        background-color: rgba(234, 179, 8, 0.20);
        color: #facc15;
    }

    .lean {
        background-color: rgba(148, 163, 184, 0.18);
        color: #cbd5e1;
    }

    .tossup {
        background-color: rgba(100, 116, 139, 0.18);
        color: #94a3b8;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Helpers
# --------------------------------------------------

@st.cache_data
def load_predictions():
    if not PREDICTIONS_FILE.exists():
        return pd.DataFrame()

    return pd.read_csv(PREDICTIONS_FILE)


def badge_class(label):
    mapping = {
        "Highest Confidence": "highest",
        "High Confidence": "high",
        "Strong Lean": "strong",
        "Lean": "lean",
        "Toss-up": "tossup",
    }

    return mapping.get(label, "tossup")


# --------------------------------------------------
# Load predictions
# --------------------------------------------------

predictions = load_predictions()


if predictions.empty:
    st.warning(
        "No saved predictions were found. "
        "Run `python -m src.run_predictions` "
        "to generate the latest picks."
    )

    st.stop()


predictions = predictions.sort_values(
    "favorite_probability",
    ascending=False,
).reset_index(drop=True)


season = int(predictions["season"].iloc[0])
week = int(predictions["week"].iloc[0])


updated_text = "Unknown"

if "predictions_updated" in predictions.columns:
    updated = pd.to_datetime(
        predictions["predictions_updated"].iloc[0]
    )

    updated_text = (
        f"{updated:%b %d, %Y · %I:%M %p}"
    )


# --------------------------------------------------
# Hero
# --------------------------------------------------

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-kicker">
            Machine Learning · Weekly Forecast
        </div>

        <div class="hero-title">
            🏈 NFL Game Predictions
        </div>

        <div class="hero-subtitle">
            {season} Week {week}
            &nbsp;·&nbsp;
            Updated {updated_text}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# KPI strip
# --------------------------------------------------

games_count = len(predictions)

picks_75 = int(
    (
        predictions["favorite_probability"]
        >= 0.75
    ).sum()
)

top_confidence = (
    predictions["favorite_probability"].max()
)


kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric(
    "Games",
    games_count,
)

kpi2.metric(
    "75%+ Picks",
    picks_75,
)

kpi3.metric(
    "Top Confidence",
    f"{top_confidence:.1%}",
)

kpi4.metric(
    "Historical Accuracy",
    "63.4%",
)


# --------------------------------------------------
# Featured picks
# --------------------------------------------------

st.subheader("Featured Picks")

st.caption(
    "The model's three highest-confidence "
    "predictions for the upcoming week."
)


featured = predictions.head(3)

featured_columns = st.columns(3)


for column, (_, game) in zip(
    featured_columns,
    featured.iterrows(),
):

    label = game["confidence_label"]

    css_class = badge_class(label)

    matchup = (
        f'{game["away_team"]} @ '
        f'{game["home_team"]}'
    )

    winner = game["predicted_winner"]

    probability = game[
        "favorite_probability"
    ]

    with column:
        st.markdown(
            f"""
            <div class="prediction-card">

                <div class="matchup">
                    {matchup}
                </div>

                <div class="pick">
                    {winner}
                </div>

                <div class="probability">
                    {probability:.1%}
                </div>

                <span class="badge {css_class}">
                    {label}
                </span>

            </div>
            """,
            unsafe_allow_html=True,
        )


# --------------------------------------------------
# Full week
# --------------------------------------------------

st.subheader("Full Week")

filter_options = [
    "All Picks",
    "Highest Confidence",
    "High Confidence",
    "Strong Lean",
    "Lean",
    "Toss-up",
]


selected_filter = st.selectbox(
    "Confidence filter",
    filter_options,
)


if selected_filter == "All Picks":
    filtered = predictions.copy()

else:
    filtered = predictions[
        predictions["confidence_label"]
        == selected_filter
    ].copy()


if filtered.empty:
    st.info(
        "No games match this confidence level."
    )

else:

    table = filtered[
        [
            "away_team",
            "home_team",
            "predicted_winner",
            "favorite_probability",
            "confidence_label",
        ]
    ].copy()

    table["Matchup"] = (
        table["away_team"]
        + " @ "
        + table["home_team"]
    )

    table["Confidence"] = (
        table["favorite_probability"]
        .map(lambda x: f"{x:.1%}")
    )

    table = table.rename(
        columns={
            "predicted_winner": "Model Pick",
            "confidence_label": "Rating",
        }
    )

    table = table[
        [
            "Matchup",
            "Model Pick",
            "Confidence",
            "Rating",
        ]
    ]

    st.dataframe(
        table,
        hide_index=True,
        use_container_width=True,
    )


# --------------------------------------------------
# Matchup details
# --------------------------------------------------

st.subheader("Game Details")


game_options = (
    predictions["away_team"]
    + " @ "
    + predictions["home_team"]
).tolist()


selected_game = st.selectbox(
    "Select a matchup",
    game_options,
)


selected = predictions[
    (
        predictions["away_team"]
        + " @ "
        + predictions["home_team"]
    )
    == selected_game
].iloc[0]


away_team = selected["away_team"]
home_team = selected["home_team"]

away_probability = selected[
    "away_win_probability"
]

home_probability = selected[
    "home_win_probability"
]


away_col, center_col, home_col = (
    st.columns([2, 1, 2])
)


away_col.metric(
    away_team,
    f"{away_probability:.1%}",
)


center_col.markdown(
    "<div style='text-align:center;"
    "padding-top:18px;'>"
    "<strong>AT</strong>"
    "</div>",
    unsafe_allow_html=True,
)


home_col.metric(
    home_team,
    f"{home_probability:.1%}",
)


st.progress(
    float(home_probability),
    text=(
        f"{home_team} win probability: "
        f"{home_probability:.1%}"
    ),
)


st.write(
    "**Model Pick:** "
    f"{selected['predicted_winner']} · "
    f"{selected['favorite_probability']:.1%} · "
    f"{selected['confidence_label']}"
)


# --------------------------------------------------
# Methodology
# --------------------------------------------------

with st.expander(
    "Model & Validation"
):

    st.markdown(
        """
### Model

The prediction engine uses **Logistic Regression**
with standardized features and an **8-game rolling
window**.

### Features

The final model uses six pregame matchup features:

1. Point-differential advantage
2. Win-percentage advantage
3. Defensive EPA advantage
4. Offensive success-rate advantage
5. Defensive success-rate advantage
6. Offensive yards-per-play advantage

### Validation

The model was evaluated using **walk-forward
validation** rather than a random train/test split.

Historical test accuracy:

- **2022:** 60.3%
- **2023:** 62.5%
- **2024:** 67.4%
- **2025:** 63.4%

Average walk-forward accuracy was approximately
**63.4%**.

Live and historical feature calculations were also
tested for exact parity before deployment.
"""
    )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.markdown("---")

st.caption(
    "Model probabilities are estimates based on "
    "historical NFL performance and are not "
    "guaranteed outcomes."
)