from abc import abstractmethod

import pandas as pd

from pytrade.events.event import Event


class IInstrumentData:

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
    def Open(self):
        return self.df.Open

    @property
    def High(self):
        return self.df.High

    @property
    def Low(self):
        return self.df.Low

    @property
    def Close(self):
        return self.df.Close