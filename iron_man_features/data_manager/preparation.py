import pandas as pd


def calculate_features(
    feature_df: pd.DataFrame,
    feature_classes: list,
    information_df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculates features for a given list of feature classes."""
    try:
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
            col for col in feature_df.columns if map_name in col.lower()
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
