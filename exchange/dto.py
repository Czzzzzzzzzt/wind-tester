from dataclasses import dataclass


@dataclass
class Ohlc:
    open: float
    high: float
    low: float
    close: float

    def __iter__(self):
        yield self.open
        yield self.high
        yield self.low
        yield self.close
