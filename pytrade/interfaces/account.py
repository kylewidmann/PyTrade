from abc import abstractmethod


class IAccount:

    @property
    @abstractmethod
    def equity(self) -> float:
        raise NotImplementedError()

    @property
    @abstractmethod
    def margin_available(self) -> float:
        raise NotImplementedError()

    @property
    @abstractmethod
    def leverage(self) -> float:
        raise NotImplementedError()
