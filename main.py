"""!
@file main.py
@brief Главный файл запуска программы.
@details Запускает выполнение модульных тестов для проверки работы базы данных и DAO-слоя приложения Timetracker.
"""

from tests import run_all_tests

if __name__ == "__main__":
    print("Запуск модульных тестов DAO-слоя приложения Timetracker...\n")
    run_all_tests("student_tracker.db")
