from typing import List, Optional

from broker.enums import OrderStatus
from broker.model import Order
from broker.repository.order_repository import OrderRepository


class GeneralOrderRepository(OrderRepository):
    def __init__(self):
        self.orders: List[Order] = []

    def save_order(self, order: Order) -> int:
        order.id = len(self.orders)
        self.orders.append(order)
        return order.id

    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        if order_id < 0 or order_id >= len(self.orders):
            return None
        return self.orders[order_id]

    def get_order_by_status(self, status: OrderStatus) -> List[Order]:
        return [order for order in self.orders if order.status == status]
