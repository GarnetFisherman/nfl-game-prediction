import pandas as pd

MODEL_FEATURES = [
    "point_diff_diff",
    "win_pct_diff",
    "def_epa_advantage",
    "off_success_rate_advantage",
    "def_success_rate_advantage",
    "off_ypp_advantage",
]


def add_rolling_team_features(
    team_games: pd.DataFrame,
    window: int = 8
) -> pd.DataFrame:
    """
    Create leakage-safe rolling team performance features.

    Each feature uses games completed before the current game.
    """

    df = team_games.copy()

    df = df.sort_values(
        ["team", "season", "week"]
    ).reset_index(drop=True)

    df[f"avg_points_scored_last{window}"] = (
        df.groupby("team")["points_scored"]
        .transform(
            lambda x: x.shift(1).rolling(window).mean()
        )
    )

    df[f"avg_points_allowed_last{window}"] = (
        df.groupby("team")["points_allowed"]
        .transform(
            lambda x: x.shift(1).rolling(window).mean()
        )
    )

    df[f"avg_point_diff_last{window}"] = (
        df[f"avg_points_scored_last{window}"]
        - df[f"avg_points_allowed_last{window}"]
    )

    df[f"win_pct_last{window}"] = (
        df.groupby("team")["team_win"]
        .transform(
            lambda x: x.shift(1).rolling(window).mean()
        )
    )

    return df

def add_rolling_epa_features(
    team_epa: pd.DataFrame,
    window: int = 8
) -> pd.DataFrame:
    """
    Create leakage-safe rolling offensive and defensive EPA features.

    Each feature uses games completed before the current game.
    """

    df = team_epa.copy()

    df = df.sort_values(
        ["team", "season", "week"]
    ).reset_index(drop=True)

    df[f"off_epa_last{window}"] = (
        df.groupby("team")["off_epa_per_play"]
        .transform(
            lambda x: x.shift(1).rolling(window).mean()
        )
    )

    df[f"def_epa_last{window}"] = (
        df.groupby("team")["def_epa_per_play"]
        .transform(
            lambda x: x.shift(1).rolling(window).mean()
        )
    )

    return df

def add_rolling_success_features(
    team_success: pd.DataFrame,
    window: int = 8
) -> pd.DataFrame:
    """
    Create leakage-safe rolling offensive and defensive success-rate features.

    Each feature uses games completed before the current game.
    """

    df = team_success.copy()

    df = df.sort_values(
        ["team", "season", "week"]
    ).reset_index(drop=True)

    df[f"off_success_rate_last{window}"] = (
        df.groupby("team")["off_success_rate"]
        .transform(
            lambda x: x.shift(1).rolling(window).mean()
        )
    )

    df[f"def_success_rate_allowed_last{window}"] = (
        df.groupby("team")["def_success_rate_allowed"]
        .transform(
            lambda x: x.shift(1).rolling(window).mean()
        )
    )

    return df

def add_rolling_ypp_features(
    team_ypp: pd.DataFrame,
    window: int = 8
) -> pd.DataFrame:
    """
    Create leakage-safe rolling offensive and defensive yards-per-play features.

    Each feature uses games completed before the current game.
    """

    df = team_ypp.copy()

    df = df.sort_values(
        ["team", "season", "week"]
    ).reset_index(drop=True)

    df[f"off_ypp_last{window}"] = (
        df.groupby("team")["off_ypp"]
        .transform(
            lambda x: x.shift(1).rolling(window).mean()
        )
    )

    df[f"def_ypp_allowed_last{window}"] = (
        df.groupby("team")["def_ypp_allowed"]
        .transform(
            lambda x: x.shift(1).rolling(window).mean()
        )
    )

    return df

