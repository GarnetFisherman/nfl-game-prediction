import pandas as pd

from src.features import MODEL_FEATURES




def get_upcoming_games(
    games: pd.DataFrame
) -> pd.DataFrame:
    """
    Return games that do not yet have final scores.
    """

    upcoming = games[
        games["home_score"].isna()
        & games["away_score"].isna()
    ].copy()

    upcoming = upcoming.sort_values(
        ["season", "week", "gameday"]
    ).reset_index(drop=True)

    return upcoming

def get_next_week(
    upcoming_games: pd.DataFrame
) -> pd.DataFrame:
    """
    Return the earliest upcoming NFL week in the schedule.
    """

    if upcoming_games.empty:
        return upcoming_games.copy()

    next_season = upcoming_games["season"].min()

    season_games = upcoming_games[
        upcoming_games["season"] == next_season
    ].copy()

    next_week = season_games["week"].min()

    return season_games[
        season_games["week"] == next_week
    ].copy()

def build_current_team_state(
    team_games: pd.DataFrame,
    team_epa: pd.DataFrame,
    team_success: pd.DataFrame,
    team_ypp: pd.DataFrame,
    window: int = 8,
) -> pd.DataFrame:
    """
    Build each team's current state using its most recent
    completed games.

    Intended for predicting future games.
    """

    # ---------------------------------
    # Recent game results
    # ---------------------------------

    recent_games = (
        team_games
        .sort_values(["team", "season", "week"])
        .groupby("team")
        .tail(window)
    )

    game_state = (
        recent_games
        .groupby("team")
        .agg(
            avg_point_diff=(
                "points_scored",
                lambda x: x.mean()
            ),
            avg_points_allowed=(
                "points_allowed",
                "mean"
            ),
            win_pct=(
                "team_win",
                "mean"
            ),
        )
        .reset_index()
    )

    # Convert scoring average into point differential.
    avg_points_scored = (
        recent_games
        .groupby("team")["points_scored"]
        .mean()
    )

    avg_points_allowed = (
        recent_games
        .groupby("team")["points_allowed"]
        .mean()
    )

    point_diff = (
        avg_points_scored
        - avg_points_allowed
    )

    game_state["avg_point_diff"] = (
        game_state["team"]
        .map(point_diff)
    )

    # ---------------------------------
    # Defensive EPA
    # ---------------------------------

    recent_epa = (
        team_epa
        .sort_values(["team", "season", "week"])
        .groupby("team")
        .tail(window)
    )

    epa_state = (
        recent_epa
        .groupby("team")
        .agg(
            def_epa=("def_epa_per_play", "mean")
        )
        .reset_index()
    )

    # ---------------------------------
    # Success rate
    # ---------------------------------

    recent_success = (
        team_success
        .sort_values(["team", "season", "week"])
        .groupby("team")
        .tail(window)
    )

    success_state = (
        recent_success
        .groupby("team")
        .agg(
            off_success_rate=("off_success_rate", "mean"),
            def_success_rate_allowed=(
                "def_success_rate_allowed",
                "mean"
            ),
        )
        .reset_index()
    )

    # ---------------------------------
    # Offensive YPP
    # ---------------------------------

    recent_ypp = (
        team_ypp
        .sort_values(["team", "season", "week"])
        .groupby("team")
        .tail(window)
    )

    ypp_state = (
        recent_ypp
        .groupby("team")
        .agg(
            off_ypp=("off_ypp", "mean")
        )
        .reset_index()
    )

    # ---------------------------------
    # Combine team state
    # ---------------------------------

    state = game_state.merge(
        epa_state,
        on="team",
        how="inner",
    )

    state = state.merge(
        success_state,
        on="team",
        how="inner",
    )

    state = state.merge(
        ypp_state,
        on="team",
        how="inner",
    )

    return state

def build_upcoming_features(
    upcoming_games: pd.DataFrame,
    team_state: pd.DataFrame,
) -> pd.DataFrame:
    """
    Attach current team state to upcoming games and create
    the six matchup features used by the model.

    Positive feature values represent an advantage
    for the home team.
    """

    games = upcoming_games.copy()

    # -------------------------
    # Home-team state
    # -------------------------

    home_state = team_state.rename(
        columns={
            "team": "home_team",
            "avg_point_diff": "home_avg_point_diff",
            "win_pct": "home_win_pct",
            "def_epa": "home_def_epa",
            "off_success_rate": "home_off_success_rate",
            "def_success_rate_allowed":
                "home_def_success_rate_allowed",
            "off_ypp": "home_off_ypp",
        }
    )

    # -------------------------
    # Away-team state
    # -------------------------

    away_state = team_state.rename(
        columns={
            "team": "away_team",
            "avg_point_diff": "away_avg_point_diff",
            "win_pct": "away_win_pct",
            "def_epa": "away_def_epa",
            "off_success_rate": "away_off_success_rate",
            "def_success_rate_allowed":
                "away_def_success_rate_allowed",
            "off_ypp": "away_off_ypp",
        }
    )

    # -------------------------
    # Join state to matchups
    # -------------------------

    result = games.merge(
        home_state,
        on="home_team",
        how="left",
    )

    result = result.merge(
        away_state,
        on="away_team",
        how="left",
    )

    # -------------------------
    # Final six model features
    # -------------------------

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


    