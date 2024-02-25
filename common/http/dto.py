from dataclasses import dataclass


@dataclass
class SymbolDto:
    symbolId: str
    minimumTickSize: float
    multiplier: int
    marginRate: float
    upperLimit: float
    lowerLimit: float
    commissionFee: float
    commissionRate: float
