import logging
from datetime import datetime
from typing import Optional, List

from broker.enums import OrderDirection, OrderType, OrderStatus
from broker.model import Order
from broker.repository.order_repository import OrderRepository
from broker.service.order_service import OrderService
from data.repository.data_repository import DataRepository


# This class is a concrete implementation of the OrderService interface.
# It is responsible for CRUD operations on the Order model.
class GeneralOrderService(OrderService):
    def __init__(self, order_repository: OrderRepository, data_repository: DataRepository):
        self.order_repository: OrderRepository = order_repository
        self.data_repository: DataRepository = data_repository

    def create_order(self, symbol_id: str, price: float, amount: int, direction: OrderDirection,
                     order_type: OrderType) -> Order:
        current_time = self.data_repository.get_current_bar_data(name="datetime", timeframe="1m")
        assert isinstance(current_time, datetime)

        new_order: Order = Order(id=-1, symbol_id=symbol_id, price=price, amount=amount, direction=direction,
                                 type=order_type, status=OrderStatus.PENDING, created_at=current_time,
                                 updated_at=current_time, commissions=None, execution_price=None)
        self.order_repository.save_order(order=new_order)
        logging.info(f'An order has been created: {new_order}')
        return new_order

    def update_order(self, order_id: int, new_price: Optional[float], new_amount: Optional[int]) -> None:
        order: Optional[Order] = self.order_repository.get_order_by_id(order_id=order_id)
        assert order is not None
        order.amount = new_amount if new_amount is not None else order.amount
        order.price = new_price if new_price is not None else order.price
        logging.info(f"Order {order_id} updated to {order.amount} at {order.price}")

    def cancel_order(self, order_id: int) -> None:
        order: Optional[Order] = self.order_repository.get_order_by_id(order_id=order_id)
        assert order is not None
        order.status = OrderStatus.CANCELLED
        logging.info(f"Order {order_id} has been cancelled")

    def get_order_by_status(self, status: OrderStatus) -> List[Order]:
        return self.order_repository.get_order_by_status(status=status)

    def get_order(self, order_id: int) -> Optional[Order]:
        return self.order_repository.get_order_by_id(order_id=order_id)
