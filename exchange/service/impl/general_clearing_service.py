import logging
from typing import Optional

from broker.enums import OrderDirection
from broker.model import Order, Position
from broker.repository.account_repository import AccountRepository
from data.model import Symbol
from data.repository.data_repository import DataRepository
from exchange.service.clearing_service import ClearingService


class GeneralClearingService(ClearingService):
    def __init__(self, account_repository: AccountRepository, data_repository: DataRepository):
        self.account_repository: AccountRepository = account_repository
        self.data_repository: DataRepository = data_repository

    def clear_order(self, order: Order) -> None:
        self._update_order_commissions(order=order)
        self._update_account(order=order)

    def _update_account(self, order: Order) -> None:
        self._update_account_equity(order=order)
        self._update_account_position(order=order)
        self._update_account_balance()

    def _update_order_commissions(self, order: Order) -> None:
        symbol: Symbol = self.data_repository.get_symbol()
        commission: float = symbol.commission_rate * order.amount * order.execution_price * symbol.multiplier
        commission += symbol.commission_fee * order.amount
        order.commissions = commission

    def _update_account_equity(self, order: Order) -> None:
        self.account_repository.set_equity(equity=self.account_repository.get_equity() - order.commissions)

        position: Optional[Position] = self.account_repository.get_position()
        if position is not None and position.direction != order.direction:
            symbol: Symbol = self.data_repository.get_symbol()

            closed_amount: int = max(order.amount, position.amount)
            realized_pnl: float = (order.execution_price - position.average_price) * closed_amount * symbol.multiplier
            realized_pnl = realized_pnl if position.direction == OrderDirection.BUY else -1.0 * realized_pnl
            logging.info(f"Order {order.id} realized pnl: {realized_pnl}")
            self.account_repository.set_equity(equity=self.account_repository.get_equity() + realized_pnl)

    def _update_account_position(self, order: Order) -> None:
        position: Optional[Position] = self.account_repository.get_position()
        if position is None:
            self._update_account_no_position(order=order)
        elif position.direction == order.direction:
            self._update_account_same_direction(order=order, position=position)
        else:
            self._update_account_opposite_direction(order=order, position=position)

    def _update_account_balance(self) -> None:
        position: Optional[Position] = self.account_repository.get_position()
        unrealized_pnl: float = 0

        if position is None:
            return

        unrealized_pnl += self._get_position_unrealized_pnl(position=position)
        self.account_repository.set_balance(balance=self.account_repository.get_equity() + unrealized_pnl)

    def _get_position_unrealized_pnl(self, position: Position) -> float:
        close_price: float = self.data_repository.get_current_bar_data(name="close", timeframe="1m")
        symbol: Symbol = self.data_repository.get_symbol()

        unrealized_pnl: float = (close_price - position.average_price) * position.amount * symbol.multiplier
        return unrealized_pnl if position.direction == OrderDirection.BUY else -1.0 * unrealized_pnl

    def _update_account_no_position(self, order: Order) -> None:
        position: Position = Position(symbol_id=order.symbol_id, average_price=order.execution_price,
                                      amount=order.amount,
                                      direction=order.direction)
        self.account_repository.set_position(position=position)

    def _update_account_same_direction(self, order: Order, position: Position) -> None:
        new_amount: int = position.amount + order.amount
        new_average_price: float = (position.average_price * position.amount +
                                    order.execution_price * order.amount) / new_amount
        position.amount = new_amount
        position.average_price = new_average_price
        self.account_repository.set_position(position=position)

    def _update_account_opposite_direction(self, order: Order, position: Position) -> None:
        new_amount: int = position.amount - order.amount
        if new_amount == 0:
            self.account_repository.set_position(position=None)
        else:
            if new_amount < 0:
                position.amount = -new_amount
                position.direction = order.direction
                position.average_price = order.execution_price
                self.account_repository.set_position(position=position)
            else:
                position.amount = new_amount
                self.account_repository.set_position(position=position)
