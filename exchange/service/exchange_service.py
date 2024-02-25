from abc import ABC, abstractmethod

from broker.service.order_service import OrderService
from broker.service.risk_service import RiskService
from exchange.service.clearing_service import ClearingService
from exchange.service.match_service import MatchService
from exchange.service.match_validation_service import MatchValidationService


class ExchangeService(ABC):
    @abstractmethod
    def match_and_clear_all_orders(self, match_service: MatchService, clearing_service: ClearingService,
                                   risk_service: RiskService, order_service: OrderService,
                                   match_validation_service: MatchValidationService) -> None:
        pass

    @abstractmethod
    def examine_and_force_close_account(self, risk_service: RiskService, match_service: MatchService,
                                        clearing_service: ClearingService, order_service: OrderService) -> None:
        pass

    @abstractmethod
    def update_account_balance_on_bar(self) -> None:
        pass
