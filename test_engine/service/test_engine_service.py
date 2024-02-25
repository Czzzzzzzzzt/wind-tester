from abc import ABC

from data.model import TestConfig
from strategy.base_strategy import BaseStrategy


class TestEngineService(ABC):
    def run_test(self, test_config: TestConfig, strategy: BaseStrategy) -> None:
        pass
