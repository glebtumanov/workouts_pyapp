#!/usr/bin/env python3
"""
Скрипт создания базы данных для приложения домашних тренировок.
Создает все необходимые таблицы и инициализирует настройки по умолчанию.
"""

import sqlite3
import os
import sys
from datetime import datetime
from uuid import uuid4


def get_db_path():
    """Возвращает путь к файлу базы данных."""
    # БД будет в корневой папке проекта
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'workout_app.db')


def create_workout_set_table(cursor):
    """Создает таблицу комплексов упражнений."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workout_sets (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')


def create_exercise_table(cursor):
    """Создает таблицу упражнений."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercises (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            images TEXT,  -- JSON массив путей к изображениям
            video_url TEXT,
            repeat_count INTEGER NOT NULL,
            round_count INTEGER NOT NULL,
            rest_seconds INTEGER NOT NULL,
            workoutset_code TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (workoutset_code) REFERENCES workout_sets (code) ON DELETE CASCADE
        )
    ''')


def create_user_prefs_table(cursor):
    """Создает таблицу настроек пользователя."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_prefs (
            code TEXT PRIMARY KEY,
            default_repeat_count INTEGER NOT NULL DEFAULT 10,
            default_round_count INTEGER NOT NULL DEFAULT 3,
            default_rest_seconds INTEGER NOT NULL DEFAULT 60,
            timer_sound TEXT DEFAULT 'default',
            notifications_enabled BOOLEAN NOT NULL DEFAULT TRUE
        )
    ''')


def create_workout_log_table(cursor):
    """Создает таблицу журнала тренировок."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workout_logs (
            code TEXT PRIMARY KEY,
            date TIMESTAMP NOT NULL,
            workoutset_code TEXT NOT NULL,
            duration_seconds INTEGER NOT NULL,
            completed_exercises TEXT,  -- JSON массив завершенных упражнений
            FOREIGN KEY (workoutset_code) REFERENCES workout_sets (code)
        )
    ''')


def create_indexes(cursor):
    """Создает индексы для оптимизации запросов."""
    indexes = [
        'CREATE INDEX IF NOT EXISTS idx_exercises_workoutset ON exercises(workoutset_code)',
        'CREATE INDEX IF NOT EXISTS idx_workout_logs_date ON workout_logs(date DESC)',
        'CREATE INDEX IF NOT EXISTS idx_workout_logs_workoutset ON workout_logs(workoutset_code)'
    ]

    for index_sql in indexes:
        cursor.execute(index_sql)


def init_default_user_prefs(cursor):
    """Инициализирует настройки пользователя по умолчанию."""
    # Проверяем, есть ли уже настройки
    cursor.execute('SELECT COUNT(*) FROM user_prefs')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO user_prefs (
                code, default_repeat_count, default_round_count,
                default_rest_seconds, timer_sound, notifications_enabled
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (str(uuid4()), 10, 3, 60, 'default', True))
        print("✓ Созданы настройки пользователя по умолчанию")


def create_triggers(cursor):
    """Создает триггеры для автоматического обновления updated_at."""
    triggers = [
        '''
        CREATE TRIGGER IF NOT EXISTS update_workout_sets_timestamp
        AFTER UPDATE ON workout_sets
        BEGIN
            UPDATE workout_sets SET updated_at = CURRENT_TIMESTAMP WHERE code = NEW.code;
        END
        ''',
        '''
        CREATE TRIGGER IF NOT EXISTS update_exercises_timestamp
        AFTER UPDATE ON exercises
        BEGIN
            UPDATE exercises SET updated_at = CURRENT_TIMESTAMP WHERE code = NEW.code;
        END
        '''
    ]

    for trigger_sql in triggers:
        cursor.execute(trigger_sql)


def create_database(force_recreate=False):
    """
    Создает базу данных и все необходимые таблицы.

    Args:
        force_recreate: Если True, удаляет существующую БД и создает заново
    """
    db_path = get_db_path()

    if force_recreate and os.path.exists(db_path):
        os.remove(db_path)
        print(f"✓ Удалена существующая база данных: {db_path}")

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Включаем поддержку внешних ключей
            cursor.execute('PRAGMA foreign_keys = ON')

            # Создаем таблицы
            print("Создание таблиц...")
            create_workout_set_table(cursor)
            print("✓ Таблица workout_sets создана")

            create_exercise_table(cursor)
            print("✓ Таблица exercises создана")

            create_user_prefs_table(cursor)
            print("✓ Таблица user_prefs создана")

            create_workout_log_table(cursor)
            print("✓ Таблица workout_logs создана")

            # Создаем индексы
            create_indexes(cursor)
            print("✓ Индексы созданы")

            # Создаем триггеры
            create_triggers(cursor)
            print("✓ Триггеры созданы")

            # Инициализируем настройки по умолчанию
            init_default_user_prefs(cursor)

            conn.commit()
            print(f"\n🎉 База данных успешно создана: {db_path}")

    except sqlite3.Error as e:
        print(f"❌ Ошибка при создании базы данных: {e}")
        raise


def show_help():
    """Показывает справку по использованию скрипта."""
    print("""
Использование: python make_db.py [опции]

Опции:
  --force, -f     Пересоздать базу данных (удалить существующую)
  --migrate, -m   Выполнить миграцию базы данных (добавить новые поля)
  --help, -h      Показать эту справку

Примеры:
  python make_db.py           # Создать БД (если не существует)
  python make_db.py --force   # Пересоздать БД с нуля
  python make_db.py --migrate # Обновить существующую БД
    """)


def main():
    """Основная функция скрипта."""
    args = sys.argv[1:]

    if '--help' in args or '-h' in args:
        show_help()
        return

    force_recreate = '--force' in args or '-f' in args
    migrate = '--migrate' in args or '-m' in args

    try:
        if migrate:
            migrate_database()
        else:
            create_database(force_recreate=force_recreate)
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)


def migrate_database():
    """Выполняет миграцию базы данных для добавления новых полей."""
    db_path = get_db_path()

    if not os.path.exists(db_path):
        print("База данных не существует. Создаем новую...")
        create_database()
        return

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Проверяем, есть ли уже поле completed_exercises в таблице workout_logs
            cursor.execute("PRAGMA table_info(workout_logs)")
            columns = [column[1] for column in cursor.fetchall()]

            if 'completed_exercises' not in columns:
                print("Добавляем поле completed_exercises в таблицу workout_logs...")
                cursor.execute('''
                    ALTER TABLE workout_logs
                    ADD COLUMN completed_exercises TEXT
                ''')
                conn.commit()
                print("✓ Поле completed_exercises успешно добавлено")
            else:
                print("✓ Поле completed_exercises уже существует")

    except sqlite3.Error as e:
        print(f"❌ Ошибка при миграции базы данных: {e}")
        raise


if __name__ == '__main__':
    main()