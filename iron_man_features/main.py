import json
import logging

import pandas as pd
from sqlalchemy import create_engine
from iron_man_features.elo_system import EloSystem


DB_CONNECTION_STRING = "mysql+pymysql://iron_man:iron_man@localhost:10010/iron_man"


logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)

engine = create_engine(DB_CONNECTION_STRING, pool_recycle=3600)


with open("queries/games_for_elo.sql", "r") as f:
    query = f.read()

data = pd.read_sql(
    query, con=engine
).sort_values("start_date", ascending=True)

elo_system = EloSystem()
elos = elo_system.calculate_elo(data)


elos.sort_values('overall_elo', ascending=False).to_csv('elos.csv', index=False)
with open("elo_ratings.json", "w") as f:
    json.dump(elo_system.ratings, f, indent=4)
