from abc import ABC, abstractmethod

class MenuItem(ABC):
    @abstractmethod
    def get_price(self) -> float:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

class IndividualItem(MenuItem):
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

    def get_price(self) -> float:
        return self.price

    def get_description(self) -> str:
        return self.name

class FoodCombo(MenuItem):
    def __init__(self, name: str, base_price_adjustment: float = 0.0):
        self.name = name
        self.base_price_adjustment = base_price_adjustment
        self.items: list[MenuItem] = []

    def add_item(self, item: MenuItem):
        self.items.append(item)

    def get_price(self) -> float:
        total_price = self.base_price_adjustment
        for item in self.items:
            total_price += item.get_price()
        return total_price

    def get_description(self) -> str:
        if not self.items:
            return f"{self.name} (vacío)"
        components = [item.get_description() for item in self.items]
        adjustment_str = f" (ajuste: ${self.base_price_adjustment:.2f})" if self.base_price_adjustment != 0 else ""
        return f"{self.name}{adjustment_str} [Contiene: {', '.join(components)}]"
