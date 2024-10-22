import logging
import os
from typing import Dict

import pandas as pd

from iron_man_features.data_manager.connection import engine


def get_dataframes(folder: str) -> Dict[str, pd.DataFrame]:
    dfs = {}
    for file in os.listdir(folder):
        if file.endswith(".sql"):
            name = file[:-4]  # Remove a extensão .sql
            path = os.path.join(folder, file)
            with open(path, "r") as file:
                query = file.read()
                dfs[name] = pd.read_sql(query, engine)
                logging.info(f"Downloaded {name} df")
    return dfs
