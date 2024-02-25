from abc import ABC, abstractmethod
from typing import Optional, List

from broker.enums import OrderDirection, OrderType, OrderStatus
from broker.model import Order


class Broker(ABC):
    @abstractmethod
    def create_order(self, symbol_id: str, price: float, amount: int, direction: OrderDirection,
                     order_type: OrderType) -> Optional[Order]:
        pass

    @abstractmethod
    def update_order(self, order_id: int, new_price: Optional[float], new_amount: Optional[int]) -> bool:
        pass

    @abstractmethod
    def cancel_order(self, order_id: int) -> bool:
        pass

    @abstractmethod
    def get_order(self, order_id: int) -> Optional[Order]:
        pass

    @abstractmethod
    def get_orders_by_status(self, order_status: OrderStatus) -> List[Order]:
        pass
