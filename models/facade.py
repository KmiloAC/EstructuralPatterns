from .bridge import WebApp, VentaAbstract
from .composite import FoodCombo, IndividualItem

# models/facade.py
class CineFacade:
    def __init__(self):
        self.pelicula = "Avengers"
        self.hora = "18:00"
        self.sala = "Sala IMAX"
        self.asientos_ocupados = set()
        self.estado_asientos = {}
        self.menu_combos = self.crear_menu_combos()

    def crear_menu_combos(self) -> list[FoodCombo]:
        # Crear ítems individuales
        gaseosa = IndividualItem("Gaseosa", 6.0)
        palomitas = IndividualItem("Palomitas", 8.0)
        nachos = IndividualItem("Nachos", 7.5)
        hotdog = IndividualItem("Hot Dog", 9.0)

        # Crear combos
        combo_individual = FoodCombo("Combo Individual", -2.0)
        combo_individual.add_item(gaseosa)
        combo_individual.add_item(palomitas)

        combo_duo = FoodCombo("Combo Dúo", -3.5)
        combo_duo.add_item(combo_individual)
        combo_duo.add_item(nachos)

        combo_max = FoodCombo("Combo Max", -4.0)
        combo_max.add_item(combo_duo)
        combo_max.add_item(hotdog)

        return [combo_individual, combo_duo, combo_max]

    def generar_cartelera_html(self) -> str:
        sala_id = self.sala.replace(" ", "_")
        return f"""
        <div class='funcion card mb-3'>
            <div class='card-body'>
                <h4 class='card-title'>{self.pelicula}</h4>
                <p class='card-text'>Sala: {self.sala} | Hora: {self.hora}</p>
                <a href='/sala/{sala_id}' class='btn btn-primary btn-comprar'>
                    Comprar
                </a>
            </div>
        </div>
        """

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

    def emitir_ticket(self, datos: dict) -> str:
        """Genera un ticket en formato HTML"""
        return f"""
        <div class='ticket-web'>
            <h3>🎟️ Ticket Virtual</h3>
            <p>Asiento: {datos['asiento']}</p>
            <p>Precio: ${datos['precio']}</p>
            <img src='/static/qr.png' width='100'>
        </div>
        """

    def comprar_entrada(self, asiento: str, tipo_venta: str) -> str:
        """Genera un ticket individual"""
        precio_base = 15.0  # Precio fijo por entrada
        return self.emitir_ticket({"asiento": asiento, "precio": precio_base})

    def obtener_asientos_ocupados(self) -> dict:
        """Retorna el diccionario de estados de asientos"""
        return self.estado_asientos

    def comprar_combo(self, nombre_combo: str, payment_data: dict) -> tuple[bool, str]:
        pago_valido, error = self.verificar_pago(payment_data)
        if not pago_valido:
            return False, error

        combo = next((c for c in self.menu_combos if c.name == nombre_combo), None)
        if not combo:
            return False, f"Combo '{nombre_combo}' no disponible."

        canal = WebApp()
        venta = VentaAbstract(canal)
        ticket = venta.realizar_venta({
            "combo": combo.name,
            "descripcion": combo.get_description(),
            "precio": combo.get_price()
        })

        return True, ticket

    def obtener_menu_completo(self) -> list[dict]:
        return [{
            "nombre": combo.name,
            "descripcion": combo.get_description(),
            "precio": combo.get_price()
        } for combo in self.menu_combos]