import pandas as pd

from iron_man_features.features.model_feature import ModelFeature


class Categorical(ModelFeature):
    """
    Classe Categorical cria uma feature binária para cada categoria do campo
    selecionado.

    Parâmetros:
    - field (str): Campo do banco de dados scouts selecionado.

    Atributos:
    - live (bool): Indica se a feature é calculada em tempo real ou não. Padrão: False.
    - feature_type (str): Tipo de feature. Padrão: 'numeric'.
    """

    live: bool = True
    feature_type: str = "numeric"

    def __init__(self, field: str):
        self.field = field
        self.name = f"categorical({self.field})"

    def calculation(self, df: pd.DataFrame) -> pd.DataFrame:
        result = pd.DataFrame(index=df.index)

        values = list(df[self.field].drop_duplicates())
        new_categorical_fields = {
            value: f"categorical({self.field}={value})" for value in values
        }

        for value, name in new_categorical_fields.items():
            result[name] = (df[self.field] == value).astype(int)

        return result
