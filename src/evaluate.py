import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    log_loss,
)

from src.features import MODEL_FEATURES
from src.model import create_model


def evaluate_season(
    model_data: pd.DataFrame,
    test_season: int,
) -> dict:
    """
    Train on seasons before test_season and evaluate
    on the specified test season.
    """

    train = model_data[
        model_data["season"] < test_season
    ].dropna(
        subset=MODEL_FEATURES + ["home_win"]
    ).copy()

    test = model_data[
        model_data["season"] == test_season
    ].dropna(
        subset=MODEL_FEATURES + ["home_win"]
    ).copy()

    X_train = train[MODEL_FEATURES]
    y_train = train["home_win"]

    X_test = test[MODEL_FEATURES]
    y_test = test["home_win"]

    model = create_model()
    model.fit(X_train, y_train)

    probabilities = model.predict_proba(X_test)[:, 1]

    predictions = (
        probabilities >= 0.5
    ).astype(int)

    return {
        "test_season": test_season,
        "training_games": len(train),
        "test_games": len(test),
        "accuracy": accuracy_score(
            y_test,
            predictions,
        ),
        "log_loss": log_loss(
            y_test,
            probabilities,
        ),
        "brier_score": brier_score_loss(
            y_test,
            probabilities,
        ),
    }

def evaluate_walk_forward(
    model_data: pd.DataFrame,
    test_seasons: list[int],
) -> pd.DataFrame:
    """
    Run chronological walk-forward evaluation across
    multiple NFL seasons.
    """

    results = []

    for test_season in test_seasons:

        result = evaluate_season(
            model_data=model_data,
            test_season=test_season,
        )

        results.append(result)

    return pd.DataFrame(results)

def evaluate_walk_forward(
    model_data: pd.DataFrame,
    test_seasons: list[int],
) -> pd.DataFrame:
    """
    Run chronological walk-forward evaluation across
    multiple test seasons.
    """

    results = []

    for test_season in test_seasons:
        result = evaluate_season(
            model_data=model_data,
            test_season=test_season,
        )

        results.append(result)

    return pd.DataFrame(results)