#!/usr/bin/env python3
"""
Скрипт для создания тестовых данных в приложении тренировок.
"""

from models import WorkoutSetModel, ExerciseModel, UserPrefsModel, WorkoutLogModel
from datetime import datetime, timedelta
import random

def create_test_exercises(workoutset_code, exercises_data):
    """Создает тестовые упражнения для комплекса."""
    created_codes = []

    for exercise_data in exercises_data:
        try:
            code = ExerciseModel.create(
                workoutset_code=workoutset_code,
                name=exercise_data['name'],
                description=exercise_data.get('description', ''),
                repeat_count=exercise_data.get('repeat_count', 10),
                round_count=exercise_data.get('round_count', 3),
                rest_seconds=exercise_data.get('rest_seconds', 60)
            )
            created_codes.append(code)
            print(f"  ✓ Создано упражнение: {exercise_data['name']}")
        except Exception as e:
            print(f"  ❌ Ошибка при создании упражнения {exercise_data['name']}: {e}")

    return created_codes

def create_test_workout_sets():
    """Создает тестовые комплексы упражнений с упражнениями."""

    test_sets = [
        {
            'name': 'Утренняя разминка',
            'description': 'Простой комплекс упражнений для пробуждения и разогрева мышц. Идеально подходит для начала дня.',
            'exercises': [
                {
                    'name': 'Махи руками',
                    'description': 'Круговые движения руками для разогрева плечевых суставов',
                    'repeat_count': 15,
                    'round_count': 2,
                    'rest_seconds': 30
                },
                {
                    'name': 'Повороты корпуса',
                    'description': 'Скручивания корпуса влево и вправо для разогрева позвоночника',
                    'repeat_count': 10,
                    'round_count': 2,
                    'rest_seconds': 30
                },
                {
                    'name': 'Приседания',
                    'description': 'Классические приседания для активации мышц ног',
                    'repeat_count': 15,
                    'round_count': 2,
                    'rest_seconds': 45
                }
            ]
        },
        {
            'name': 'Кардио HIIT',
            'description': 'Высокоинтенсивная интервальная тренировка для сжигания калорий и укрепления сердечно-сосудистой системы.',
            'exercises': [
                {
                    'name': 'Берпи',
                    'description': 'Комплексное упражнение: присед, упор лежа, отжимание, прыжок',
                    'repeat_count': 8,
                    'round_count': 4,
                    'rest_seconds': 90
                },
                {
                    'name': 'Прыжки с разведением',
                    'description': 'Прыжки на месте с разведением рук и ног (jumping jacks)',
                    'repeat_count': 20,
                    'round_count': 3,
                    'rest_seconds': 60
                },
                {
                    'name': 'Высокие колени',
                    'description': 'Бег на месте с высоким подниманием коленей',
                    'repeat_count': 30,
                    'round_count': 3,
                    'rest_seconds': 60
                },
                {
                    'name': 'Планка',
                    'description': 'Удержание позиции планки для укрепления кора',
                    'repeat_count': 30,  # секунды
                    'round_count': 3,
                    'rest_seconds': 90
                }
            ]
        },
        {
            'name': 'Силовая тренировка',
            'description': 'Комплекс упражнений с собственным весом для развития силы и выносливости всех групп мышц.',
            'exercises': [
                {
                    'name': 'Отжимания',
                    'description': 'Классические отжимания от пола для мышц груди, плеч и трицепсов',
                    'repeat_count': 12,
                    'round_count': 3,
                    'rest_seconds': 60
                },
                {
                    'name': 'Приседания с прыжком',
                    'description': 'Приседания с выпрыгиванием вверх для взрывной силы ног',
                    'repeat_count': 15,
                    'round_count': 3,
                    'rest_seconds': 90
                },
                {
                    'name': 'Подтягивания',
                    'description': 'Подтягивания на турнике для мышц спины и бицепсов',
                    'repeat_count': 8,
                    'round_count': 3,
                    'rest_seconds': 120
                },
                {
                    'name': 'Выпады',
                    'description': 'Выпады вперед попеременно каждой ногой',
                    'repeat_count': 12,
                    'round_count': 3,
                    'rest_seconds': 60
                }
            ]
        },
        {
            'name': 'Йога и растяжка',
            'description': 'Комплекс упражнений для гибкости, расслабления и восстановления после интенсивных тренировок.',
            'exercises': [
                {
                    'name': 'Собака мордой вниз',
                    'description': 'Классическая поза йоги для растяжки задней поверхности ног и спины',
                    'repeat_count': 30,  # секунды удержания
                    'round_count': 3,
                    'rest_seconds': 30
                },
                {
                    'name': 'Кошка-корова',
                    'description': 'Мобилизация позвоночника: прогиб и округление спины',
                    'repeat_count': 10,
                    'round_count': 2,
                    'rest_seconds': 30
                },
                {
                    'name': 'Поза ребенка',
                    'description': 'Расслабляющая поза для восстановления и растяжки спины',
                    'repeat_count': 60,  # секунды удержания
                    'round_count': 2,
                    'rest_seconds': 30
                }
            ]
        }
    ]

    created_codes = []

    for workout_set in test_sets:
        try:
            # Создаем комплекс
            code = WorkoutSetModel.create(
                name=workout_set['name'],
                description=workout_set['description']
            )
            created_codes.append(code)
            print(f"✓ Создан комплекс: {workout_set['name']}")

            # Создаем упражнения для комплекса
            exercise_codes = create_test_exercises(code, workout_set['exercises'])
            print(f"  Создано {len(exercise_codes)} упражнений")

        except Exception as e:
            print(f"❌ Ошибка при создании комплекса {workout_set['name']}: {e}")

    return created_codes

