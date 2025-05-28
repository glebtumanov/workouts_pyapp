// Основной JavaScript файл для приложения домашних тренировок

document.addEventListener('DOMContentLoaded', function() {
    // Автоматическое скрытие алертов через 5 секунд
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Подтверждение удаления
    const deleteButtons = document.querySelectorAll('[data-bs-toggle="modal"]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const itemName = this.getAttribute('data-name');
            const itemCode = this.getAttribute('data-code');

            // Обновляем текст в модальном окне
            const modalElement = document.querySelector(this.getAttribute('data-bs-target'));
            if (modalElement) {
                const nameSpan = modalElement.querySelector('#deleteItemName');
                const form = modalElement.querySelector('#deleteForm');

                if (nameSpan) nameSpan.textContent = itemName;
                if (form && itemCode) {
                    form.action = form.action.replace(/\/[^\/]+\/delete$/, `/${itemCode}/delete`);
                }
            }
        });
    });

    // Улучшение UX для форм
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Сохранение...';
            }
        });
    });

    // Автофокус на первое поле ввода в модальных окнах
    const modals = document.querySelectorAll('.modal');
    modals.forEach(function(modal) {
        modal.addEventListener('shown.bs.modal', function() {
            const firstInput = modal.querySelector('input, textarea, select');
            if (firstInput) {
                firstInput.focus();
            }
        });
    });
});