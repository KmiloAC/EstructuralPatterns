from abc import ABC, abstractmethod

# models/bridge.py
class CanalVenta(ABC):
    @abstractmethod
    def emitir_ticket(self, datos: dict) -> str:
        pass

class VentaAbstract(ABC):
    def __init__(self, canal: CanalVenta):
        self.canal = canal

    @abstractmethod
    def calcular_precio_base(self) -> float:
        pass

    def realizar_venta(self, asiento: str) -> str:
        precio = self.calcular_precio_base()
        return self.canal.emitir_ticket({"asiento": asiento, "precio": precio})

class WebApp(CanalVenta):
    def emitir_ticket(self, datos: dict) -> str:
        return f"""
        <div class='ticket-web'>
            <h3>🎟️ Ticket Virtual</h3>
            <p>Asiento: {datos['asiento']}</p>
            <p>Precio: ${datos['precio']}</p>
            <img src='/static/qr.png' width='100'>
        </div>
        """

class Taquilla(CanalVenta):
    def emitir_ticket(self, datos: dict) -> str:
        return f"📠 Ticket Impreso: Asiento {datos['asiento']} - ${datos['precio']}"

class VentaRegular(VentaAbstract):
    def calcular_precio_base(self) -> float:
        return 15.0