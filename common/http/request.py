from dataclasses import dataclass
from datetime import datetime


@dataclass
class GetBarDataRequest:
    symbol_id: str
    start_date: datetime
    end_date: datetime
    timeframe: str

    def to_dict(self):
        return {
            "symbolId": self.symbol_id,
            "startDate": self.start_date,
            "endDate": self.end_date,
            "timeframe": self.timeframe
        }


@dataclass
class GetSymbolRequest:
    symbol_id: str

    def to_dict(self):
        return {
            "symbolId": self.symbol_id
        }
