from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import os
import json
from models import WorkoutSetModel, ExerciseModel, UserPrefsModel, WorkoutLogModel

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'images', 'exercises')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Разрешенные расширения для изображений
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Проверяет, разрешен ли файл для загрузки."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    """Создает папку для загрузок, если она не существует."""
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])


@app.route('/')
def index():
    """Главная страница приложения"""
    return render_template('index.html')


@app.route('/workout-sets')
def workout_sets_list():
    """Страница со списком всех комплексов упражнений"""
    workout_sets = WorkoutSetModel.get_all()
    for workout_set in workout_sets:
        exercises = ExerciseModel.get_by_workoutset(workout_set['code'])
        workout_set['exercise_count'] = len(exercises)

        # Подсчитываем общее количество подходов и примерную длительность
        total_rounds = sum(ex['round_count'] for ex in exercises)
        total_rest_time = sum(ex['rest_seconds'] * (ex['round_count'] - 1) for ex in exercises)
        estimated_duration = round((total_rest_time + total_rounds * 30) / 60)  # примерно 30 сек на подход

        workout_set['total_rounds'] = total_rounds
        workout_set['estimated_duration'] = estimated_duration

        # Получаем информацию о последней тренировке
        last_workout = WorkoutLogModel.get_last_workout_for_set(workout_set['code'])
        if last_workout:
            from datetime import datetime, timezone

            # Парсим дату последней тренировки
            try:
                last_date = datetime.fromisoformat(last_workout['date'].replace('Z', '+00:00'))
                now = datetime.now(timezone.utc)

                # Если время последней тренировки в UTC, конвертируем текущее время
                if last_date.tzinfo is None:
                    last_date = last_date.replace(tzinfo=timezone.utc)
                    now = datetime.now(timezone.utc)
                else:
                    now = datetime.now(timezone.utc)

                days_ago = (now - last_date).days
                workout_set['last_workout_days_ago'] = days_ago
                workout_set['last_workout_date'] = last_workout['date']
            except Exception as e:
                print(f"Ошибка при обработке даты тренировки: {e}")
                workout_set['last_workout_days_ago'] = None
                workout_set['last_workout_date'] = None
        else:
            workout_set['last_workout_days_ago'] = None
            workout_set['last_workout_date'] = None

    return render_template('workout_sets/list.html', workout_sets=workout_sets)


@app.route('/workout-sets/new')
def workout_sets_new():
    """Форма создания нового комплекса"""
    defaults = UserPrefsModel.get_defaults()
    return render_template('workout_sets/form.html',
                         workout_set=None,
                         exercises=[],
                         defaults=defaults,
                         title='Создать комплекс')


@app.route('/workout-sets/create', methods=['POST'])
def workout_sets_create():
    """Создание нового комплекса"""
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()

    if not name:
        flash('Название комплекса обязательно для заполнения', 'error')
        defaults = UserPrefsModel.get_defaults()
        return render_template('workout_sets/form.html',
                             workout_set={'name': name, 'description': description},
                             exercises=[],
                             defaults=defaults,
                             title='Создать комплекс')

    try:
        # Создаем комплекс
        workoutset_code = WorkoutSetModel.create(name, description)

        flash('Комплекс успешно создан! Теперь добавьте упражнения.', 'success')
        return redirect(url_for('workout_sets_edit', code=workoutset_code))

    except Exception as e:
        flash(f'Ошибка при создании комплекса: {str(e)}', 'error')
        defaults = UserPrefsModel.get_defaults()
        return render_template('workout_sets/form.html',
                             workout_set={'name': name, 'description': description},
                             exercises=[],
                             defaults=defaults,
                             title='Создать комплекс')


@app.route('/workout-sets/<code>/edit')
def workout_sets_edit(code):
    """Форма редактирования комплекса"""
    workout_set = WorkoutSetModel.get_by_code(code)
    if not workout_set:
        flash('Комплекс не найден', 'error')
        return redirect(url_for('workout_sets_list'))

    exercises = ExerciseModel.get_by_workoutset(code)
    defaults = UserPrefsModel.get_defaults()

    return render_template('workout_sets/form.html',
                         workout_set=workout_set,
                         exercises=exercises,
                         defaults=defaults,
                         title='Редактировать комплекс')


@app.route('/workout-sets/<code>/update', methods=['POST'])
def workout_sets_update(code):
    """Обновление комплекса"""
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()

    if not name:
        flash('Название комплекса обязательно для заполнения', 'error')
        return redirect(url_for('workout_sets_edit', code=code))

    try:
        # Обновляем основную информацию комплекса
        success = WorkoutSetModel.update(code, name, description)
        if not success:
            flash('Комплекс не найден', 'error')
            return redirect(url_for('workout_sets_list'))

        # Проверяем, есть ли данные упражнений для обработки
        exercises_data_raw = request.form.get('exercises_data', '').strip()
        if exercises_data_raw:
            # Обрабатываем упражнения только если есть данные
            exercises_data = json.loads(exercises_data_raw)

            # Получаем существующие упражнения
            existing_exercises = {ex['code']: ex for ex in ExerciseModel.get_by_workoutset(code)}
            processed_codes = set()

            ensure_upload_folder()

            for exercise_index, exercise_data in enumerate(exercises_data):
                if not exercise_data.get('name', '').strip():
                    continue

                exercise_code = exercise_data.get('code')
                images = exercise_data.get('existing_images', [])

                # Обрабатываем новые изображения для данного упражнения
                image_pattern = f'exercise_{exercise_index}_image_'
                for field_name in request.files:
                    if field_name.startswith(image_pattern):
                        image_file = request.files[field_name]
                        if (image_file and image_file.filename != '' and
                            allowed_file(image_file.filename)):

                            filename = secure_filename(image_file.filename)
                            filename = f"{code}_{exercise_index}_{len(images)}_{filename}"
                            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                            image_file.save(filepath)
                            images.append(f"images/exercises/{filename}")

                if exercise_code and exercise_code in existing_exercises:
                    # Обновляем существующее упражнение
                    ExerciseModel.update(
                        code=exercise_code,
                        name=exercise_data['name'],
                        description=exercise_data.get('description', ''),
                        images=images,
                        video_url=exercise_data.get('video_url', ''),
                        repeat_count=int(exercise_data.get('repeat_count', 10)),
                        round_count=int(exercise_data.get('round_count', 3)),
                        rest_seconds=int(exercise_data.get('rest_seconds', 60))
                    )
                    processed_codes.add(exercise_code)
                else:
                    # Создаем новое упражнение
                    new_code = ExerciseModel.create(
                        workoutset_code=code,
                        name=exercise_data['name'],
                        description=exercise_data.get('description', ''),
                        images=images,
                        video_url=exercise_data.get('video_url', ''),
                        repeat_count=int(exercise_data.get('repeat_count', 10)),
                        round_count=int(exercise_data.get('round_count', 3)),
                        rest_seconds=int(exercise_data.get('rest_seconds', 60))
                    )
                    processed_codes.add(new_code)

            # Удаляем упражнения, которые не были обработаны
            for exercise_code in existing_exercises:
                if exercise_code not in processed_codes:
                    ExerciseModel.delete(exercise_code)

        flash('Информация о комплексе успешно сохранена', 'success')
        return redirect(url_for('workout_sets_edit', code=code))

    except Exception as e:
        flash(f'Ошибка при обновлении комплекса: {str(e)}', 'error')
        return redirect(url_for('workout_sets_edit', code=code))


@app.route('/workout-sets/<code>/delete', methods=['POST'])
def workout_sets_delete(code):
    """Удаление комплекса"""
    try:
        # Сначала удаляем все записи тренировок для этого комплекса
        WorkoutLogModel.delete_by_workoutset(code)
        # Затем удаляем все упражнения (они могут удалиться автоматически через CASCADE)
        ExerciseModel.delete_by_workoutset(code)
        # Наконец удаляем сам комплекс
        success = WorkoutSetModel.delete(code)
        if success:
            flash('Комплекс успешно удален', 'success')
        else:
            flash('Комплекс не найден', 'error')
    except Exception as e:
        flash(f'Ошибка при удалении комплекса: {str(e)}', 'error')

    return redirect(url_for('workout_sets_list'))


@app.route('/settings')
def settings():
    """Страница настроек приложения"""
    prefs = UserPrefsModel.get_first()
    return render_template('settings.html', prefs=prefs)


@app.route('/exercises/<code>/delete', methods=['POST'])
def exercise_delete(code):
    """Удаление упражнения"""
    try:
        success = ExerciseModel.delete(code)
        if success:
            return jsonify({'success': True, 'message': 'Упражнение удалено'})
        else:
            return jsonify({'success': False, 'message': 'Упражнение не найдено'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'}), 500


@app.route('/exercises/create', methods=['POST'])
def exercise_create():
    """Создание нового упражнения"""
    try:
        workoutset_code = request.form.get('workoutset_code')
        name = request.form.get('name', '').strip()

        if not workoutset_code or not name:
            return jsonify({'success': False, 'message': 'Неполные данные'}), 400

        # Проверяем что комплекс существует
        workout_set = WorkoutSetModel.get_by_code(workoutset_code)
        if not workout_set:
            return jsonify({'success': False, 'message': 'Комплекс не найден'}), 404

        # Обрабатываем изображения
        images = []
        ensure_upload_folder()

        for field_name in request.files:
            if field_name.startswith('image_'):
                image_file = request.files[field_name]
                if (image_file and image_file.filename != '' and
                    allowed_file(image_file.filename)):

                    filename = secure_filename(image_file.filename)
                    filename = f"{workoutset_code}_{len(images)}_{filename}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image_file.save(filepath)
                    images.append(f"images/exercises/{filename}")

        # Создаем упражнение
        exercise_code = ExerciseModel.create(
            workoutset_code=workoutset_code,
            name=name,
            description=request.form.get('description', ''),
            images=images,
            video_url=request.form.get('video_url', ''),
            repeat_count=int(request.form.get('repeat_count', 10)),
            round_count=int(request.form.get('round_count', 3)),
            rest_seconds=int(request.form.get('rest_seconds', 60))
        )

        # Получаем созданное упражнение для ответа
        exercise = ExerciseModel.get_by_code(exercise_code)

        return jsonify({
            'success': True,
            'message': 'Упражнение создано',
            'exercise': exercise
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'}), 500


@app.route('/exercises/<code>/update', methods=['POST'])
def exercise_update(code):
    """Обновление упражнения"""
    try:
        name = request.form.get('name', '').strip()

        if not name:
            return jsonify({'success': False, 'message': 'Название обязательно'}), 400

        # Получаем существующее упражнение
        existing_exercise = ExerciseModel.get_by_code(code)
        if not existing_exercise:
            return jsonify({'success': False, 'message': 'Упражнение не найдено'}), 404

        # Обрабатываем изображения - начинаем с существующих
        images = existing_exercise.get('images', []).copy()

        # Удаляем изображения, помеченные для удаления
        deleted_images_str = request.form.get('deleted_images', '')
        if deleted_images_str:
            deleted_images = [img.strip() for img in deleted_images_str.split(',') if img.strip()]
            # Удаляем из списка изображений
            images = [img for img in images if img not in deleted_images]

            # Удаляем физические файлы
            for deleted_image in deleted_images:
                try:
                    file_path = os.path.join(app.static_folder, deleted_image)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Ошибка при удалении файла {deleted_image}: {e}")

        # Добавляем новые изображения
        ensure_upload_folder()

        for field_name in request.files:
            if field_name.startswith('image_'):
                image_file = request.files[field_name]
                if (image_file and image_file.filename != '' and
                    allowed_file(image_file.filename)):

                    filename = secure_filename(image_file.filename)
                    filename = f"{existing_exercise['workoutset_code']}_{len(images)}_{filename}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image_file.save(filepath)
                    images.append(f"images/exercises/{filename}")

        # Обновляем упражнение
        success = ExerciseModel.update(
            code=code,
            name=name,
            description=request.form.get('description', ''),
            images=images,
            video_url=request.form.get('video_url', ''),
            repeat_count=int(request.form.get('repeat_count', 10)),
            round_count=int(request.form.get('round_count', 3)),
            rest_seconds=int(request.form.get('rest_seconds', 60))
        )

        if success:
            # Получаем обновленное упражнение для ответа
            exercise = ExerciseModel.get_by_code(code)
            return jsonify({
                'success': True,
                'message': 'Упражнение обновлено',
                'exercise': exercise
            })
        else:
            return jsonify({'success': False, 'message': 'Ошибка обновления'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'}), 500


@app.route('/settings/save', methods=['POST'])
def settings_save():
    """Сохранение настроек"""
    try:
        default_round_count = int(request.form.get('default_round_count', 3))
        default_repeat_count = int(request.form.get('default_repeat_count', 10))
        default_rest_seconds = int(request.form.get('default_rest_seconds', 60))

        # Валидация значений
        if not (1 <= default_round_count <= 99):
            flash('Число подходов должно быть от 1 до 99', 'error')
            return redirect(url_for('settings'))

        if not (1 <= default_repeat_count <= 999):
            flash('Число повторений должно быть от 1 до 999', 'error')
            return redirect(url_for('settings'))

        if not (0 <= default_rest_seconds <= 9999):
            flash('Время отдыха должно быть от 0 до 9999 секунд', 'error')
            return redirect(url_for('settings'))

        # Проверяем, есть ли уже настройки
        existing_prefs = UserPrefsModel.get_first()

        if existing_prefs:
            # Обновляем существующие настройки
            UserPrefsModel.update(
                code=existing_prefs['code'],
                default_repeat_count=default_repeat_count,
                default_round_count=default_round_count,
                default_rest_seconds=default_rest_seconds
            )
            flash('Настройки успешно обновлены', 'success')
        else:
            # Создаем новые настройки
            UserPrefsModel.create(
                default_repeat_count=default_repeat_count,
                default_round_count=default_round_count,
                default_rest_seconds=default_rest_seconds
            )
            flash('Настройки успешно сохранены', 'success')

    except ValueError:
        flash('Все поля должны содержать числовые значения', 'error')
    except Exception as e:
        flash(f'Ошибка при сохранении настроек: {str(e)}', 'error')

    return redirect(url_for('settings'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)