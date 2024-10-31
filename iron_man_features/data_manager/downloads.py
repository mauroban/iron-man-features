import logging
from typing import Dict

import pandas as pd

from iron_man_features.data_manager.connection import engine
from iron_man_features.queries import QUERIES


def get_dataframes() -> Dict[str, pd.DataFrame]:
    dfs = {}
    for name, query in QUERIES.items():
        dfs[name] = pd.read_sql(query, engine)
        logging.info(f"Downloaded {name} df")
    return dfs
