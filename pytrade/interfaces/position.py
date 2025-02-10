from abc import abstractmethod


class IPosition:
    """
    Currently held asset position, available as
    `backtesting.backtesting.Strategy.position` within
    `backtesting.backtesting.Strategy.next`.
    Can be used in boolean contexts, e.g.

        if self.position:
            ...  # we have a position, either long or short
    """

    @property
    @abstractmethod
    def size(self) -> float:
        raise NotImplementedError()

    @property
    @abstractmethod
    def pl(self) -> float:
        """Profit (positive) or loss (negative) of the current position in cash units."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def pl_pct(self) -> float:
        """Profit (positive) or loss (negative) of the current position in percent."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def is_long(self) -> bool:
        """True if the position is long (position size is positive)."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def is_short(self) -> bool:
        """True if the position is short (position size is negative)."""
        raise NotImplementedError()