def build_model_features(
    games: pd.DataFrame,
    team_games: pd.DataFrame,
    team_epa: pd.DataFrame,
    team_success: pd.DataFrame,
    team_ypp: pd.DataFrame,
    window: int = 8,
) -> pd.DataFrame:
    """
    Build the matchup-level features used by the NFL prediction model.

    Positive feature values consistently represent an advantage
    for the home team.
    """

    # ---------------------------------
    # Team results / recent form
    # ---------------------------------

    team_stats = add_rolling_team_features(
        team_games,
        window=window,
    )

    home_stats = team_stats[
        team_stats["is_home"] == 1
    ][
        [
            "game_id",
            f"avg_point_diff_last{window}",
            f"win_pct_last{window}",
        ]
    ].copy()

    home_stats = home_stats.rename(
        columns={
            f"avg_point_diff_last{window}":
                "home_avg_point_diff",
            f"win_pct_last{window}":
                "home_win_pct",
        }
    )

    away_stats = team_stats[
        team_stats["is_home"] == 0
    ][
        [
            "game_id",
            f"avg_point_diff_last{window}",
            f"win_pct_last{window}",
        ]
    ].copy()

    away_stats = away_stats.rename(
        columns={
            f"avg_point_diff_last{window}":
                "away_avg_point_diff",
            f"win_pct_last{window}":
                "away_win_pct",
        }
    )

    # ---------------------------------
    # EPA
    # ---------------------------------

    epa = add_rolling_epa_features(
        team_epa,
        window=window,
    )

    home_epa = epa[
        [
            "game_id",
            "team",
            f"def_epa_last{window}",
        ]
    ].merge(
        games[
            ["game_id", "home_team"]
        ],
        on="game_id",
        how="inner",
    )

    home_epa = home_epa[
        home_epa["team"] == home_epa["home_team"]
    ][
        [
            "game_id",
            f"def_epa_last{window}",
        ]
    ].rename(
        columns={
            f"def_epa_last{window}":
                "home_def_epa"
        }
    )

    away_epa = epa[
        [
            "game_id",
            "team",
            f"def_epa_last{window}",
        ]
    ].merge(
        games[
            ["game_id", "away_team"]
        ],
        on="game_id",
        how="inner",
    )

    away_epa = away_epa[
        away_epa["team"] == away_epa["away_team"]
    ][
        [
            "game_id",
            f"def_epa_last{window}",
        ]
    ].rename(
        columns={
            f"def_epa_last{window}":
                "away_def_epa"
        }
    )

    # ---------------------------------
    # Success rate
    # ---------------------------------

    success = add_rolling_success_features(
        team_success,
        window=window,
    )

    home_success = success[
        [
            "game_id",
            "team",
            f"off_success_rate_last{window}",
            f"def_success_rate_allowed_last{window}",
        ]
    ].merge(
        games[
            ["game_id", "home_team"]
        ],
        on="game_id",
        how="inner",
    )

    home_success = home_success[
        home_success["team"] == home_success["home_team"]
    ][
        [
            "game_id",
            f"off_success_rate_last{window}",
            f"def_success_rate_allowed_last{window}",
        ]
    ].rename(
        columns={
            f"off_success_rate_last{window}":
                "home_off_success_rate",
            f"def_success_rate_allowed_last{window}":
                "home_def_success_rate_allowed",
        }
    )

    away_success = success[
        [
            "game_id",
            "team",
            f"off_success_rate_last{window}",
            f"def_success_rate_allowed_last{window}",
        ]
    ].merge(
        games[
            ["game_id", "away_team"]
        ],
        on="game_id",
        how="inner",
    )

    away_success = away_success[
        away_success["team"] == away_success["away_team"]
    ][
        [
            "game_id",
            f"off_success_rate_last{window}",
            f"def_success_rate_allowed_last{window}",
        ]
    ].rename(
        columns={
            f"off_success_rate_last{window}":
                "away_off_success_rate",
            f"def_success_rate_allowed_last{window}":
                "away_def_success_rate_allowed",
        }
    )

    # ---------------------------------
    # Yards per play
    # ---------------------------------

    ypp = add_rolling_ypp_features(
        team_ypp,
        window=window,
    )

    home_ypp = ypp[
        [
            "game_id",
            "team",
            f"off_ypp_last{window}",
        ]
    ].merge(
        games[
            ["game_id", "home_team"]
        ],
        on="game_id",
        how="inner",
    )

    home_ypp = home_ypp[
        home_ypp["team"] == home_ypp["home_team"]
    ][
        [
            "game_id",
            f"off_ypp_last{window}",
        ]
    ].rename(
        columns={
            f"off_ypp_last{window}":
                "home_off_ypp"
        }
    )

    away_ypp = ypp[
        [
            "game_id",
            "team",
            f"off_ypp_last{window}",
        ]
    ].merge(
        games[
            ["game_id", "away_team"]
        ],
        on="game_id",
        how="inner",
    )

    away_ypp = away_ypp[
        away_ypp["team"] == away_ypp["away_team"]
    ][
        [
            "game_id",
            f"off_ypp_last{window}",
        ]
    ].rename(
        columns={
            f"off_ypp_last{window}":
                "away_off_ypp"
        }
    )

    # ---------------------------------
    # Assemble game-level dataset
    # ---------------------------------

    result = games.copy()

    for feature_table in [
        home_stats,
        away_stats,
        home_epa,
        away_epa,
        home_success,
        away_success,
        home_ypp,
        away_ypp,
    ]:
        result = result.merge(
            feature_table,
            on="game_id",
            how="left",
        )

    # ---------------------------------
    # Final matchup features
    # Positive = advantage home team
    # ---------------------------------

    result["point_diff_diff"] = (
        result["home_avg_point_diff"]
        - result["away_avg_point_diff"]
    )

    result["win_pct_diff"] = (
        result["home_win_pct"]
        - result["away_win_pct"]
    )

    # Lower defensive EPA allowed is better.
    result["def_epa_advantage"] = (
        result["away_def_epa"]
        - result["home_def_epa"]
    )

    result["off_success_rate_advantage"] = (
        result["home_off_success_rate"]
        - result["away_off_success_rate"]
    )

    # Lower defensive success rate allowed is better.
    result["def_success_rate_advantage"] = (
        result["away_def_success_rate_allowed"]
        - result["home_def_success_rate_allowed"]
    )

    result["off_ypp_advantage"] = (
        result["home_off_ypp"]
        - result["away_off_ypp"]
    )

    return result