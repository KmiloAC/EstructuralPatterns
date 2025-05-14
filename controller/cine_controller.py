class CineController:
    def __init__(self):
        self._menu = {
            "combo1": {
                "nombre": "Combo Personal",
                "precio": 15.0,
                "items": ["Palomitas medianas", "Refresco mediano"]
            },
            "combo2": {
                "nombre": "Combo Pareja",
                "precio": 25.0,
                "items": ["Palomitas grandes", "2 Refrescos medianos"]
            },
            "combo3": {
                "nombre": "Combo Familiar",
                "precio": 35.0,
                "items": ["2 Palomitas grandes", "4 Refrescos medianos"]
            }
        }

    def get_menu(self) -> dict:
        return dict(self._menu)  # Return a copy of the menu dictionary

    def comprar_combo(self, combo_id: str, datos_pago: dict):
        try:
            # Validar que el combo exista
            if combo_id not in self._menu:
                return False, "Combo no válido"
            
            # Validar datos de pago
            if not self._validar_pago(datos_pago):
                return False, "Datos de pago inválidos"

            combo = self._menu[combo_id]
            return True, self._generar_ticket_combo(combo)
        except Exception as e:
            return False, f"Error al procesar la compra: {str(e)}"

    def _validar_pago(self, datos_pago: dict) -> bool:
        """Validar los datos de pago"""
        return (
            datos_pago.get('cardNumber', '').strip() == '4242424242424242' and
            datos_pago.get('cardExpiry', '').strip() == '12/25' and
            datos_pago.get('cardCvv', '').strip() == '123'
        )

    def _generar_ticket_combo(self, combo: dict) -> str:
        items_html = "\n".join([f"<li>{item}</li>" for item in combo["items"]])
        return f"""
        <div class='ticket-web'>
            <h3>🍿 Ticket Combo</h3>
            <h4>{combo['nombre']}</h4>
            <ul>
                {items_html}
            </ul>
            <p>Total: ${combo['precio']:.2f}</p>
        </div>
        """

# Crear una instancia global del controlador
cine_controller = CineController()
