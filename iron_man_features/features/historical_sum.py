import pandas as pd

from iron_man_features.features.calculation_functions import calculate_sum
from iron_man_features.features.model_feature import ModelFeature


class HistoricalSum(ModelFeature):
    """
    Classe HistoricalSum calcula a soma histórica para cada jogador de um campo
    especificado.

    Parâmetros:
    - field (str): Campo do banco de dados scouts para o qual a soma será
                    calculada.
    - **kwargs: Filtros adicionais para a consulta.

    Atributos:
    - live (bool): Indica se a feature é calculada em tempo real ou não. Padrão: False.
    - feature_type (str): Tipo de feature. Padrão: 'numeric'.
    - base_df (str): DataFrame base utilizado. Padrão: 'scouts'.

    Uso:
    >>> ma = HistoricalSum(field="pontos", n_matches=6)
    >>> print(ma.name)
    'historical_sum(pontos, 6)'
    """

    live: bool = False
    feature_type: str = "numeric"
    field: str

    def __init__(self, field: str, **kwargs):
        self.field = field
        self.filters = kwargs
        kwargs_string = ", ".join([f"{k}={v}" for k, v in self.filters.items()])
        self.name = f"historical_sum({self.field}"
        if len(kwargs_string) > 2:
            self.name += f", {kwargs_string})"
        else:
            self.name += ")"

    def calculation(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        result = pd.DataFrame(index=df.index)

        result[self.name] = calculate_sum(
            df=df,
            field=self.field,
            filters=self.filters,
        )

        return result[self.name]
