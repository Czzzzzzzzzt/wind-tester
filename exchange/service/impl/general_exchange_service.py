import logging
from typing import List, Optional

from broker.enums import OrderStatus, OrderType, OrderDirection
from broker.model import Order, Position
from broker.repository.account_repository import AccountRepository
from broker.repository.order_repository import OrderRepository
from broker.service.order_service import OrderService
from broker.service.risk_service import RiskService
from data.model import Symbol
from data.repository.data_repository import DataRepository
from exchange.service.clearing_service import ClearingService
from exchange.service.exchange_service import ExchangeService
from exchange.service.match_service import MatchService
from exchange.service.match_validation_service import MatchValidationService


class GeneralExchangeService(ExchangeService):

    def __init__(self, data_repository: DataRepository, order_repository: OrderRepository,
                 account_repository: AccountRepository):
        self.data_repository: DataRepository = data_repository
        self.order_repository: OrderRepository = order_repository
        self.account_repository: AccountRepository = account_repository

    def match_and_clear_all_orders(self, match_service: MatchService, clearing_service: ClearingService,
                                   risk_service: RiskService, order_service: OrderService,
                                   match_validation_service: MatchValidationService) -> None:
        pending_orders: List[Order] = self.order_repository.get_order_by_status(status=OrderStatus.PENDING)
        for order in pending_orders:
            if not risk_service.validate_account_risk():
                self.force_close_account(order_service=order_service, match_service=match_service,
                                         clearing_service=clearing_service)
                return
            if not match_validation_service.validate_match(order=order):
                continue
            match_service.match_order(order=order)
            clearing_service.clear_order(order=order)

    def examine_and_force_close_account(self, risk_service: RiskService, match_service: MatchService,
                                        clearing_service: ClearingService, order_service: OrderService) -> None:
        if not risk_service.validate_account_risk():
            self.force_close_account(order_service=order_service, match_service=match_service,
                                     clearing_service=clearing_service)

    def update_account_balance_on_bar(self) -> None:
        bar_close: float = self.data_repository.get_current_bar_data(name="close", timeframe="1m")
        position: Optional[Position] = self.account_repository.get_position()
        symbol: Symbol = self.data_repository.get_symbol()
        if position is None:
            return
        if position.direction == OrderDirection.BUY:
            unrealized_pnl: float = (bar_close - position.average_price) * position.amount * symbol.multiplier
        else:
            unrealized_pnl: float = (position.average_price - bar_close) * position.amount * symbol.multiplier
        self.account_repository.set_balance(balance=unrealized_pnl + self.account_repository.get_equity())

    def force_close_account(self, order_service: OrderService, match_service: MatchService,
                            clearing_service: ClearingService) -> None:
        self._cancel_all_orders(order_service=order_service)
        self._force_close_position(order_service=order_service, match_service=match_service,
                                   clearing_service=clearing_service)

    def _cancel_all_orders(self, order_service: OrderService) -> None:
        pending_orders: List[Order] = self.order_repository.get_order_by_status(status=OrderStatus.PENDING)
        for order in pending_orders:
            order_service.cancel_order(order_id=order.id)

    def _force_close_position(self, order_service: OrderService, match_service: MatchService,
                              clearing_service: ClearingService) -> None:
        position: Optional[Position] = self.account_repository.get_position()
        if position is None:
            return

        direction: OrderDirection = OrderDirection.BUY if position.direction == OrderDirection.SELL \
            else OrderDirection.SELL

        if direction == OrderDirection.BUY:
            price: float = self.data_repository.get_current_bar_data(name="ask", timeframe="1m")
        else:
            price: float = self.data_repository.get_current_bar_data(name="bid", timeframe="1m")

        order: Optional[Order] = order_service.create_order(symbol_id=position.symbol_id, price=price,
                                                            amount=position.amount, direction=direction,
                                                            order_type=OrderType.LMT)

        match_service.match_order(order=order)

        if order.status != OrderStatus.FILLED:
            logging.error(f"Force close position failed: {order}")
            raise RuntimeError(f"Force close position failed: {order}")

        clearing_service.clear_order(order=order)
