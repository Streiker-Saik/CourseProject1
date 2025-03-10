import calendar
import datetime
import json
import logging
import os
from typing import Any, Dict, List

import pandas as pd

# создание абсолютного пути из относительного
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
log_file = os.path.join(project_root, "logs", "services.log")
# создаем директорию и файл если она не существует
os.makedirs(os.path.dirname(log_file), exist_ok=True)

services_logger = logging.getLogger("services")
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
file_formater = logging.Formatter("%(asctime)s - %(name)s: %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formater)
services_logger.addHandler(file_handler)
services_logger.setLevel(logging.DEBUG)


def get_top_three_category(data: List[Dict[str, Any]], year: int, month: int) -> str:
    """
    Функция принимает данные с транзакциями, год и месяц за который проводится анализ,
    выводит JSON строку 3 лучших категорий
    """
    services_logger.info("Функция получения топ 3 категории начата")

    df = pd.DataFrame(data)
    cashback = 0.1  # 10%

    date_from = datetime.datetime(year, month, 1)
    max_day = calendar.monthrange(year, month)[1]
    date_to = datetime.datetime(year, month, max_day)

    # Проверяем наличие необходимых столбцов
    required_columns = ["Дата операции", "Статус", "Сумма платежа", "Категория"]
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        error_message = f"DataFrame должен содержать столбцы: {missing_columns}"
        services_logger.error(error_message)
        raise ValueError(error_message)

    # переводим в df дату (DD.MM.YYYY HH:MM:SS) в datetime
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)

    # фильтруем транзакции за период, со статусом OK, только траты, исключая категории
    # ["Другое", "Наличные", "Переводы"]
    filtered_df_by_date = df[
        (df["Дата операции"] >= date_from)
        & (df["Дата операции"] <= date_to)
        & (df["Статус"] == "OK")
        & (df["Сумма платежа"] < 0)
        & (df["Категория"] != "Другое")
        & (df["Категория"] != "Наличные")
        & (df["Категория"] != "Переводы")
    ]

    # Группируем по категориям и суммируем, первые 3
    group_cate_category = (
        filtered_df_by_date.groupby("Категория")
        .agg({"Сумма платежа": "sum"})
        .abs()
        .sort_values(by="Сумма платежа", ascending=False)
        .head(3)
    )

    # Выводим в абсолютных значения, процент cashback, с двумя знаками после запятой
    group_cate_category["Сумма платежа"] = (group_cate_category["Сумма платежа"].abs() * cashback).round(2)

    if group_cate_category.empty:
        services_logger.warning("Отфильтрованные данные пустые")
        return json.dumps({}, indent=4, ensure_ascii=False)

    top_three_category = group_cate_category.to_dict(orient="index")
    data_output = {category: values["Сумма платежа"] for category, values in top_three_category.items()}
    result = json.dumps(data_output, indent=4, ensure_ascii=False)
    services_logger.info("Функция получения топ 3 категории выполнена")
    return result
