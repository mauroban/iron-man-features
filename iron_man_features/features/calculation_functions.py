from typing import Dict

import pandas as pd


# Cache global para armazenar resultados de groupby
groupby_cache: Dict[str, pd.DataFrame] = {}


def apply_filters(df, filters):
    """
    Aplica filtros ao DataFrame.

    :param df: DataFrame pandas.
    :param filters: Dicionário de filtros a serem aplicados.
    :return: DataFrame filtrado.
    """
    filtered_df = df.copy()
    for key, value in filters.items():
        filtered_df = filtered_df[(filtered_df[key] == value)]
    return filtered_df


def get_grouped_df(
    df, groupby_key, shift, filters=None
) -> pd.DataFrame:
    # Convertendo a chave do groupby em uma tupla, se for uma lista
    groupby_fields = groupby_key
    if isinstance(groupby_key, list):
        groupby_key = tuple(sorted(groupby_key))

    # Criar uma representação dos filtros
    filters_repr = str(sorted(filters.items())) if filters else "no_filters"

    # Criar a chave do cache com as informações adicionais
    cache_key = (groupby_key, shift, filters_repr)

    if cache_key not in groupby_cache:
        filtered_df = apply_filters(df, filters)
        groupby_cache[cache_key] = filtered_df.groupby(groupby_fields)
    return groupby_cache[cache_key]


def calculate_sum(df, field, shift=1, filters=None):
    grouped_df = get_grouped_df(
        df=df,
        groupby_key="roster_hash",
        shift=shift,
        filters=filters,
    )
    hist_sum = (
        grouped_df[field]
        .apply(lambda x: x.rolling(window=1000, min_periods=1).sum().shift(shift))
        .reset_index(level=0, drop=True)
    )
    return hist_sum


def calculate_average(df, field, shift=1, filters=None):
    grouped_df = get_grouped_df(
        df=df,
        groupby_key="roster_hash",
        shift=shift,
        filters=filters,
    )
    average = (
        grouped_df[field]
        .apply(lambda x: x.rolling(window=1000, min_periods=1).mean().shift(shift))
        .reset_index(level=0, drop=True)
    )
    return average


def calculate_moving_average(
    df, field, window, shift=1, filters=None
):
    grouped_df = get_grouped_df(
        df=df,
        groupby_key="roster_hash",
        shift=shift,
        filters=filters,
    )
    moving_average = (
        grouped_df[field]
        .apply(
            lambda x: x.rolling(
                window=window, min_periods=window // 2 if window > 1 else 1
            )
            .mean()
            .shift(shift)
        )
        .reset_index(level=0, drop=True)
    )
    return moving_average


def null_if_zero(value, return_value=None):
    if value == 0:
        return return_value
    return value


def calculate_games_last_n_days(df, n_days, shift=1, filters=None):
    """
    Calcula o número de jogos de cada time nos últimos x dias, excluindo o jogo atual.

    :param df: DataFrame com os dados.
    :param n_days: Número de dias para a contagem rolling.
    :param shift: Número de linhas para desconsiderar o jogo atual.
    :param filters: Filtros opcionais a serem aplicados no DataFrame.
    :return: Série com a contagem de jogos nos últimos x dias.
    """
    grouped_df = get_grouped_df(
        df=df,
        groupby_key="roster_hash",
        shift=shift,
        filters=filters,
    )
    games_last_n_days = (
        grouped_df[['game_played', 'match_date']]
        .apply(
            lambda x: x.rolling(
                f'{n_days}D', on='match_date'
            )['game_played']
            .sum()
            .shift(shift)
        )
        .reset_index(level=0, drop=True)
    )
    return games_last_n_days