def create_test_workout_logs():
    """Создает тестовые записи в журнале тренировок."""
    print("Создание тестовых записей в журнале тренировок...")

    # Получаем все существующие комплексы
    workout_sets = WorkoutSetModel.get_all()
    if not workout_sets:
        print("Нет комплексов для создания тренировок. Сначала создайте комплексы.")
        return

    # Создаем записи тренировок за последние 30 дней
    base_date = datetime.now()

    for workout_set in workout_sets:
        # Создаем 3-7 записей для каждого комплекса
        num_workouts = random.randint(3, 7)

        for i in range(num_workouts):
            # Случайная дата в последние 30 дней
            days_ago = random.randint(1, 30)
            workout_date = (base_date - timedelta(days=days_ago)).isoformat()

            # Случайная продолжительность тренировки (20-90 минут)
            duration_minutes = random.randint(20, 90)
            duration_seconds = duration_minutes * 60

            try:
                workout_log_code = WorkoutLogModel.create(
                    workoutset_code=workout_set['code'],
                    duration_seconds=duration_seconds,
                    workout_date=workout_date
                )
                print(f"  ✓ Тренировка {workout_set['name']}: {duration_minutes} мин, {days_ago} дней назад")
            except Exception as e:
                print(f"  ✗ Ошибка создания тренировки для {workout_set['name']}: {e}")

    print("Тестовые записи тренировок созданы!")

def create_test_user_prefs():
    """Создает тестовые настройки пользователя."""
    try:
        # Проверяем, есть ли уже настройки
        existing_prefs = UserPrefsModel.get_first()

        if existing_prefs:
            print("  ✓ Настройки пользователя уже существуют")
            return existing_prefs['code']

        # Создаем новые настройки
        code = UserPrefsModel.create(
            default_repeat_count=15,
            default_round_count=4,
            default_rest_seconds=90,
            default_warmup_rest_seconds=120,  # 2 минуты по умолчанию
            timer_sound='default',
            notifications_enabled=True
        )
        print("  ✓ Созданы настройки пользователя")
        return code
    except Exception as e:
        print(f"  ❌ Ошибка при создании настроек: {e}")
        return None

def create_all_test_data():
    """Создает все тестовые данные включая журнал тренировок."""
    # Сначала создаем все остальные данные
    create_test_workout_sets()

    # Затем создаем тестовые записи тренировок
    create_test_workout_logs()

def main():
    """Основная функция."""
    print("Создание тестовых данных...")
    create_all_test_data()
    print("Готово!")

if __name__ == '__main__':
    main()