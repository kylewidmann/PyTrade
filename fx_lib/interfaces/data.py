from abc import abstractmethod

import pandas as pd

from fx_lib.events import Event


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
