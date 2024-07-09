from typing import Callable

import pandas as pd

from fx_lib.interfaces import IBroker, IClient
from fx_lib.models.granularity import Granularity
from fx_lib.models.instruments import Candlestick, Instrument


class FxBroker(IBroker):

    def __init__(self, client: IClient):
        self.client = client

    def new_order(self, size, limit, stop, sl, tp, tag):
        raise NotImplementedError

    @property
    def equity(self) -> float:
        raise NotImplementedError
        # return self._cash + sum(trade.pl for trade in self.trades)

    @property
    def margin_available(self) -> float:
        raise NotImplementedError
        # From https://github.com/QuantConnect/Lean/pull/3768
        # margin_used = sum(trade.value / self._leverage for trade in self.trades)
        # return max(0, self.equity - margin_used)

    def process_orders(self):
        pass

    def subscribe(
        self,
        instrument: Instrument,
        granularity: Granularity,
        callback: Callable[[Candlestick], None],
    ):
        # self.client.subscribe(instrument, granularity, callback)
        pass


class BacktestBroker:

    def __init__(self, data: pd.DataFrame):
        pass

    def run(
        self,
    ):
        pass

    def new_order(self, size, limit, stop, sl, tp, tag):
        pass
