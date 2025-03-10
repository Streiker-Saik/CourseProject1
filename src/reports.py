import datetime
import json
import logging
import os
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd

from src.utils import validate_and_format_date

# создание абсолютного пути из относительного
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
log_file = os.path.join(project_root, "logs", "reports.log")
# создаем директорию и файл если она не существует
os.makedirs(os.path.dirname(log_file), exist_ok=True)

reports_logger = logging.getLogger("reports")
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
file_formater = logging.Formatter("%(asctime)s - %(name)s: %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formater)
reports_logger.addHandler(file_handler)
reports_logger.setLevel(logging.DEBUG)


def report_execution(fail_path: Optional[str] = None) -> Callable:
    """Декоратор выводящий результат выполнения функции(с DataFrame) файл *.csv, по умолчанию там же"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            if not fail_path:
                names_path = f"data/{func.__name__}.json"
            else:
                names_path = fail_path

            with open(names_path, "w", encoding="UTF-8") as file_json:
                data = json.loads(result)
                json.dump(data, file_json, indent=4, ensure_ascii=False)
            return result

        return wrapper

    return decorator


@report_execution()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> str:
    """Функция принимает DataFrame с транзакциями, название категории и опциональную дату(YYYY-MM-DD).
    Возвращает траты по заданной категории за последние 90 дней (от переданной даты) в JSON"""
    reports_logger.info(f"Функция фильтрации DataFrame по {category} началась")
    if not date:
        reports_logger.info("Дата не указана, принимается текущая дата(datetime)")
        date_obj = datetime.datetime.now()
    else:
        date_obj = validate_and_format_date(date)
        reports_logger.info("Дата преобразована datetime")
    date_to = date_obj
    date_from = date_obj - datetime.timedelta(days=90)

    # Проверяем наличие необходимых столбцов
    required_columns = ["Дата операции", "Статус", "Сумма платежа", "Категория"]
    missing_columns = [column for column in required_columns if column not in transactions.columns]
    if missing_columns:
        error_message = f"DataFrame должен содержать столбцы: {missing_columns}"
        reports_logger.error(error_message)
        raise ValueError(error_message)

    # переводим в df дату (DD.MM.YYYY HH:MM:SS) в datetime
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)

    # фильтруем транзакции за период, со статусом OK, только траты и введенную категорию
    filtered_df = transactions[
        (transactions["Дата операции"] >= date_from)
        & (transactions["Дата операции"] <= date_to)
        & (transactions["Статус"] == "OK")
        & (transactions["Сумма платежа"] < 0)
        & (transactions["Категория"] == category)
    ].copy()

    # переводим в df дату обратно в строку "DD.MM.YYYY HH:MM:SS", т.к. из df в json не переводит <>
    filtered_df["Дата операции"] = filtered_df["Дата операции"].apply(lambda x: x.strftime("%d.%m.%Y %H:%M:%S"))

    reports_logger.info(f"Функция фильтрации DataFrame по {category} завершена успешно")

    result_list = filtered_df.to_dict(orient="records")
    result = json.dumps(result_list, ensure_ascii=False)

    reports_logger.info("Функция фильтрации DataFrame c преобразованием в JSON - завершена успешно")
    return result
