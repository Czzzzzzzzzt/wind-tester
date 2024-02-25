from abc import ABC, abstractmethod
from typing import Optional, List

from broker.enums import OrderStatus
from broker.model import Order


class OrderRepository(ABC):
    @abstractmethod
    def save_order(self, order: Order) -> int:
        pass

    @abstractmethod
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        pass

    @abstractmethod
    def get_order_by_status(self, status: OrderStatus) -> List[Order]:
        pass
