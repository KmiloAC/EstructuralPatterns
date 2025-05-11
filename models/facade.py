# models/facade.py
from models.bridge import WebApp, VentaRegular
from models.composite import DiaCartelera, Funcion

class CineFacade:
    def __init__(self):
        self.cartelera = DiaCartelera("25 Oct 2023")
        self.cartelera.agregar(Funcion("Avengers", "18:00", "Sala IMAX"))

    def comprar_entrada(self, asiento: str, tipo_venta: str) -> str:
        canal = WebApp()
        venta = VentaRegular(canal)
        venta.realizar_venta(asiento)
        return canal.emitir_ticket({"asiento": asiento, "precio": venta.calcular_precio_base()})