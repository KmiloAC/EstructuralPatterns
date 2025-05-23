/**
 * Script principal para la sala de cine.
 * Gestiona la carga de asientos, selección, actualización del total a pagar y navegación entre pasos.
 */

let currentStep = 1;
let selectedSeats = [];
let occupiedSeats = new Set();

// Función para cargar asientos ocupados
async function cargarAsientosOcupados(salaId) {
    try {
        const response = await fetch(`/asientos-ocupados/${salaId}`);
        const asientos = await response.json();
        occupiedSeats = new Set(asientos);
        return occupiedSeats;
    } catch (error) {
        console.error('Error cargando asientos ocupados:', error);
        return new Set();
    }
}

async function inicializarSala(salaId) {
    const sala = document.getElementById('sala-cine');
    if (!sala) return;

    // Cargar asientos ocupados primero
    await cargarAsientosOcupados(salaId);

    // Crear solo 32 asientos
    for(let i = 1; i <= 32; i++) {
        const asientoId = `${salaId}-${i}`;
        const btn = document.createElement('button');
        btn.className = 'asiento';
        btn.dataset.asiento = asientoId;
        btn.textContent = i;
        
        if (occupiedSeats.has(asientoId)) {
            btn.classList.add('ocupado');
            btn.disabled = true;
            btn.title = 'Asiento no disponible';
        } else {
            btn.onclick = () => seleccionarAsiento(btn);
        }
        
        sala.appendChild(btn);
    }
}

function seleccionarAsiento(btn) {
    if (btn.disabled || btn.classList.contains('ocupado')) {
        return;
    }

    btn.classList.toggle('seleccionado');
    const asiento = btn.dataset.asiento;
    
    if (btn.classList.contains('seleccionado')) {
        selectedSeats.push(asiento);
    } else {
        selectedSeats = selectedSeats.filter(seat => seat !== asiento);
    }

    // Actualizar contador y total
    const seatsCount = document.getElementById('seats-count');
    const seatsTotal = document.getElementById('seats-total');
    if (seatsCount) seatsCount.textContent = selectedSeats.length;
    if (seatsTotal) seatsTotal.textContent = `$${(selectedSeats.length * 15000).toLocaleString('es-CO')} COP`;
}

function calcularTotal() {
    const precioBase = 15000; // Precio por entrada en COP
    const total = selectedSeats.length * precioBase;
    const totalElement = document.getElementById('total-pagar');
    if (totalElement) {
        const totalFormatted = total.toLocaleString('es-CO');
        totalElement.textContent = `Total a pagar por ${selectedSeats.length} asiento(s): $${totalFormatted} COP`;
    }
    return total;
}

function siguientePaso() {
    if (currentStep === 1 && selectedSeats.length === 0) {
        alert('Por favor selecciona al menos un asiento');
        return;
    }
    
    if (currentStep === 1) {
        // Actualizar total antes de mostrar form de pago
        calcularTotal();
    }
    
    document.getElementById(`step-${currentStep}`).classList.add('hidden');
    currentStep++;
    document.getElementById(`step-${currentStep}`).classList.remove('hidden');
    updateProgressBar();
}

function pasoAnterior() {
    document.getElementById(`step-${currentStep}`).classList.add('hidden');
    currentStep--;
    document.getElementById(`step-${currentStep}`).classList.remove('hidden');
    updateProgressBar();
}

function formatCardNumber(input) {
    let value = input.value.replace(/\s/g, '').replace(/\D/g, '');
    let formatted = '';
    for(let i = 0; i < value.length; i++) {
        if(i > 0 && i % 4 === 0) {
            formatted += ' ';
        }
        formatted += value[i];
    }
    input.value = formatted;
}

function formatExpiry(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length > 2) {
        input.value = value.slice(0,2) + '/' + value.slice(2);
    }
}

function validateCard(formData) {
    const cardNumber = formData.get('cardNumber').replace(/\s/g, '');
    const cardExpiry = formData.get('cardExpiry');
    const cardCvv = formData.get('cardCvv');

    if (cardNumber !== '4242424242424242') {
        throw new Error('Por favor usa la tarjeta de prueba proporcionada');
    }

    if (cardExpiry !== '12/25') {
        throw new Error('Por favor usa la fecha de vencimiento de prueba');
    }

    if (cardCvv !== '123') {
        throw new Error('Por favor usa el CVV de prueba');
    }

    return true;
}

function setupPaymentForm() {
    const form = document.getElementById('payment-form');
    if (!form) return;

    form.onsubmit = async (e) => {
        e.preventDefault();
        
        // Validar que haya asientos seleccionados
        if (selectedSeats.length === 0) {
            alert('Por favor seleccione al menos un asiento');
            return;
        }

        const formData = new FormData(form);
        const btnPagar = document.getElementById('btn-pagar');
        const errorDiv = document.getElementById('card-errors');
        
        try {
            // Deshabilitar botón y mostrar estado
            btnPagar.disabled = true;
            btnPagar.textContent = 'Procesando...';
            errorDiv.style.display = 'none';

            // Validar datos de tarjeta
            validateCard(formData);

            // Preparar datos para el servidor
            const requestData = {
                asientos: selectedSeats,
                total: calcularTotal(),
                paymentData: {
                    cardNumber: formData.get('cardNumber').replace(/\s/g, ''),
                    cardName: formData.get('cardName'),
                    cardExpiry: formData.get('cardExpiry'),
                    cardCvv: formData.get('cardCvv')
                }
            };

            // Enviar solicitud al servidor
            const response = await fetch('/comprar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Error en el proceso de pago');
            }

            // Actualizar UI con éxito
            document.getElementById('ticket').innerHTML = data.ticket;
            
            // Actualizar estado de asientos
            selectedSeats.forEach(asiento => {
                const btn = document.querySelector(`[data-asiento="${asiento}"]`);
                if (btn) {
                    btn.disabled = true;
                    btn.classList.remove('seleccionado');
                    btn.classList.add('ocupado');
                }
            });

            // Actualizar conjunto de asientos ocupados
            selectedSeats.forEach(asiento => occupiedSeats.add(asiento));

            // Limpiar selección
            selectedSeats = [];
            
            // Mostrar confirmación
            siguientePaso();

        } catch (error) {
            console.error('Error en el pago:', error);
            errorDiv.textContent = error.message;
            errorDiv.style.display = 'block';
            
            // Volver al paso de pago
            currentStep = 2;
            updateProgressBar();
            
        } finally {
            // Restaurar botón
            btnPagar.disabled = false;
            btnPagar.textContent = 'Pagar';
        }
    };
}

function volverCartelera() {
    window.location.href = '/';
}

function updateProgressBar() {
    document.querySelectorAll('.step').forEach((step, index) => {
        if (index + 1 <= currentStep) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
}
