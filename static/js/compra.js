/**
 * Script para procesar la compra de entradas.
 * Envía datos de asientos y pago al endpoint '/procesar_compra' y actualiza la interfaz.
 */

// Función para procesar la compra
async function procesarCompra(asientos, paymentData, sala) {
    try {
        if (!asientos || asientos.length === 0) {
            throw new Error('Por favor seleccione al menos un asiento');
        }

        if (!paymentData || !paymentData.cardNumber) {
            throw new Error('Datos de pago incompletos');
        }

        const response = await fetch('/procesar_compra', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                asientos: asientos,
                payment_data: paymentData,
                sala: sala
            })
        });

        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Error procesando la compra');
        }

        return { 
            success: true, 
            tickets: data.tickets 
        };
    } catch (error) {
        console.error('Error al procesar la compra:', error);
        return { 
            success: false, 
            error: error.message || 'Error procesando la compra' 
        };
    }
}

function marcarAsientoComoOcupado(asiento) {
    const seatElement = document.querySelector(`[data-asiento="${asiento}"]`);
    if (seatElement) {
        seatElement.classList.remove('seleccionado');
        seatElement.classList.add('ocupado');
        seatElement.disabled = true;
        seatElement.style.pointerEvents = 'none';
        seatElement.style.backgroundColor = '#dc3545';
    }
}

async function actualizarEstadoAsientos(sala) {
    try {
        const response = await fetch(`/asientos-ocupados/${sala}`);
        const asientosOcupados = await response.json();
        
        // Actualizar todos los asientos según el estado del servidor
        asientosOcupados.forEach(asiento => {
            marcarAsientoComoOcupado(asiento);
        });
    } catch (error) {
        console.error('Error actualizando estado de asientos:', error);
    }
}

// Función para actualizar periódicamente el estado de los asientos
function iniciarActualizacionAutomatica(sala) {
    setInterval(() => actualizarEstadoAsientos(sala), 5000); // Actualizar cada 5 segundos
}
