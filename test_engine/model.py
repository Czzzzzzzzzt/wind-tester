from dataclasses import dataclass
from typing import List

from broker.broker_api import BrokerApi
from broker.model import Order
from broker.repository.account_repository import AccountRepository
from broker.repository.order_repository import OrderRepository
from broker.service.order_service import OrderService
from broker.service.order_validation_service import OrderValidationService
from broker.service.risk_service import RiskService
from data.data_api import DataApi
from data.repository.data_repository import DataRepository
from data.service.data_service import DataService
from exchange.exchange_api import ExchangeApi
from exchange.service.clearing_service import ClearingService
from exchange.service.exchange_service import ExchangeService
from exchange.service.match_service import MatchService
from exchange.service.match_validation_service import MatchValidationService


@dataclass
class RepositoryContainer:
    order_repository: OrderRepository
    data_repository: DataRepository
    account_repository: AccountRepository


@dataclass
class ServiceContainer:
    order_service: OrderService
    order_validation_service: OrderValidationService
    risk_service: RiskService
    data_service: DataService
    clearing_service: ClearingService
    exchange_service: ExchangeService
    match_service: MatchService
    match_validation_service: MatchValidationService


@dataclass
class ApiContainer:
    broker_api: BrokerApi
    data_api: DataApi
    exchange_api: ExchangeApi


@dataclass
class TestResult:
    order_history: List[Order]
    balance_history: List[float]
    equity_history: List[float]
