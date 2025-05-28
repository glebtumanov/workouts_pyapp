#!/usr/bin/env python3
"""
Скрипт для создания тестовых данных в приложении тренировок.
"""

from models import WorkoutSetModel, ExerciseModel

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

def main():
    """Основная функция."""
    print("Создание тестовых данных...")

    # Проверяем существующие комплексы
    existing_sets = WorkoutSetModel.get_all()
    if existing_sets:
        print(f"В БД уже есть {len(existing_sets)} комплексов")
        response = input("Создать дополнительные тестовые комплексы? (y/n): ")
        if response.lower() != 'y':
            print("Отменено")
            return

        # Удаляем старые тестовые данные
        confirm = input("Удалить существующие комплексы перед созданием новых? (y/n): ")
        if confirm.lower() == 'y':
            for workout_set in existing_sets:
                try:
                    ExerciseModel.delete_by_workoutset(workout_set['code'])
                    WorkoutSetModel.delete(workout_set['code'])
                    print(f"✓ Удален комплекс: {workout_set['name']}")
                except Exception as e:
                    print(f"❌ Ошибка при удалении комплекса {workout_set['name']}: {e}")

    # Создаем тестовые комплексы
    created_codes = create_test_workout_sets()

    print(f"\n🎉 Создано {len(created_codes)} тестовых комплексов с упражнениями")
    print("\nВы можете открыть приложение по адресу: http://localhost:5000")

if __name__ == '__main__':
    main()