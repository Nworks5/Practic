import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path: str = "timetracker.db"):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Загрузка структуры таблиц из файла init.sql"""
        if not os.path.exists("init.sql"):
            raise FileNotFoundError("Файл init.sql не найден!")
        with open("init.sql", "r", encoding="utf-8") as f:
            sql_script = f.read()
        with self.get_connection() as conn:
            conn.executescript(sql_script)
            conn.commit()
