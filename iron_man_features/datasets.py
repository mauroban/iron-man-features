import json
import logging
from typing import List

import pandas as pd

from iron_man_features.config import (
    FEATURES_DF_PATH,
    FEATURES_LIST_PATH,
    MATCHES_TO_PREDICT_PATH,
)
from iron_man_features.data_manager.downloads import get_dataframes
from iron_man_features.data_manager.preparation import (
    calculate_features,
    create_elo_crossing_features,
    create_opponent_features,
    keep_only_played_map_columns,
)
from iron_man_features.elo_system import EloSystem, calculate_elos
from iron_man_features.features import FEATURES


# Constants
GAME_ID_COLUMNS = [
    "match_id",
    "match_date",
    "team_id",
    "team_id_op",
    "game_id",
    "played_map",
    "won",
]

ELO_SYSTEMS_CONFIG = [
    {"base_k_factor": 32, "postfix": ""},
    # {"base_k_factor": 10, "postfix": "_slow"},
    # {"base_k_factor": 50, "postfix": "_fast", "boost_diff": True},
]


def initialize_elo_systems(configs: List[dict]) -> List[EloSystem]:
    """
    Initialize multiple EloSystem instances based on provided configurations.
    """
    elo_systems = []
    for config in configs:
        elo_system = EloSystem(**config)
        elo_systems.append(elo_system)
    return elo_systems


def calculate_elos_for_systems(
    data: pd.DataFrame, games_for_elo: pd.DataFrame, elo_systems: List[EloSystem]
) -> pd.DataFrame:
    """
    Calculate Elo ratings for multiple Elo systems and add them to the data.
    """
    for elo_system in elo_systems:
        data = calculate_elos(data, games_for_elo, elo_system)
    return data


def save_feature_list(feature_df: pd.DataFrame, filename: str) -> None:
    """
    Save the list of features to a JSON file.
    """
    feature_list = [
        f for f in feature_df.columns if f not in GAME_ID_COLUMNS and "(" in f
    ]
    logging.info(f"Saving features list of {len(feature_list)} features to {filename}")
    with open(filename, "w") as f:
        json.dump({"features_list": sorted(feature_list)}, f, indent=4)


def process_features(data: pd.DataFrame, elo_system: EloSystem) -> pd.DataFrame:
    """
    Process and calculate all features for the dataset.
    """
    feature_df = data[GAME_ID_COLUMNS].copy()

    feature_df = calculate_features(
        feature_df=feature_df,
        feature_classes=FEATURES,
        information_df=data,
    )

    feature_df = create_opponent_features(feature_df)
    # Assuming create_elo_crossing_features can handle multiple Elo systems
    feature_df = create_elo_crossing_features(feature_df, elo_system)
    feature_df = keep_only_played_map_columns(feature_df)

    return feature_df


def update_feature_df():
    """
    Update the feature DataFrame with all games and save the features and matches to
    predict.
    """
    dfs = get_dataframes()

    data = pd.concat([dfs["team_games"], dfs["matches_to_predict"]], ignore_index=True)
    data = data.sort_values(["match_date", "game_hltv_id"])

    # Initialize Elo systems
    elo_systems = initialize_elo_systems(ELO_SYSTEMS_CONFIG)

    # Calculate Elo ratings and add them to the data
    data = calculate_elos_for_systems(data, dfs["games_for_elo"], elo_systems)

    feature_df = process_features(data, elo_systems[0])

    # Separate matches to predict from historical data
    is_new_match = feature_df["won"].isna()
    matches_to_predict = feature_df[is_new_match].drop_duplicates()
    feature_df = feature_df[~is_new_match]

    # Save feature DataFrame
    logging.info(
        f"Saving features DataFrame with {len(feature_df)} rows and "
        f"{len(feature_df.columns)} columns to {FEATURES_DF_PATH}"
    )
    feature_df.to_csv(FEATURES_DF_PATH, index=False)

    # Save matches to predict
    logging.info(
        f"Saving matches to predict DataFrame with {len(matches_to_predict)} rows and "
        f"{len(matches_to_predict.columns)} columns to {MATCHES_TO_PREDICT_PATH}"
    )
    matches_to_predict.to_csv(MATCHES_TO_PREDICT_PATH, index=False)

    # Save feature list
    save_feature_list(feature_df, FEATURES_LIST_PATH)


def calculate_features_for_matches_to_predict():
    """
    Calculate features only for matches to predict and save the results.
    """
    dfs = get_dataframes()

    # Use only matches_to_predict
    matches_to_predict = dfs["matches_to_predict"].copy()
    matches_to_predict = matches_to_predict.sort_values(["match_date"])

    # Initialize Elo systems
    elo_systems = initialize_elo_systems(ELO_SYSTEMS_CONFIG)

    # Calculate Elo ratings using all historical games
    for elo_system in elo_systems:
        elo_system.calculate_elo(games=dfs["games_for_elo"])
        matches_to_predict = elo_system.add_elos_to_df(matches_to_predict)

    # Get unique roster hashes involved in matches to predict
    roster_hashes = set(matches_to_predict["roster_hash"].unique())

    # Filter historical games for relevant teams before the earliest prediction date
    earliest_prediction_date = matches_to_predict["match_date"].min()
    team_games = dfs["team_games"].copy()
    team_games = team_games[
        team_games["roster_hash"].isin(roster_hashes)
        & (team_games["match_date"] < earliest_prediction_date)
    ]

    # Combine filtered historical games with matches to predict
    data = pd.concat([team_games, matches_to_predict], ignore_index=True)
    data = data.sort_values(["match_date", "game_hltv_id"])

    feature_df = process_features(data, elo_systems[0])
    matches_to_predict = feature_df[feature_df["won"].isna()]

    # Save matches to predict
    logging.info(
        f"Saving matches to predict DataFrame with {len(matches_to_predict)} "
        f"rows and {len(matches_to_predict.columns)} columns to "
        f"{MATCHES_TO_PREDICT_PATH}"
    )
    matches_to_predict.to_csv(MATCHES_TO_PREDICT_PATH, index=False)

    # Save feature list
    save_feature_list(matches_to_predict, FEATURES_LIST_PATH)


if __name__ == "__main__":
    import importlib

    importlib.reload(logging)

    logging.basicConfig(
        format="%(asctime)s %(filename)s %(levelname)s: %(message)s",
        level=logging.INFO,
        datefmt="%H:%M:%S",
        encoding="utf-8",
    )
    update_feature_df()
