"""
Módulo bridge:
Implementa el patrón Bridge para separar la abstracción de la emisión de tickets (ventas)
de la implementación de canales de venta.
"""

from abc import ABC, abstractmethod

class CanalVenta(ABC):
    @abstractmethod
    def emitir_ticket(self, datos: dict) -> str:
        pass

class WebApp(CanalVenta):
    def emitir_ticket(self, datos: dict) -> str:
        if 'combo' in datos:
            return f"""
            <div class='ticket-web'>
                <h3>🍔 Combo Comprado</h3>
                <p><strong>{datos['combo']}</strong></p>
                <p>Incluye: {datos['descripcion']}</p>
                <p>Precio: ${datos['precio']}</p>
                <img src='/static/qr.png' width='100'>
            </div>
            """
        else:
            return f"""
            <div class='ticket-web'>
                <h3>🎟️ Ticket Virtual</h3>
                <p>Asiento: {datos['asiento']}</p>
                <p>Precio: ${datos['precio']}</p>
                <img src='/static/qr.png' width='100'>
            </div>
            """

class VentaAbstract:
    def __init__(self, canal: CanalVenta):
        self.canal = canal

    def realizar_venta(self, datos: dict) -> str:
        """
        Realiza la venta delegando la emisión del ticket al canal.
        """
        return self.canal.emitir_ticket(datos)
