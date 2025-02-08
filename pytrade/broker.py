from typing import List

from pytrade.data import CandleData
from pytrade.instruments import Granularity, Instrument
from pytrade.interfaces.broker import IBroker
from pytrade.interfaces.client import IClient
from pytrade.interfaces.position import IPosition
from pytrade.interfaces.data import IInstrumentData
from pytrade.models import Order


class Broker(IBroker):

    def __init__(self, client: IClient):
        self.client = client
        self._orders: List[Order] = []
        self._data_context = CandleData()

    @property
    def equity(self) -> float:
        return self.client.account.equity

    @property
    def margin_available(self) -> float:
        return self.client.account.margin_available

    @property
    def leverage(self) -> float:
        return self.client.account.leverage

    def get_position(self, instrument: Instrument) -> IPosition:
        return self.client.get_position(instrument)

    def close_position(self, instrument: Instrument):
        return self.client.close_position(instrument)

    def order(self, order: Order):
        self._orders.append(order)

    def process_orders(self):
        for order in self._orders:
            self.client.order(order)

        self._orders.clear()

    def subscribe(
        self, instrument: Instrument, granularity: Granularity
    ) -> IInstrumentData:

        instrument_data = self._data_context.get(instrument, granularity)

        self.client.subscribe(instrument, granularity, instrument_data.update)

        return instrument_data
