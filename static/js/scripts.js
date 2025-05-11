let currentStep = 1;
let selectedSeats = [];

document.addEventListener('DOMContentLoaded', () => {
    inicializarSala('default');
    setupPaymentForm();
});

function inicializarSala(salaId) {
    const sala = document.getElementById('sala-cine');
    if (!sala) return;

    for(let i = 1; i <= 32; i++) {
        const btn = document.createElement('button');
        btn.className = 'asiento';
        btn.dataset.asiento = `${salaId}-${i}`;
        btn.textContent = i;
        btn.onclick = () => seleccionarAsiento(btn);
        sala.appendChild(btn);
    }
}

function seleccionarAsiento(btn) {
    btn.classList.toggle('seleccionado');
    const asiento = btn.dataset.asiento;
    
    if (btn.classList.contains('seleccionado')) {
        selectedSeats.push(asiento);
    } else {
        selectedSeats = selectedSeats.filter(seat => seat !== asiento);
    }
}

function siguientePaso() {
    if (currentStep === 1 && selectedSeats.length === 0) {
        alert('Por favor selecciona al menos un asiento');
        return;
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

function setupPaymentForm() {
    const form = document.getElementById('payment-form');
    if (!form) return;

    form.onsubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch('/comprar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    asientos: selectedSeats,
                    paymentData: Object.fromEntries(new FormData(form))
                })
            });
            
            const data = await response.json();
            if (data.success) {
                document.getElementById('ticket').innerHTML = data.ticket;
                siguientePaso();
            }
        } catch (error) {
            console.error('Error en el pago:', error);
            alert('Error procesando el pago');
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
