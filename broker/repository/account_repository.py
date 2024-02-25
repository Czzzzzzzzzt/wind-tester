from abc import ABC, abstractmethod
from typing import Optional

from broker.model import Position


class AccountRepository(ABC):
    @abstractmethod
    def get_balance(self) -> float:
        pass

    @abstractmethod
    def get_equity(self) -> float:
        pass

    @abstractmethod
    def set_equity(self, equity: float) -> None:
        pass

    @abstractmethod
    def set_balance(self, balance: float) -> None:
        pass

    @abstractmethod
    def set_position(self, position: Optional[Position]) -> None:
        pass

    @abstractmethod
    def get_position(self) -> Optional[Position]:
        pass
