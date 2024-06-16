import sys
from abc import ABCMeta, abstractmethod
from itertools import chain
from typing import Callable, Optional

import numpy as np
import pandas as pd

from fx_lib.broker import Broker

from ._util import _as_str, _Data, _Indicator, try_

from backtesting import Strategy as BTStrategy

class BacktestStrategy(BTStrategy):
    pass
#     """
#     A trading strategy base class. Extend this class and
#     override methods
#     `backtesting.backtesting.Strategy.init` and
#     `backtesting.backtesting.Strategy.next` to define
#     your own strategy.
#     """

#     def __init__(self, broker, data, params):
#         self._indicators = []
#         self._broker: Broker = broker
#         self._data: _Data = data
#         self._params = self._check_params(params)

#     def __repr__(self):
#         return "<Strategy " + str(self) + ">"

#     def __str__(self):
#         params = ",".join(
#             f"{i[0]}={i[1]}"
#             for i in zip(self._params.keys(), map(_as_str, self._params.values()))
#         )
#         if params:
#             params = "(" + params + ")"
#         return f"{self.__class__.__name__}{params}"

#     def _check_params(self, params):
#         for k, v in params.items():
#             if not hasattr(self, k):
#                 raise AttributeError(
#                     f"Strategy '{self.__class__.__name__}' is missing parameter '{k}'."
#                     "Strategy class should define parameters as class variables before they "
#                     "can be optimized or run with."
#                 )
#             setattr(self, k, v)
#         return params

#     def I(  # noqa: E743
#         self,
#         func: Callable,
#         *args,
#         name=None,
#         plot=True,
#         overlay=None,
#         color=None,
#         scatter=False,
#         **kwargs,
#     ) -> np.ndarray:
#         """
#         Declare an indicator. An indicator is just an array of values,
#         but one that is revealed gradually in
#         `backtesting.backtesting.Strategy.next` much like
#         `backtesting.backtesting.Strategy.data` is.
#         Returns `np.ndarray` of indicator values.

#         `func` is a function that returns the indicator array(s) of
#         same length as `backtesting.backtesting.Strategy.data`.

#         In the plot legend, the indicator is labeled with
#         function name, unless `name` overrides it.

#         If `plot` is `True`, the indicator is plotted on the resulting
#         `backtesting.backtesting.Backtest.plot`.

#         If `overlay` is `True`, the indicator is plotted overlaying the
#         price candlestick chart (suitable e.g. for moving averages).
#         If `False`, the indicator is plotted standalone below the
#         candlestick chart. By default, a heuristic is used which decides
#         correctly most of the time.

#         `color` can be string hex RGB triplet or X11 color name.
#         By default, the next available color is assigned.

#         If `scatter` is `True`, the plotted indicator marker will be a
#         circle instead of a connected line segment (default).

#         Additional `*args` and `**kwargs` are passed to `func` and can
#         be used for parameters.

#         For example, using simple moving average function from TA-Lib:

#             def init():
#                 self.sma = self.I(ta.SMA, self.data.Close, self.n_sma)
#         """
#         if name is None:
#             params = ",".join(filter(None, map(_as_str, chain(args, kwargs.values()))))
#             func_name = _as_str(func)
#             name = f"{func_name}({params})" if params else f"{func_name}"
#         else:
#             name = name.format(
#                 *map(_as_str, args),
#                 **dict(zip(kwargs.keys(), map(_as_str, kwargs.values()))),
#             )

#         try:
#             value = func(*args, **kwargs)
#         except Exception as e:
#             raise RuntimeError(f'Indicator "{name}" error') from e

#         if isinstance(value, pd.DataFrame):
#             value = value.values.T

#         if value is not None:
#             value = try_(lambda: np.asarray(value, order="C"), None)
#         is_arraylike = bool(value is not None and value.shape)

#         # Optionally flip the array if the user returned e.g. `df.values`
#         if is_arraylike and np.argmax(value.shape) == 0:
#             value = value.T

#         if (
#             not is_arraylike
#             or not 1 <= value.ndim <= 2
#             or value.shape[-1] != len(self._data.Close)
#         ):
#             raise ValueError(
#                 "Indicators must return (optionally a tuple of) numpy.arrays of same "
#                 f'length as `data` (data shape: {self._data.Close.shape}; indicator "{name}" '
#                 f'shape: {getattr(value, "shape", "")}, returned value: {value})'
#             )

#         if plot and overlay is None and np.issubdtype(value.dtype, np.number):
#             x = value / self._data.Close
#             # By default, overlay if strong majority of indicator values
#             # is within 30% of Close
#             with np.errstate(invalid="ignore"):
#                 overlay = ((x < 1.4) & (x > 0.6)).mean() > 0.6

#         value = _Indicator(
#             value,
#             name=name,
#             plot=plot,
#             overlay=overlay,
#             color=color,
#             scatter=scatter,
#             # _Indicator.s Series accessor uses this:
#             index=self.data.index,
#         )
#         self._indicators.append(value)
#         return value

