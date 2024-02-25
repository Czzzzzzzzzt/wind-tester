import unittest
from unittest.mock import Mock, call

from broker.enums import OrderDirection
from broker.model import Order
from broker.repository.account_repository import AccountRepository
from data.repository.data_repository import DataRepository
from exchange.service.impl.general_clearing_service import GeneralClearingService


class TestBarClearingService(unittest.TestCase):
    def setUp(self):
        self.mock_account_repository = Mock(spec=AccountRepository)
        self.mock_data_repository = Mock(spec=DataRepository)
        self.service = GeneralClearingService(self.mock_account_repository, self.mock_data_repository)

    def test_update_position_with_no_position(self):
        self.mock_account_repository.get_position.return_value = None
        order = Mock(spec=Order, symbol_id="test", execution_price=10, direction=OrderDirection.BUY, amount=10)
        self.service._update_account_position(order)
        self.mock_account_repository.get_position.assert_called_once()
        _, kwargs = self.mock_account_repository.set_position.call_args
        position = kwargs["position"]
        self.assertEqual(position.symbol_id, "test")
        self.assertEqual(position.average_price, 10)
        self.assertEqual(position.amount, 10)
        self.assertEqual(position.direction, OrderDirection.BUY)

    def test_update_position_with_same_direction(self):
        self.mock_account_repository.get_position.return_value = Mock(average_price=10, amount=10,
                                                                      direction=OrderDirection.BUY)
        order = Mock(spec=Order, symbol_id="test", execution_price=10, direction=OrderDirection.BUY, amount=10)
        self.service._update_account_position(order)
        self.mock_account_repository.get_position.assert_called_once()
        _, kwargs = self.mock_account_repository.set_position.call_args
        position = kwargs["position"]
        self.assertEqual(position.amount, 20)
        self.assertEqual(position.average_price, 10)

    def test_update_position_with_opposite_direction(self):
        self.mock_account_repository.get_position.return_value = Mock(average_price=10, amount=10,
                                                                      direction=OrderDirection.BUY)
        order = Mock(spec=Order, symbol_id="test", execution_price=10, direction=OrderDirection.SELL, amount=5)
        self.service._update_account_position(order)
        self.mock_account_repository.get_position.assert_called_once()
        _, kwargs = self.mock_account_repository.set_position.call_args
        position = kwargs["position"]
        self.assertEqual(position.amount, 5)
        self.assertEqual(position.average_price, 10)

    def test_update_position_with_opposite_direction_equal_amount(self):
        self.mock_account_repository.get_position.return_value = Mock(average_price=10, amount=10,
                                                                      direction=OrderDirection.BUY)
        order = Mock(spec=Order, symbol_id="test", execution_price=10, direction=OrderDirection.SELL, amount=10)
        self.service._update_account_position(order)
        self.mock_account_repository.get_position.assert_called_once()
        self.mock_account_repository.set_position.assert_called_once_with(position=None)

    def test_update_position_with_opposite_direction_greater_amount(self):
        self.mock_account_repository.get_position.return_value = Mock(average_price=10, amount=10,
                                                                      direction=OrderDirection.BUY)
        order = Mock(spec=Order, symbol_id="test", execution_price=10, direction=OrderDirection.SELL, amount=15)
        self.service._update_account_position(order)
        self.mock_account_repository.get_position.assert_called_once()
        position = self.mock_account_repository.set_position.call_args[1]["position"]
        self.assertEqual(position.amount, 5)
        self.assertEqual(position.average_price, 10)
        self.assertEqual(position.direction, OrderDirection.SELL)

    def test_update_account_balance_with_no_position(self):
        self.mock_account_repository.get_position.return_value = None
        self.service._update_account_balance()
        self.mock_account_repository.set_balance.assert_not_called()

    def test_update_account_balance_with_buy_position(self):
        self.mock_account_repository.get_position.return_value = Mock(average_price=10, amount=10,
                                                                      direction=OrderDirection.BUY)
        self.mock_data_repository.get_current_bar_data.return_value = 11
        self.mock_data_repository.get_symbol.return_value = Mock(multiplier=1)
        self.mock_account_repository.get_equity.return_value = 100
        self.service._update_account_balance()
        self.mock_account_repository.set_balance.assert_called_once_with(balance=110)

    def test_update_account_balance_with_sell_position(self):
        self.mock_account_repository.get_position.return_value = Mock(average_price=10, amount=10,
                                                                      direction=OrderDirection.SELL)
        self.mock_data_repository.get_current_bar_data.return_value = 11
        self.mock_data_repository.get_symbol.return_value = Mock(multiplier=1)
        self.mock_account_repository.get_equity.return_value = 100
        self.service._update_account_balance()
        self.mock_account_repository.set_balance.assert_called_once_with(balance=90)

    def test_update_account_equity_with_no_position(self):
        self.mock_account_repository.get_equity.return_value = 100
        self.mock_account_repository.get_position.return_value = None
        order = Mock(spec=Order, execution_price=10, amount=10, direction=OrderDirection.BUY, commissions=10)

        self.service._update_account_equity(order)

        self.mock_account_repository.set_equity.assert_called_once_with(equity=90)

    def test_update_account_equity_with_opposite_position(self):
        self.mock_account_repository.get_equity.side_effect = [100, 90]
        self.mock_account_repository.get_position.return_value = Mock(average_price=10, amount=10,
                                                                      direction=OrderDirection.SELL)
        self.mock_data_repository.get_symbol.return_value = Mock(multiplier=1)
        order = Mock(spec=Order, id=1, execution_price=10, amount=10, direction=OrderDirection.BUY, commissions=10)

        self.service._update_account_equity(order)

        self.mock_account_repository.set_equity.assert_has_calls([call(equity=90), call(equity=90.0)])
