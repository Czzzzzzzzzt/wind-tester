from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from broker.enums import OrderStatus, OrderDirection, OrderType


@dataclass
class Order:
    id: int
    symbol_id: str
    price: float
    amount: int
    direction: OrderDirection
    type: OrderType
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    commissions: Optional[float]
    execution_price: Optional[float]


@dataclass
class Position:
    symbol_id: str
    amount: int
    direction: OrderDirection
    average_price: float


@dataclass
class Account:
    balance: float
    equity: float
    position: Optional[Position]
