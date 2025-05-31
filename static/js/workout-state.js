/**
 * Модуль для управления состоянием тренировки
 */
class WorkoutState {
    static STORAGE_KEY = 'activeWorkout';

    /**
     * Получить активную тренировку
     * @returns {Object|null} Состояние активной тренировки или null
     */
    static getActive() {
        const savedState = localStorage.getItem(this.STORAGE_KEY);
        if (savedState) {
            try {
                return JSON.parse(savedState);
            } catch (e) {
                console.error('Ошибка при парсинге состояния тренировки:', e);
                this.clear(); // Очищаем поврежденные данные
                return null;
            }
        }
        return null;
    }

    /**
     * Сохранить состояние тренировки
     * @param {Object} state - Состояние тренировки
     */
    static save(state) {
        try {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(state));
        } catch (e) {
            console.error('Ошибка при сохранении состояния тренировки:', e);
        }
    }

    /**
     * Очистить состояние тренировки
     */
    static clear() {
        console.log('🔥 WorkoutState.clear() вызван');
        console.log('🔥 localStorage до удаления:', localStorage.getItem(this.STORAGE_KEY));
        localStorage.removeItem(this.STORAGE_KEY);
        console.log('🔥 localStorage после удаления:', localStorage.getItem(this.STORAGE_KEY));
        // НЕ вызываем updateIndicators здесь чтобы избежать циклов
    }

    /**
     * Проверить, есть ли активная тренировка для конкретного комплекса
     * @param {string} workoutSetCode - Код комплекса
     * @returns {boolean}
     */
    static isActive(workoutSetCode) {
        const activeWorkout = this.getActive();
        return activeWorkout && activeWorkout.workoutSetCode === workoutSetCode;
    }

    /**
     * Создать новое состояние тренировки
     * @param {string} workoutSetCode - Код комплекса
     * @param {string} workoutSetName - Название комплекса
     * @returns {Object} Новое состояние тренировки
     */
    static create(workoutSetCode, workoutSetName) {
        const state = {
            workoutSetCode,
            workoutSetName,
            currentExerciseIndex: 0,
            currentRound: 0,
            isResting: false,
            isWarmingUp: false,
            startTime: Date.now(),
            completedRounds: {},
            restEndTime: null
        };
        this.save(state);
        return state;
    }

    /**
     * Обновить индикаторы активной тренировки на странице
     */
    static updateIndicators() {
        console.log('🔥 WorkoutState.updateIndicators() вызван');
        const activeWorkout = this.getActive();
        console.log('🔥 Активная тренировка:', activeWorkout);

        // Обновляем глобальный индикатор в навигации
        this.updateGlobalIndicator(activeWorkout);

        // Обновляем карточки комплексов
        const workoutCards = document.querySelectorAll('[data-workout-code]');
        console.log('🔥 Найдено карточек комплексов:', workoutCards.length);

        workoutCards.forEach((card, index) => {
            const workoutCode = card.dataset.workoutCode;
            const indicator = card.querySelector('.active-workout-indicator');
            const startBtn = card.querySelector('.start-workout-btn');

            console.log(`🔥 Карточка ${index} (код: ${workoutCode}):`, {
                hasIndicator: !!indicator,
                hasStartBtn: !!startBtn,
                isActive: activeWorkout && activeWorkout.workoutSetCode === workoutCode,
                indicatorCurrentDisplay: indicator ? indicator.style.display : 'нет элемента',
                btnCurrentClasses: startBtn ? startBtn.className : 'нет элемента'
            });

            if (indicator && startBtn) {
                if (activeWorkout && activeWorkout.workoutSetCode === workoutCode) {
                    console.log(`🔥 Показываем индикатор для карточки ${workoutCode}`);
                    // Показываем индикатор активной тренировки
                    indicator.style.display = 'block';

                    // Меняем кнопку на "Продолжить"
                    const btnText = startBtn.querySelector('.btn-text');
                    const btnIcon = startBtn.querySelector('i');

                    if (btnText) {
                        btnText.textContent = 'Продолжить тренировку';
                        console.log(`🔥 Текст кнопки изменен на "Продолжить тренировку"`);
                    }
                    if (btnIcon) {
                        btnIcon.className = 'bi bi-play-fill';
                        console.log(`🔥 Иконка кнопки изменена на bi-play-fill`);
                    }

                    startBtn.classList.remove('btn-success');
                    startBtn.classList.add('btn-warning');
                    console.log(`🔥 Классы кнопки: убрали btn-success, добавили btn-warning`);
                } else {
                    console.log(`🔥 Скрываем индикатор для карточки ${workoutCode}`);
                    // Скрываем индикатор
                    indicator.style.display = 'none';

                    // Возвращаем обычную кнопку
                    const btnText = startBtn.querySelector('.btn-text');
                    const btnIcon = startBtn.querySelector('i');

                    if (btnText) {
                        btnText.textContent = 'Начать тренировку';
                        console.log(`🔥 Текст кнопки возвращен на "Начать тренировку"`);
                    }
                    if (btnIcon) {
                        btnIcon.className = 'bi bi-play-circle';
                        console.log(`🔥 Иконка кнопки возвращена на bi-play-circle`);
                    }

                    startBtn.classList.remove('btn-warning');
                    startBtn.classList.add('btn-success');
                    console.log(`🔥 Классы кнопки: убрали btn-warning, добавили btn-success`);
                }

                // Проверяем финальное состояние
                console.log(`🔥 Финальное состояние карточки ${workoutCode}:`, {
                    indicatorDisplay: indicator.style.display,
                    btnText: startBtn.querySelector('.btn-text')?.textContent,
                    btnClasses: startBtn.className
                });
            } else {
                console.warn(`🔥 Карточка ${workoutCode}: отсутствуют элементы`, {
                    hasIndicator: !!indicator,
                    hasStartBtn: !!startBtn
                });
            }
        });

        console.log('🔥 updateIndicators завершен');
    }

    /**
     * Обновить глобальный индикатор в навигации
     */
    static updateGlobalIndicator(activeWorkout) {
        const indicator = document.getElementById('activeWorkoutIndicator');
        const nameSpan = document.getElementById('activeWorkoutName');
        const timeSpan = document.getElementById('activeWorkoutTime');

        if (indicator && nameSpan && timeSpan) {
            if (activeWorkout) {
                // Показываем индикатор
                indicator.style.display = 'block';
                nameSpan.textContent = activeWorkout.workoutSetName || 'Тренировка';

                // Обновляем время
                const duration = this.getCurrentDuration();
                timeSpan.textContent = this.formatTime(duration);

                // Делаем индикатор кликабельным для перехода к тренировке
                indicator.style.cursor = 'pointer';
                indicator.onclick = () => {
                    window.location.href = `/workout-sets/${activeWorkout.workoutSetCode}/start`;
                };
            } else {
                // Скрываем индикатор
                indicator.style.display = 'none';
                indicator.onclick = null;
            }
        }
    }

    /**
     * Получить время выполнения текущей тренировки
     * @returns {number} Время в секундах
     */
    static getCurrentDuration() {
        const activeWorkout = this.getActive();
        if (activeWorkout && activeWorkout.startTime && !activeWorkout.isWarmingUp) {
            return Math.floor((Date.now() - activeWorkout.startTime) / 1000);
        }
        return 0;
    }

    /**
     * Форматировать время в строку ММ:СС
     * @param {number} seconds - Время в секундах
     * @returns {string} Отформатированное время
     */
    static formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    /**
     * Принудительный сброс состояния тренировки (для отладки)
     */
    static forceReset() {
        console.log('🔥 WorkoutState.forceReset() - Принудительный сброс тренировки');

        // Очищаем localStorage полностью
        try {
            localStorage.removeItem(this.STORAGE_KEY);
            console.log('🔥 localStorage очищен');
        } catch (e) {
            console.error('🔥 Ошибка очистки localStorage:', e);
        }

        // Обновляем индикаторы
        this.updateIndicators();

        console.log('🔥 Состояние сброшено, индикаторы обновлены');

        // Показываем уведомление
        alert('Состояние тренировки принудительно сброшено!');

        return true;
    }
}

// Глобальная функция для обратной совместимости
function getActiveWorkout() {
    return WorkoutState.getActive();
}

// Глобальная функция для принудительного сброса
function forceResetWorkout() {
    return WorkoutState.forceReset();
}

// Автоматически обновляем индикаторы при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔥 WorkoutState модуль загружен');
    WorkoutState.updateIndicators();

    // Временно отключаем автообновление для отладки
    // setInterval(() => {
    //     WorkoutState.updateIndicators();
    // }, 1000);
});

// Слушаем изменения в localStorage из других вкладок
window.addEventListener('storage', function(e) {
    if (e.key === WorkoutState.STORAGE_KEY) {
        WorkoutState.updateIndicators();
    }
});