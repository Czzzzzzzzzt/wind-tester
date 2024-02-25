from abc import ABC, abstractmethod
from typing import Optional

from broker.enums import OrderDirection


class RiskService(ABC):
    @abstractmethod
    def validate_new_order_risk(self, symbol_id: str, price: float, amount: int, direction: OrderDirection) -> bool:
        pass

    @abstractmethod
    def validate_update_order_risk(self, order_id: int, new_price: Optional[float], new_amount: Optional[int]) -> bool:
        pass

    @abstractmethod
    def validate_account_risk(self) -> bool:
        pass
