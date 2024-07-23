from typing import Callable, List

import pandas as pd

from fx_lib.interfaces.broker import IBroker
from fx_lib.interfaces.client import IClient
from fx_lib.models.instruments import Candlestick, Granularity, Instrument
from fx_lib.models.order import OrderRequest


class FxBroker(IBroker):

    def __init__(self, client: IClient):
        self.client = client
        self._pending_orders: List[OrderRequest] = []

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

    def order(self, order: OrderRequest):
        self._pending_orders.append(order)

    def process_orders(self):
        for order in self._pending_orders:
            self.client.order(order)

    def subscribe(
        self,
        instrument: Instrument,
        granularity: Granularity,
        callback: Callable[[Candlestick], None],
    ):
        self.client.subscribe(instrument, granularity, callback)


class BacktestBroker:

    def __init__(self, data: pd.DataFrame):
        pass

    def run(
        self,
    ):
        pass

    def new_order(self, size, limit, stop, sl, tp, tag):
        pass
