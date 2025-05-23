"""
Aplicación Flask para gestionar la compra de entradas y combos en CinemaEstructurales.

Funcionalidades principales:
- Inicialización del objeto Flask y configuración de las plantillas.
- Configuración del logging y uso de un Facade (CineFacade) para la lógica del negocio.
- Endpoints:
    • '/' : Renderiza la página principal con la cartelera y menú de opciones.
    • '/comprar/<asiento>' : Procesa la compra de una entrada regular.
    • '/sala/<sala_id>' : Muestra la vista de compra para una sala específica.
    • '/procesar_compra' : Procesa la compra de entradas, validando datos y emitiendo tickets.
    • '/asientos-ocupados/<sala_id>' : Consulta los asientos ocupados de una sala.
    • '/comprar-combo' : Procesa la compra de combos.
    • Rutas para archivos estáticos y manejo de errores (404 y 500).
"""

from flask import Flask, render_template, jsonify, request, url_for
from models.facade import CineFacade
from controller.cine_controller import cine_controller  # Actualizar import
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Initialize Facade
try:
    facade = CineFacade()
except Exception as e:
    logger.error(f"Error initializing CineFacade: {e}")
    facade = None

# Agregar un set para mantener registro de asientos ocupados
asientos_ocupados = set()

@app.route('/')
def index():
    if facade is None:
        return "Error: Sistema no disponible", 500
    try:
        menu_data = cine_controller.get_menu()
        logger.info(f"Menu data: {menu_data}")
        if not isinstance(menu_data, dict):
            menu_data = {}
        return render_template('index.html', 
                            cartelera_html=facade.generar_cartelera_html(),
                            menu=menu_data)
    except Exception as e:
        logger.error(f"Error loading menu: {str(e)}")
        return render_template('index.html',
                            cartelera_html=facade.generar_cartelera_html(),
                            menu={})

@app.route('/comprar/<asiento>')
def comprar(asiento):
    if facade is None:
        return jsonify({"error": "Sistema no disponible"}), 500
    try:
        ticket_html = facade.comprar_entrada(asiento, "regular")
        return jsonify({"ticket": ticket_html})
    except Exception as e:
        logger.error(f"Error processing purchase: {e}")
        return jsonify({"error": "Error processing purchase"}), 500

@app.route('/sala/<sala_id>')
def sala(sala_id):
    logger.info(f"Accediendo a sala: {sala_id}")
    if facade is None:
        logger.error("Sistema no disponible al intentar acceder a sala")
        return "Error: Sistema no disponible", 500
    try:
        logger.info(f"Renderizando sala {sala_id}")
        return render_template('compra.html', sala_id=sala_id)
    except Exception as e:
        logger.error(f"Error al renderizar sala {sala_id}: {e}")
        return "Error: No se pudo cargar la sala", 500

@app.route('/procesar_compra', methods=['POST'])  # Cambiar ruta de /comprar a /procesar_compra
def procesar_compra():
    if facade is None:
        return jsonify({"success": False, "error": "Sistema no disponible"}), 500
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Datos inválidos"}), 400
            
        asientos = data.get('asientos', [])
        payment_data = data.get('payment_data', {})
        
        if not asientos:
            return jsonify({"success": False, "error": "No se seleccionaron asientos"}), 400
        
        # Procesar la compra usando el facade
        success, error, tickets = facade.procesar_compra(asientos, payment_data)
        
        if not success:
            return jsonify({"success": False, "error": error}), 400
            
        return jsonify({
            "success": True,
            "tickets": tickets
        })
        
    except Exception as e:
        logger.error(f"Error processing purchase: {str(e)}")
        return jsonify({"success": False, "error": "Error en el procesamiento de la compra"}), 500

@app.route('/asientos-ocupados/<sala_id>')
def obtener_asientos_ocupados(sala_id):
    logger.info(f"Consultando asientos ocupados para sala: {sala_id}")
    try:
        if facade is None:
            return jsonify([]), 500
        # Usar el estado de asientos del facade
        asientos = list(facade.obtener_asientos_ocupados().keys())
        logger.info(f"Asientos ocupados en {sala_id}: {asientos}")
        return jsonify(asientos)
    except Exception as e:
        logger.error(f"Error obteniendo asientos ocupados para {sala_id}: {e}")
        return jsonify([]), 500

@app.route('/static/<path:filename>')
def static_files(filename):
    return app.send_static_file(filename)

@app.route("/comprar-combo", methods=["POST"])  # Nueva ruta para combos
def comprar_combo():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Datos inválidos"}), 400

        combo = data.get('combo')
        payment_data = data.get('payment_data', {})

        if not combo or not payment_data:
            return jsonify({"success": False, "error": "Datos incompletos"}), 400

        ok, resultado = cine_controller.comprar_combo(combo, payment_data)
        if ok:
            return jsonify({"success": True, "ticket": resultado})
        else:
            return jsonify({"success": False, "error": resultado}), 400
    except Exception as e:
        logger.error(f"Error comprando combo: {str(e)}")
        return jsonify({"success": False, "error": "Error procesando la compra"}), 500

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"Página no encontrada: {request.url}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Error interno del servidor: {error}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Disable reloader for Python 3.13 compatibility
    app.run(debug=True, use_reloader=False)