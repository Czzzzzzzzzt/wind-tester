from abc import ABC, abstractmethod

from broker.model import Order


class ClearingService(ABC):
    @abstractmethod
    def clear_order(self, order: Order) -> None:
        pass
