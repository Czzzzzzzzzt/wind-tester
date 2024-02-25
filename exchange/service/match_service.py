from abc import ABC, abstractmethod

from broker.model import Order


class MatchService(ABC):
    @abstractmethod
    def match_order(self, order: Order) -> None:
        pass
