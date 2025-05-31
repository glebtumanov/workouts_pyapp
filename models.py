"""
Модели для работы с базой данных приложения тренировок.
"""

import sqlite3
import os
import json
from datetime import datetime
from uuid import uuid4
from typing import List, Optional, Dict, Any
from contextlib import contextmanager


def get_db_path() -> str:
    """Возвращает путь к файлу базы данных."""
    return os.path.join(os.path.dirname(__file__), 'workout_app.db')


@contextmanager
def get_db_connection():
    """Контекстный менеджер для работы с БД."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row  # Возвращать результаты как dict
    conn.execute('PRAGMA foreign_keys = ON')
    try:
        yield conn
    finally:
        conn.close()


class UserPrefsModel:
    """Модель для работы с настройками пользователя."""

    @staticmethod
    def get_defaults() -> Dict[str, Any]:
        """Получает настройки по умолчанию."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT default_repeat_count, default_round_count, default_rest_seconds,
                       default_warmup_rest_seconds, timer_sound, notifications_enabled
                FROM user_prefs
                LIMIT 1
            ''')
            row = cursor.fetchone()
            if row:
                return dict(row)
            else:
                # Возвращаем значения по умолчанию, если настроек нет
                return {
                    'default_repeat_count': 10,
                    'default_round_count': 3,
                    'default_rest_seconds': 60,
                    'default_warmup_rest_seconds': 120,
                    'timer_sound': 'default',
                    'notifications_enabled': True
                }

    @staticmethod
    def get_first() -> Optional[Dict[str, Any]]:
        """Получает первую запись настроек пользователя."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT code, default_repeat_count, default_round_count, default_rest_seconds,
                       default_warmup_rest_seconds, timer_sound, notifications_enabled
                FROM user_prefs
                LIMIT 1
            ''')
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def create(default_repeat_count: int = 10, default_round_count: int = 3,
               default_rest_seconds: int = 60, default_warmup_rest_seconds: int = 120,
               timer_sound: str = 'default', notifications_enabled: bool = True) -> str:
        """Создает новые настройки пользователя."""
        code = str(uuid4())
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_prefs (
                    code, default_repeat_count, default_round_count, default_rest_seconds,
                    default_warmup_rest_seconds, timer_sound, notifications_enabled
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (code, default_repeat_count, default_round_count, default_rest_seconds,
                  default_warmup_rest_seconds, timer_sound, notifications_enabled))
            conn.commit()
        return code

    @staticmethod
    def update(code: str, default_repeat_count: int = 10, default_round_count: int = 3,
               default_rest_seconds: int = 60, default_warmup_rest_seconds: int = 120,
               timer_sound: str = 'default', notifications_enabled: bool = True) -> bool:
        """Обновляет настройки пользователя."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE user_prefs
                SET default_repeat_count = ?, default_round_count = ?, default_rest_seconds = ?,
                    default_warmup_rest_seconds = ?, timer_sound = ?, notifications_enabled = ?
                WHERE code = ?
            ''', (default_repeat_count, default_round_count, default_rest_seconds,
                  default_warmup_rest_seconds, timer_sound, notifications_enabled, code))
            conn.commit()
            return cursor.rowcount > 0


class ExerciseModel:
    """Модель для работы с упражнениями."""

    @staticmethod
    def get_by_code(code: str) -> Optional[Dict[str, Any]]:
        """Получает упражнение по коду."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT code, name, description, images, video_url,
                       repeat_count, round_count, rest_seconds,
                       workoutset_code, created_at, updated_at
                FROM exercises
                WHERE code = ?
            ''', (code,))
            row = cursor.fetchone()
            if row:
                exercise = dict(row)
                # Парсим JSON список изображений
                try:
                    exercise['images'] = json.loads(exercise['images']) if exercise['images'] else []
                except (json.JSONDecodeError, TypeError):
                    exercise['images'] = []
                return exercise
            return None

    @staticmethod
    def get_by_workoutset(workoutset_code: str) -> List[Dict[str, Any]]:
        """Получает все упражнения комплекса."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT code, name, description, images, video_url,
                       repeat_count, round_count, rest_seconds,
                       created_at, updated_at
                FROM exercises
                WHERE workoutset_code = ?
                ORDER BY created_at ASC
            ''', (workoutset_code,))
            exercises = []
            for row in cursor.fetchall():
                exercise = dict(row)
                # Парсим JSON список изображений
                try:
                    exercise['images'] = json.loads(exercise['images']) if exercise['images'] else []
                except (json.JSONDecodeError, TypeError):
                    exercise['images'] = []
                exercises.append(exercise)
            return exercises

    @staticmethod
    def get_by_code(code: str) -> Optional[Dict[str, Any]]:
        """Получает упражнение по коду."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT code, name, description, images, video_url,
                       repeat_count, round_count, rest_seconds,
                       workoutset_code, created_at, updated_at
                FROM exercises
                WHERE code = ?
            ''', (code,))
            row = cursor.fetchone()
            if row:
                exercise = dict(row)
                try:
                    exercise['images'] = json.loads(exercise['images']) if exercise['images'] else []
                except (json.JSONDecodeError, TypeError):
                    exercise['images'] = []
                return exercise
            return None

    @staticmethod
    def create(workoutset_code: str, name: str, description: str = '',
               images: List[str] = None, video_url: str = '',
               repeat_count: int = 10, round_count: int = 3,
               rest_seconds: int = 60) -> str:
        """Создает новое упражнение."""
        code = str(uuid4())
        images_json = json.dumps(images or [])

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO exercises (
                    code, name, description, images, video_url,
                    repeat_count, round_count, rest_seconds, workoutset_code
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (code, name, description, images_json, video_url,
                  repeat_count, round_count, rest_seconds, workoutset_code))
            conn.commit()
        return code

    @staticmethod
    def update(code: str, name: str, description: str = '',
               images: List[str] = None, video_url: str = '',
               repeat_count: int = 10, round_count: int = 3,
               rest_seconds: int = 60) -> bool:
        """Обновляет упражнение."""
        images_json = json.dumps(images or [])

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE exercises
                SET name = ?, description = ?, images = ?, video_url = ?,
                    repeat_count = ?, round_count = ?, rest_seconds = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE code = ?
            ''', (name, description, images_json, video_url,
                  repeat_count, round_count, rest_seconds, code))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(code: str) -> bool:
        """Удаляет упражнение."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM exercises WHERE code = ?', (code,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete_by_workoutset(workoutset_code: str) -> int:
        """Удаляет все упражнения комплекса."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM exercises WHERE workoutset_code = ?', (workoutset_code,))
            conn.commit()
            return cursor.rowcount


class WorkoutSetModel:
    """Модель для работы с комплексами упражнений."""

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Получает все комплексы упражнений."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT code, name, description, created_at, updated_at
                FROM workout_sets
                ORDER BY created_at DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_code(code: str) -> Optional[Dict[str, Any]]:
        """Получает комплекс по коду."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT code, name, description, created_at, updated_at
                FROM workout_sets
                WHERE code = ?
            ''', (code,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def create(name: str, description: str = '') -> str:
        """Создает новый комплекс упражнений."""
        code = str(uuid4())
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO workout_sets (code, name, description)
                VALUES (?, ?, ?)
            ''', (code, name, description))
            conn.commit()
        return code

    @staticmethod
    def update(code: str, name: str, description: str = '') -> bool:
        """Обновляет комплекс упражнений."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE workout_sets
                SET name = ?, description = ?, updated_at = CURRENT_TIMESTAMP
                WHERE code = ?
            ''', (name, description, code))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(code: str) -> bool:
        """Удаляет комплекс упражнений."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM workout_sets WHERE code = ?', (code,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def count_exercises(code: str) -> int:
        """Подсчитывает количество упражнений в комплексе."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM exercises WHERE workoutset_code = ?
            ''', (code,))
            return cursor.fetchone()[0]


class WorkoutLogModel:
    """Модель для работы с журналом тренировок."""

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Получает все записи журнала тренировок."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT wl.code, wl.date, wl.workoutset_code, wl.duration_seconds,
                       wl.completed_exercises, ws.name as workoutset_name
                FROM workout_logs wl
                LEFT JOIN workout_sets ws ON wl.workoutset_code = ws.code
                ORDER BY wl.date DESC
            ''')
            logs = []
            for row in cursor.fetchall():
                log = dict(row)
                # Парсим JSON массив завершенных упражнений
                try:
                    log['completed_exercises'] = json.loads(log['completed_exercises']) if log['completed_exercises'] else []
                except (json.JSONDecodeError, TypeError):
                    log['completed_exercises'] = []
                logs.append(log)
            return logs

    @staticmethod
    def get_last_workout_for_set(workoutset_code: str) -> Optional[Dict[str, Any]]:
        """Получает последнюю тренировку для указанного комплекса."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT code, date, workoutset_code, duration_seconds, completed_exercises
                FROM workout_logs
                WHERE workoutset_code = ?
                ORDER BY date DESC
                LIMIT 1
            ''', (workoutset_code,))
            row = cursor.fetchone()
            if row:
                log = dict(row)
                # Парсим JSON массив завершенных упражнений
                try:
                    log['completed_exercises'] = json.loads(log['completed_exercises']) if log['completed_exercises'] else []
                except (json.JSONDecodeError, TypeError):
                    log['completed_exercises'] = []
                return log
            return None

    @staticmethod
    def create(workoutset_code: str, duration_seconds: int, workout_date: str = None,
               completed_exercises: List[str] = None) -> str:
        """Создает новую запись в журнале тренировок."""
        code = str(uuid4())
        if workout_date is None:
            workout_date = datetime.now().isoformat()

        completed_exercises_json = json.dumps(completed_exercises or [])

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO workout_logs (code, date, workoutset_code, duration_seconds, completed_exercises)
                VALUES (?, ?, ?, ?, ?)
            ''', (code, workout_date, workoutset_code, duration_seconds, completed_exercises_json))
            conn.commit()
        return code

    @staticmethod
    def delete(code: str) -> bool:
        """Удаляет запись из журнала тренировок."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM workout_logs WHERE code = ?', (code,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete_by_workoutset(workoutset_code: str) -> int:
        """Удаляет все записи тренировок для указанного комплекса."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM workout_logs WHERE workoutset_code = ?', (workoutset_code,))
            conn.commit()
            return cursor.rowcount

    @staticmethod
    def delete_all() -> int:
        """Удаляет все записи из журнала тренировок."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM workout_logs')
            conn.commit()
            return cursor.rowcount

    @staticmethod
    def calculate_completion_percentage(workoutset_code: str, completed_exercises: List[str]) -> int:
        """Рассчитывает процент завершения тренировки."""
        if not completed_exercises:
            return 0

        # Получаем общее количество упражнений в комплексе
        total_exercises = WorkoutSetModel.count_exercises(workoutset_code)

        if total_exercises == 0:
            return 0

        # Рассчитываем процент
        completed_count = len(completed_exercises)
        percentage = round((completed_count / total_exercises) * 100)

        return min(percentage, 100)  # Ограничиваем максимум 100%


class DatabaseManager:
    """Класс для управления бэкапом и восстановлением базы данных."""

    @staticmethod
    def create_backup() -> str:
        """
        Создает бэкап базы данных.
        Возвращает путь к созданному файлу бэкапа.
        """
        import shutil
        from datetime import datetime

        backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'workout_backup_{timestamp}.db'
        backup_path = os.path.join(backup_dir, backup_filename)

        db_path = get_db_path()
        if not os.path.exists(db_path):
            raise FileNotFoundError("База данных не найдена")

        shutil.copy2(db_path, backup_path)
        return backup_path

    @staticmethod
    def restore_from_backup(backup_file_path: str) -> bool:
        """
        Восстанавливает базу данных из бэкапа.

        Args:
            backup_file_path: Путь к файлу бэкапа

        Returns:
            bool: True если восстановление прошло успешно

        Raises:
            FileNotFoundError: Если файл бэкапа не найден
            sqlite3.DatabaseError: Если файл не является корректной БД SQLite
        """
        import shutil

        if not os.path.exists(backup_file_path):
            raise FileNotFoundError("Файл бэкапа не найден")

        # Проверяем что файл является корректной БД SQLite
        try:
            test_conn = sqlite3.connect(backup_file_path)
            # Проверяем что в БД есть нужные таблицы
            cursor = test_conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name IN ('workout_sets', 'exercises', 'user_prefs', 'workout_logs')
            """)
            tables = [row[0] for row in cursor.fetchall()]
            test_conn.close()

            if len(tables) < 3:  # Минимум 3 основные таблицы должны быть
                raise sqlite3.DatabaseError("Файл не содержит корректную структуру БД приложения")

        except sqlite3.Error as e:
            raise sqlite3.DatabaseError(f"Неверный формат файла базы данных: {str(e)}")

        # Создаем резервную копию текущей БД
        db_path = get_db_path()
        if os.path.exists(db_path):
            from datetime import datetime
            backup_current = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(db_path, backup_current)

        # Восстанавливаем из бэкапа
        shutil.copy2(backup_file_path, db_path)
        return True

    @staticmethod
    def get_database_info() -> Dict[str, Any]:
        """Получает информацию о текущей базе данных."""
        db_path = get_db_path()

        if not os.path.exists(db_path):
            return {
                'exists': False,
                'size': 0,
                'modified': None,
                'tables_count': 0,
                'records_count': {}
            }

        # Размер файла
        size = os.path.getsize(db_path)

        # Дата модификации
        modified = datetime.fromtimestamp(os.path.getmtime(db_path))

        # Подсчет записей в таблицах
        records_count = {}
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                # Получаем список таблиц
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]

                # Подсчитываем записи в каждой таблице
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    records_count[table] = cursor.fetchone()[0]

        except sqlite3.Error:
            records_count = {}

        return {
            'exists': True,
            'size': size,
            'modified': modified,
            'tables_count': len(tables) if 'tables' in locals() else 0,
            'records_count': records_count
        }

    @staticmethod
    def list_backups() -> List[Dict[str, Any]]:
        """Возвращает список доступных бэкапов."""
        backup_dir = os.path.join(os.path.dirname(__file__), 'backups')

        if not os.path.exists(backup_dir):
            return []

        backups = []
        for filename in os.listdir(backup_dir):
            if filename.startswith('workout_backup_') and filename.endswith('.db'):
                filepath = os.path.join(backup_dir, filename)
                size = os.path.getsize(filepath)
                modified = datetime.fromtimestamp(os.path.getmtime(filepath))

                backups.append({
                    'filename': filename,
                    'filepath': filepath,
                    'size': size,
                    'modified': modified
                })

        # Сортируем по дате (новые сначала)
        backups.sort(key=lambda x: x['modified'], reverse=True)
        return backups

    @staticmethod
    def delete_backup(filename: str) -> bool:
        """Удаляет файл бэкапа."""
        backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
        backup_path = os.path.join(backup_dir, filename)

        if not os.path.exists(backup_path) or not filename.startswith('workout_backup_'):
            return False

        try:
            os.remove(backup_path)
            return True
        except OSError:
            return False