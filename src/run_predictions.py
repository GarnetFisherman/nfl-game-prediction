from src.data import (
    load_games,
    prepare_completed_games,
    build_team_games,
    load_play_by_play,
    build_team_epa,
    build_team_success,
    build_team_ypp,
)

from src.build_dataset import build_training_dataset

from src.predict import (
    get_upcoming_games,
    get_next_week,
    build_current_team_state,
    build_upcoming_features,
)

from src.model import (
    train_model,
    add_predictions,
)

def run_predictions():

    # -------------------------
    # Load schedules
    # -------------------------

    games = load_games()

    current_season = int(
        games["season"].max()
    )

    seasons = list(
        range(2021, current_season + 1)
    )

    completed_games = prepare_completed_games(games)

    upcoming_games = get_upcoming_games(games)

    next_week = get_next_week(upcoming_games)

    # -------------------------
    # Historical team data
    # -------------------------

    team_games = build_team_games(completed_games)

    pbp = load_play_by_play(seasons)

    team_epa = build_team_epa(pbp)
    team_success = build_team_success(pbp)
    team_ypp = build_team_ypp(pbp)

    # -------------------------
    # Training dataset
    # -------------------------

    training_data = build_training_dataset(
        seasons,
        window=8,
    )

    model = train_model(training_data)

    # -------------------------
    # Current team state
    # -------------------------

    team_state = build_current_team_state(
        team_games=team_games,
        team_epa=team_epa,
        team_success=team_success,
        team_ypp=team_ypp,
        window=8,
    )

    # -------------------------
    # Upcoming-game features
    # -------------------------

    prediction_data = build_upcoming_features(
        upcoming_games=next_week,
        team_state=team_state,
    )

    # -------------------------
    # Predictions
    # -------------------------

    predictions = add_predictions(
        model=model,
        model_data=prediction_data,
    )

    predictions = predictions.sort_values(
        "favorite_probability",
        ascending=False,
    )

    return predictions


if __name__ == "__main__":

    predictions = run_predictions()

    columns = [
        "season",
        "week",
        "gameday",
        "away_team",
        "home_team",
        "away_win_probability",
        "home_win_probability",
        "predicted_winner",
        "favorite_probability",
        "confidence_label",
    ]

    print(
        predictions[columns].to_string(
            index=False
        )
    )