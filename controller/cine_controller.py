class CineController:
    def __init__(self):
        self._menu = {
            "combo1": {
                "nombre": "Combo Personal",
                "precio": 28000,  # Actualizado a COP
                "items": ["Crispetas Medianas", "Gaseosa 16oz"]
            },
            "combo2": {
                "nombre": "Combo Pareja",
                "precio": 45000,  # Actualizado a COP
                "items": ["Crispetas Grandes", "2 Gaseosas 16oz", "Chocolatina Jet"]
            },
            "combo3": {
                "nombre": "Combo Familiar",
                "precio": 65000,  # Actualizado a COP
                "items": ["2 Crispetas Grandes", "4 Gaseosas 16oz", "2 Chocolatinas Jet", "Nachos con Queso"]
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
        precio_formatted = "{:,.0f}".format(combo["precio"]).replace(",", ".")
        return f"""
        <div class='ticket-web'>
            <h3>🍿 Ticket Combo</h3>
            <h4>{combo['nombre']}</h4>
            <ul>
                {items_html}
            </ul>
            <p>Total: ${precio_formatted} COP</p>
        </div>
        """

# Crear una instancia global del controlador
cine_controller = CineController()
