from typing import Optional, List

from broker.enums import OrderDirection, OrderType, OrderStatus
from broker.model import Order
from broker.service.order_service import OrderService
from broker.service.order_validation_service import OrderValidationService
from broker.service.risk_service import RiskService
from strategy.dependency.broker import Broker


class BrokerApi(Broker):
    def __init__(self, order_service: OrderService, risk_service: RiskService,
                 order_validation_service: OrderValidationService):
        self.order_service: OrderService = order_service
        self.risk_service: RiskService = risk_service
        self.order_validation_service: OrderValidationService = order_validation_service

    def create_order(self, symbol_id: str, price: float, amount: int, direction: OrderDirection,
                     order_type: OrderType) -> Optional[Order]:
        if not self.order_validation_service.validate_new_order_input(symbol_id=symbol_id, price=price, amount=amount):
            return None
        if not self.risk_service.validate_new_order_risk(symbol_id=symbol_id, price=price, amount=amount,
                                                         direction=direction):
            return None
        return self.order_service.create_order(symbol_id=symbol_id, price=price, amount=amount, direction=direction,
                                               order_type=order_type)

    def update_order(self, order_id: int, new_price: Optional[float], new_amount: Optional[int]) -> bool:
        if not self.order_validation_service.validate_update_order_input(order_id=order_id, new_price=new_price,
                                                                         new_amount=new_amount):
            return False
        if not self.risk_service.validate_update_order_risk(order_id=order_id, new_price=new_price,
                                                            new_amount=new_amount):
            return False
        self.order_service.update_order(order_id=order_id, new_price=new_price, new_amount=new_amount)
        return True

    def cancel_order(self, order_id: int) -> bool:
        if not self.order_validation_service.validate_cancel_order_input(order_id=order_id):
            return False
        self.order_service.cancel_order(order_id=order_id)
        return True

    def get_order(self, order_id: int) -> Optional[Order]:
        return self.order_service.get_order(order_id=order_id)

    def get_orders_by_status(self, order_status: OrderStatus) -> List[Order]:
        return self.order_service.get_order_by_status(status=order_status)
