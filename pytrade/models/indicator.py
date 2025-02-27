from abc import abstractmethod

import numpy as np

from pytrade.interfaces.data import IInstrumentData


class _Array(np.ndarray):
    """
    ndarray extended to supply .name and other arbitrary properties
    in ._opts dict.
    """

    def __new__(cls, array=[], *, name=None, **kwargs):
        obj = np.asarray(array).view(cls)
        # obj.name = name or array.name
        # obj._opts = kwargs
        return obj

    def __array_finalize__(self, obj):
        pass
        # if obj is not None:
        # self.name = getattr(obj, "name", "")
        # self._opts = getattr(obj, "_opts", {})

    # Make sure properties name and _opts are carried over
    # when (un-)pickling.
    def __reduce__(self):
        value = super().__reduce__()
        return value[:2] + (value[2] + (self.__dict__,),)

    def __setstate__(self, state):
        self.__dict__.update(state[-1])
        super().__setstate__(state[:-1])

    def __bool__(self):
        try:
            return bool(self[-1])
        except IndexError:
            return super().__bool__()

    def __float__(self):
        try:
            return float(self[-1])
        except IndexError:
            return super().__float__()

    # def to_series(self):
    #     warnings.warn(
    #         "`.to_series()` is deprecated. For pd.Series conversion, use accessor `.s`"
    #     )
    #     return self.s

    # @property
    # def s(self) -> pd.Series:
    #     values = np.atleast_2d(self)
    #     index = self._opts["index"][: values.shape[1]]
    #     return pd.Series(values[0], index=index, name=self.name)

    # @property
    # def df(self) -> pd.DataFrame:
    #     values = np.atleast_2d(np.asarray(self))
    #     index = self._opts["index"][: values.shape[1]]
    #     df = pd.DataFrame(values.T, index=index, columns=[self.name] * len(values))
    #     return df


class Indicator:

    def __init__(self, data: IInstrumentData, *args, **kwargs):
        self._data = data
        data.on_update += self._update
        self._args = args
        self._kwargs = kwargs
        self._values = self._run(self._args, self._kwargs)

    def _update(self):
        self._values = self._run(self._args, self._kwargs)

    @abstractmethod
    def _run(self, *args, **kwargs) -> np.ndarray:
        raise NotImplementedError()

    @property
    def value(self):
        return self._values[-1] if len(self._values) > 0 else None

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
