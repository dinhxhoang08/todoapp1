document.addEventListener('DOMContentLoaded', function() {
    // Dark mode toggle
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const htmlElement = document.documentElement;

    function setTheme(theme) {
        htmlElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);
        if (darkModeToggle) {
            darkModeToggle.innerHTML = theme === 'dark'
                ? '<i class="bi bi-sun-fill"></i>'
                : '<i class="bi bi-moon-fill"></i>';
        }
    }

    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);

    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            const current = htmlElement.getAttribute('data-bs-theme');
            setTheme(current === 'dark' ? 'light' : 'dark');
        });
    }

    // Toast notification handler
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) return;

        const toastData = evt.detail?.xhr?.getResponseHeader('HX-Trigger');
        if (toastData) {
            try {
                const triggers = JSON.parse(toastData);
                if (triggers.toast) {
                    showToast(triggers.toast.message, triggers.toast.type || 'success');
                }
            } catch(e) {}
        }
    });
});

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const icons = {
        success: 'bi-check-circle-fill text-success',
        error: 'bi-x-circle-fill text-danger',
        warning: 'bi-exclamation-triangle-fill text-warning',
        info: 'bi-info-circle-fill text-info'
    };

    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-bg-light border-0 show';
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="bi ${icons[type] || icons.info} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    container.appendChild(toast);
    setTimeout(() => {
        toast.remove();
    }, 4000);
}

// Reinitialize modals after HTMX swaps
document.body.addEventListener('htmx:afterSettle', function(evt) {
    // Handle modal initialization
    const modalElement = document.getElementById('taskModal') || document.getElementById('categoryModal') || document.getElementById('tagModal');
    if (modalElement && !modalElement._bsModal) {
        new bootstrap.Modal(modalElement);
    }
});
