import pandas as pd
import polars as pl
import nflreadpy as nfl

def load_games() -> pd.DataFrame:
    """
    Load NFL schedule/game data and return it as a pandas DataFrame.
    """

    games = nfl.load_schedules()

    return games.to_pandas()

def prepare_completed_games(
    games: pd.DataFrame
) -> pd.DataFrame:
    """
    Prepare completed NFL games for historical model training.

    Removes games without final scores and tied games,
    then creates the binary home_win target.
    """

    df = games.copy()

    df = df[
        df["home_score"].notna()
        & df["away_score"].notna()
    ].copy()

    df = df[
        df["home_score"] != df["away_score"]
    ].copy()

    df["home_win"] = (
        df["home_score"] > df["away_score"]
    ).astype(int)

    df = df.sort_values(
        ["season", "week"]
    ).reset_index(drop=True)

    return df

def build_team_games(
    games: pd.DataFrame
) -> pd.DataFrame:
    """
    Convert one-row-per-game data into one-row-per-team-per-game data.
    """

    home = games[
        [
            "game_id",
            "season",
            "week",
            "gameday",
            "home_team",
            "away_team",
            "home_score",
            "away_score",
        ]
    ].copy()

    home = home.rename(
        columns={
            "home_team": "team",
            "away_team": "opponent",
            "home_score": "points_scored",
            "away_score": "points_allowed",
        }
    )

    home["is_home"] = 1

    away = games[
        [
            "game_id",
            "season",
            "week",
            "gameday",
            "away_team",
            "home_team",
            "away_score",
            "home_score",
        ]
    ].copy()

    away = away.rename(
        columns={
            "away_team": "team",
            "home_team": "opponent",
            "away_score": "points_scored",
            "home_score": "points_allowed",
        }
    )

    away["is_home"] = 0

    team_games = pd.concat(
        [home, away],
        ignore_index=True
    )

    team_games["team_win"] = (
        team_games["points_scored"]
        > team_games["points_allowed"]
    ).astype(int)

    team_games = team_games.sort_values(
        ["team", "season", "week"]
    ).reset_index(drop=True)

    return team_games

def load_play_by_play(
    seasons: list[int]
) -> pd.DataFrame:
    """
    Load NFL play-by-play data for the requested seasons.

    Keeps only fields needed by the final model.
    """

    pbp = nfl.load_pbp(seasons)

    columns = [
        "game_id",
        "season",
        "week",
        "posteam",
        "defteam",
        "play_type",
        "epa",
        "success",
        "yards_gained",
    ]

    return pbp.select(columns).to_pandas()

def build_team_epa(
    pbp: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate offensive and defensive EPA per play
    for each team-game.
    """

    plays = pbp[
        pbp["posteam"].notna()
        & pbp["defteam"].notna()
        & pbp["epa"].notna()
        & pbp["play_type"].isin(["run", "pass"])
    ].copy()

    offense = (
        plays
        .groupby(
            ["game_id", "season", "week", "posteam"],
            as_index=False
        )["epa"]
        .mean()
        .rename(
            columns={
                "posteam": "team",
                "epa": "off_epa_per_play",
            }
        )
    )

    defense = (
        plays
        .groupby(
            ["game_id", "season", "week", "defteam"],
            as_index=False
        )["epa"]
        .mean()
        .rename(
            columns={
                "defteam": "team",
                "epa": "def_epa_per_play",
            }
        )
    )

    return offense.merge(
        defense,
        on=["game_id", "season", "week", "team"],
        how="inner",
    )

def build_team_success(
    pbp: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate offensive success rate and defensive
    success rate allowed for each team-game.
    """

    plays = pbp[
        pbp["posteam"].notna()
        & pbp["defteam"].notna()
        & pbp["success"].notna()
        & pbp["play_type"].isin(["run", "pass"])
    ].copy()

    offense = (
        plays
        .groupby(
            ["game_id", "season", "week", "posteam"],
            as_index=False,
        )["success"]
        .mean()
        .rename(
            columns={
                "posteam": "team",
                "success": "off_success_rate",
            }
        )
    )

    defense = (
        plays
        .groupby(
            ["game_id", "season", "week", "defteam"],
            as_index=False,
        )["success"]
        .mean()
        .rename(
            columns={
                "defteam": "team",
                "success": "def_success_rate_allowed",
            }
        )
    )

    return offense.merge(
        defense,
        on=["game_id", "season", "week", "team"],
        how="inner",
    )

def build_team_ypp(
    pbp: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate offensive yards per play and defensive
    yards per play allowed for each team-game.
    """

    plays = pbp[
        pbp["posteam"].notna()
        & pbp["defteam"].notna()
        & pbp["yards_gained"].notna()
        & pbp["play_type"].isin(["run", "pass"])
    ].copy()

    offense = (
        plays
        .groupby(
            ["game_id", "season", "week", "posteam"],
            as_index=False,
        )["yards_gained"]
        .mean()
        .rename(
            columns={
                "posteam": "team",
                "yards_gained": "off_ypp",
            }
        )
    )

    defense = (
        plays
        .groupby(
            ["game_id", "season", "week", "defteam"],
            as_index=False,
        )["yards_gained"]
        .mean()
        .rename(
            columns={
                "defteam": "team",
                "yards_gained": "def_ypp_allowed",
            }
        )
    )

    return offense.merge(
        defense,
        on=["game_id", "season", "week", "team"],
        how="inner",
    )