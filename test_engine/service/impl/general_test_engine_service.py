import logging
from datetime import datetime
from typing import Dict, Optional, List, Type

from broker.broker_api import BrokerApi
from broker.repository.account_repository import AccountRepository
from broker.repository.impl.general_account_repository import GeneralAccountRepository
from broker.repository.impl.general_order_repository import GeneralOrderRepository
from broker.repository.order_repository import OrderRepository
from broker.service.impl.general_order_service import GeneralOrderService
from broker.service.impl.general_order_validation_service import GeneralOrderValidationService
from broker.service.impl.general_risk_service import GeneralRiskService
from broker.service.order_service import OrderService
from broker.service.order_validation_service import OrderValidationService
from broker.service.risk_service import RiskService
from common.http.api import get_bar_data, get_symbol
from common.http.dto import SymbolDto
from common.http.request import GetBarDataRequest, GetSymbolRequest
from common.http.response import GetBarDataResponse, GetSymbolResponse
from data.data_api import DataApi
from data.model import TestConfig, Symbol
from data.repository.data_repository import DataRepository
from data.repository.impl.general_data_repository import GeneralDataRepository
from data.service.data_service import DataService
from data.service.impl.general_data_service import GeneralDataService
from exchange.exchange_api import ExchangeApi
from exchange.service.clearing_service import ClearingService
from exchange.service.exchange_service import ExchangeService
from exchange.service.impl.general_clearing_service import GeneralClearingService
from exchange.service.impl.general_exchange_service import GeneralExchangeService
from exchange.service.impl.general_match_service import GeneralMatchService
from exchange.service.impl.general_match_validation_service import GeneralMatchValidationService
from exchange.service.match_service import MatchService
from exchange.service.match_validation_service import MatchValidationService
from strategy.base_strategy import BaseStrategy
from test_engine.model import RepositoryContainer, ServiceContainer, ApiContainer
from test_engine.service.test_engine_service import TestEngineService


