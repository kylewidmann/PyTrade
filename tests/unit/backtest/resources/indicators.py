import sys

import pandas as pd
from pytrade.indicator import Indicator, crossover
from pytrade.instruments import CandleSubscription, FxInstrument, Granularity
from pytrade.interfaces.data import IInstrumentData
from pytrade.strategy import FxStrategy

BACKTEST_INSTRUMENT = FxInstrument.EURUSD
BACKTEST_GRANULARITY = Granularity.M5


class BacktestIndicator(Indicator):
    def _run(self, *args, **kwargs):
        return self._data.Open > self._data.Close


class BacktestStrategy(FxStrategy):
    @property
    def subscriptions(self) -> list[CandleSubscription]:
        """
        Declare the `InstrumentSubscription`s this strategy should use
        for its signals
        """
        return [CandleSubscription(BACKTEST_INSTRUMENT, BACKTEST_GRANULARITY)]

    def _init(self) -> None:
        """
        Create indicators to be used for signals in the `_next` method.
        """
        data = self.get_data(BACKTEST_INSTRUMENT, BACKTEST_GRANULARITY)
        self.test_indicator = BacktestIndicator(data)

    def _next(self) -> None:
        """
        Evaluate indicators and submit orders to the broker
        """
        if self.test_indicator:
            self.sell(1)
        else:
            self.buy(1)




class Sma(Indicator):
    def __init__(self, data: IInstrumentData, period: int):
        self._period = period
        super().__init__(data)

    def _run(self):
        return pd.Series(self._data.Close).rolling(self._period).mean()


class SmaCross(FxStrategy):
    fast = 10
    slow = 30

    @property
    def subscriptions(self) -> list[CandleSubscription]:
        """
        Declare the `InstrumentSubscription`s this strategy should use
        for its signals
        """
        return [CandleSubscription("GOOG", Granularity.D1)]

    def _init(self) -> None:
        """
        Create indicators to be used for signals in the `_next` method.
        """
        self.data = self.get_data("GOOG", Granularity.D1)
        self.sma1 = Sma(self.data, self.fast)
        self.sma2 = Sma(self.data, self.slow)

    def _next(self):
        if crossover(self.sma1._values, self.sma2._values):
            self.broker.close_position("GOOG")
            rel_size = 1 - sys.float_info.epsilon
            self.buy("GOOG", rel_size)
        elif crossover(self.sma2._values, self.sma1._values):
            self.broker.close_position("GOOG")
            rel_size = 1 - sys.float_info.epsilon
            self.sell("GOOG", rel_size)
