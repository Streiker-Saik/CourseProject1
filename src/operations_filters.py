import datetime
import json
import logging
import os
from typing import Any, Dict, List


def filter_operations_by_month_and_date(
    operations: List[Dict[str, Any]], date_obj: datetime.datetime
) -> List[Dict[str, Any]]:
    """Функция принимает операции и дату запроса, выводит список транзакций с 1 числа месяца по введенное число"""
    # определяем месяц и год запроса
    year = date_obj.year
    month = date_obj.month
    # дата начала и дата конца фильтрации
    date_to = date_obj
    date_from = datetime.datetime(year, month, 1)
    # "Дата операции": "31.12.2021 16:44:00"
    return [
        operation
        for operation in operations
        if date_from <= datetime.datetime.strptime(operation["Дата операции"], "%d.%m.%Y %H:%M:%S") <= date_to
    ]