#     @abstractmethod
#     def init(self):
#         """
#         Initialize the strategy.
#         Override this method.
#         Declare indicators (with `backtesting.backtesting.Strategy.I`).
#         Precompute what needs to be precomputed or can be precomputed
#         in a vectorized fashion before the strategy starts.

#         If you extend composable strategies from `backtesting.lib`,
#         make sure to call:

#             super().init()
#         """

#     @abstractmethod
#     def next(self):
#         """
#         Main strategy runtime method, called as each new
#         `backtesting.backtesting.Strategy.data`
#         instance (row; full candlestick bar) becomes available.
#         This is the main method where strategy decisions
#         upon data precomputed in `backtesting.backtesting.Strategy.init`
#         take place.

#         If you extend composable strategies from `backtesting.lib`,
#         make sure to call:

#             super().next()
#         """

#     class __FULL_EQUITY(float):  # noqa: N801
#         def __repr__(self):
#             return ".9999"

#     _FULL_EQUITY = __FULL_EQUITY(1 - sys.float_info.epsilon)

#     def buy(
#         self,
#         *,
#         size: float = _FULL_EQUITY,
#         limit: Optional[float] = None,
#         stop: Optional[float] = None,
#         sl: Optional[float] = None,
#         tp: Optional[float] = None,
#         tag: object = None,
#     ):
#         """
#         Place a new long order. For explanation of parameters, see `Order` and its properties.

#         See `Position.close()` and `Trade.close()` for closing existing positions.

#         See also `Strategy.sell()`.
#         """
#         size_valid = 0 < size < 1 or round(size) == size
#         if not size_valid:
#             raise RuntimeError(
#                 "size must be a positive fraction of equity, or a positive whole number of units"
#             )
#         return self._broker.new_order(size, limit, stop, sl, tp, tag)

#     def sell(
#         self,
#         *,
#         size: float = _FULL_EQUITY,
#         limit: Optional[float] = None,
#         stop: Optional[float] = None,
#         sl: Optional[float] = None,
#         tp: Optional[float] = None,
#         tag: object = None,
#     ):
#         """
#         Place a new short order. For explanation of parameters, see `Order` and its properties.

#         See also `Strategy.buy()`.

#         .. note::
#             If you merely want to close an existing long position,
#             use `Position.close()` or `Trade.close()`.
#         """
#         size_valid = 0 < size < 1 or round(size) == size
#         if not size_valid:
#             raise RuntimeError(
#                 "size must be a positive fraction of equity, or a positive whole number of units"
#             )
#         return self._broker.new_order(-size, limit, stop, sl, tp, tag)

#     @property
#     def equity(self) -> float:
#         """Current account equity (cash plus assets)."""
#         return self._broker.equity

#     @property
#     def data(self) -> _Data:
#         """
#         Price data, roughly as passed into
#         `backtesting.backtesting.Backtest.__init__`,
#         but with two significant exceptions:

#         * `data` is _not_ a DataFrame, but a custom structure
#           that serves customized numpy arrays for reasons of performance
#           and convenience. Besides OHLCV columns, `.index` and length,
#           it offers `.pip` property, the smallest price unit of change.
#         * Within `backtesting.backtesting.Strategy.init`, `data` arrays
#           are available in full length, as passed into
#           `backtesting.backtesting.Backtest.__init__`
#           (for precomputing indicators and such). However, within
#           `backtesting.backtesting.Strategy.next`, `data` arrays are
#           only as long as the current iteration, simulating gradual
#           price point revelation. In each call of
#           `backtesting.backtesting.Strategy.next` (iteratively called by
#           `backtesting.backtesting.Backtest` internally),
#           the last array value (e.g. `data.Close[-1]`)
#           is always the _most recent_ value.
#         * If you need data arrays (e.g. `data.Close`) to be indexed
#           **Pandas series**, you can call their `.s` accessor
#           (e.g. `data.Close.s`). If you need the whole of data
#           as a **DataFrame**, use `.df` accessor (i.e. `data.df`).
#         """
#         return self._data

    # @property
    # def position(self) -> Position:
    #     """Instance of `backtesting.backtesting.Position`."""
    #     return self._broker.position

    # @property
    # def orders(self) -> Tuple[Order, ...]:
    #     """List of orders (see `Order`) waiting for execution."""
    #     return _Orders(self._broker.orders)

    # @property
    # def trades(self) -> Tuple[Trade, ...]:
    #     """List of active trades (see `Trade`)."""
    #     return tuple(self._broker.trades)

    # @property
    # def closed_trades(self) -> Tuple[Trade, ...]:
    #     """List of settled trades (see `Trade`)."""
    #     return tuple(self._broker.closed_trades)

class Strategy():

    def __init__(self, broker, params = None):
        super().__init__(broker, _Data(), params)
        self.init()

    def init(self):
        pass

    def next(self):
        pass