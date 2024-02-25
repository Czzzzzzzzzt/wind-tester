import unittest
from unittest.mock import Mock

from broker.enums import OrderDirection
from broker.repository.account_repository import AccountRepository
from broker.repository.order_repository import OrderRepository
from broker.service.impl.general_risk_service import GeneralRiskService
from data.repository.data_repository import DataRepository


class TestBarRiskService(unittest.TestCase):
    def setUp(self):
        self.account_repository = Mock(spec=AccountRepository)
        self.order_repository = Mock(spec=OrderRepository)
        self.data_repository = Mock(spec=DataRepository)
        self.service = GeneralRiskService(self.account_repository, self.order_repository, self.data_repository)

    def test_validate_new_order_risk(self):
        self.account_repository.get_balance.return_value = 1000.0
        self.data_repository.get_test_config.return_value = Mock(margin_requirement=0.1)
        self.data_repository.get_symbol.return_value = Mock(multiplier=1, margin_rate=0.1)
        self.order_repository.get_order_by_status.return_value = []
        self.account_repository.get_position.return_value = None
        result = self.service.validate_new_order_risk('symbol1', 10.0, 5, OrderDirection.BUY)
        self.assertTrue(result)

    def test_validate_update_order_risk(self):
        self.account_repository.get_balance.return_value = 1000.0
        self.data_repository.get_test_config.return_value = Mock(margin_requirement=0.1)
        self.data_repository.get_symbol.return_value = Mock(multiplier=1, margin_rate=0.1)
        self.order_repository.get_order_by_id.return_value = Mock(symbol_id='symbol1', price=10.0, amount=5,
                                                                  direction=OrderDirection.BUY)
        self.order_repository.get_order_by_status.return_value = [Mock(symbol_id='symbol1', price=10.0, amount=5,
                                                                       direction=OrderDirection.BUY)]
        self.account_repository.get_position.return_value = None
        result = self.service.validate_update_order_risk(1, 20.0, 10)
        self.assertTrue(result)

    def test_validate_new_order_risk_with_existing_orders_and_positions(self):
        self.account_repository.get_balance.return_value = 1000.0
        self.data_repository.get_test_config.return_value = Mock(margin_requirement=0.1)
        self.data_repository.get_symbol.return_value = Mock(multiplier=1, margin_rate=0.1)
        self.order_repository.get_order_by_status.return_value = [
            Mock(symbol_id='symbol1', price=10.0, amount=5, direction=OrderDirection.BUY)]
        self.account_repository.get_position.return_value = Mock(symbol_id='symbol1', average_price=10.0, amount=5,
                                                                 direction=OrderDirection.BUY)

        result = self.service.validate_new_order_risk('symbol1', 10.0, 5, OrderDirection.BUY)
        self.assertTrue(result)

    def test_validate_update_order_risk_with_existing_orders_and_positions(self):
        self.account_repository.get_balance.return_value = 10000.0
        self.data_repository.get_test_config.return_value = Mock(margin_requirement=0.1)
        self.data_repository.get_symbol.return_value = Mock(multiplier=1, margin_rate=0.1)
        self.order_repository.get_order_by_id.return_value = Mock(symbol_id='symbol1', price=10.0, amount=5,
                                                                  direction=OrderDirection.BUY)
        self.order_repository.get_order_by_status.return_value = [
            Mock(symbol_id='symbol1', price=10.0, amount=5, direction=OrderDirection.BUY)]
        self.account_repository.get_position.return_value = Mock(symbol_id='symbol1', average_price=10.0, amount=5,
                                                                 direction=OrderDirection.BUY)
        result = self.service.validate_update_order_risk(1, 20.0, 10)
        self.assertTrue(result)

    def test_validate_new_order_risk_failure(self):
        self.account_repository.get_balance.return_value = 100.0
        self.data_repository.get_test_config.return_value = Mock(margin_requirement=0.1)
        self.data_repository.get_symbol.return_value = Mock(multiplier=1, margin_rate=0.1)
        self.order_repository.get_order_by_status.return_value = []
        self.account_repository.get_position.return_value = None
        result = self.service.validate_new_order_risk('symbol1', 1000.0, 5, OrderDirection.BUY)
        self.assertFalse(result)

    def test_validate_update_order_risk_failure(self):
        self.account_repository.get_balance.return_value = 100.0
        self.data_repository.get_test_config.return_value = Mock(margin_requirement=0.1)
        self.data_repository.get_symbol.return_value = Mock(multiplier=1, margin_rate=0.1)
        self.order_repository.get_order_by_id.return_value = Mock(symbol_id='symbol1', price=10.0, amount=5,
                                                                  direction=OrderDirection.BUY)
        self.order_repository.get_order_by_status.return_value = []
        self.account_repository.get_position.return_value = None
        result = self.service.validate_update_order_risk(1, 1000.0, 10)
        self.assertFalse(result)
