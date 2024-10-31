from iron_man_features.features.categorical import Categorical
from iron_man_features.features.historical_average import HistoricalAverage
from iron_man_features.features.historical_sum import HistoricalSum
from iron_man_features.features.moving_average import MovingAverage
from iron_man_features.features.simple_feature import SimpleFeature
from iron_man_features.features.games_played_last_days import GamesPlayedLastDays


FEATURES = [
    SimpleFeature("overall_elo"),
    # SimpleFeature("overall_elo_slow"),
    SimpleFeature("overall_elo_fast"),
    SimpleFeature("overall_elo", shift=5),
    # SimpleFeature("overall_elo_slow", shift=5),
    SimpleFeature("overall_elo_fast", shift=5),
    HistoricalSum("game_played"),
    Categorical("played_map"),
    SimpleFeature("hltv_rank"),
    # SimpleFeature("lan"),
]

MAPS = [
    "anubis",
    "mirage",
    "nuke",
    "dust2",
    "vertigo",
    "ancient",
    "inferno",
    "overpass",
]

WINDOWS = [5, 10, 20, 50, 100]

for days in [1, 3, 5, 10, 30]:
    FEATURES.append(GamesPlayedLastDays(days))
    for map_name in MAPS:
        FEATURES.append(GamesPlayedLastDays(days, played_map=map_name))

average_columns = [
    "won",
    "kills_per_round",
    "deaths_per_round",
    "first_kills_per_round",
    "flash_assists_per_round",
    "avg_rating",
    "avg_kast",
    "clutches_per_round",
    "pistols_won",
    "hltv_rank",
    "hltv_rank_op",
    "player_carried",
    "player_carried_down",
    "rounds_lost_on_win",
    "rounds_won_on_loss",
]

important_average_columns = [
    "won",
    "kills_per_round",
    "deaths_per_round",
    "first_kills_per_round",
    "flash_assists_per_round",
    "pistols_won",
    "rounds_lost_on_win",
    "rounds_won_on_loss",
]


for rank_range in [5, 10, 20, 50, 100, 500]:
    FEATURES.append(HistoricalSum("game_played", rank_range_op=rank_range))
    for avg_column in important_average_columns:
        FEATURES.append(HistoricalAverage(avg_column, rank_range_op=rank_range))
        for map_name in MAPS:
            FEATURES.append(
                HistoricalAverage(
                    avg_column,
                    played_map=map_name.lower(),
                    rank_range_op=rank_range,
                )
            )


for avg_column in average_columns:
    FEATURES.append(HistoricalAverage(avg_column))
    for map_name in MAPS:
        FEATURES.append(HistoricalAverage(avg_column, played_map=map_name.lower()))

for avg_column in average_columns:
    for window in WINDOWS:
        FEATURES.append(MovingAverage(avg_column, window))
        for map_name in MAPS:
            FEATURES.append(
                MovingAverage(avg_column, window, played_map=map_name.lower())
            )

for map_name in MAPS:
    FEATURES.append(SimpleFeature(f"{map_name.lower()}_elo"))
    # FEATURES.append(SimpleFeature(f"{map_name.lower()}_elo_slow"))
    FEATURES.append(SimpleFeature(f"{map_name.lower()}_elo_fast"))
    FEATURES.append(SimpleFeature(f"{map_name.lower()}_elo", shift=5))
    # FEATURES.append(SimpleFeature(f"{map_name.lower()}_elo_slow", shift=5))
    FEATURES.append(SimpleFeature(f"{map_name.lower()}_elo_fast", shift=5))
    # FEATURES.append(SimpleFeature(f"{map_name.lower()}_ct_elo"))
    # FEATURES.append(SimpleFeature(f"{map_name.lower()}_tr_elo"))
    FEATURES.append(HistoricalSum("game_played", played_map=map_name))
