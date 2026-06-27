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
    const sidebarClose = document.getElementById('sidebarClose');
    const overlay = document.getElementById('sidebarOverlay');

    function closeSidebar() {
        sidebar.classList.remove('show');
        sidebar.classList.add('hidden');
        document.getElementById('content').classList.add('wide');
        if (overlay) overlay.classList.remove('show');
    }

    function toggleSidebar() {
        const isOpen = sidebar.classList.contains('show');
        if (isOpen) {
            closeSidebar();
        } else {
            sidebar.classList.remove('hidden');
            sidebar.classList.add('show');
            document.getElementById('content').classList.remove('wide');
            if (overlay && window.innerWidth < 768) overlay.classList.add('show');
        }
    }

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', toggleSidebar);
        if (overlay) overlay.addEventListener('click', closeSidebar);
        if (sidebarClose) sidebarClose.addEventListener('click', closeSidebar);
    }

    document.querySelectorAll('#sidebar .nav-link').forEach(function(link) {
        link.addEventListener('click', function() {
            if (window.innerWidth < 768) closeSidebar();
        });
    });
});
