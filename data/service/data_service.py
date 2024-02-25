from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from data.model import DataHandler, IndicatorParams


class DataService(ABC):
    @abstractmethod
    def get_current_bar_data(self, name: str, timeframe: str) -> Optional[float | datetime]:
        pass

    @abstractmethod
    def subscribe_bar_data(self, timeframe: str) -> bool:
        pass

    @abstractmethod
    def get_bar_data_handler(self, name: str, timeframe: str, size: int) -> Optional[DataHandler]:
        pass

    @abstractmethod
    def get_indicator_handler(self, name: str, timeframe: str, size: int,
                              params: IndicatorParams) -> Optional[DataHandler]:
        pass

    @abstractmethod
    def update_on_bar(self):
        pass
