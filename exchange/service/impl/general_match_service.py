import logging
from typing import Optional, Tuple

from broker.enums import OrderDirection, OrderType, OrderStatus
from broker.model import Order
from broker.repository.order_repository import OrderRepository
from data.model import TestConfig, Symbol
from data.repository.data_repository import DataRepository
from exchange.dto import Ohlc
from exchange.service.match_service import MatchService


class GeneralMatchService(MatchService):
    def __init__(self, data_repository: DataRepository, order_repository: OrderRepository):
        self.data_repository: DataRepository = data_repository
        self.order_repository: OrderRepository = order_repository

    def match_order(self, order: Order) -> bool:
        if order.direction == OrderDirection.BUY and order.type == OrderType.LMT:
            return self._match_lmt_buy_order(order=order)
        elif order.direction == OrderDirection.SELL and order.type == OrderType.LMT:
            return self._match_lmt_sell_order(order=order)
        elif order.direction == OrderDirection.BUY and order.type == OrderType.STP:
            return self._match_stp_buy_order(order=order)
        elif order.direction == OrderDirection.SELL and order.type == OrderType.STP:
            return self._match_stp_sell_order(order=order)

    def _match_lmt_buy_order(self, order: Order) -> bool:
        match_price: Optional[float] = None
        bar_open, bar_high, bar_low, _ = self._get_ohlc()
        slippage, spread = self._get_slippage_and_spread()

        if bar_low + spread <= order.price:
            match_price = order.price

        if bar_high + spread <= order.price:
            match_price = bar_open + spread

        if match_price is None:
            return False

        match_price += slippage
        self._update_matched_order(order=order, match_price=match_price)
        return True

    def _match_lmt_sell_order(self, order: Order) -> bool:
        match_price: Optional[float] = None
        bar_open, bar_high, bar_low, _ = self._get_ohlc()
        slippage, spread = self._get_slippage_and_spread()

        if bar_high - spread >= order.price:
            match_price = order.price

        if bar_low - spread >= order.price:
            match_price = bar_open - spread

        if match_price is None:
            return False

        match_price -= slippage
        self._update_matched_order(order=order, match_price=match_price)
        return True

    def _match_stp_buy_order(self, order: Order) -> bool:
        match_price: Optional[float] = None
        bar_open, bar_high, bar_low, _ = self._get_ohlc()
        slippage, spread = self._get_slippage_and_spread()

        if bar_high + spread >= order.price:
            match_price = order.price

        if bar_low + spread >= order.price:
            match_price = bar_open + spread

        if match_price is None:
            return False

        match_price += slippage
        self._update_matched_order(order=order, match_price=match_price)
        return True

    def _match_stp_sell_order(self, order: Order) -> bool:
        match_price: Optional[float] = None
        bar_open, bar_high, bar_low, _ = self._get_ohlc()
        slippage, spread = self._get_slippage_and_spread()

        if bar_low - spread <= order.price:
            match_price = order.price

        if bar_high - spread <= order.price:
            match_price = bar_open - spread

        if match_price is None:
            return False

        match_price -= slippage
        self._update_matched_order(order=order, match_price=match_price)
        return True

    def _get_ohlc(self) -> Ohlc:
        bar_open: float = self.data_repository.get_current_bar_data(name="open", timeframe="1m")
        bar_high: float = self.data_repository.get_current_bar_data(name="high", timeframe="1m")
        bar_low: float = self.data_repository.get_current_bar_data(name="low", timeframe="1m")
        bar_close: float = self.data_repository.get_current_bar_data(name="close", timeframe="1m")

        assert bar_open is not None
        assert bar_high is not None
        assert bar_low is not None
        assert bar_close is not None

        return Ohlc(open=bar_open, high=bar_high, low=bar_low, close=bar_close)

    def _update_matched_order(self, order: Order, match_price: float) -> None:
        logging.info(f"Order {order.id} matched at {match_price}")
        order.updated_at = self.data_repository.get_current_bar_data(name="datetime", timeframe="1m")
        order.execution_price = match_price
        order.status = OrderStatus.FILLED

    def _get_slippage_and_spread(self) -> Tuple[float, float]:
        test_config: TestConfig = self.data_repository.get_test_config()

        symbol: Symbol = self.data_repository.get_symbol()

        return test_config.slippage * symbol.minimum_tick_size, test_config.spread * symbol.minimum_tick_size
