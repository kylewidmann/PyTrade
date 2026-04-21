from abc import abstractmethod
from numbers import Number
from typing import Sequence

import numpy as np
import pandas as pd

from pytrade.interfaces.data import IInstrumentData



def crossover(series1: Sequence, series2: Sequence) -> bool:
    """
    Return `True` if `series1` just crossed over (above) `series2`.

    Useful for detecting when a fast indicator crosses above a slow one::

        crossover(sma_fast._values, sma_slow._values)
    """
    series1 = (
        series1.values
        if isinstance(series1, pd.Series)
        else (series1, series1)
        if isinstance(series1, Number)
        else series1
    )
    series2 = (
        series2.values
        if isinstance(series2, pd.Series)
        else (series2, series2)
        if isinstance(series2, Number)
        else series2
    )
    try:
        return series1[-2] < series2[-2] and series1[-1] > series2[-1]
    except IndexError:
        return False


class Indicator:
    def __init__(self, data: IInstrumentData):
        self._data = data
        data.on_update += self._update
        self._values = self._run()

    def __str__(self):
        return f"<{self.__class__.__name__} value={self.value}>"

    def _update(self):
        self._values = self._run()

    @abstractmethod
    def _run(self) -> np.ndarray:
        raise NotImplementedError()

    @property
    def value(self):
        return self._values.iloc[-1] if len(self._values) > 0 else None

    @property
    def to_array(self):
        return self._values

    def __eq__(self, other):
        result = False
        if isinstance(other, Indicator):
            result = self.value == other.value
        else:
            result = self.value == other

        return result

    def __gt__(self, other):
        result = False
        if isinstance(other, Indicator):
            result = self.value > other.value
        else:
            result = self.value > other

        return result

    def __lt__(self, other):
        result = False
        if isinstance(other, Indicator):
            result = self.value < other.value
        else:
            result = self.value < other

        return result

    def __bool__(self):
        return bool(self.value)

    def __float__(self):
        return float(self.value)
