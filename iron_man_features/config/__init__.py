import os


def safe_path_join(*args):
    """Join parts of a URL or file path, ensuring there's exactly one separator."""
    # Remove any trailing or leading slashes from parts and join with a single slash
    return "/".join(part.strip("/") for part in args if part)


# Configured paths
DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
FEATURES_DF_PATH = os.getenv("FEATURES_DF_PATH", "data/features.csv")
MATCHES_TO_PREDICT_PATH = os.getenv(
    "MATCHES_TO_PREDICT_PATH", "data/matches_to_predict.csv"
)
FEATURES_LIST_PATH = os.getenv("FEATURES_LIST_PATH", "data/feature_list.json")
