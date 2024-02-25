import logging

from broker.enums import OrderDirection
from broker.model import Order
from data.model import Symbol
from data.repository.data_repository import DataRepository
from exchange.service.match_validation_service import MatchValidationService


class GeneralMatchValidationService(MatchValidationService):

    def __init__(self, data_repository: DataRepository):
        self.data_repository: DataRepository = data_repository

    def validate_match(self, order: Order) -> bool:
        is_valid_limit: bool = self._validate_limit(order=order)
        is_valid_volume: bool = self._validate_volume(order=order)
        return is_valid_limit and is_valid_volume

    def _validate_limit(self, order: Order) -> bool:
        percent_change: float = self.data_repository.get_current_bar_data(name="percent_change", timeframe="1m")
        symbol: Symbol = self.data_repository.get_symbol()
        if order.direction == OrderDirection.BUY:
            if percent_change > 0 and percent_change > symbol.upper_limit:
                logging.info(f"Order {order.id} has been rejected due to upper limit breach")
                return False
        else:
            if percent_change < 0 and percent_change < symbol.lower_limit:
                logging.info(f"Order {order.id} has been rejected due to lower limit breach")
                return False
        return True

    def _validate_volume(self, order: Order) -> bool:
        volume: float = self.data_repository.get_current_bar_data(name="volume", timeframe="1m")
        if order.amount > volume:
            logging.info(f"Order {order.id} has been rejected due to insufficient volume")
            return False
        return True
