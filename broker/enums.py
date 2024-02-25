from enum import Enum


class OrderDirection(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"


class OrderType(Enum):
    LMT = "LMT"
    STP = "STP"
