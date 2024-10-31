import pandas as pd

from iron_man_features.features.calculation_functions import calculate_games_last_n_days
from iron_man_features.features.model_feature import ModelFeature


class GamesPlayedLastDays(ModelFeature):
    """
    Classe SimpleFeature extrai um campo da tabela de scouts do banco de dados para a
    rodada atual ou rodadas anteriores.

    Parâmetros:
    - field (str): Campo do banco de dados scouts a ser extraído.
    - shift (int): Define o deslocamento para rodadas anteriores. Padrão: 0.

    Atributos:
    - live (bool): Indica se a feature é calculada em tempo real ou não. Padrão: False.
    - feature_type (str): Tipo de feature. Padrão: 'numeric'.
    - base_df (str): DataFrame base utilizado. Padrão: 'scouts'.

    Uso:
    >>> simple_feature = SimpleFeature(field="gols", shift=1)
    >>> print(simple_feature.name)
    'simple_feature(gols, 1)'
    """

    live: bool = False
    feature_type: str = "numeric"
    shift: int

    def __init__(self, days: int, **kwargs):
        self.days = days
        self.filters = kwargs
        kwargs_string = "-".join([f"{k}={v}" for k, v in self.filters.items()])
        self.name = f"games_played_last_days({self.days}"
        if len(kwargs_string) > 2:
            self.name += f"-{kwargs_string})"
        else:
            self.name += ")"

    def calculation(self, df: pd.DataFrame) -> pd.DataFrame:
        result = pd.DataFrame(index=df.index)

        result[self.name] = calculate_games_last_n_days(
            df,
            n_days=self.days,
            filters=self.filters,
        )

        return result[self.name]
