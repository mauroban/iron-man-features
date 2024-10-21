from iron_man_features.features.moving_average import MovingAverage
from iron_man_features.features.simple_feature import SimpleFeature

FEATURES = [
    SimpleFeature("overall_elo"),
    SimpleFeature("overall_elo_op"),
]

MAPS = ["Anubis", "Mirage", "Nuke", "Dust2", "Vertigo", "Ancient", "Inferno"]

WINDOWS = [3, 5, 10, 20, 50]

average_columns = [
    "won",
    "kills_per_round",
    "deaths_per_round",
    "first_kills_per_round",
    "flash_assists_per_round",
    "pistols_won",
]

for window in WINDOWS:
    FEATURES.append(MovingAverage("won", window, player_carried=1))
    FEATURES.append(MovingAverage("won", window, player_carried_down=1))

for avg_column in average_columns:
    for window in WINDOWS:
        FEATURES.append(MovingAverage(avg_column, window))
        for pistols in [0, 1, 2]:
            FEATURES.append(MovingAverage(avg_column, window, pistols_won=pistols))
        for map_name in MAPS:
            FEATURES.append(
                MovingAverage(avg_column, window, played_map=map_name.lower())
            )
            for pistols in [0, 1, 2]:
                FEATURES.append(
                    MovingAverage(
                        avg_column,
                        window,
                        pistols_won=pistols,
                        played_map=map_name.lower(),
                    )
                )

for map_name in MAPS:
    FEATURES.append(SimpleFeature(f"{map_name.lower()}_elo"))
    FEATURES.append(SimpleFeature(f"{map_name.lower()}_elo_op"))
