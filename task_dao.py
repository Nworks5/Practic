"""!
@file task_dao.py
@brief Модуль для работы с таблицами базы данных (DAO-слой).
@details Содержит классы для добавления, получения и удаления заметок, задач, таймеров, записей времени и отчетов.
"""

import sqlite3
from typing import List, Optional
from database import DatabaseManager


class NotesDAO:
    """!
    @brief Класс для работы с таблицей заметок (notes).
    """

    def __init__(self, db: DatabaseManager):
        """!
        @brief Конструктор класса.
        @param db Объект менеджера базы данных.
        """
        self.db = db

    def insert(self, title: str, content: str) -> int:
        """!
        @brief Добавляет новую заметку в базу.
        @param title Заголовок заметки.
        @param content Текст заметки.
        @return ID добавленной заметки.
        """
        with self.db.get_connection() as conn:
            return conn.execute("INSERT INTO notes (title, content) VALUES (?, ?);", (title, content)).lastrowid

    def delete(self, id_val: int) -> bool:
        """!
        @brief Удаляет заметку по ее ID.
        @param id_val ID заметки.
        @return True, если заметка удалена.
        """
        with self.db.get_connection() as conn:
            return conn.execute("DELETE FROM notes WHERE note_id = ?;", (id_val,)).rowcount > 0


class TaskDAO:
    """!
    @brief Класс для работы с таблицей задач (task).
    """

    def __init__(self, db: DatabaseManager):
        """!
        @brief Конструктор класса.
        @param db Объект менеджера базы данных.
        """
        self.db = db

    def insert(self, note_id: Optional[int], task_text: str) -> int:
        """!
        @brief Добавляет новую задачу.
        @param note_id ID связанной заметки (может быть None).
        @param task_text Текст задачи.
        @return ID созданной задачи.
        """
        with self.db.get_connection() as conn:
            return conn.execute("INSERT INTO task (note_id, task_text) VALUES (?, ?);", (note_id, task_text)).lastrowid

    def getAll(self) -> List[sqlite3.Row]:
        """!
        @brief Возвращает список всех задач из базы.
        @return Список строк таблицы task.
        """
        with self.db.get_connection() as conn:
            return conn.execute("SELECT task_id, note_id, task_text, is_complete FROM task;").fetchall()

    def delete(self, id_val: int) -> bool:
        """!
        @brief Удаляет задачу по ее ID.
        @param id_val ID задачи.
        @return True, если задача удалена.
        """
        with self.db.get_connection() as conn:
            return conn.execute("DELETE FROM task WHERE task_id = ?;", (id_val,)).rowcount > 0


class TimerDAO:
    """!
    @brief Класс для работы с активными таймерами (timer).
    """

    def __init__(self, db: DatabaseManager):
        """!
        @brief Конструктор класса.
        @param db Объект менеджера базы данных.
        """
        self.db = db

    def insert(self, task_id: int, start_time: str):
        """!
        @brief Запускает новый таймер для задачи.
        @param task_id ID задачи.
        @param start_time Время начала работы.
        """
        with self.db.get_connection() as conn:
            conn.execute("INSERT INTO timer (task_id, start_time) VALUES (?, ?);", (task_id, start_time))


class TimeLogsDAO:
    """!
    @brief Класс для сохранения истории затраченного времени (time_logs).
    """

    def __init__(self, db: DatabaseManager):
        """!
        @brief Конструктор класса.
        @param db Объект менеджера базы данных.
        """
        self.db = db

    def insert(self, task_id: int, start_time: str, duration: int, end_time: str):
        """!
        @brief Записывает завершенную сессию работы в историю.
        @param task_id ID задачи.
        @param start_time Время старта.
        @param duration Длительность в минутах.
        @param end_time Время окончания.
        """
        with self.db.get_connection() as conn:
            conn.execute("INSERT INTO time_logs (task_id, start_time, duration, end_time) VALUES (?, ?, ?, ?);", 
                         (task_id, start_time, duration, end_time))


class StudentBusinessDAO:
    """!
    @brief Класс для сложных запросов и формирования отчетов.
    """

    def __init__(self, db: DatabaseManager):
        """!
        @brief Конструктор класса.
        @param db Объект менеджера базы данных.
        """
        self.db = db

    def getFilteredTimeReport(self, startDate: str, endDate: str) -> List[sqlite3.Row]:
        """!
        @brief Считает общее время по каждой задаче за выбранный период.
        @param startDate Начальная дата периода.
        @param endDate Конечная дата периода.
        @return Список задач с суммарным временем.
        """
        sql = """
        SELECT t.task_text, SUM(tl.duration) AS total_duration
        FROM task t JOIN time_logs tl ON t.task_id = tl.task_id
        WHERE tl.start_time BETWEEN ? AND ? GROUP BY t.task_id;
        """
        with self.db.get_connection() as conn:
            return conn.execute(sql, (startDate, endDate)).fetchall()

    def getTasksWithNotesContext(self) -> List[sqlite3.Row]:
        """!
        @brief Возвращает список задач вместе с названиями их заметок.
        @return Список задач и заголовков заметок (или 'Без категории').
        """
        sql = """
        SELECT t.task_id, t.task_text, COALESCE(n.title, 'Без категории') AS note_title
        FROM task t LEFT JOIN notes n ON t.note_id = n.note_id;
        """
        with self.db.get_connection() as conn:
            return conn.execute(sql).fetchall()
