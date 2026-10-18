import sqlite3
from database import DatabaseManager
from task_dao import NotesDAO, TaskDAO, TimerDAO, TimeLogsDAO, StudentBusinessDAO

def run_all_tests(db_name: str):
    manager = DatabaseManager(db_name)
    manager.init_database()

    notes_dao = NotesDAO(manager)
    task_dao = TaskDAO(manager)
    timer_dao = TimerDAO(manager)
    logs_dao = TimeLogsDAO(manager)
    business_dao = StudentBusinessDAO(manager)

    print("=== ШАГ 3.1: Тест успешной вставки учебных данных ===")
    note_id = notes_dao.insert('Базы данных', 'Подготовка к сессии')
    task_id = task_dao.insert(note_id, 'Написать лабораторную по базам данных')
    timer_dao.insert(task_id, '2026-10-12 12:00:00')
    logs_dao.insert(task_id, '2026-10-12 12:00:00', 45, '2026-10-12 12:45:00')
    print("[УСПЕХ]: Данные студента добавлены.")

    print("\n=== ШАГ 3.2: Тест защиты CHECK (Отрицательное время) ===")
    try:
        logs_dao.insert(task_id, '2026-10-12 13:00:00', -15, '2026-10-12 12:45:00')
    except sqlite3.IntegrityError:
        print("[УСПЕХ]: База данных заблокировала ошибку (-15 минут).")

    print("\n=== ШАГ 3.3: Тест защиты ON DELETE RESTRICT ===")
    try:
        task_dao.delete(task_id)
    except sqlite3.IntegrityError:
        print("[УСПЕХ]: Удаление заблокировано. История подготовки защищена.")

    print("\n=== ПРОВЕРКА МЕНЮ ОТЧЕТОВ ===")
    for row in business_dao.getFilteredTimeReport('2026-10-01', '2026-10-30'):
        print(f"Задача: {row['task_text']} | Натиканное время: {row['total_duration']} мин.")

    print("\n=== ШАГ 3.4: Тест правила ON DELETE SET NULL ===")
    notes_dao.delete(note_id)
    print("[УСПЕХ]: Предмет удален.")
    for row in business_dao.getTasksWithNotesContext():
        print(f"Задача: {row['task_text']} | Категория: {row['note_title']}")
