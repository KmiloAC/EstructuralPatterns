document.addEventListener('DOMContentLoaded', () => {
    // Setup para botones de compra
    document.querySelectorAll('.comprar-combo').forEach(btn => {
        btn.addEventListener('click', () => {
            const comboId = btn.dataset.combo;
            document.getElementById('combo-id').value = comboId;
            $('#pagoModal').modal('show');
        });
    });

    // Setup para formulario de pago
    document.getElementById('btn-pagar').addEventListener('click', async () => {
        const form = document.getElementById('pago-form');
        const formData = new FormData(form);
        const btnPagar = document.getElementById('btn-pagar');
        const errorDiv = document.getElementById('error-mensaje');
        
        try {
            btnPagar.disabled = true;
            btnPagar.textContent = 'Procesando...';
            errorDiv.style.display = 'none';

            // Crear objeto de datos de pago en el formato correcto
            const paymentData = {
                cardNumber: formData.get('cardNumber').replace(/\s/g, ''),
                cardExpiry: formData.get('cardExpiry'),
                cardCvv: formData.get('cardCvv')
            };

            const response = await fetch('/comprar-combo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    combo: formData.get('combo'),
                    payment_data: paymentData
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                $('#pagoModal').modal('hide');
                Swal.fire({
                    title: '¡Compra Exitosa!',
                    html: data.ticket,
                    icon: 'success'
                }).then(() => {
                    window.location.reload(); // Recargar página después de compra exitosa
                });
            } else {
                errorDiv.textContent = data.error || 'Error procesando la compra';
                errorDiv.style.display = 'block';
            }
        } catch (error) {
            console.error('Error:', error);
            errorDiv.textContent = 'Error procesando la compra';
            errorDiv.style.display = 'block';
        } finally {
            btnPagar.disabled = false;
            btnPagar.textContent = 'Pagar';
        }
    });
});
