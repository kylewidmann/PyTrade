import abc


class IClient(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "subscribe")
            and callable(subclass.subscribe)
            or NotImplemented
        )
