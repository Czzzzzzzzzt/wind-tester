import logging
import math
from typing import Optional

from broker.enums import OrderStatus
from broker.model import Order
from broker.repository.order_repository import OrderRepository
from broker.service.order_validation_service import OrderValidationService
from data.model import Symbol
from data.repository.data_repository import DataRepository


class GeneralOrderValidationService(OrderValidationService):
    def __init__(self, data_repository: DataRepository, order_repository: OrderRepository):
        self.data_repository: DataRepository = data_repository
        self.order_repository: OrderRepository = order_repository

    def validate_new_order_input(self, symbol_id: str, price: float, amount: int) -> bool:
        is_price_valid: bool = self._validate_price(symbol_id=symbol_id, price=price, order_id=None)
        is_amount_valid: bool = self._validate_amount(amount=amount)
        return is_price_valid and is_amount_valid

    def validate_update_order_input(self, order_id: int, new_price: Optional[float], new_amount: Optional[int]) -> bool:
        is_order_exist: bool = self._validate_is_order_exist(order_id=order_id)
        is_pending: bool = self._validate_is_pending(order_id=order_id)
        is_price_valid: bool = True if new_price is None else self._validate_price(order_id=order_id, price=new_price,
                                                                                   symbol_id=None)
        is_amount_valid: bool = True if new_amount is None else self._validate_amount(amount=new_amount)
        return is_order_exist and is_pending and is_price_valid and is_amount_valid

    def validate_cancel_order_input(self, order_id: int) -> bool:
        is_order_exist: bool = self._validate_is_order_exist(order_id=order_id)
        is_pending: bool = self._validate_is_pending(order_id=order_id)
        return is_order_exist and is_pending

    def _validate_price(self, order_id: Optional[int], symbol_id: Optional[str], price: float) -> bool:
        if order_id is not None:
            order: Optional[Order] = self.order_repository.get_order_by_id(order_id=order_id)
            if order is None:
                logging.error(f"Order {order_id} does not exist")
                return False
            symbol_id = order.symbol_id

        if symbol_id is None:
            logging.error("Symbol is not provided")
            return False
        symbol: Optional[Symbol] = self.data_repository.get_symbol()

        assert symbol is not None
        is_larger_than_zero: bool = price > 0
        is_divisible_by_tick_size: bool = math.isclose(abs(price % symbol.minimum_tick_size - symbol.minimum_tick_size),
                                                       0.0, abs_tol=1e-9) or math.isclose(
            abs(price % symbol.minimum_tick_size), 0.0, abs_tol=1e-9)
        if not is_larger_than_zero or not is_divisible_by_tick_size:
            logging.error(f"Price {price} is not valid")
        return is_larger_than_zero and is_divisible_by_tick_size

    @staticmethod
    def _validate_amount(amount: int) -> bool:
        if amount <= 0:
            logging.error(f"Amount {amount} is not valid")
            return False
        return True

    def _validate_is_pending(self, order_id: int) -> bool:
        order: Optional[Order] = self.order_repository.get_order_by_id(order_id=order_id)
        if order is None:
            return False
        if order.status != OrderStatus.PENDING:
            logging.error(f"Order {order_id} is not pending")
            return False
        return True

    def _validate_is_order_exist(self, order_id: int) -> bool:
        order: Optional[Order] = self.order_repository.get_order_by_id(order_id=order_id)
        if order is None:
            logging.error(f"Order {order_id} does not exist")
            return False
        return True