class GeneralTestEngineService(TestEngineService):
    def __init__(self):
        self.api_container: Optional[ApiContainer] = None
        self.repository_container: Optional[RepositoryContainer] = None
        self.service_container: Optional[ServiceContainer] = None
        self.test_config: Optional[TestConfig] = None
        self.strategy_timeframe_datetime: Optional[List[datetime]] = None
        self.strategy_timeframe_bar_count: int = 0
        self.balance_history: List[float] = []
        self.equity_history: List[float] = []

    def run_test(self, test_config: TestConfig, strategy_constructor: Type[BaseStrategy]) -> None:
        self.test_config: TestConfig = test_config
        self._init_containers()
        strategy: BaseStrategy = strategy_constructor(_=self.api_container.data_api)
        self.strategy_timeframe_datetime = (
            self.repository_container.data_repository.get_all_data(name="datetime",
                                                                   timeframe=self.test_config.timeframe))

        datetime_1m: List[datetime] = self.repository_container.data_repository.get_all_data(name="datetime",
                                                                                             timeframe="1m")
        logging.info('Starting test')
        for index, dt in enumerate(datetime_1m):
            if index == len(datetime_1m) - 1:
                logging.critical('Test finished')
                break
            try:
                self._update_strategy(current_datetime=dt, strategy=strategy)
                self.api_container.data_api.update_on_bar()
                self.api_container.exchange_api.update_account_balance_on_bar()
                self.api_container.exchange_api.examine_and_force_close_account()
                self.balance_history.append(self.repository_container.account_repository.get_balance())
                self.equity_history.append(self.repository_container.account_repository.get_equity())

            except (IndexError,):
                logging.critical('Strategy backtest timeframe reached limit, test finished')
                break

    def _update_strategy(self, current_datetime: datetime, strategy: BaseStrategy) -> None:
        strategy_datetime: datetime = self.strategy_timeframe_datetime[self.strategy_timeframe_bar_count]
        if current_datetime >= strategy_datetime:
            self.strategy_timeframe_bar_count += 1
            strategy.on_bar(broker=self.api_container.broker_api)
            self.api_container.exchange_api.match_and_clear_all_orders()

    def _init_containers(self) -> None:
        self.repository_container: RepositoryContainer = self._init_repository_container()
        self.service_container: ServiceContainer = self._init_service_container()
        self.api_container: ApiContainer = self._init_api_container()

    def _init_api_container(self) -> ApiContainer:
        logging.info('Initializing api container')
        broker_api: BrokerApi = BrokerApi(order_service=self.service_container.order_service,
                                          risk_service=self.service_container.risk_service,
                                          order_validation_service=self.service_container.order_validation_service)
        data_api: DataApi = DataApi(data_service=self.service_container.data_service)
        exchange_api: ExchangeApi = (
            ExchangeApi(clearing_service=self.service_container.clearing_service,
                        exchange_service=self.service_container.exchange_service,
                        match_service=self.service_container.match_service,
                        match_validation_service=self.service_container.match_validation_service,
                        order_service=self.service_container.order_service,
                        risk_service=self.service_container.risk_service))
        return ApiContainer(broker_api=broker_api, data_api=data_api, exchange_api=exchange_api)

    def _init_service_container(self) -> ServiceContainer:
        logging.info('Initializing service container')
        order_service: OrderService = GeneralOrderService(order_repository=self.repository_container.order_repository,
                                                          data_repository=self.repository_container.data_repository)
        order_validation_service: OrderValidationService = GeneralOrderValidationService(
            order_repository=self.repository_container.order_repository,
            data_repository=self.repository_container.data_repository)
        risk_service: RiskService = GeneralRiskService(account_repository=self.repository_container.account_repository,
                                                       order_repository=self.repository_container.order_repository,
                                                       data_repository=self.repository_container.data_repository)
        data_service: DataService = GeneralDataService(data_repository=self.repository_container.data_repository)
        clearing_service: ClearingService = GeneralClearingService(
            account_repository=self.repository_container.account_repository,
            data_repository=self.repository_container.data_repository)
        exchange_service: ExchangeService = GeneralExchangeService(
            data_repository=self.repository_container.data_repository,
            order_repository=self.repository_container.order_repository,
            account_repository=self.repository_container.account_repository)
        match_service: MatchService = GeneralMatchService(data_repository=self.repository_container.data_repository,
                                                          order_repository=self.repository_container.order_repository)
        match_validation_service: MatchValidationService = GeneralMatchValidationService(
            data_repository=self.repository_container.data_repository)
        return ServiceContainer(order_service=order_service, order_validation_service=order_validation_service,
                                risk_service=risk_service, data_service=data_service, clearing_service=clearing_service,
                                exchange_service=exchange_service, match_service=match_service,
                                match_validation_service=match_validation_service)

    def _init_repository_container(self) -> RepositoryContainer:
        order_repository: OrderRepository = GeneralOrderRepository()
        account_repository: AccountRepository = GeneralAccountRepository(initial_equity=self.test_config.initial_equity)
        data_repository: DataRepository = GeneralDataRepository(symbol=self._fetch_symbol(),
                                                                test_config=self.test_config)
        data_repository.save_data(timeframe='1m', data=self._fetch_1m_bar_data())
        data_repository.save_data(timeframe=self.test_config.timeframe, data=self._fetch_test_data())
        return RepositoryContainer(order_repository=order_repository, account_repository=account_repository,
                                   data_repository=data_repository)

    def _fetch_symbol(self) -> Symbol:
        symbol_id: str = self.test_config.symbol_id
        request: GetSymbolRequest = GetSymbolRequest(symbol_id=symbol_id)
        try:
            logging.info('Fetching symbol')
            response: GetSymbolResponse = get_symbol(request=request, token=self.test_config.token)
            symbol_dto: SymbolDto = response.data
            symbol: Symbol = Symbol(id=symbol_dto.symbolId, minimum_tick_size=symbol_dto.minimumTickSize,
                                    multiplier=symbol_dto.multiplier, commission_fee=symbol_dto.commissionFee,
                                    commission_rate=symbol_dto.commissionRate, margin_rate=symbol_dto.marginRate,
                                    upper_limit=symbol_dto.upperLimit, lower_limit=symbol_dto.lowerLimit)
            return symbol
        except (Exception,):
            logging.error('Failed to fetch symbol')
            raise RuntimeError('Failed to fetch symbol')

    def _fetch_1m_bar_data(self) -> Dict:
        token: str = self.test_config.token
        symbol_id: str = self.test_config.symbol_id
        start_date: datetime = self.test_config.start_date
        end_date: datetime = self.test_config.end_date
        request: GetBarDataRequest = GetBarDataRequest(symbol_id=symbol_id, start_date=start_date, end_date=end_date,
                                                       timeframe='1m')

        try:
            logging.info('Fetching 1m bar data')
            response: GetBarDataResponse = get_bar_data(token=token, request=request)
            return response.data
        except (Exception,):
            logging.error('Failed to fetch 1m bar data')
            raise RuntimeError('Failed to fetch 1m bar data')

    def _fetch_test_data(self) -> Optional[Dict]:
        if self.test_config.timeframe == "1m":
            return None

        token: str = self.test_config.token
        symbol_id: str = self.test_config.symbol_id
        start_date: datetime = self.test_config.start_date
        end_date: datetime = self.test_config.end_date
        timeframe: str = self.test_config.timeframe
        request: GetBarDataRequest = GetBarDataRequest(symbol_id=symbol_id, start_date=start_date, end_date=end_date,
                                                       timeframe=timeframe)
        try:
            logging.info(f'Fetching {timeframe} bar data')
            response: GetBarDataResponse = get_bar_data(token=token, request=request)
            return response.data
        except (Exception,):
            logging.error(f'Failed to fetch {timeframe} bar data')
            raise RuntimeError(f'Failed to fetch {timeframe} bar data')
