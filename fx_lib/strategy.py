import asyncio
from abc import abstractmethod
from typing import List

from fx_lib.broker import FxBroker
from fx_lib.interfaces.broker import IBroker
from fx_lib.models.data import Indicator
from fx_lib.models.instruments import (
    MINUTES_MAP,
    CandleData,
    Candlestick,
    CandleSubscription,
)

# from ._util import Data


# class Strategy(metaclass=ABCMeta):
#     """
#     A trading strategy base class. Extend this class and
#     override methods
#     `backtesting.backtesting.Strategy.init` and
#     `backtesting.backtesting.Strategy.next` to define
#     your own strategy.
#     """

#     def __init__(self, broker: IBroker, data: Data):
#         self._indicators: List[Indicator] = []
#         self._broker = broker
#         self._data = data

#     def __repr__(self):
#         return "<Strategy " + str(self) + ">"

#     def __str__(self):
#         return f"{self.__class__.__name__}"

#     def I(  # noqa: E741, E743
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
#         Declare indicator. An indicator is just an array of values,
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
#         # if name is None:
#         #     params = ','.join(filter(None, map(_as_str, chain(args, kwargs.values()))))
#         #     func_name = _as_str(func)
#         #     name = (f'{func_name}({params})' if params else f'{func_name}')
#         # else:
#         #     name = name.format(*map(_as_str, args),
#         #                        **dict(zip(kwargs.keys(), map(_as_str, kwargs.values()))))

#         try:
#             value = func(*args, **kwargs)
#         except Exception as e:
#             raise RuntimeError(f'Indicator "{name}" errored with exception: {e}')

#         # if isinstance(value, pd.DataFrame):
#         #     value = value.values.T

#         # if value is not None:
#         #     value = try_(lambda: np.asarray(value, order='C'), None)
#         # is_arraylike = value is not None

#         # # Optionally flip the array if the user returned e.g. `df.values`
#         # if is_arraylike and np.argmax(value.shape) == 0:
#         #     value = value.T

#         # if not is_arraylike or not 1 <= value.ndim <= 2 or value.shape[-1] != len(self._data.Close):
#         #     raise ValueError(
#         #         'Indicators must return (optionally a tuple of) numpy.arrays of same '
#         #         f'length as `data` (data shape: {self._data.Close.shape}; indicator "{name}"'
#         #         f'shape: {getattr(value, "shape" , "")}, returned value: {value})')

#         # if plot and overlay is None and np.issubdtype(value.dtype, np.number):
#         #     x = value / self._data.Close
#         #     # By default, overlay if strong majority of indicator values
#         #     # is within 30% of Close
#         #     with np.errstate(invalid='ignore'):
#         #         overlay = ((x < 1.4) & (x > .6)).mean() > .6

#         value = Indicator(
#             value,
#             name=name,
#             plot=plot,
#             overlay=overlay,
#             color=color,
#             scatter=scatter,
#             # Indicator.s Series accessor uses this:
#             index=self.data.index,
#         )
#         # self._indicators.append(value)
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

#     def buy(
#         self,
#         *,
#         size: float,
#         limit: float = None,
#         stop: float = None,
#         sl: float = None,
#         tp: float = None,
#     ):
#         """
#         Place a new long order. For explanation of parameters, see `Order` and its properties.

#         See also `Strategy.sell()`.
#         """
#         if 0 < size < 1 or round(size) == size:
#             raise RuntimeError(
#                 "size must be a positive fraction of equity, or a positive whole number of units"
#             )
#         return self._broker.new_order(size, limit, stop, sl, tp)

#     def sell(
#         self,
#         *,
#         size: float,
#         limit: float = None,
#         stop: float = None,
#         sl: float = None,
#         tp: float = None,
#     ):
#         """
#         Place a new short order. For explanation of parameters, see `Order` and its properties.

#         See also `Strategy.buy()`.
#         """
#         if 0 < size < 1 or round(size) == size:
#             raise RuntimeError(
#                 "size must be a positive fraction of equity, or a positive whole number of units"
#             )
#         return self._broker.new_order(-size, limit, stop, sl, tp)

