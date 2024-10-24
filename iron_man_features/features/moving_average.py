import pandas as pd

from iron_man_features.features.calculation_functions import calculate_moving_average
from iron_man_features.features.model_feature import ModelFeature


class MovingAverage(ModelFeature):
    """
    Classe MovingAverage calcula a média móvel para cada jogador de um campo
    especificado, baseada em um número definido de partidas anteriores.

    A média móvel é calculada com um 'shift' para a partida anterior, ignorando
    a partida atual.

    Parâmetros:
    - field (str): Campo do banco de dados scouts para o qual a média móvel será
                    calculada.
    - n_games (int): Número de partidas anteriores a considerar para a média móvel.
    - **kwargs: Filtros adicionais para a consulta.

    Atributos:
    - live (bool): Indica se a feature é calculada em tempo real ou não. Padrão: False.
    - feature_type (str): Tipo de feature. Padrão: 'numeric'.
    - base_df (str): DataFrame base utilizado. Padrão: 'scouts'.

    Uso:
    >>> ma = MovingAverage(field="pontos", n_games=6)
    >>> print(ma.name)
    'moving_average(pontos, 6)'
    """

    live: bool = False
    feature_type: str = "numeric"
    field: str
    n_games: int

    def __init__(self, field: str, n_games: int, **kwargs):
        self.field = field
        self.n_games = n_games
        self.filters = kwargs
        kwargs_string = "-".join([f"{k}={v}" for k, v in self.filters.items()])
        self.name = f"moving_average({self.field}-{self.n_games}"
        if len(kwargs_string) > 2:
            self.name += f"-{kwargs_string})"
        else:
            self.name += ")"

    def calculation(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        result = pd.DataFrame(index=df.index)

        result[self.name] = calculate_moving_average(
            df=df,
            field=self.field,
            window=self.n_games,
            filters=self.filters,
        )

        return result[self.name]
