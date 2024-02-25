import unittest
from unittest.mock import Mock

from broker.enums import OrderDirection, OrderType
from broker.repository.account_repository import AccountRepository
from broker.repository.order_repository import OrderRepository
from data.repository.data_repository import DataRepository
from exchange.service.impl.general_match_service import GeneralMatchService


class TestBarExchangeService(unittest.TestCase):
    def setUp(self):
        self.data_repository = Mock(spec=DataRepository)
        self.order_repository = Mock(spec=OrderRepository)
        self.account_repository = Mock(spec=AccountRepository)
        self.service = GeneralMatchService(self.data_repository, self.order_repository)

    def test_match_lmt_buy_order_success(self):
        self.data_repository.get_current_bar_data.return_value = 9.99
        self.data_repository.get_test_config.return_value = Mock(spread=1, slippage=0)
        self.data_repository.get_symbol.return_value = Mock(minimum_tick_size=0.01)
        order = Mock(symbol_id='symbol1', price=10.0, amount=5, direction=OrderDirection.BUY, type=OrderType.LMT)
        result = self.service._match_lmt_buy_order(order)
        self.assertTrue(result)

    def test_match_lmt_buy_order_fail(self):
        self.data_repository.get_current_bar_data.return_value = 10.0
        self.data_repository.get_test_config.return_value = Mock(spread=1, slippage=0)
        self.data_repository.get_symbol.return_value = Mock(minimum_tick_size=0.01)
        order = Mock(symbol_id='symbol1', price=10.0, amount=5, direction=OrderDirection.BUY, type=OrderType.LMT)
        result = self.service._match_lmt_buy_order(order)
        self.assertFalse(result)

    def test_match_lmt_sell_order_success(self):
        self.data_repository.get_current_bar_data.return_value = 10.01
        self.data_repository.get_test_config.return_value = Mock(spread=1, slippage=0)
        self.data_repository.get_symbol.return_value = Mock(minimum_tick_size=0.01)
        order = Mock(symbol_id='symbol1', price=10.0, amount=5, direction=OrderDirection.SELL, type=OrderType.LMT)
        result = self.service._match_lmt_sell_order(order)
        self.assertTrue(result)

    def test_match_lmt_sell_order_fail(self):
        self.data_repository.get_current_bar_data.return_value = 10.0
        self.data_repository.get_test_config.return_value = Mock(spread=1, slippage=0)
        self.data_repository.get_symbol.return_value = Mock(minimum_tick_size=0.01)
        order = Mock(symbol_id='symbol1', price=10.0, amount=5, direction=OrderDirection.SELL, type=OrderType.LMT)
        result = self.service._match_lmt_sell_order(order)
        self.assertFalse(result)

    def test_match_stp_buy_order_success(self):
        self.data_repository.get_current_bar_data.return_value = 9.99
        self.data_repository.get_test_config.return_value = Mock(spread=1, slippage=0)
        self.data_repository.get_symbol.return_value = Mock(minimum_tick_size=0.01)
        order = Mock(symbol_id='symbol1', price=10.0, amount=5, direction=OrderDirection.BUY, type=OrderType.STP)
        result = self.service._match_stp_buy_order(order)
        self.assertTrue(result)

    def test_match_stp_buy_order_fail(self):
        self.data_repository.get_current_bar_data.return_value = 9.98
        self.data_repository.get_test_config.return_value = Mock(spread=1, slippage=0)
        self.data_repository.get_symbol.return_value = Mock(minimum_tick_size=0.01)
        order = Mock(symbol_id='symbol1', price=10.0, amount=5, direction=OrderDirection.BUY, type=OrderType.STP)
        result = self.service._match_stp_buy_order(order)
        self.assertFalse(result)

    def test_match_stp_sell_order_success(self):
        self.data_repository.get_current_bar_data.return_value = 10.01
        self.data_repository.get_test_config.return_value = Mock(spread=1, slippage=0)
        self.data_repository.get_symbol.return_value = Mock(minimum_tick_size=0.01)
        order = Mock(symbol_id='symbol1', price=10.0, amount=5, direction=OrderDirection.SELL, type=OrderType.STP)
        result = self.service._match_stp_sell_order(order)
        self.assertTrue(result)

    def test_match_stp_sell_order_fail(self):
        self.data_repository.get_current_bar_data.return_value = 10.02
        self.data_repository.get_test_config.return_value = Mock(spread=1, slippage=0)
        self.data_repository.get_symbol.return_value = Mock(minimum_tick_size=0.01)
        order = Mock(symbol_id='symbol1', price=10.0, amount=5, direction=OrderDirection.SELL, type=OrderType.STP)
        result = self.service._match_stp_sell_order(order)
        self.assertFalse(result)
