# logic/task_service.py
import datetime
from typing import List, Dict, Any

class TaskService:
    def __init__(self, task_dao, timer_dao, time_logs_dao, business_dao):
        # Принимаем ваши готовые объекты DAO классов
        self.task_dao = task_dao
        self.timer_dao = timer_dao
        self.time_logs_dao = time_logs_dao
        self.business_dao = business_dao

    def stop_and_save_timer(self, task_id: int, stop_time: str) -> bool:
        """
        Операция 1: Остановка таймера и фиксация времени сессии.
        Проверяет наличие активного таймера и хронологию дат.
        """
        if task_id <= 0:
            raise ValueError("Неверный номер задачи")

        # Ищем запущенный таймер в базе через соединение менеджера
        with self.timer_dao.db.get_connection() as conn:
            row = conn.execute("SELECT timer_id, task_id, start_time FROM timer WHERE task_id = ?;", (task_id,)).fetchone()
        
        if row is None:
            raise ValueError("Активный таймер не найден")
            
        timer_id, _, start_time_str = row[0], row[1], row[2]

        # Расчет длительности сессии в минутах
        date_format = "%Y-%m-%d %H:%M:%S"
        start_dt = datetime.datetime.strptime(start_time_str, date_format)
        stop_dt = datetime.datetime.strptime(stop_time, date_format)
        
        duration = int((stop_dt - start_dt).total_seconds() / 60)

        # Бизнес-правило: защита от отрицательного или нулевого времени сессии
        if duration <= 0:
            raise ValueError("Время стопа не может быть раньше старта")

        # Перенос записи в историю и удаление временного таймера с помощью ваших DAO
        with self.timer_dao.db.get_connection() as conn:
            conn.execute("INSERT INTO time_logs (task_id, start_time, duration, end_time) VALUES (?, ?, ?, ?);", 
                         (task_id, start_time_str, duration, stop_time))
            conn.execute("DELETE FROM timer WHERE timer_id = ?;", (timer_id,))
        return True

    def safe_delete_task(self, task_id: int) -> bool:
        """
        Операция 2: Безопасное удаление задачи.
        Блокирует операцию, если у задачи есть связанные логи времени.
        """
        # Бизнес-операция №4 из вашего файла: Подсчет логов с помощью SQL-запроса
        with self.task_dao.db.get_connection() as conn:
            row = conn.execute("SELECT COUNT(*) FROM time_logs WHERE task_id = ?;", (task_id,)).fetchone()
            logs_count = row[0] if row else 0

        # Бизнес-правило: Запрет удаления при наличии записей времени
        if logs_count > 0:
            raise PermissionError("Нельзя удалить запись задач уже с существующими записями времени")

        # Если логов нет, выполняем удаление через ваш TaskDAO
        return self.task_dao.delete(task_id)

    def get_filtered_time_report(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Операция 3: Валидация диапазонов дат перед выводом отчета.
        """
        if start_date == "" or end_date == "":
            raise ValueError("Поля дат не должны быть пустыми")
            
        if start_date > end_date:
            raise ValueError("Некорректный диапазон дат")
            
        # Вызываем ваш готовый StudentBusinessDAO
        rows = self.business_dao.getFilteredTimeReport(start_date, end_date)
        return [{"task_text": r["task_text"], "total_duration": r["total_duration"]} for r in rows]
