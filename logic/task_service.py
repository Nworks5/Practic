"""!
@file task_service.py
@brief Файл с основной логикой работы задач и таймера.
"""

import datetime
from typing import List, Dict, Any


class TaskService:
    """!
    @brief Класс для работы с таймерами, удалением задач и отчетами.
    """

    def __init__(self, task_dao, timer_dao, time_logs_dao, business_dao):
        """!
        @brief Конструктор класса.
        @param task_dao Объект для работы с таблицей задач.
        @param timer_dao Объект для работы с таймерами.
        @param time_logs_dao Объект для работы с логом времени.
        @param business_dao Объект для получения отчетов.
        """
        # Принимаем ваши готовые объекты DAO классов
        self.task_dao = task_dao
        self.timer_dao = timer_dao
        self.time_logs_dao = time_logs_dao
        self.business_dao = business_dao

    def stop_and_save_timer(self, task_id: int, stop_time: str) -> bool:
        """!
        @brief Останавливает таймер и сохраняет потраченное время в историю.
        @param task_id ID задачи.
        @param stop_time Время остановки (формат ГГГГ-ММ-ДД ЧЧ:ММ:СС).
        @return True, если время успешно сохранилось.
        @throws ValueError Если таймер не найден или время остановки меньше времени старта.
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
        """!
        @brief Удаляет задачу, если по ней еще нет записей времени.
        @param task_id ID задачи для удаления.
        @return True, если задача удалена.
        @throws PermissionError Если у задачи уже есть записанное время.
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
        """!
        @brief Возвращает отчет по времени за выбранные даты.
        @param start_date Начальная дата.
        @param end_date Конечная дата.
        @return Список задач с общим затраченным временем.
        @throws ValueError Если даты пустые или начальная дата больше конечной.
        """
        if start_date == "" or end_date == "":
            raise ValueError("Поля дат не должны быть пустыми")
            
        if start_date > end_date:
            raise ValueError("Некорректный диапазон дат")
            
        # Вызываем ваш готовый StudentBusinessDAO
        rows = self.business_dao.getFilteredTimeReport(start_date, end_date)
        return [{"task_text": r["task_text"], "total_duration": r["total_duration"]} for r in rows]
