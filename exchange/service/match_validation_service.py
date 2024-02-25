from abc import ABC, abstractmethod

from broker.model import Order


class MatchValidationService(ABC):
    @abstractmethod
    def validate_match(self, order: Order) -> bool:
        pass
