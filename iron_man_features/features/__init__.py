from iron_man_features.features.moving_average import MovingAverage
from iron_man_features.features.simple_feature import SimpleFeature


FEATURES = [
    SimpleFeature("overall_elo"),
]

MAPS = []


average_columns = [
    "won"
]

for avg_column in average_columns:
    for window in [3, 5, 10, 20]:
        FEATURES.append(
            MovingAverage(avg_column, window)
        )
