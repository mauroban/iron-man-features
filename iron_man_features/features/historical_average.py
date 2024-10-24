import pandas as pd

from iron_man_features.features.calculation_functions import calculate_average
from iron_man_features.features.model_feature import ModelFeature


class HistoricalAverage(ModelFeature):
    """
    Classe HistoricalAverage calcula a média histórica para cada jogador de um campo
    especificado.

    Parâmetros:
    - field (str): Campo do banco de dados scouts para o qual a média será
                    calculada.
    - **kwargs: Filtros adicionais para a consulta.

    Atributos:
    - live (bool): Indica se a feature é calculada em tempo real ou não. Padrão: False.
    - feature_type (str): Tipo de feature. Padrão: 'numeric'.
    - base_df (str): DataFrame base utilizado. Padrão: 'scouts'.

    Uso:
    >>> ma = HistoricalAverage(field="pontos", n_matches=6)
    >>> print(ma.name)
    'historical_average(pontos, 6)'
    """

    live: bool = False
    feature_type: str = "numeric"
    base_df: str = "scouts"
    field: str

    def __init__(self, field: str, **kwargs):
        self.field = field
        self.filters = kwargs
        kwargs_string = "-".join([f"{k}={v}" for k, v in self.filters.items()])
        self.name = f"historical_average({self.field}"
        if len(kwargs_string) > 2:
            self.name += f"-{kwargs_string})"
        else:
            self.name += ")"

    def calculation(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        result = pd.DataFrame(index=df.index)

        result[self.name] = calculate_average(
            df=df,
            field=self.field,
            filters=self.filters,
        )

        return result[self.name]
