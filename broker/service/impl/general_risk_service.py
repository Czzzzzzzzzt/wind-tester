import logging
from typing import Optional, Tuple, List

from broker.enums import OrderDirection, OrderStatus
from broker.model import Order, Position
from broker.repository.account_repository import AccountRepository
from broker.repository.order_repository import OrderRepository
from broker.service.risk_service import RiskService
from data.model import Symbol, TestConfig
from data.repository.data_repository import DataRepository


class GeneralRiskService(RiskService):
    def __init__(self, account_repository: AccountRepository, order_repository: OrderRepository,
                 data_repository: DataRepository):
        self.account_repository: AccountRepository = account_repository
        self.order_repository: OrderRepository = order_repository
        self.data_repository: DataRepository = data_repository

    def validate_account_risk(self) -> bool:
        buy_margin, sell_margin = self._get_used_margins()
        available_margin: float = self._get_available_margin()
        required_margin: float = max(buy_margin, sell_margin)
        return self._validate_margin(required_margin=required_margin, available_margin=available_margin)

    def validate_new_order_risk(self, symbol_id: str, price: float, amount: int, direction: OrderDirection) -> bool:
        buy_margin, sell_margin = self._get_used_margins()
        order_margin: float = self._get_margin(price=price, amount=amount)
        buy_margin += order_margin if direction == OrderDirection.BUY else 0
        sell_margin += order_margin if direction == OrderDirection.SELL else 0
        required_margin: float = max(buy_margin, sell_margin)
        available_margin: float = self._get_available_margin()
        return self._validate_margin(required_margin=required_margin, available_margin=available_margin)

    def validate_update_order_risk(self, order_id: int, new_price: Optional[float], new_amount: Optional[int]) -> bool:
        buy_margin, sell_margin = self._get_used_margins()

        order: Optional[Order] = self.order_repository.get_order_by_id(order_id=order_id)
        assert order is not None
        order_margin: float = self._get_margin(price=order.price, amount=order.amount)
        new_margin: float = self._get_margin(price=new_price or order.price,
                                             amount=new_amount or order.amount)
        diff_margin: float = new_margin - order_margin
        buy_margin += diff_margin if order.direction == OrderDirection.BUY else 0
        sell_margin += diff_margin if order.direction == OrderDirection.SELL else 0

        required_margin: float = max(buy_margin, sell_margin)
        available_margin: float = self._get_available_margin()
        return self._validate_margin(required_margin=required_margin, available_margin=available_margin)

    @staticmethod
    def _validate_margin(required_margin, available_margin) -> bool:
        if required_margin >= available_margin:
            logging.error(f"Required margin {required_margin} is larger than available margin {available_margin}")
            return False
        return True

    def _get_available_margin(self) -> float:
        test_config: TestConfig = self.data_repository.get_test_config()
        return self.account_repository.get_balance() * (1 - test_config.margin_requirement)

    def _get_pending_order_margins(self) -> Tuple[float, float]:
        orders: List[Order] = self.order_repository.get_order_by_status(OrderStatus.PENDING)
        buy_margin: float = 0
        sell_margin: float = 0

        for order in orders:
            order_margin: float = self._get_margin(price=order.price, amount=order.amount)
            buy_margin += order_margin if order.direction == OrderDirection.BUY else 0
            sell_margin += order_margin if order.direction == OrderDirection.SELL else 0

        return buy_margin, sell_margin

    def _get_position_margins(self) -> Tuple[float, float]:
        buy_margin: float = 0
        sell_margin: float = 0
        position: Optional[Position] = self.account_repository.get_position()

        if position is None:
            return 0, 0

        position_margin: float = self._get_margin(price=position.average_price,
                                                  amount=position.amount)
        buy_margin += position_margin if position.direction == OrderDirection.BUY else 0
        sell_margin += position_margin if position.direction == OrderDirection.SELL else 0
        return buy_margin, sell_margin

    def _get_margin(self, price: float, amount: int) -> float:
        symbol: Symbol = self.data_repository.get_symbol()
        return price * amount * symbol.multiplier * symbol.margin_rate

    def _get_used_margins(self) -> Tuple[float, float]:
        position_margins: Tuple[float, float] = self._get_position_margins()
        pending_order_margins: Tuple[float, float] = self._get_pending_order_margins()
        return position_margins[0] + pending_order_margins[0], position_margins[1] + pending_order_margins[1]
