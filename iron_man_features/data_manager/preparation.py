import logging

import pandas as pd

from iron_man_features.features import MAPS


def calculate_features(
    feature_df: pd.DataFrame,
    feature_classes: list,
    information_df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculates features for a given list of feature classes."""
    try:
        logging.info(f"Calculating {len(feature_classes)} features")
        features = [feature_df] + [
            f.calculation(information_df) for f in feature_classes
        ]
        return pd.concat(features, axis=1)
    except KeyError as e:
        print(e.args)
        raise ValueError(f"Base DataFrame for feature calculation not found: {e}")


# Assume feature_df has a "played_map" column and other relevant map feature columns
def get_map_based_features(feature_df):
    # Get unique maps from the "played_map" column
    unique_maps = feature_df["played_map"].unique()

    # Create a dictionary to store the mapping from specific features to generic
    # 'played_map'
    map_feature_dict = {}

    # For each unique map, find the relevant features and store the new feature names
    for map_name in unique_maps:
        specific_map_features = [
            col
            for col in feature_df.columns
            if map_name.lower() in col.lower() and "categorical" not in col.lower()
        ]
        new_features = [
            col.replace(map_name, "played_map") for col in specific_map_features
        ]

        # Store the mapping in the dictionary
        map_feature_dict[map_name] = (specific_map_features, new_features)

    # Now, apply the mapping in a vectorized way for each map
    for map_name, (specific_map_features, new_features) in map_feature_dict.items():
        # For rows with this particular map_name, copy values from
        # specific_map_features to new_features
        mask = feature_df["played_map"] == map_name
        feature_df.loc[mask, new_features] = feature_df.loc[
            mask, specific_map_features
        ].values

    return feature_df


def keep_only_played_map_columns(df):
    logging.info("Creating specific map features")
    map_related_columns = [
        # col
        # for col in df.columns
        # if "played_map" in col.lower() and col != "played_map"
    ]
    for map_name in MAPS:
        for f in df.columns:
            if map_name.lower() in f.lower() and "categorical" not in f:
                map_related_columns.append(f)

    logging.info(f"Removing {len(map_related_columns)} general map features")
    return get_map_based_features(df).drop(columns=map_related_columns)


def create_opponent_features(df: pd.DataFrame):
    feat_columns = [
        f for f in df.columns if "(" in f and "categorical(played_map" not in f
    ]
    logging.info(f"Creating {len(feat_columns)} opponent features")
    op_df = df[["team_id", "game_id", "played_map"] + feat_columns].copy()
    op_df = op_df.rename(lambda c: f"{c}_op", axis=1)
    df = df.merge(
        op_df,
        how="left",
        left_on=["game_id", "played_map", "team_id_op"],
        right_on=["game_id_op", "played_map_op", "team_id_op"],
    )
    return df


def create_elo_crossing_features(df: pd.DataFrame, elo_system):
    team_elo_features = [f for f in df.columns if "elo" in f and "_op" not in f]
    for f in team_elo_features:
        new_feature_name = f.replace("elo", "elo_cross")
        if "_tr" in f:
            op_f_name = f"{f.replace("_tr", "_ct")}_op"
        elif "_ct" in f:
            op_f_name = f"{f.replace("_ct", "_tr")}_op"
        else:
            op_f_name = f"{f}_op"
        df[new_feature_name] = df.apply(
            lambda r: elo_system.calc_expected_score(r[f], r[op_f_name]), axis=1
        )

    return df
