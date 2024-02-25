from datetime import datetime
from typing import Optional

from data.model import DataHandler, IndicatorParams
from data.service.data_service import DataService
from strategy.dependency.init_api import InitApi


class DataApi(InitApi):
    def __init__(self, data_service: DataService):
        self.data_service: DataService = data_service

    def get_current_bar_data(self, name: str, timeframe: str) -> Optional[float | datetime]:
        return self.data_service.get_current_bar_data(name=name, timeframe=timeframe)

    def subscribe_bar_data(self, timeframe: str) -> bool:
        return self.data_service.subscribe_bar_data(timeframe=timeframe)

    def get_bar_data_handler(self, name: str, timeframe: str, size: int) -> DataHandler:
        return self.data_service.get_bar_data_handler(name=name, timeframe=timeframe, size=size)

    def get_indicator_handler(self, name: str, timeframe: str, size: int, params: IndicatorParams) -> DataHandler:
        return self.data_service.get_indicator_handler(name=name, timeframe=timeframe, size=size, params=params)

    def update_on_bar(self):
        return self.data_service.update_on_bar()
