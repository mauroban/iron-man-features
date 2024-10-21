from abc import ABC, abstractmethod

from pandas import DataFrame


# Classe base abstrata para features
class ModelFeature(ABC):
    live: bool
    feature_type: str
    base_df: str

    @abstractmethod
    def calculation(self, df: DataFrame) -> DataFrame:
        raise NotImplementedError
