ЧАСТЬ 1. СОЗДАНИЕ ТАБЛИЦ И СВЯЗЕЙ


Включение контроля внешних ключей в SQLite
PRAGMA foreign_keys = ON;

Удаление таблиц 
DROP TABLE IF EXISTS timer;
DROP TABLE IF EXISTS time_logs;
DROP TABLE IF EXISTS task;
DROP TABLE IF EXISTS notes;
DROP TABLE IF EXISTS backup_log;

1. Таблица заметок
CREATE TABLE notes (
    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK(length(title) > 0),
    content TEXT,
    created_date TEXT NOT NULL DEFAULT (datetime('now'))
);

2. Таблица задач 
CREATE TABLE task (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id INTEGER,
    task_text TEXT NOT NULL CHECK(length(task_text) > 0),
    is_completed INTEGER NOT NULL DEFAULT 0 CHECK (is_completed IN (0, 1)),

    FOREIGN KEY (note_id) REFERENCES notes(note_id) ON DELETE SET NULL
);

3. Таблица логов времени
CREATE TABLE time_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    start_time TEXT NOT NULL,
    duration INTEGER NOT NULL CHECK (duration > 0), 
    end_time TEXT NOT NULL,

    FOREIGN KEY (task_id) REFERENCES task(task_id) ON DELETE RESTRICT
);

4. Таблица таймеров 
CREATE TABLE timer (
    timer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL UNIQUE,
    start_time TEXT NOT NULL,

    FOREIGN KEY (task_id) REFERENCES task(task_id) ON DELETE CASCADE
);

5. Таблица логов бэкапа 
CREATE TABLE backup_log (
    backup_id INTEGER PRIMARY KEY AUTOINCREMENT,
    backup_time TEXT NOT NULL DEFAULT (datetime('now')),
    file_path TEXT NOT NULL UNIQUE CHECK(length(file_path) > 0), 
    status TEXT NOT NULL CHECK (status IN ('success', 'failed', 'in_progress'))
);

Индексы для оптимизации поиска
CREATE INDEX idx_task_note_id ON task(note_id);
CREATE INDEX idx_time_logs_task_id ON time_logs(task_id);


ЧАСТЬ 2. ТЕСТИРОВАНИЕ И ПРОВЕРКА ОГРАНИЧЕНИЙ


Шаг 3.1: Тест успешной вставки корректных данных
INSERT INTO notes (title, content) VALUES ('Списки задач', 'Подготовка к сессии');
INSERT INTO task (note_id, task_text) VALUES (1, 'Написать лабораторную по базам данных');
INSERT INTO timer (task_id, start_time) VALUES (1, '2026-10-12 12:00:00');
INSERT INTO time_logs (task_id, start_time, duration, end_time) 
VALUES (1, '2026-10-12 12:00:00', 45, '2026-10-12 12:45:00');

Выводим данные для проверки, что всё успешно вставилось
SELECT 'Данные успешно добавлены' AS статус, * FROM task;


Шаг 3.2: Тест ограничения CHECK (Попытка вставить отрицательное время)

INSERT INTO time_logs (task_id, start_time, duration, end_time) 
VALUES (1, '2026-10-12 13:00:00', -15, '2026-10-12 12:45:00');


Шаг 3.3: Тест ограничения ON DELETE RESTRICT (Защита связанных данных)

DELETE FROM task WHERE task_id = 1;


Шаг 3.4: Тест правила ON DELETE SET NULL
DELETE FROM notes WHERE note_id = 1;

SELECT 'Результат SET NULL (поле note_id должно быть NULL)' AS тест, * FROM task;
