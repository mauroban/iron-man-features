import importlib
import logging
import pandas as pd

from iron_man_features.data_manager.downloads import get_dataframes
from iron_man_features.data_manager.preparation import (
    calculate_features,
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
logging.info(len(data))

data = calculate_elos(data, dfs["games_for_elo"])

logging.info(len(data))

feature_df = data[
    ["match_id", "team_id", "team_id_op", "game_id", "played_map", "won"]
].copy()

logging.info(len(feature_df))

feature_df = calculate_features(
    feature_df=feature_df,
    feature_classes=FEATURES,
    information_df=data,
)

logging.info(len(feature_df))

updated_feat_df = keep_only_played_map_columns(feature_df)
new = pd.isna(updated_feat_df["won"])

updated_feat_df[~new].to_csv("data/features.csv", index=False)
updated_feat_df[new].to_csv("data/matches_to_predict.csv", index=False)
