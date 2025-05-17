from .bridge import WebApp, VentaAbstract
from .composite import FoodCombo, IndividualItem

"""
Módulo facade: Provee una interfaz simplificada para interactuar con la lógica del sistema de cine.
Esta clase encapsula la gestión de funciones como la creación de combos de alimentos, 
la generación y emisión de tickets, la validación de asientos y pagos, y el manejo de compras.
Utiliza patrones de diseño (Composite y Bridge) para estructurar la venta y combinaciones de productos.
"""

class CineFacade:
    def __init__(self):
        # Inicializa datos básicos de la función cinematográfica, estados de asientos y menú de combos.
        self.pelicula = "Avengers"
        self.hora = "18:00"
        self.sala = "Sala IMAX"
        self.asientos_ocupados = set()
        self.estado_asientos = {}
        self.menu_combos = self.crear_menu_combos()

    def crear_menu_combos(self) -> list[FoodCombo]:
        """
        Crea y configura el menú de combos aplicando el patrón Composite.
        
        Genera:
            - Combo Individual: Incluye gaseosa y palomitas.
            - Combo Dúo: Combina un Combo Individual y nachos.
            - Combo Max: Combina un Combo Dúo y hotdog.
            
        Returns:
            Lista de FoodCombo disponibles para la compra de combos.
        """
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
        """
        Genera el HTML para la cartelera de la función.
        
        Reemplaza espacios en el nombre de la sala para formar la URL correcta, e inserta
        los detalles de película, sala y hora, junto con un botón para acceder a la compra.
        
        Returns:
            Cadena HTML con la información de la función.
        """
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
        """
        Verifica la disponibilidad de los asientos solicitados.
        
        Recorre la lista de asientos y comprueba en el diccionario de estados si se encuentran ocupados.
        
        Args:
            asientos: Lista de identificadores de asientos a verificar.
            
        Returns:
            Una tupla donde el primer valor es un booleano indicando disponibilidad, y el
            segundo un mensaje de error en caso de que el asiento no esté disponible.
        """
        for asiento in asientos:
            if asiento in self.estado_asientos and self.estado_asientos[asiento] == "ocupado":
                return False, f"El asiento {asiento} ya no está disponible"
        return True, ""

    def verificar_pago(self, payment_data: dict) -> tuple[bool, str]:
        """
        Valida los datos de pago recibidos.
        
        Se requieren datos completos y se comparan contra valores de prueba predeterminados.
        
        Args:
            payment_data: Diccionario con los detalles del pago.
            
        Returns:
            Una tupla donde el primer elemento indica si el pago es válido y el segundo un mensaje de error.
        """
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
        """
        Procesa la compra de entradas para los asientos indicados.
        
        Se verifican primero la disponibilidad de los asientos y la validez de los datos de pago.
        Si todo es correcto, genera un ticket para cada asiento, actualiza el estado de los mismos,
        y retorna una lista de tickets generados.
        
        Args:
            asientos: Lista de asientos solicitados.
            payment_data: Información del pago.
            
        Returns:
            Una tupla que contiene:
                - Booleano indicando éxito.
                - Mensaje de error (vacío si no hay error).
                - Lista de tickets en formato HTML.
        """
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
        """
        Genera y retorna un ticket virtual en formato HTML.
        
        Presenta la información del asiento y el precio, e incluye una imagen QR simulada.
        
        Args:
            datos: Diccionario con 'asiento' y 'precio'.
            
        Returns:
            Cadena HTML que representa el ticket virtual.
        """
        return f"""
        <div class='ticket-web'>
            <h3>🎟️ Ticket Virtual</h3>
            <p>Asiento: {datos['asiento']}</p>
            <p>Precio: ${datos['precio']}</p>
            <img src='/static/qr.png' width='100'>
        </div>
        """

    def comprar_entrada(self, asiento: str, tipo_venta: str) -> str:
        """
        Genera un ticket individual para un asiento específico.
        
        Utiliza un precio base, que se formatea en moneda COP, y llama a emitir_ticket para generar el HTML.
        
        Args:
            asiento: Identificador del asiento.
            tipo_venta: Tipo de venta (e.g. "regular"). Actualmente no se usa para lógica adicional.
            
        Returns:
            Cadena HTML representando el ticket de compra.
        """
        precio_base = 15000  # Precio de entrada en COP
        return self.emitir_ticket({"asiento": asiento, "precio": self._format_price(precio_base)})

    def _format_price(self, price: float) -> str:
        """
        Formatea un número en un string de precio usando el formato de moneda COP.
        
        Args:
            price: Valor numérico del precio.
            
        Returns:
            Cadena con el precio formateado, separando miles con puntos.
        """
        return "{:,.0f}".format(price).replace(",", ".")

    def obtener_asientos_ocupados(self) -> dict:
        """
        Retorna el estado actual de los asientos.
        
        Cada asiento tiene un estado asignado (por ejemplo, "ocupado").
        
        Returns:
            Diccionario mapeando cada asiento a su estado.
        """
        return self.estado_asientos

    def comprar_combo(self, nombre_combo: str, payment_data: dict) -> tuple[bool, str]:
        """
        Procesa la compra de un combo alimenticio.
        
        Verifica primero la validez del pago, busca el combo en el menú y,
        utilizando el patrón Bridge, realiza la venta que genera un ticket.
        
        Args:
            nombre_combo: Nombre del combo a comprar.
            payment_data: Información del pago.
            
        Returns:
            Tupla con un booleano de éxito y el ticket en HTML o un mensaje de error.
        """
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
        """
        Retorna una representación completa del menú de combos.
        
        Cada entrada del menú incluye nombre, descripción y precio del combo.
        
        Returns:
            Lista de diccionarios con la información de cada combo.
        """
        return [{
            "nombre": combo.name,
            "descripcion": combo.get_description(),
            "precio": combo.get_price()
        } for combo in self.menu_combos]