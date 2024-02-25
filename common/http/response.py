from dataclasses import dataclass
from typing import Dict

from common.http.dto import SymbolDto


@dataclass
class GetBarDataResponse:
    status: int
    message: str
    data: Dict


@dataclass
class GetSymbolResponse:
    status: int
    message: str
    data: SymbolDto
