from abc import ABC, abstractmethod


class OrderValidationService(ABC):
    @abstractmethod
    def validate_new_order_input(self, symbol_id: str, price: float, amount: int) -> bool:
        pass

    @abstractmethod
    def validate_update_order_input(self, order_id: int, new_price: float, new_amount: int) -> bool:
        pass

    @abstractmethod
    def validate_cancel_order_input(self, order_id: int) -> bool:
        pass
