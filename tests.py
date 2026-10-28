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
# tests.py
import sqlite3
import os
from database import DatabaseManager
from task_dao import NotesDAO, TaskDAO, TimerDAO, TimeLogsDAO, StudentBusinessDAO
from logic.task_service import TaskService

def run_all_tests(db_name: str):
    # Очищаем старый файл БД перед тестами для чистоты окружения
    if os.path.exists(db_name):
        os.remove(db_name)

    manager = DatabaseManager(db_name)
    manager.init_database()

    notes_dao = NotesDAO(manager)
    task_dao = TaskDAO(manager)
    timer_dao = TimerDAO(manager)
    logs_dao = TimeLogsDAO(manager)
    business_dao = StudentBusinessDAO(manager)

    # Инициализация сервиса бизнес-логики
    service = TaskService(task_dao, timer_dao, logs_dao, business_dao)

    print("=== ШАГ 3.1: Тест успешной вставки учебных данных ===")
    note_id = notes_dao.insert('Базы данных', 'Подготовка к сессии')
    task_id = task_dao.insert(note_id, 'Написать лабораторную по базам данных')
    timer_dao.insert(task_id, '2026-10-12 12:00:00')
    logs_dao.insert(task_id, '2026-10-12 12:00:00', 45, '2026-10-12 12:45:00')
    print("[УСПЕХ]: Данные студента добавлены.")

    print("\n=== ШАГ 3.2: Тест защиты CHECK (Отрицательное время) ===")
    try:
        logs_dao.insert(task_id, '2026-10-12 13:00:00', -15, '2026-10-12 12:45:00')
        print("[ОШИБКА]: База данных пропустила отрицательное время.")
    except sqlite3.IntegrityError:
        print("[УСПЕХ]: База данных заблокировала ошибку (-15 минут).")

    print("\n=== ШАГ 3.3: Тест защиты ON DELETE RESTRICT ===")
    try:
        task_dao.delete(task_id)
        print("[ОШИБКА]: База данных позволила удалить задачу со связанными логами.")
    except sqlite3.IntegrityError:
        print("[УСПЕХ]: Удаление заблокировано. История подготовки защищена.")

    print("\n=== ПРОВЕРКА МЕНЮ ОТЧЕТОВ ===")
    for row in business_dao.getFilteredTimeReport('2026-10-01', '2026-10-30'):
        print(f"Задача: {row['task_text']} | Натиканное время: {row['total_duration']} мин.")

    # -------------------------------------------------------------------------
    # НОВЫЙ БЛОК: ТЕСТИРОВАНИЕ ВЫПОЛНЕНИЯ ПРАВИЛ БИЗНЕС-ЛОГИКИ (ПО ТЗ)
    # -------------------------------------------------------------------------
    print("\n=== ТЕСТИРОВАНИЕ СЛОЯ БИЗНЕС-ЛОГИКИ (SERVICES) ===")

    # Тест бизнес-логики таймера: Ошибка хронологии
    print("Тест бизнес-правила 1 (Время остановки таймера в прошлом):")
    try:
        # Пытаемся остановить задачу 1 (старт в 12:00:00) временем 11:30:00
        service.stop_and_save_timer(task_id=1, stop_time="2026-10-12 11:30:00")
        print("[ОШИБКА]: Бизнес-логика пропустила некорректное время остановки.")
    except ValueError as error:
        print(f"[УСПЕХ]: Исключение перехвачено сервисом. Сообщение: {error}")

    # Тест бизнес-логики удаления: Защита на уровне приложения
    print("Тест бизнес-правила 2 (Запрет удаления задачи при наличии логов):")
    try:
        service.safe_delete_task(task_id=1)
        print("[ОШИБКА]: Сервис позволил удалить задачу с историей.")
    except PermissionError as error:
        print(f"[УСПЕХ]: Исключение безопасности успешно обработано. Сообщение: {error}")

    # Тест бизнес-логики отчетов: Проверка корректности ввода границ периода
    print("Тест бизнес-правила 3 (Нарушение хронологического порядка дат отчета):")
    try:
        service.get_filtered_time_report(start_date="2026-10-30", end_date="2026-10-01")
        print("[ОШИБКА]: Сервис сгенерировал отчет по некорректному диапазону дат.")
    except ValueError as error:
        print(f"[УСПЕХ]: Исключение валидации параметров успешно перехвачено. Сообщение: {error}")

    # Успешное выполнение операции бизнес-логики
    print("Тест успешного выполнения операции остановки таймера:")
    # Создаем новую задачу без логов для чистой проверки таймера
    clean_task_id = task_dao.insert(note_id, 'Чистая задача для проверки таймера')
    timer_dao.insert(clean_task_id, '2026-10-15 10:00:00')
    
    success_stop = service.stop_and_save_timer(task_id=clean_task_id, stop_time="2026-10-15 11:00:00")
    print(f"[УСПЕХ]: Таймер успешно остановлен сервисом: {success_stop} (Зафиксировано 60 минут).")
    # -------------------------------------------------------------------------

    print("\n=== ШАГ 3.4: Тест правила ON DELETE SET NULL ===")
    notes_dao.delete(note_id)
    print("[УСПЕХ]: Предмет удален.")
    for row in business_dao.getTasksWithNotesContext():
        print(f"Задача: {row['task_text']} | Категория: {row['note_title']}")

if __name__ == "__main__":
    run_all_tests("timetracker.db")
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
