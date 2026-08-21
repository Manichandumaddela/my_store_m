document.addEventListener('DOMContentLoaded', function () {
    // ===== AUTO-HIDE MESSAGES =====
    const messages = document.querySelectorAll('.message');
    messages.forEach(function (message) {
        setTimeout(function () {
            message.style.opacity = '0';
            setTimeout(function () {
                message.style.display = 'none';
            }, 500);
        }, 5000);
    });

    // ===== CONFIRM DELETE =====
    const deleteButtons = document.querySelectorAll('.btn-danger');
    deleteButtons.forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure you want to delete this item?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // ===== STATUS UPDATE ANIMATION =====
    const statusSelects = document.querySelectorAll('.status-select');
    statusSelects.forEach(function (select) {
        select.addEventListener('change', function () {
            const row = this.closest('tr');
            if (row) {
                row.style.opacity = '0.5';
                setTimeout(function () {
                    row.style.opacity = '1';
                }, 300);
            }
        });
    });

    // ===== SIDEBAR ACTIVE STATE =====
    const navItems = document.querySelectorAll('.sidebar-nav .nav-item');
    navItems.forEach(function (item) {
        item.addEventListener('click', function () {
            navItems.forEach(function (i) {
                i.classList.remove('active');
            });
            this.classList.add('active');
        });
    });

    // ===== CHART HELPER =====
    function createChart(canvasId, data, options) {
        const ctx = document.getElementById(canvasId);
        if (ctx && typeof Chart !== 'undefined') {
            return new Chart(ctx.getContext('2d'), {
                data: data,
                options: options
            });
        }
        return null;
    }

    // ===== EXPORT TO CSV =====
    function exportToCSV(filename, rows) {
        const csvContent = rows.map(row => row.join(',')).join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }

    // ===== FORMAT PRICE (Rupee) =====
    function formatRupee(price) {
        return '₹' + parseFloat(price).toFixed(2);
    }

    // ===== MAKE HELPER FUNCTIONS GLOBAL =====
    window.formatRupee = formatRupee;
    window.exportToCSV = exportToCSV;
    window.createChart = createChart;
});