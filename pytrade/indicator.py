from abc import abstractmethod

import numpy as np

from pytrade.interfaces.data import IInstrumentData


class Indicator:

    def __init__(self, data: IInstrumentData):
        self._data = data
        data.on_update += self._update
        self._values = self._run()

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
