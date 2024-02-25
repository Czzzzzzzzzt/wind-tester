from collections import deque
from datetime import datetime
from typing import List, Optional

from data.handler.data_handler_manager import DataHandlerManager
from data.model import DataHandler, BarDataHandler
from data.repository.data_repository import DataRepository


class BarDataDataHandlerManager(DataHandlerManager):
    def __init__(self, name: str, timeframe: str, size: int, data_repository: DataRepository) -> None:
        bar_data: Optional[List[any]] = data_repository.get_all_data(name=name, timeframe=timeframe)
        if bar_data is None:
            raise Exception(f"No data for {name} in timeframe {timeframe}")
        self.bar_data: deque[any] = deque(bar_data)
        self.bar_data_vo: deque[any] = deque(maxlen=size)
        bar_data_datetime: List[datetime] = data_repository.get_all_data(name='datetime', timeframe=timeframe)
        self.bar_data_datetime: deque[datetime] = deque(bar_data_datetime)

    def update(self, current_datetime: datetime) -> None:
        if current_datetime >= self.bar_data_datetime[0]:
            self.bar_data_vo.append(self.bar_data.popleft())
            self.bar_data_datetime.popleft()

    def get_data_handler(self) -> DataHandler:
        return BarDataHandler(data=self.bar_data_vo)
