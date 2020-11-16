"""Define a set of pipeline-agnostic methods to help build pipelines."""
from functools import reduce

import pandas as pd


def join_all(*dfs: pd.DataFrame, on=None, how="left") -> pd.DataFrame:
    """Successively merge DataFrames either on index or on a key column.

    Args:
        dfs: The pandas DataFrames or named Series to successively join.
        on: Column or index level name(s) in the accumulator to join on.
        how: How to handle the join operation (see `pd.DataFrame.join`).

    Returns:
        A DataFrame containing the columns from each DataFrame in `dfs`.
    """
    return reduce(lambda df, other: df.join(other, on=on, how=how), dfs)
