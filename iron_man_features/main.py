import importlib
import logging
import pandas as pd

from iron_man_features.data_manager.downloads import get_dataframes
from iron_man_features.data_manager.preparation import (
    calculate_features,
    create_opponent_features,
    keep_only_played_map_columns,
)
from iron_man_features.elo_system import calculate_elos
from iron_man_features.features import FEATURES

importlib.reload(logging)


logging.basicConfig(
    format="%(asctime)s %(filename)s %(levelname)s: %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
    encoding="utf-8",
)

dfs = get_dataframes("iron_man_features/queries")

data = pd.concat([dfs["team_games"], dfs["matches_to_predict"]])
data = calculate_elos(data, dfs["games_for_elo"])

feature_df = data[
    ["match_id", "team_id", "team_id_op", "game_id", "played_map", "won"]
].copy()

feature_df = calculate_features(
    feature_df=feature_df,
    feature_classes=FEATURES,
    information_df=data,
)

feature_df = create_opponent_features(feature_df)


feature_df = keep_only_played_map_columns(feature_df)
new = pd.isna(feature_df["won"])

matches_to_predict = feature_df[new]
feature_df = feature_df[~new]

logging.info(
    f"Saving features df with {len(feature_df)} rows and {len(feature_df.columns)} "
    "columns"
)
feature_df.to_csv("data/features.csv", index=False)

logging.info(
    f"Saving matches to predict df with {len(matches_to_predict)} rows and "
    f"{len(matches_to_predict.columns)} columns"
)
matches_to_predict.to_csv("data/matches_to_predict.csv", index=False)
