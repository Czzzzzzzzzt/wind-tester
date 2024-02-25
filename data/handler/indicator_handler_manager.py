import logging
from abc import ABC, abstractmethod

from data.handler.data_handler_manager import DataHandlerManager
from data.model import IndicatorParams
from data.repository.data_repository import DataRepository


class IndicatorHandlerManager(DataHandlerManager, ABC):
    @abstractmethod
    def __init__(self, timeframe: str, size: int, params: IndicatorParams,
                 data_repository: DataRepository) -> None:
        logging.debug(f"IndicatorHandlerManager.__init__({timeframe}, {size}, {params}, {data_repository})")
        pass
