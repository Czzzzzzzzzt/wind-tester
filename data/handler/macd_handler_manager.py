from collections import deque
from datetime import datetime
from typing import Tuple, List, Optional

import pandas as pd

from data.handler.indicator_handler_manager import IndicatorHandlerManager
from data.model import DataHandler, IndicatorParams, MacdParams, MacdHandler
from data.repository.data_repository import DataRepository


class MacdHandlerManager(IndicatorHandlerManager):
    def __init__(self, timeframe: str, size: int, params: IndicatorParams,
                 data_repository: DataRepository) -> None:
        super().__init__(timeframe, size, params, data_repository)
        if not isinstance(params, MacdParams):
            raise Exception(f"params is not of type MacdParams")
        self.params: MacdParams = params
        self.timeframe: str = timeframe
        macd, signal = self._get_macd_and_signal(data_repository)
        self.macd: deque[float] = macd
        self.signal: deque[float] = signal
        self.macd_vo: deque[float] = deque(maxlen=size)
        self.signal_vo: deque[float] = deque(maxlen=size)
        bar_datetime: Optional[List[datetime]] = data_repository.get_all_data(name="datetime", timeframe=self.timeframe)
        assert bar_datetime is not None
        self.bar_datetime: deque[datetime] = deque(bar_datetime)

    def update(self, current_datetime: datetime) -> None:
        if self.bar_datetime[0] >= current_datetime:
            self.macd_vo.append(self.macd.popleft())
            self.signal_vo.append(self.signal.popleft())
            self.bar_datetime.popleft()

    def get_data_handler(self) -> DataHandler:
        return MacdHandler(macd=self.macd_vo, signal=self.signal_vo)

    def _get_macd_and_signal(self, data_repository: DataRepository) -> Tuple[deque[float], deque[float]]:
        bar_close: Optional[List[float]] = data_repository.get_all_data(name="close", timeframe=self.timeframe)
        if bar_close is None:
            raise Exception(f"No data for close in timeframe {self.timeframe}")
        df_close = pd.DataFrame(bar_close)
        df_close.columns = ['close']
        df_close['fast_ema'] = df_close['close'].ewm(span=self.params.fast_period, adjust=False).mean()
        df_close['slow_ema'] = df_close['close'].ewm(span=self.params.slow_period, adjust=False).mean()
        df_close['macd'] = df_close['fast_ema'] - df_close['slow_ema']
        df_close['signal'] = df_close['macd'].ewm(span=self.params.signal_period, adjust=False).mean()
        return deque(df_close['macd'].values), deque(df_close['signal'].values)
