from typing import Dict

import pandas as pd


def calculate_features(
    feature_df: pd.DataFrame,
    feature_classes: list,
    dfs: Dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Calculates features for a given list of feature classes."""
    try:
        features = [feature_df] + [
            f.calculation(dfs[f.base_df]) for f in feature_classes
        ]
        return pd.concat(features, axis=1)
    except KeyError as e:
        print(e.args)
        raise ValueError(f"Base DataFrame for feature calculation not found: {e}")
