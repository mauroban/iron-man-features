import json
import logging

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


GAME_ID_COLUMNS = [
    "match_id",
    "match_date",
    "team_id",
    "team_id_op",
    "game_id",
    "played_map",
    "won",
]


def update_feature_df():
    dfs = get_dataframes()

    data = pd.concat([dfs["team_games"], dfs["matches_to_predict"]])

    data = data.sort_values(["match_date", "game_hltv_id"])

    elo_system = EloSystem()
    elo_system_slow = EloSystem(
        k_factor=10,
        postfix="_slow",
    )
    elo_system_fast = EloSystem(
        k_factor=64,
        postfix="_fast",
        boost_factor=1.2,
        boost_threshold=6,
    )

    data = calculate_elos(data, dfs["games_for_elo"], elo_system)
    data = calculate_elos(data, dfs["games_for_elo"], elo_system_slow)
    data = calculate_elos(data, dfs["games_for_elo"], elo_system_fast)

    feature_df = data[GAME_ID_COLUMNS].copy()

    feature_df = calculate_features(
        feature_df=feature_df,
        feature_classes=FEATURES,
        information_df=data,
    )

    feature_df = create_opponent_features(feature_df)
    feature_df = create_elo_crossing_features(feature_df, elo_system)
    feature_df = keep_only_played_map_columns(feature_df)

    new = pd.isna(feature_df["won"])

    matches_to_predict = feature_df[new].drop_duplicates()
    feature_df = feature_df[~new]

    logging.info(
        f"Saving features df with {len(feature_df)} rows and {len(feature_df.columns)} "
        f"columns to {FEATURES_DF_PATH}"
    )
    feature_df.to_csv(FEATURES_DF_PATH, index=False)

    logging.info(
        f"Saving matches to predict df with {len(matches_to_predict)} rows and "
        f"{len(matches_to_predict.columns)} columns to {MATCHES_TO_PREDICT_PATH}"
    )
    matches_to_predict.to_csv(MATCHES_TO_PREDICT_PATH, index=False)

    feature_list = [
        f for f in feature_df.columns if f not in GAME_ID_COLUMNS and "(" in f
    ]

    logging.info(
        f"Saving features list of {len(feature_list)} features TO {FEATURES_LIST_PATH}"
    )

    with open(FEATURES_LIST_PATH, "w") as f:
        json.dump({"features_list": sorted(feature_list)}, f, indent=4)


if __name__ == "__main__":
    update_feature_df()
