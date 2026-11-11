import sys
from pathlib import Path

import streamlit as st


# Allow the app to import from the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.run_predictions import run_predictions


st.set_page_config(
    page_title="NFL Game Predictions",
    page_icon="🏈",
    layout="wide",
)


@st.cache_data(ttl=3600)
def load_predictions():
    """
    Generate predictions and cache them for one hour.
    """
    return run_predictions()


st.title("🏈 NFL Game Predictions")

st.caption(
    "Win probabilities generated from an 8-game "
    "Logistic Regression model."
)


with st.spinner("Loading NFL data and generating predictions..."):
    predictions = load_predictions()


if predictions.empty:
    st.warning("No upcoming NFL games were found.")
    st.stop()


season = int(predictions["season"].iloc[0])
week = int(predictions["week"].iloc[0])


st.subheader(
    f"{season} Week {week}"
)


# ---------------------------------
# Confidence filter
# ---------------------------------

confidence_options = [
    "All Picks",
    "Highest Confidence",
    "High Confidence",
    "Strong Lean",
    "Lean",
    "Toss-up",
]

selected_confidence = st.selectbox(
    "Filter by confidence",
    confidence_options,
)


if selected_confidence == "All Picks":
    display_predictions = predictions.copy()

else:
    display_predictions = predictions[
        predictions["confidence_label"]
        == selected_confidence
    ].copy()


# ---------------------------------
# Summary metrics
# ---------------------------------

col1, col2, col3 = st.columns(3)

col1.metric(
    "Games",
    len(display_predictions),
)

high_confidence_count = (
    display_predictions["favorite_probability"]
    >= 0.75
).sum()

col2.metric(
    "75%+ Picks",
    int(high_confidence_count),
)

top_probability = (
    display_predictions["favorite_probability"].max()
    if not display_predictions.empty
    else 0
)

col3.metric(
    "Top Confidence",
    f"{top_probability:.1%}",
)


# ---------------------------------
# Prediction cards
# ---------------------------------

if display_predictions.empty:

    st.info(
        "No games match the selected confidence level."
    )

else:

    for _, game in display_predictions.iterrows():

        away_team = game["away_team"]
        home_team = game["home_team"]

        away_probability = game[
            "away_win_probability"
        ]

        home_probability = game[
            "home_win_probability"
        ]

        predicted_winner = game[
            "predicted_winner"
        ]

        favorite_probability = game[
            "favorite_probability"
        ]

        confidence = game[
            "confidence_label"
        ]

        st.markdown("---")

        st.subheader(
            f"{away_team} @ {home_team}"
        )

        left, middle, right = st.columns(
            [2, 2, 2]
        )

        left.metric(
            away_team,
            f"{away_probability:.1%}",
        )

        middle.metric(
            "Model Pick",
            predicted_winner,
        )

        right.metric(
            home_team,
            f"{home_probability:.1%}",
        )

        st.write(
            f"**{confidence}** · "
            f"{favorite_probability:.1%} model confidence"
        )


st.markdown("---")

st.caption(
    "Probabilities are model estimates, not guaranteed outcomes. "
    "The core model achieved approximately 63% average "
    "walk-forward accuracy during historical testing."
)