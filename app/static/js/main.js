document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bs = bootstrap.Alert.getOrCreateInstance(alert);
            bs.close();
        }, 5000);
    });

    document.querySelectorAll('.toggle-password').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const input = this.closest('.input-group').querySelector('input');
            const icon = this.querySelector('i');
            if (input.type === 'password') {
                input.type = 'text';
                icon.className = 'bi bi-eye-slash';
            } else {
                input.type = 'password';
                icon.className = 'bi bi-eye';
            }
        });
    });

    const deleteModal = document.getElementById('modalDelete');
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', function(event) {
            const btn = event.relatedTarget;
            const url = btn.getAttribute('data-url');
            const name = btn.getAttribute('data-name');
            document.getElementById('deleteModalBtn').href = url;
            document.getElementById('deleteModalMessage').textContent = '¿Estás seguro de eliminar "' + name + '"?';
        });
    }

    const tipoSelect = document.getElementById('tipo_id');
    const promoSelect = document.getElementById('promo_id');
    const precioFinalSpan = document.getElementById('precio-final');
    const duracionFinalSpan = document.getElementById('duracion-final');
    const promoInfo = document.getElementById('promo-info');

    function calcularPrecio() {
        const tipoId = tipoSelect ? tipoSelect.value : '';
        const promoId = promoSelect ? promoSelect.value : '';
        if (!tipoId) {
            if (precioFinalSpan) precioFinalSpan.textContent = '0';
            if (duracionFinalSpan) duracionFinalSpan.textContent = '0';
            if (promoInfo) promoInfo.classList.add('d-none');
            return;
        }
        let url = '/promociones/calcular?tipo_id=' + tipoId;
        if (promoId) url += '&promo_id=' + promoId;
        fetch(url)
            .then(r => r.json())
            .then(data => {
                if (precioFinalSpan) precioFinalSpan.textContent = data.precio.toFixed(2);
                if (duracionFinalSpan) duracionFinalSpan.textContent = data.dias;
                if (promoInfo && data.promo_nombre) {
                    promoInfo.classList.remove('d-none');
                    promoInfo.querySelector('strong').textContent = data.promo_nombre;
                } else if (promoInfo) {
                    promoInfo.classList.add('d-none');
                }
            });
    }

    if (tipoSelect) tipoSelect.addEventListener('change', calcularPrecio);
    if (promoSelect) promoSelect.addEventListener('change', calcularPrecio);

    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const overlay = document.getElementById('sidebarOverlay');

    if (sidebarToggle && sidebar) {
        function toggleSidebar() {
            sidebar.classList.toggle('show');
            sidebar.classList.toggle('hidden');
            document.getElementById('content').classList.toggle('wide');
            if (overlay && window.innerWidth < 768) overlay.classList.toggle('show');
        }

        sidebarToggle.addEventListener('click', toggleSidebar);
        if (overlay) overlay.addEventListener('click', toggleSidebar);
    }
});
