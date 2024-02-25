from abc import ABC

from data.model import DataHandler, IndicatorParams


class InitApi(ABC):
    def subscribe_bar_data(self, timeframe: str) -> bool:
        pass

    def get_data_handler(self, name: str, timeframe: str, size: int) -> DataHandler:
        pass

    def get_indicator_handler(self, name: str, timeframe: str, size: int, params: IndicatorParams) -> DataHandler:
        pass
