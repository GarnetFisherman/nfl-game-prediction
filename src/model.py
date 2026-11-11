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
