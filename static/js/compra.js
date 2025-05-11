// Función para procesar la compra
async function procesarCompra(asientos, paymentData) {
    try {
        const response = await fetch('/procesar_compra', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                asientos: asientos,
                payment_data: paymentData
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Marcar asientos como ocupados visualmente
            asientos.forEach(asiento => {
                const seatElement = document.querySelector(`[data-asiento="${asiento}"]`);
                if (seatElement) {
                    seatElement.classList.remove('seleccionado');
                    seatElement.classList.add('ocupado');
                    seatElement.disabled = true;
                }
            });
            return { success: true, tickets: data.tickets };
        } else {
            return { success: false, error: data.error };
        }
    } catch (error) {
        console.error('Error al procesar la compra:', error);
        return { success: false, error: 'Error en la comunicación con el servidor' };
    }
}
