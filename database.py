"""!
@file database.py
@brief Модуль для подключения к базе данных SQLite.
"""

import sqlite3
import os


class DatabaseManager:
    """!
    @brief Класс для работы с базой данных и создания таблиц.
    """

    def __init__(self, db_path: str = "timetracker.db"):
        """!
        @brief Конструктор класса.
        @param db_path Путь к файлу базы данных.
        """
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        """!
        @brief Открывает соединение с базой данных.
        @return Объект подключения sqlite3.Connection.
        """
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """!
        @brief Создает таблицы в базе из файла init.sql.
        @throws FileNotFoundError Если файл init.sql не найден.
        """
        if not os.path.exists("init.sql"):
            raise FileNotFoundError("Файл init.sql не найден!")
        with open("init.sql", "r", encoding="utf-8") as f:
            sql_script = f.read()
        with self.get_connection() as conn:
            conn.executescript(sql_script)
            conn.commit()
