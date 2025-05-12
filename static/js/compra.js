// Función para procesar la compra
async function procesarCompra(asientos, paymentData, sala) {
    try {
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

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error en la comunicación con el servidor');
        }

        const data = await response.json();
        
        if (data.success) {
            // Marcar asientos como ocupados visualmente
            asientos.forEach(asiento => {
                marcarAsientoComoOcupado(asiento);
            });
            // Actualizar el estado global
            actualizarEstadoAsientos(sala);
            return { success: true, tickets: data.tickets };
        } else {
            throw new Error(data.error || 'Error procesando la compra');
        }
    } catch (error) {
        console.error('Error al procesar la compra:', error);
        return { success: false, error: error.message };
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
