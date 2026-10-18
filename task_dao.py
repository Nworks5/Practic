import sqlite3
from typing import List, Optional
from database import DatabaseManager

class NotesDAO:
    def __init__(self, db: DatabaseManager): self.db = db
    def insert(self, title: str, content: str) -> int:
        with self.db.get_connection() as conn:
            return conn.execute("INSERT INTO notes (title, content) VALUES (?, ?);", (title, content)).lastrowid
    def delete(self, id_val: int) -> bool:
        with self.db.get_connection() as conn:
            return conn.execute("DELETE FROM notes WHERE note_id = ?;", (id_val,)).rowcount > 0

class TaskDAO:
    def __init__(self, db: DatabaseManager): self.db = db
    def insert(self, note_id: Optional[int], task_text: str) -> int:
        with self.db.get_connection() as conn:
            return conn.execute("INSERT INTO task (note_id, task_text) VALUES (?, ?);", (note_id, task_text)).lastrowid
    def getAll(self) -> List[sqlite3.Row]:
        with self.db.get_connection() as conn:
            return conn.execute("SELECT task_id, note_id, task_text, is_complete FROM task;").fetchall()
    def delete(self, id_val: int) -> bool:
        with self.db.get_connection() as conn:
            return conn.execute("DELETE FROM task WHERE task_id = ?;", (id_val,)).rowcount > 0

class TimerDAO:
    def __init__(self, db: DatabaseManager): self.db = db
    def insert(self, task_id: int, start_time: str):
        with self.db.get_connection() as conn:
            conn.execute("INSERT INTO timer (task_id, start_time) VALUES (?, ?);", (task_id, start_time))

class TimeLogsDAO:
    def __init__(self, db: DatabaseManager): self.db = db
    def insert(self, task_id: int, start_time: str, duration: int, end_time: str):
        with self.db.get_connection() as conn:
            conn.execute("INSERT INTO time_logs (task_id, start_time, duration, end_time) VALUES (?, ?, ?, ?);", 
                         (task_id, start_time, duration, end_time))

class StudentBusinessDAO:
    def __init__(self, db: DatabaseManager): self.db = db
    def getFilteredTimeReport(self, startDate: str, endDate: str) -> List[sqlite3.Row]:
        sql = """
        SELECT t.task_text, SUM(tl.duration) AS total_duration
        FROM task t JOIN time_logs tl ON t.task_id = tl.task_id
        WHERE tl.start_time BETWEEN ? AND ? GROUP BY t.task_id;
        """
        with self.db.get_connection() as conn: return conn.execute(sql, (startDate, endDate)).fetchall()

    def getTasksWithNotesContext(self) -> List[sqlite3.Row]:
        sql = """
        SELECT t.task_id, t.task_text, COALESCE(n.title, 'Без категории') AS note_title
        FROM task t LEFT JOIN notes n ON t.note_id = n.note_id;
        """
        with self.db.get_connection() as conn: return conn.execute(sql).fetchall()
