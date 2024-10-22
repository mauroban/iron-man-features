from iron_man_features.features.categorical import Categorical
from iron_man_features.features.historical_average import HistoricalAverage
from iron_man_features.features.historical_sum import HistoricalSum
from iron_man_features.features.moving_average import MovingAverage
from iron_man_features.features.simple_feature import SimpleFeature


FEATURES = [
    SimpleFeature("overall_elo"),
    SimpleFeature("overall_elo_strong"),
    HistoricalSum("game_played"),
    Categorical("played_map"),
    # SimpleFeature("hltv_rank"),
    # SimpleFeature("overall_elo_op"),
]

MAPS = ["Anubis", "Mirage", "Nuke", "Dust2", "Vertigo", "Ancient", "Inferno"]

WINDOWS = [3, 5, 10, 20, 50, 100]

average_columns = [
    "won",
    "kills_per_round",
    "deaths_per_round",
    "first_kills_per_round",
    "flash_assists_per_round",
    "clutches_per_round",
    "pistols_won",
    "player_carried",
    "player_carried_down",
]

for avg_column in average_columns:
    HistoricalAverage(avg_column)
    for map_name in MAPS:
        FEATURES.append(HistoricalAverage(avg_column, played_map=map_name.lower()))
    for i in [0, 1]:
        FEATURES.append(HistoricalAverage(avg_column, lan=i))


# for window in WINDOWS:
#     # FEATURES.append(MovingAverage("won", window, player_carried=1))
#     # FEATURES.append(MovingAverage("won", window, player_carried_down=1))
#     for map_name in MAPS:
#         for pistols in [0, 1, 2]:
#             FEATURES.append(
#                 MovingAverage(
#                     "won",
#                     window,
#                     pistols_won=pistols,
#                     played_map=map_name.lower(),
#                 )
#             )

for avg_column in average_columns:
    for window in WINDOWS:
        FEATURES.append(MovingAverage(avg_column, window))
        for map_name in MAPS:
            FEATURES.append(
                MovingAverage(avg_column, window, played_map=map_name.lower())
            )

for map_name in MAPS:
    FEATURES.append(SimpleFeature(f"{map_name.lower()}_elo"))
    FEATURES.append(SimpleFeature(f"{map_name.lower()}_elo_strong"))
    FEATURES.append(SimpleFeature(f"{map_name.lower()}_ct_elo"))
    FEATURES.append(SimpleFeature(f"{map_name.lower()}_tr_elo"))
    HistoricalSum("game_played", played_map=map_name),
    # FEATURES.append(SimpleFeature(f"{map_name.lower()}_elo_op"))
