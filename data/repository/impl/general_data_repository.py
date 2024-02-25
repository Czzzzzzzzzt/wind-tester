import logging
from datetime import datetime
from typing import Optional, Dict, List

from data.model import TestConfig, Symbol
from data.repository.data_repository import DataRepository


class GeneralDataRepository(DataRepository):
    def __init__(self, symbol: Symbol, test_config: TestConfig):
        self.symbol: Symbol = symbol
        self.test_config: TestConfig = test_config
        self.bar_count: int = 0
        self.data: Dict[str, Dict[str, List[any]]] = {}
        self.timeframes: Dict[str, int] = {}
        self._init_timeframes()

    def get_bar_count(self) -> int:
        return self.bar_count

    def set_bar_count(self, bar_count: int) -> None:
        self.bar_count = bar_count

    def get_all_data(self, name: str, timeframe: str) -> Optional[List[float] | List[datetime]]:
        if timeframe not in self.timeframes:
            logging.error(f'Timeframe {timeframe} is not supported')
            return None
        if name not in self.data[timeframe]:
            logging.error(f'No data for {name} in timeframe {timeframe}')
            return None
        return self.data[timeframe][name]

    def get_current_bar_data(self, name: str, timeframe: str) -> Optional[datetime | float]:
        if timeframe not in self.timeframes:
            logging.error(f'Timeframe {timeframe} is not supported')
            return None
        if name not in self.data[timeframe]:
            logging.error(f'No data for {name} in timeframe {timeframe}')
            return None

        timeframe_to_int: int = self.timeframes[timeframe]
        mapped_bar_count: int = self.bar_count // timeframe_to_int

        if mapped_bar_count >= len(self.data[timeframe][name]):
            logging.error(f'No data for {name} in timeframe {timeframe} at bar {self.bar_count}')
            return None
        return self.data[timeframe][name][mapped_bar_count]

    def get_symbol(self) -> Symbol:
        return self.symbol

    def get_test_config(self) -> TestConfig:
        return self.test_config

    def save_data(self, timeframe: str, data: dict) -> None:
        if timeframe in self.data:
            logging.error(f'Data for timeframe {timeframe} already exists')
            return
        self.data[timeframe] = data

    def _init_timeframes(self) -> None:
        self.timeframes['1m'] = 1
        self.timeframes['15m'] = 15
        self.timeframes['30m'] = 30
        self.timeframes['1h'] = 60
        self.timeframes['4h'] = 240
