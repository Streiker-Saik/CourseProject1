import json
import logging
import os
from typing import Any, Dict, List, cast

import pandas as pd
import requests
from dotenv import load_dotenv
import datetime

# создание абсолютного пути из относительного
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
log_file = os.path.join(project_root, "logs", "utils.log")
# создаем директорию и файл если она не существует
os.makedirs(os.path.dirname(log_file), exist_ok=True)

utils_logger = logging.getLogger("utils")
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
file_formater = logging.Formatter("%(asctime)s - %(name)s: %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formater)
utils_logger.addHandler(file_handler)
utils_logger.setLevel(logging.DEBUG)


def get_transactions_from_excel(file_path: str) -> List[Dict[str, Any]]:
    """Функция принимает файл (*.xlsx) и выводит список словарей"""
    try:
        utils_logger.info(f'Выполняем преобразование EXCEL-файла "{file_path}" в объект Python')
        data = pd.read_excel(file_path)
        records = data.to_dict(orient="records")

        # Заменяем пустые значения NaN на None
        for record in records:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = 0
        result = cast(List[Dict[str, Any]], records)
        utils_logger.info(f'Преобразование JSON-файла "{file_path}" в объект Python выполнено')
        return result

    except FileNotFoundError:
        error_message = f"Файл '{file_path}' - не найден"
        utils_logger.error(error_message)
        raise FileNotFoundError(error_message)

    except Exception as exc_info:
        error_message = f"Что-то пошло не так при чтении {file_path}. Ошибка {exc_info}"
        utils_logger.error(error_message)
        raise Exception(error_message)


def get_user_settings_from_json(file_path: str) -> List[Dict[str, Any]]:
    """Функцию, принимает на вход путь до JSON-файла и возвращает список словарей с данными убирая пустые словари"""
    if not os.path.exists(file_path):
        utils_logger.error(f"Файл '{file_path}' - не найден")
        return []

    try:
        utils_logger.info(f'Выполняем преобразование JSON-файла "{file_path}" в объект Python')
        with open(file_path, "r", encoding="utf-8") as json_file:
            transactions: List[Dict[str, Any]] = json.load(json_file)

            if type(transactions) is not list:
                utils_logger.error("Файл содержит не список")
                return []

            # убираем пустые словари
            result = list(filter(bool, transactions))
            utils_logger.info(f'Преобразование JSON-файла "{file_path}" в объект Python выполнено')
            return result

    except json.JSONDecodeError as exc_info:
        utils_logger.error(f"Невозможно преобразовать json дынные: {exc_info}")
        return []

    except Exception as exc_info:
        error_message = f"Что-то пошло не так при чтении {file_path}. Ошибка {exc_info}"
        utils_logger.error(error_message)
        raise Exception(error_message)


def get_apilayer_convert_rates(*, base: str, symbols: str) -> float:
    """Функция курса валюты, Exchange Rates Data API GET/latest: https://apilayer.com/marketplace/exchangerates_data-api"""
    load_dotenv("../.env")
    api_key = os.getenv("APILAYER_EDAPI_KEY")

    payload: Dict[Any, Any] = {}
    headers = {"apikey": api_key}

    url = f"https://api.apilayer.com/exchangerates_data/latest?symbols={symbols}&base={base}"

    try:
        utils_logger.info(f"Выполняем запрос у Exchange Rates Data API GET/latest")
        response = requests.request("GET", url, headers=headers, data=payload)
        # status_code = response.status_code
        # result = response.text

        if response.status_code != 200:
            error_message = f"Ошибка API: {response.status_code} - {response.text}"
            utils_logger.error(error_message)
            raise Exception(error_message)

        output_data = response.json()
        # {
        #     "base": "USD",
        #     "date": "2021-03-17",
        #     "rates": {
        #         "EUR": 0.813399,
        #         "GBP": 0.72007,
        #         "JPY": 107.346001
        #     },
        #     "success": true,
        #     "timestamp": 1519296206
        # }
        result = round(float(output_data["rates"][symbols]), 2)
        utils_logger.info(f"Получение данный у Exchange Rates Data API GET/latest - прошло успешно")
        return result

    except requests.exceptions.ConnectionError:
        error_message = "Connection Error. Please check your network connection"
        utils_logger.error(error_message)
        raise Exception(error_message)

    except Exception as exc_info:
        error_message = f"Что-то пошло не так. {str(exc_info)}"
        utils_logger.error(error_message)
        raise Exception(error_message)


def get_currencies_rates_in_rub(currencies: List[str]) -> List[Dict[str, Any]]:
    """Функция принимает список валют и возвращает курсы валют в рублях, с запросом в API"""
    try:
        utils_logger.info(f"Началась функция перевода валют '{currencies}'")
        result = []
        for currency in currencies:
            result_dict = {"currency": currency, "rate": get_apilayer_convert_rates(base=currency, symbols="RUB")}
            result.append(result_dict)
        utils_logger.info(f"Функция с валютами '{currencies}' прошла успешно")
        return result

    except Exception as exc_info:
        error_message = f"Что-то пошло не так. {str(exc_info)}"
        utils_logger.error(error_message)
        raise Exception(error_message)


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


# if __name__ == "__main__":
#     print(get_transactions_from_excel("../data/operations.xlsx")[0])
#     transactions = get_transactions_from_excel("../data/operations.xlsx")
#     for transaction in transactions:
#         print(transaction["Номер карты"])
#     print(get_transactions_from_json("../user_settings.json"))
