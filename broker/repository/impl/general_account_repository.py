from typing import Optional

from broker.model import Position, Account
from broker.repository.account_repository import AccountRepository


class GeneralAccountRepository(AccountRepository):
    def __init__(self, initial_equity: float):
        self.account: Account = Account(balance=initial_equity, equity=initial_equity, position=None)

    def get_balance(self) -> float:
        return self.account.balance

    def get_equity(self) -> float:
        return self.account.equity

    def set_equity(self, equity: float) -> None:
        self.account.equity = equity

    def set_balance(self, balance: float) -> None:
        self.account.balance = balance

    def set_position(self, position: Optional[Position]) -> None:
        self.account.position = position

    def get_position(self) -> Optional[Position]:
        return self.account.position
