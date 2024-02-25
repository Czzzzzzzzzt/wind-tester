from abc import ABC, abstractmethod

from strategy.dependency.broker import Broker
from strategy.dependency.init_api import InitApi


class BaseStrategy(ABC):
    @abstractmethod
    def __init__(self, _: InitApi):
        pass

    @abstractmethod
    def on_bar(self, broker: Broker):
        pass
