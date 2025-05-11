from flask import Flask, render_template, jsonify, request, url_for
from models.facade import CineFacade
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
    return render_template('index.html', cartelera_html=facade.cartelera.mostrar_html())

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

@app.route('/comprar', methods=['POST'])
def procesar_compra():
    if facade is None:
        return jsonify({"success": False, "error": "Sistema no disponible"}), 500
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "Datos inválidos"}), 400
            
        asientos = data.get('asientos', [])
        if not asientos:
            return jsonify({"success": False, "error": "No se seleccionaron asientos"}), 400
        
        # Verificar si algún asiento ya está ocupado
        if any(asiento in asientos_ocupados for asiento in asientos):
            return jsonify({
                "success": False,
                "error": "Algunos asientos ya no están disponibles"
            }), 400
        
        # Procesar el pago
        payment_data = data.get('paymentData', {})
        if not payment_data or payment_data.get('cardNumber') != '4242424242424242':
            return jsonify({
                "success": False,
                "error": "Datos de pago inválidos"
            }), 400
            
        # Marcar asientos como ocupados y generar tickets
        tickets_html = []
        for asiento in asientos:
            try:
                ticket = facade.comprar_entrada(asiento, "regular")
                tickets_html.append(ticket)
                asientos_ocupados.add(asiento)
            except Exception as e:
                logger.error(f"Error generando ticket para asiento {asiento}: {e}")
                continue
        
        if not tickets_html:
            return jsonify({
                "success": False,
                "error": "Error generando tickets"
            }), 500
            
        return jsonify({
            "success": True,
            "ticket": "".join(tickets_html)
        })
        
    except Exception as e:
        logger.error(f"Error processing purchase: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/asientos-ocupados/<sala_id>')
def obtener_asientos_ocupados(sala_id):
    logger.info(f"Consultando asientos ocupados para sala: {sala_id}")
    try:
        asientos = list(asientos_ocupados)
        logger.info(f"Asientos ocupados en {sala_id}: {asientos}")
        return jsonify(asientos)
    except Exception as e:
        logger.error(f"Error obteniendo asientos ocupados para {sala_id}: {e}")
        return jsonify({"error": "Error al obtener asientos ocupados"}), 500

@app.route('/static/<path:filename>')
def static_files(filename):
    return app.send_static_file(filename)

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