from typing import Callable, List

from pytrade.interfaces.broker import IBroker
from pytrade.interfaces.client import IClient
from pytrade.models.instruments import Candlestick, Granularity, FxInstrument
from pytrade.models.order import OrderRequest


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

        self._pending_orders.clear()

    def subscribe(
        self,
        instrument: FxInstrument,
        granularity: Granularity,
        callback: Callable[[Candlestick], None],
    ):
        self.client.subscribe(instrument, granularity, callback)
