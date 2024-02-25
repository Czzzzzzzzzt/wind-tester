from broker.service.order_service import OrderService
from broker.service.risk_service import RiskService
from exchange.service.clearing_service import ClearingService
from exchange.service.exchange_service import ExchangeService
from exchange.service.match_service import MatchService
from exchange.service.match_validation_service import MatchValidationService


class ExchangeApi:
    def __init__(self, match_service: MatchService, clearing_service: ClearingService,
                 risk_service: RiskService, order_service: OrderService, exchange_service: ExchangeService,
                 match_validation_service: MatchValidationService):
        self.match_service: MatchService = match_service
        self.clearing_service: ClearingService = clearing_service
        self.risk_service: RiskService = risk_service
        self.order_service: OrderService = order_service
        self.exchange_service: ExchangeService = exchange_service
        self.match_validation_service: MatchValidationService = match_validation_service

    def match_and_clear_all_orders(self) -> None:
        self.exchange_service.match_and_clear_all_orders(match_service=self.match_service,
                                                         clearing_service=self.clearing_service,
                                                         risk_service=self.risk_service,
                                                         order_service=self.order_service,
                                                         match_validation_service=self.match_validation_service)

    def examine_and_force_close_account(self) -> None:
        self.exchange_service.examine_and_force_close_account(risk_service=self.risk_service,
                                                              clearing_service=self.clearing_service,
                                                              order_service=self.order_service,
                                                              match_service=self.match_service)

    def update_account_balance_on_bar(self) -> None:
        self.exchange_service.update_account_balance_on_bar()
