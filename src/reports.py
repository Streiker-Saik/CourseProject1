import os
import logging
import json
import datetime
from typing import Optional
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


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция принимает DataFrame с транзакциями, название категории и опциональную дату(YYYY-MM-DD).
    Возвращает траты по заданной категории за последние 90 дней (от переданной даты)"""
    reports_logger.info(f"Функция фильтрации DataFrame по {category} началась")
    if not date:
        reports_logger.info("Дата не указана, принимается текущая дата(datetime)")
        date_obj = datetime.datetime.now()
    else:
        date_obj = validate_and_format_date(date)
        reports_logger.info("Дата преобразована datetime")
    date_to = date_obj
    date_from = date_obj - datetime.timedelta(days=90)

    columns = ["Дата операции", "Статус", "Сумма платежа", "Категория"]
    if not all(column in transactions.columns for column in columns):
        error_message = f"DataFrame должен содержать столбцы: {columns}"
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
    ]
    # group = filtered_df.groupby("Категория").agg({"Сумма платежа": "sum"})
    # group_dict = group.to_dict(orient="index")
    # print(group_dict)
    reports_logger.info(f"Функция фильтрации DataFrame по {category} завершена успешно")
    return filtered_df


# if __name__ == "__main__":
#     file_excel = "../data/operations.xlsx"
#     transactions = pd.read_excel(file_excel)
#     # category = transactions.Категория.unique()
#     # print(category)
#     print(spending_by_category(transactions, "Аптеки", ))
