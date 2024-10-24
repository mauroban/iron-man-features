import pandas as pd

from iron_man_features.features.model_feature import ModelFeature


class SimpleFeature(ModelFeature):
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
    base_df: str = "scouts"
    shift: int

    def __init__(self, field: str, shift=0):
        self.field = field
        self.shift = shift
        if self.shift == 0:
            self.live = True
        self.name = f"simple_feature({self.field}-shift={self.shift})"

    def calculation(self, df: pd.DataFrame) -> pd.DataFrame:
        result = pd.DataFrame(index=df.index)

        # Extrai o campo especificado com o deslocamento (shift) aplicado
        if self.shift > 0:
            result[self.name] = df.groupby("roster_hash")[self.field].shift(self.shift)
        else:
            result[self.name] = df[self.field]

        return result[self.name]
