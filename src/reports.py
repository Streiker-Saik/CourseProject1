import datetime
import json
import logging
import os
from typing import Optional, Tuple

import pandas as pd

from src.decorators import report_execution
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


def calculate_date_range(
    date: Optional[str] = None, number_of_days: int = 90
) -> Tuple[datetime.datetime, datetime.datetime]:
    """
    Функция принимает опциональную дату(YYYY-MM-DD) и количество дней(по умолчанию 90).
    Возвращает кортеж datetime:
    - даты (по умолчанию текущей);
    - даты, которая на указанное количество дней назад).
    """
    reports_logger.info(f"Начата функция получение дат: до {date}, от {number_of_days} назад")
    if not date:
        reports_logger.info("Дата не указана, принимается текущая дата(datetime)")
        date_obj = datetime.datetime.now()
    else:
        date_obj = validate_and_format_date(date)
        reports_logger.info("Дата преобразована datetime")
    date_to = date_obj
    date_from = date_obj - datetime.timedelta(days=number_of_days)
    reports_logger.info(f"Возвращаем диапазон дат: до {date_to}, от {date_from} (на {number_of_days} дней назад)")
    return date_to, date_from


@report_execution()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> str:
    """Функция принимает DataFrame с транзакциями, название категории и опциональную дату(YYYY-MM-DD).
    Возвращает траты по заданной категории за последние 90 дней (от переданной даты) в JSON"""
    reports_logger.info(f"Функция фильтрации DataFrame по {category} началась")
    date_to, date_from = calculate_date_range(date, 90)

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

    # переводим в df дату обратно в строку "DD.MM.YYYY HH:MM:SS", т.к. из df в json не переводит <Time>
    filtered_df["Дата операции"] = filtered_df["Дата операции"].apply(lambda x: x.strftime("%d.%m.%Y %H:%M:%S"))

    reports_logger.info(f"DataFrame отфильтрован по столбцам: {required_columns}")

    result_list = filtered_df.to_dict(orient="records")
    result = json.dumps(result_list, ensure_ascii=False)

    reports_logger.info("Функция фильтрации DataFrame c преобразованием в JSON - завершена успешно")
    return result


@report_execution()
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> str:
    """Функция принимает DataFrame с транзакциями и опциональную дату(YYYY-MM-DD).
    Возвращает средние траты за каждый день недели за последние 90 дней (от переданной даты) в JSON"""
    reports_logger.info(f"Функция получение средних трат на каждый день недели по {date} началась")
    date_to, date_from = calculate_date_range(date, 90)

    # Проверяем наличие необходимых столбцов
    required_columns = ["Дата операции", "Статус", "Сумма платежа"]
    missing_columns = [column for column in required_columns if column not in transactions.columns]
    if missing_columns:
        error_message = f"DataFrame должен содержать столбцы: {missing_columns}"
        reports_logger.error(error_message)
        raise ValueError(error_message)

    # переводим в df дату (DD.MM.YYYY) в datetime
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)

    # фильтруем транзакции за период, со статусом OK, только траты и введенную категорию
    filtered_df = transactions[
        (transactions["Дата операции"] >= date_from)
        & (transactions["Дата операции"] <= date_to)
        & (transactions["Статус"] == "OK")
        & (transactions["Сумма платежа"] < 0)
    ].copy()
    reports_logger.info(f"DataFrame отфильтрован по столбцам: {required_columns}")

    # добавляем столбец с днями недели
    filtered_df["День недели"] = filtered_df["Дата операции"].apply(lambda x: x.strftime("%A"))

    # находим средние растраты по дням недели
    grouped_date = filtered_df.groupby("День недели")["Сумма платежа"].mean().abs().round(2)
    result_dict = grouped_date.to_dict()

    # Выставляем нормальную последовательность
    output_dict = {"Monday": 0, "Tuesday": 0, "Wednesday": 0, "Thursday": 0, "Friday": 0, "Saturday": 0, "Sunday": 0}
    for key, value in result_dict.items():
        output_dict[key] = value
    result = json.dumps(output_dict, ensure_ascii=False)
    reports_logger.info(
        "Функция получение средних трат на каждый день недели, c преобразованием в JSON - завершена успешно"
    )
    return result


@report_execution()
def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> str:
    """Функция принимает DataFrame с транзакциями и опциональную дату(YYYY-MM-DD).
    Возвращает средние траты в рабочий и в выходной день за последние 90 дней (от переданной даты) в JSON"""
    reports_logger.info(f"Функция получение средних трат на рабочие и выходные по {date} началась")
    date_to, date_from = calculate_date_range(date, 90)

    # Проверяем наличие необходимых столбцов
    required_columns = ["Дата операции", "Статус", "Сумма платежа"]
    missing_columns = [column for column in required_columns if column not in transactions.columns]
    if missing_columns:
        error_message = f"DataFrame должен содержать столбцы: {missing_columns}"
        reports_logger.error(error_message)
        raise ValueError(error_message)

    # переводим в df дату (DD.MM.YYYY) в datetime
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)

    # фильтруем транзакции за период, со статусом OK, только траты и введенную категорию
    filtered_df = transactions[
        (transactions["Дата операции"] >= date_from)
        & (transactions["Дата операции"] <= date_to)
        & (transactions["Статус"] == "OK")
        & (transactions["Сумма платежа"] < 0)
    ].copy()
    reports_logger.info(f"DataFrame отфильтрован по столбцам: {required_columns}")

    # добавляем столбец с днями недели
    filtered_df["Рабочий/Выходной"] = filtered_df["Дата операции"].apply(
        lambda x: (
            "working day"
            if x.strftime("%A") in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            else "weekend"
        )
    )

    # находим средние растраты по дням недели
    grouped_date = filtered_df.groupby("Рабочий/Выходной")["Сумма платежа"].mean().abs().round(2)
    result_dict = grouped_date.to_dict()

    # Выставляем нормальную последовательность
    output_dict = {"working day": 0, "weekend": 0}
    for key, value in result_dict.items():
        output_dict[key] = value
    result = json.dumps(output_dict, ensure_ascii=False)
    reports_logger.info(
        "Функция получение средних трат на рабочие и выходные, c преобразованием в JSON - завершена успешно"
    )
    return result
