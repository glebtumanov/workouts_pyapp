// Модуль для создания звуковых уведомлений
class NotificationSound {
    constructor() {
        this.audioContext = null;
        this.isSupported = typeof AudioContext !== 'undefined' || typeof webkitAudioContext !== 'undefined';
        this.initAudioContext();
    }

    initAudioContext() {
        if (!this.isSupported) return;

        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
            console.warn('Web Audio API не поддерживается:', e);
            this.isSupported = false;
        }
    }

    // Создает простой бип-звук
    createBeep(frequency = 800, duration = 200, volume = 0.1) {
        if (!this.isSupported || !this.audioContext) {
            this.fallbackNotification();
            return;
        }

        // Возобновляем AudioContext если он приостановлен
        if (this.audioContext.state === 'suspended') {
            this.audioContext.resume();
        }

        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);

        oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(volume, this.audioContext.currentTime + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration / 1000);

        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + duration / 1000);
    }

    // Создает двойной бип
    createDoubleBeep() {
        this.createBeep(800, 150, 0.1);
        setTimeout(() => this.createBeep(1000, 150, 0.1), 200);
    }

    // Запасной вариант для браузеров без поддержки Web Audio API
    fallbackNotification() {
        // Пытаемся использовать браузерное уведомление
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('Отдых завершен!', {
                body: 'Время переходить к следующему подходу',
                icon: '/static/favicon.ico',
                tag: 'workout-timer'
            });
        } else {
            // Визуальное уведомление
            this.showVisualNotification();
        }
    }

    // Визуальное уведомление
    showVisualNotification() {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #ffc107;
            color: #000;
            padding: 15px 20px;
            border-radius: 5px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            z-index: 9999;
            font-weight: bold;
            transition: all 0.3s ease;
        `;
        notification.textContent = '🔔 Отдых завершен!';

        document.body.appendChild(notification);

        // Удаляем уведомление через 3 секунды
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // Запрашивает разрешение на уведомления
    async requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            const permission = await Notification.requestPermission();
            return permission === 'granted';
        }
        return Notification.permission === 'granted';
    }
}

// Экспортируем для использования
window.NotificationSound = NotificationSound;