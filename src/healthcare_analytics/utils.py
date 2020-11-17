"""Define a set of pipeline-agnostic methods to help build pipelines."""
from functools import partial, reduce, update_wrapper
from typing import Any, Callable, Dict

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


def make_partial(func: Callable, *args: Any, **keywords: Dict[str, Any]) -> Callable:
    """Create a convenience wrapper to enable passing literals to nodes.

    Args:
        func: A callable object or function. Calls to the `partial`
            object will be forwarded to `func` with new arguments and
            keywords.
        args: The leftmost positional arguments that will be prepended
            to the positional arguments provided to a `partial` object
            call.
        keywords: The keyword arguments that will be supplied when the
            `partial` object is called.

    Returns:
        A `partial` object which when called will behave like `func`
        called with the positional arguments `args` and keyword
        arguments `keywords`, updated to look like `func`.
    """
    return update_wrapper(partial(func, *args, **keywords), func)


def methodcaller(name: str, /, *args: Any, **kwargs: Dict[str, Any]):
    """Return a callable object that calls method `name` on its operand.

    If additional arguments and/or keyword arguments are given, they
    will be given to the method as well. For example:

    - After ``f = methodcaller('name')``, the call ``f(b)`` returns
      ``b.name()``.
    - After ``f = methodcaller('name', 'foo', bar=1)``, the call
      ``f(b)`` returns ``b.name('foo', bar=1)``.

    Equivalent to ``operator.methodcaller``, with ``__name__`` attribute
    set so that Kedro can display it in logs or any other visualization.
    Unlike ``operator.methodcaller``, this function is introspectable so
    that Kedro can validate inputs with a call to ``inspect.signature``.
    """

    def caller(obj):
        return getattr(obj, name)(*args, **kwargs)

    caller.__name__ = name
    return caller
