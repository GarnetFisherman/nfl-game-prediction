import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.features import MODEL_FEATURES


def create_model() -> Pipeline:
    """
    Create the NFL win-probability model.
    """

    model = Pipeline([
        (
            "scaler",
            StandardScaler()
        ),
        (
            "model",
            LogisticRegression(
                max_iter=1000
            )
        ),
    ])

    return model


def train_model(
    model_data: pd.DataFrame
) -> Pipeline:
    """
    Train the NFL model using completed historical games.
    """

    training_data = model_data.dropna(
        subset=MODEL_FEATURES + ["home_win"]
    ).copy()

    X = training_data[MODEL_FEATURES]
    y = training_data["home_win"]

    model = create_model()

    model.fit(X, y)

    return model


def confidence_label(probability: float) -> str:
    """
    Convert favorite win probability into a user-facing
    confidence category.
    """

    if probability >= 0.80:
        return "Highest Confidence"
    elif probability >= 0.75:
        return "High Confidence"
    elif probability >= 0.65:
        return "Strong Lean"
    elif probability >= 0.60:
        return "Lean"
    else:
        return "Toss-up"


def add_predictions(
    model: Pipeline,
    model_data: pd.DataFrame
) -> pd.DataFrame:
    """
    Add home/away win probabilities and predicted winner.
    """

    result = model_data.copy()

    usable = result[MODEL_FEATURES].notna().all(axis=1)

    result["home_win_probability"] = float("nan")
    result["away_win_probability"] = float("nan")
    result["predicted_winner"] = pd.NA

    home_probs = model.predict_proba(
        result.loc[usable, MODEL_FEATURES]
    )[:, 1]

    result.loc[
        usable,
        "home_win_probability"
    ] = home_probs

    result.loc[
        usable,
        "away_win_probability"
    ] = 1 - home_probs

    result.loc[
        usable,
        "predicted_winner"
    ] = result.loc[usable].apply(
        lambda row:
            row["home_team"]
            if row["home_win_probability"] >= 0.5
            else row["away_team"],
        axis=1
    )

    result["favorite_probability"] = result[
        [
            "home_win_probability",
            "away_win_probability"
        ]
    ].max(axis=1)

    result["confidence_label"] = (
        result["favorite_probability"]
        .apply(confidence_label)
    )

    return result