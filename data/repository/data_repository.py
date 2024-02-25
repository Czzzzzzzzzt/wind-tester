from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List

from data.model import Symbol, TestConfig


class DataRepository(ABC):
    @abstractmethod
    def get_bar_count(self) -> int:
        pass

    @abstractmethod
    def set_bar_count(self, bar_count: int) -> None:
        pass

    @abstractmethod
    def get_current_bar_data(self, name: str, timeframe: str) -> Optional[datetime | float]:
        pass

    @abstractmethod
    def get_symbol(self) -> Symbol:
        pass

    @abstractmethod
    def get_test_config(self) -> TestConfig:
        pass

    @abstractmethod
    def get_all_data(self, name: str, timeframe: str) -> Optional[List[float] | List[datetime]]:
        pass

    @abstractmethod
    def save_data(self, timeframe: str, data: dict) -> None:
        pass
