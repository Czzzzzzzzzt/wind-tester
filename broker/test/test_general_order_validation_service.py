import unittest
from unittest.mock import Mock

from broker.enums import OrderStatus
from broker.repository.order_repository import OrderRepository
from broker.service.impl.general_order_validation_service import GeneralOrderValidationService
from data.repository.data_repository import DataRepository


class TestGeneralOrderValidationService(unittest.TestCase):
    def setUp(self):
        self.data_repository = Mock(spec=DataRepository)
        self.order_repository = Mock(spec=OrderRepository)
        self.service = GeneralOrderValidationService(self.data_repository, self.order_repository)

    def test_validate_new_order_input(self):
        self.data_repository.get_symbol.return_value = Mock(minimum_tick_size=0.1)
        result = self.service.validate_new_order_input('symbol1', 10.0, 5)
        self.assertTrue(result)

    def test_validate_update_order_input(self):
        self.order_repository.get_order_by_id.return_value = Mock(status=OrderStatus.PENDING, symbol_id='symbol1')
        self.data_repository.get_symbol.return_value = Mock(minimum_tick_size=1)
        result = self.service.validate_update_order_input(1, 10.0, 5)
        self.assertTrue(result)

    def test_validate_cancel_order_input(self):
        self.order_repository.get_order_by_id.return_value = Mock(status=OrderStatus.PENDING)
        result = self.service.validate_cancel_order_input(1)
        self.assertTrue(result)
