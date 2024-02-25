from datetime import datetime
from typing import List, Optional, Dict, Type

from common.http.api import get_bar_data
from common.http.request import GetBarDataRequest
from common.http.response import GetBarDataResponse
from data.handler.bar_data_handler_manager import BarDataDataHandlerManager
from data.handler.data_handler_manager import DataHandlerManager
from data.handler.indicator_handler_manager import IndicatorHandlerManager
from data.handler.macd_handler_manager import MacdHandlerManager
from data.model import DataHandler, TestConfig, IndicatorParams
from data.repository.data_repository import DataRepository
from data.service.data_service import DataService


class GeneralDataService(DataService):

    def __init__(self, data_repository: DataRepository):
        self.data_repository: DataRepository = data_repository
        self.data_handler_managers: List[DataHandlerManager] = []
        self.indicator_manager_constructors: Dict[str, Type[IndicatorHandlerManager]] = {}

    def get_current_bar_data(self, name: str, timeframe: str) -> Optional[float | datetime]:
        return self.data_repository.get_all_data(name=name, timeframe=timeframe)

    def subscribe_bar_data(self, timeframe: str) -> bool:
        config: TestConfig = self.data_repository.get_test_config()
        token: str = config.token
        start_date: datetime = config.start_date
        end_date: datetime = config.end_date
        symbol_id: str = config.symbol_id
        request: GetBarDataRequest = GetBarDataRequest(symbol_id=symbol_id, start_date=start_date, end_date=end_date,
                                                       timeframe=timeframe)
        try:
            response: GetBarDataResponse = get_bar_data(token=token, request=request)
            self.data_repository.save_data(timeframe=timeframe, data=response.data)
            return True
        except (Exception,):
            return False

    def get_bar_data_handler(self, name: str, timeframe: str, size: int) -> Optional[DataHandler]:
        try:
            bar_data_handler_manager: BarDataDataHandlerManager = BarDataDataHandlerManager(name=name,
                                                                                            timeframe=timeframe,
                                                                                            size=size,
                                                                                            data_repository=self.
                                                                                            data_repository)
            self.data_handler_managers.append(bar_data_handler_manager)
            return bar_data_handler_manager.get_data_handler()
        except (Exception,):
            return None

    def get_indicator_handler(self, name: str, timeframe: str, size: int, params: IndicatorParams) -> DataHandler:
        try:
            indicator_manager_constructor: Type[IndicatorHandlerManager] = self.indicator_manager_constructors[name]
            indicator_manager: IndicatorHandlerManager = (
                indicator_manager_constructor(timeframe=timeframe,
                                              size=size,
                                              params=params,
                                              data_repository=self.data_repository))
            self.data_handler_managers.append(indicator_manager)
            return indicator_manager.get_data_handler()
        except (Exception,):
            raise Exception(f"Indicator manager {name} not found")

    def update_handler(self, current_datetime: datetime) -> None:
        for data_handler_manager in self.data_handler_managers:
            data_handler_manager.update(current_datetime=current_datetime)

    def update_on_bar(self):
        self.update_handler(current_datetime=self.data_repository.get_current_bar_data(name="datetime", timeframe="1m"))
        self.data_repository.set_bar_count(bar_count=self.data_repository.get_bar_count() + 1)

    def _init_indicator_manager(self):
        self.indicator_manager_constructors['macd'] = MacdHandlerManager
