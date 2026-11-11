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

from src.features import MODEL_FEATURES

from src.predict import (
    build_current_team_state,
    build_upcoming_features,
)


def validate_feature_parity(
    test_season: int = 2025,
    test_week: int = 10,
):
    """
    Compare historical training features with features generated
    by the live prediction logic at the same point in time.

    The historical game is treated as though it has not happened yet.
    """

    seasons = list(
        range(2021, test_season + 1)
    )

    # --------------------------------------------------
    # Historical reference implementation
    # --------------------------------------------------

    historical = build_training_dataset(
        seasons,
        window=8,
    )

    reference = historical[
        (historical["season"] == test_season)
        & (historical["week"] == test_week)
    ].copy()

    # --------------------------------------------------
    # Load full schedule
    # --------------------------------------------------

    games = load_games()

    # --------------------------------------------------
    # Team-result history
    #
    # This matches the training pipeline:
    # - completed games only
    # - ties removed
    # - home_win / team_win available
    # --------------------------------------------------

    completed = prepare_completed_games(
        games
    )

    prior_games = completed[
        (
            completed["season"] < test_season
        )
        |
        (
            (completed["season"] == test_season)
            & (completed["week"] < test_week)
        )
    ].copy()

    # These are the games we pretend are upcoming.
    target_games = completed[
        (completed["season"] == test_season)
        & (completed["week"] == test_week)
    ].copy()

    team_games = build_team_games(
        prior_games
    )

    # --------------------------------------------------
    # PBP history
    #
    # IMPORTANT:
    # The historical PBP feature pipeline includes all
    # completed games with scores, including tied games.
    #
    # Therefore this must NOT use prepare_completed_games(),
    # because that function removes ties.
    # --------------------------------------------------

    all_completed_games = games[
        games["home_score"].notna()
        & games["away_score"].notna()
    ].copy()

    all_completed_prior = all_completed_games[
        (
            all_completed_games["season"] < test_season
        )
        |
        (
            (all_completed_games["season"] == test_season)
            & (all_completed_games["week"] < test_week)
        )
    ].copy()

    pbp = load_play_by_play(
        seasons
    )

    prior_game_ids = set(
        all_completed_prior["game_id"]
    )

    pbp_prior = pbp[
        pbp["game_id"].isin(
            prior_game_ids
        )
    ].copy()

    # --------------------------------------------------
    # Build historical PBP team metrics
    # --------------------------------------------------

    team_epa = build_team_epa(
        pbp_prior
    )

    team_success = build_team_success(
        pbp_prior
    )

    team_ypp = build_team_ypp(
        pbp_prior
    )

    # --------------------------------------------------
    # Recreate live team state as it would have existed
    # immediately before the historical test week
    # --------------------------------------------------

    team_state = build_current_team_state(
        team_games=team_games,
        team_epa=team_epa,
        team_success=team_success,
        team_ypp=team_ypp,
        window=8,
    )

    # --------------------------------------------------
    # Treat historical Week 10 as an upcoming schedule
    # --------------------------------------------------

    live_style = build_upcoming_features(
        upcoming_games=target_games,
        team_state=team_state,
    )

    # --------------------------------------------------
    # Compare historical vs live implementations
    # --------------------------------------------------

    reference_compare = reference[
        ["game_id"] + MODEL_FEATURES
    ].copy()

    live_compare = live_style[
        ["game_id"] + MODEL_FEATURES
    ].copy()

    comparison = reference_compare.merge(
        live_compare,
        on="game_id",
        suffixes=(
            "_historical",
            "_live",
        ),
        how="inner",
    )

    for feature in MODEL_FEATURES:

        comparison[
            f"{feature}_difference"
        ] = (
            comparison[
                f"{feature}_historical"
            ]
            - comparison[
                f"{feature}_live"
            ]
        )

    return comparison


if __name__ == "__main__":

    comparison = validate_feature_parity(
        test_season=2025,
        test_week=10,
    )

    print(
        "Games compared:",
        len(comparison),
    )

    print(
        "\nMaximum absolute differences:"
    )

    all_match = True

    for feature in MODEL_FEATURES:

        difference = comparison[
            f"{feature}_difference"
        ].abs().max()

        print(
            f"{feature}: "
            f"{difference:.12f}"
        )

        if difference > 1e-10:
            all_match = False

    if all_match:
        print(
            "\nPASS: Historical and live features match."
        )
    else:
        print(
            "\nFAIL: Historical and live features differ."
        )