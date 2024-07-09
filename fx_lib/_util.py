from numbers import Number
from typing import Dict, Optional, cast

import numpy as np
import pandas as pd

from fx_lib.models.data import _Array


def try_(lazy_func, default=None, exception=Exception):
    try:
        return lazy_func()
    except exception:
        return default


def _as_str(value) -> str:
    if isinstance(value, (Number, str)):
        return str(value)
    if isinstance(value, pd.DataFrame):
        return "df"
    name = str(getattr(value, "name", "") or "")
    if name in ("Open", "High", "Low", "Close", "Volume"):
        return name[:1]
    if callable(value):
        name = getattr(value, "__name__", value.__class__.__name__).replace(
            "<lambda>", "λ"
        )
    if len(name) > 10:
        name = name[:9] + "…"
    return name


class Data:
    """
    A data array accessor. Provides access to OHLCV "columns"
    as a standard `pd.DataFrame` would, except it's not a DataFrame
    and the returned "series" are _not_ `pd.Series` but `np.ndarray`
    for performance reasons.
    """

    def __init__(self, df: pd.DataFrame):
        self.__df = df
        self.__i = len(df)
        self.__pip: Optional[float] = None
        self.__cache: Dict[str, _Array] = {}
        self.__arrays: Dict[str, _Array] = {}
        self._update()

    def __getitem__(self, item):
        return self.__get_array(item)

    def __getattr__(self, item):
        try:
            return self.__get_array(item)
        except KeyError:
            raise AttributeError(f"Column '{item}' not in data") from None

    def _set_length(self, i):
        self.__i = i
        self.__cache.clear()

    def _update(self):
        index = self.__df.index.copy()
        self.__arrays = {
            col: _Array(arr, index=index) for col, arr in self.__df.items()
        }
        # Leave index as Series because pd.Timestamp nicer API to work with
        self.__arrays["__index"] = index

    def __repr__(self):
        i = min(self.__i, len(self.__df)) - 1
        index = self.__arrays["__index"][i]
        items = ", ".join(f"{k}={v}" for k, v in self.__df.iloc[i].items())
        return f"<Data i={i} ({index}) {items}>"

    def __len__(self):
        return self.__i

    @property
    def df(self) -> pd.DataFrame:
        return self.__df.iloc[: self.__i] if self.__i < len(self.__df) else self.__df

    @property
    def pip(self) -> float:
        if self.__pip is None:
            self.__pip = float(
                10
                ** -np.median(
                    [
                        len(s.partition(".")[-1])
                        for s in self.__arrays["Close"].astype(str)
                    ]
                )
            )
        return self.__pip

    def __get_array(self, key) -> _Array:
        arr = self.__cache.get(key)
        if arr is None:
            arr = self.__cache[key] = cast(_Array, self.__arrays[key][: self.__i])
        return arr

    @property
    def Open(self) -> _Array:
        return self.__get_array("Open")

    @property
    def High(self) -> _Array:
        return self.__get_array("High")

    @property
    def Low(self) -> _Array:
        return self.__get_array("Low")

    @property
    def Close(self) -> _Array:
        return self.__get_array("Close")

    @property
    def Volume(self) -> _Array:
        return self.__get_array("Volume")

    @property
    def index(self) -> _Array:
        return self.__get_array("__index")

    # Make pickling in Backtest.optimize() work with our catch-all __getattr__
    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__ = state
