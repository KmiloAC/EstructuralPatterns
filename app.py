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
    if facade is None:
        return "Error: Sistema no disponible", 500
    return render_template('compra.html', sala_id=sala_id)

@app.route('/comprar', methods=['POST'])
def procesar_compra():
    if facade is None:
        return jsonify({"error": "Sistema no disponible"}), 500
    try:
        data = request.json
        asientos = data.get('asientos', [])
        payment_data = data.get('paymentData', {})
        
        # Aquí procesarías el pago con un gateway real
        tickets_html = [
            facade.comprar_entrada(asiento, "regular")
            for asiento in asientos
        ]
        
        return jsonify({
            "success": True,
            "ticket": "".join(tickets_html)
        })
    except Exception as e:
        logger.error(f"Error processing purchase: {e}")
        return jsonify({"error": "Error processing purchase"}), 500

@app.route('/static/<path:filename>')
def static_files(filename):
    return app.send_static_file(filename)

if __name__ == '__main__':
    # Disable reloader for Python 3.13 compatibility
    app.run(debug=True, use_reloader=False)