from collections import deque
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Symbol:
    id: str
    minimum_tick_size: float
    multiplier: int
    commission_fee: float
    commission_rate: float
    margin_rate: float
    upper_limit: float
    lower_limit: float


@dataclass
class TestConfig:
    token: str
    symbol_id: str
    start_date: datetime
    end_date: datetime
    timeframe: str
    initial_equity: float
    spread: int = 1
    slippage: int = 0
    margin_requirement: float = 0.3


@dataclass
class DataHandler:
    pass


@dataclass
class BarDataHandler(DataHandler):
    data: deque[float]


@dataclass
class IndicatorParams:
    pass


@dataclass
class MacdParams(IndicatorParams):
    fast_period: int
    slow_period: int
    signal_period: int


@dataclass
class MacdHandler(DataHandler):
    macd: deque[float]
    signal: deque[float]
