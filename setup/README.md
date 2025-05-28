# Настройка базы данных

## Описание

В этой папке находятся скрипты для инициализации и настройки базы данных приложения домашних тренировок.

## Файлы

- `make_db.py` - скрипт создания базы данных и всех необходимых таблиц

## Использование

### Создание новой базы данных

```bash
python3 make_db.py
```

### Пересоздание существующей базы данных

```bash
python3 make_db.py --force
```

### Справка

```bash
python3 make_db.py --help
```

## Структура базы данных

Скрипт создает следующие таблицы:

### workout_sets
- Хранит комплексы упражнений
- Поля: code (PK), name, description, created_at, updated_at

### exercises
- Хранит упражнения, входящие в комплексы
- Поля: code (PK), name, description, images (JSON), video_url, repeat_count, round_count, rest_seconds, workoutset_code (FK), created_at, updated_at

### user_prefs
- Настройки пользователя по умолчанию
- Поля: code (PK), default_repeat_count, default_round_count, default_rest_seconds, timer_sound, notifications_enabled

### workout_logs
- Журнал выполненных тренировок
- Поля: code (PK), date, workoutset_code (FK), duration_seconds

## Дополнительные функции

- Автоматические индексы для оптимизации запросов
- Триггеры для обновления поля `updated_at`
- Инициализация настроек пользователя по умолчанию
- Поддержка внешних ключей с каскадным удалением

## Результат

После выполнения скрипта в корневой папке проекта создается файл `workout_app.db` - база данных SQLite готовая к использованию приложением.