#     @property
#     def equity(self) -> float:
#         """Current account equity (cash plus assets)."""
#         return self._broker.equity

#     @property
#     def data(self) -> Data:
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

#     @property
#     def position(self) -> Position:
#         """Instance of `backtesting.backtesting.Position`."""
#         return self._broker.position

#     @property
#     def orders(self) -> Tuple[Order, ...]:
#         """List of orders (see `Order`) waiting for execution."""
#         return tuple(self._broker.orders)

#     @property
#     def trades(self) -> Tuple[Trade, ...]:
#         """List of active trades (see `Trade`)."""
#         return tuple(self._broker.trades)

#     @property
#     def closed_trades(self) -> Tuple[Trade, ...]:
#         """List of settled trades (see `Trade`)."""
#         return tuple(self._broker.closed_trades)


class FxStrategy:

    def __init__(self, broker: FxBroker, max_history=100):
        self.broker = broker
        self._updates_complete = asyncio.Event()
        self._data_context = CandleData(max_size=max_history)
        self._pending_updates: List[CandleSubscription] = []

    def init(self):
        self._caluclate_updates()
        self._monitor_instruments()
        self._init()

    def _caluclate_updates(self):
        self._required_updates: list[CandleSubscription] = []
        max_interval = 0
        for subscription in self.subscriptions:
            max_interval = max(max_interval, MINUTES_MAP[subscription.granularity])

        for subscription in self.subscriptions:
            expected_update_count = int(
                max_interval / MINUTES_MAP[subscription.granularity]
            )
            self._required_updates += [
                subscription for i in range(expected_update_count)
            ]

        self._pending_updates = self._required_updates.copy()

    @property
    @abstractmethod
    def subscriptions(self) -> List[CandleSubscription]:
        """
        Declare the `InstrumentSubscription`s this strategy should use
        for its signals
        """
        raise NotImplementedError()

    def _monitor_instruments(self):
        for subscription in self.subscriptions:
            self.broker.subscribe(
                subscription.instrument,
                subscription.granularity,
                self._update_instrument,
            )

    def _update_instrument(self, candle: Candlestick):
        self._data_context.update(candle)
        self._pending_updates.remove(
            CandleSubscription(candle.instrument, candle.granularity)
        )
        # Filter out update from pending
        if not self._pending_updates:
            self._updates_complete.set()

    async def next(self):
        await self._updates_complete.wait()
        self._next()
        self._pending_updates = self._required_updates.copy()

    @abstractmethod
    def _init(self):
        """
        Create indicators to be used for signals in the `_next` method.
        """
        raise NotImplementedError()

    @abstractmethod
    def _next(self):
        """
        Evaluate indicators and submit orders to the broker
        """
        raise NotImplementedError()


class BacktestStrategy:

    def init(self):
        self._create_indicators()
        self._register_indicators()

    def _create_indicators(self):
        pass

    def _register_indicators(self):
        self._indicators = {
            attr: indicator
            for attr, indicator in self.__dict__.items()
            if isinstance(indicator, Indicator)
        }.items()

    def next(self):
        for attr, indicator in self._indicator_attrs:
            # Slice indicator on the last dimension (case of 2d indicator)
            setattr(self, attr, indicator[..., : len(self.data)])


# class StrategyWrapper:

#     def __init__(self, broker, data, params):
#         self._klass: Type[Strategy] = params.get("_klass")
#         super().__init__(broker, data, params)

#     def init(self):
#         self._strategy = self._klass(self._broker, self.data)
#         self._strategy.init()
#         # Pre calculate indicators
#         self._indicators = {
#             attr: indicator
#             for attr, indicator in self._strategy.__dict__.items()
#             if isinstance(indicator, Indicator)
#         }.items()

#     def next(self):
#         for attr, indicator in self._indicators:
#             # Slice indicator on the last dimension (case of 2d indicator)
#             setattr(self._strategy, attr, indicator[..., : len(self.data)])
#         self._strategy.next()


class BacktestBroker(IBroker):

    pass
