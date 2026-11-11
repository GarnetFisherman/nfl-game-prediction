from src.data import (
    load_games,
    prepare_completed_games,
    build_team_games,
    load_play_by_play,
    build_team_epa,
    build_team_success,
    build_team_ypp,
)

from src.features import (
    MODEL_FEATURES,
    build_model_features,
)


def build_training_dataset(
    pbp_seasons: list[int],
    window: int = 8,
):
    """
    Build the complete model-ready NFL training dataset.
    """

    # -------------------------
    # Schedule / game data
    # -------------------------

    games = load_games()

    completed_games = prepare_completed_games(
        games
    )

    team_games = build_team_games(
        completed_games
    )

    # -------------------------
    # Play-by-play data
    # -------------------------

    pbp = load_play_by_play(
        pbp_seasons
    )

    team_epa = build_team_epa(pbp)

    team_success = build_team_success(pbp)

    team_ypp = build_team_ypp(pbp)

    # -------------------------
    # Build matchup features
    # -------------------------

    model_data = build_model_features(
        games=completed_games,
        team_games=team_games,
        team_epa=team_epa,
        team_success=team_success,
        team_ypp=team_ypp,
        window=window,
    )

    # Only retain games where every
    # final model feature is available.
    model_ready = model_data.dropna(
        subset=MODEL_FEATURES
    ).copy()

    return model_ready