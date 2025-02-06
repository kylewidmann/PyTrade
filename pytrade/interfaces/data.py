from abc import abstractmethod

import pandas as pd
from pandas import Timestamp

from pytrade.events.event import Event
from pytrade.instruments import Granularity, Instrument


class IInstrumentData:

    @property
    @abstractmethod
    def instrument(self) -> Instrument:
        raise NotImplementedError()

    @property
    @abstractmethod
    def granularity(self) -> Granularity:
        raise NotImplementedError()

    @property
    @abstractmethod
    def df(self) -> pd.DataFrame:
        raise NotImplementedError()

    @property
    @abstractmethod
    def on_update(self) -> Event:
        raise NotImplementedError()

    @on_update.setter
    @abstractmethod
    def on_update(self, value: Event):
        raise NotImplementedError()

    @property
    def timestamp(self) -> Timestamp:
        raise NotImplementedError()

    @property
    def Open(self):
        return self.df.open

    @property
    def High(self):
        return self.df.high

    @property
    def Low(self):
        return self.df.low

    @property
    def Close(self):
        return self.df.close

    @property
    def last_price(self):
        return self.Close.iloc[-1]


class IDataContext:

    @property
    @abstractmethod
    def universe(self) -> list[IInstrumentData]:
        raise NotImplementedError()

    @abstractmethod
    def get(self, instrument: Instrument, granularity: Granularity) -> IInstrumentData:
        raise NotImplementedError()
