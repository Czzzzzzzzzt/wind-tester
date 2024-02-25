from abc import ABC, abstractmethod
from datetime import datetime

from data.model import DataHandler


class DataHandlerManager(ABC):
    @abstractmethod
    def update(self, current_datetime: datetime) -> None:
        pass

    @abstractmethod
    def get_data_handler(self) -> DataHandler:
        pass
