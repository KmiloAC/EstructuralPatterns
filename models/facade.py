# models/facade.py
from models.bridge import WebApp, VentaRegular
from models.composite import DiaCartelera, Funcion

class CineFacade:
    def __init__(self):
        self.cartelera = DiaCartelera("25 Oct 2023")
        self.cartelera.agregar(Funcion("Avengers", "18:00", "Sala IMAX"))
        self.asientos_ocupados = set()
        self.estado_asientos = {}  # Nuevo diccionario para estados de asientos

    def verificar_disponibilidad(self, asientos: list) -> tuple[bool, str]:
        """Verifica si los asientos están disponibles"""
        for asiento in asientos:
            if asiento in self.estado_asientos and self.estado_asientos[asiento] == "ocupado":
                return False, f"El asiento {asiento} ya no está disponible"
        return True, ""

    def verificar_pago(self, payment_data: dict) -> tuple[bool, str]:
        """Verifica los datos de pago"""
        if not payment_data:
            return False, "Datos de pago faltantes"
            
        # Validación de tarjeta de prueba
        if payment_data.get('cardNumber') != '4242424242424242':
            return False, "Número de tarjeta inválido"
            
        if payment_data.get('cardExpiry') != '12/25':
            return False, "Fecha de expiración inválida"
            
        if payment_data.get('cardCvv') != '123':
            return False, "CVV inválido"
            
        return True, ""

    def procesar_compra(self, asientos: list, payment_data: dict) -> tuple[bool, str, list]:
        """Procesa la compra completa incluyendo verificación y generación de tickets"""
        disponible, error = self.verificar_disponibilidad(asientos)
        if not disponible:
            return False, error, []

        pago_valido, error = self.verificar_pago(payment_data)
        if not pago_valido:
            return False, error, []

        tickets = []
        try:
            for asiento in asientos:
                ticket = self.comprar_entrada(asiento, "regular")
                tickets.append(ticket)
                self.asientos_ocupados.add(asiento)
                self.estado_asientos[asiento] = "ocupado"  # Marcar asiento como ocupado
            return True, "", tickets
        except Exception as e:
            return False, f"Error generando tickets: {str(e)}", []

    def comprar_entrada(self, asiento: str, tipo_venta: str) -> str:
        """Genera un ticket individual"""
        canal = WebApp()
        venta = VentaRegular(canal)
        venta.realizar_venta(asiento)
        return canal.emitir_ticket({"asiento": asiento, "precio": venta.calcular_precio_base()})

    def obtener_asientos_ocupados(self) -> dict:
        """Retorna el diccionario de estados de asientos"""
        return self.estado_asientos