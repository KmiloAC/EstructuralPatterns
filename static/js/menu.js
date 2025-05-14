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
        
        try {
            const response = await fetch('/comprar-combo', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                $('#pagoModal').modal('hide');
                // Mostrar ticket
                Swal.fire({
                    title: '¡Compra Exitosa!',
                    html: data.ticket,
                    icon: 'success'
                });
            } else {
                document.getElementById('error-mensaje').textContent = data.error;
                document.getElementById('error-mensaje').style.display = 'block';
            }
        } catch (error) {
            console.error('Error:', error);
            document.getElementById('error-mensaje').textContent = 'Error procesando la compra';
            document.getElementById('error-mensaje').style.display = 'block';
        }
    });
});
