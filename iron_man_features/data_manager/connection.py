import logging

from sqlalchemy import create_engine

from iron_man_features.config import DB_CONNECTION_STRING


logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)

engine = create_engine(DB_CONNECTION_STRING, pool_recycle=3600)
