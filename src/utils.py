import datetime
import json
import logging
import os
from typing import Any, Dict, List, cast

import pandas as pd
import requests
from dotenv import load_dotenv

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


def greeting_from_time_to_time(date_obj: datetime.datetime) -> str:
    """Функция выводит сообщение приветствия согласно времени суток"""
    # try:
    hours = date_obj.hour
    utils_logger.info(f"Выполняется функция приветствия в {hours} часов")
    if 0 <= hours < 6:
        message = "Доброй ночи"
    elif 6 <= hours < 12:
        message = "Доброе утро"
    elif 12 <= hours < 18:
        message = "Добрый день"
    else:
        message = "Добрый вечер"
    utils_logger.info(f"Функция приветствия в {hours} часов выполнена")
    return message

    # except Exception as exc_info:
    #     error_message = f"Что-то пошло не так. {str(exc_info)}"
    #     utils_logger.error(error_message)
    #     raise Exception(error_message)


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
                    record[key] = None
        result = cast(List[Dict[str, Any]], records)
        utils_logger.info(f'Преобразование JSON-файла "{file_path}" в объект Python выполнено')
        return result

    except FileNotFoundError:
        error_message = f"Файл '{file_path}' - не найден"
        utils_logger.error(error_message)
        raise FileNotFoundError(error_message)

    # except Exception as exc_info:
    #     error_message = f"Что-то пошло не так при чтении {file_path}. Ошибка {exc_info}"
    #     utils_logger.error(error_message)
    #     raise Exception(error_message)


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

    # except Exception as exc_info:
    #     error_message = f"Что-то пошло не так при чтении {file_path}. Ошибка {exc_info}"
    #     utils_logger.error(error_message)
    #     raise Exception(error_message)


def get_apilayer_convert_rates(
        date_obj: datetime.datetime, *, code_to: str, code_from: str, amount: str = "1"
) -> float:
    """Функция курса валюты, Exchange Rates Data API GET/convert:
    https://apilayer.com/marketplace/exchangerates_data-api"""

    load_dotenv("../.env")
    api_key = os.getenv("APILAYER_EDAPI_KEY")

    payload: Dict[Any, Any] = {}
    headers = {"apikey": api_key}
    # YYYY-MM-DD
    date_str = date_obj.strftime("%Y-%m-%d")
    url = (
        f"https://api.apilayer.com/exchangerates_data/convert?to={code_to}&from={code_from}&amount={amount}"
        f"&date={date_str}"
    )

    try:
        utils_logger.info("Выполняем запрос у Exchange Rates Data API GET/convert")
        response = requests.request("GET", url, headers=headers, data=payload)
        # status_code = response.status_code
        # result = response.text

        if response.status_code != 200:
            error_message = f"Ошибка API: {response.status_code} - {response.text}"
            utils_logger.error(error_message)
            raise Exception(error_message)

        output_data = response.json()
        result = round(float(output_data["result"]), 2)
        utils_logger.info("Получение данный у Exchange Rates Data API GET/convert - прошло успешно")
        return result

    except requests.exceptions.ConnectionError:
        error_message = "Connection Error. Please check your network connection"
        utils_logger.error(error_message)
        raise Exception(error_message)

    # except Exception as exc_info:
    #     error_message = f"Что-то пошло не так. {str(exc_info)}"
    #     utils_logger.error(error_message)
    #     raise Exception(error_message)


def get_currencies_rates_in_rub(
        currencies: List[str], date_obj: datetime.datetime = datetime.datetime.now()
) -> List[Dict[str, Any]]:
    """Функция принимает список валют и возвращает курсы валют в рублях, с запросом в API"""
    if not currencies:
        utils_logger.info("Список пуст")
        return []

    # try:
    utils_logger.info(f"Началась функция перевода валют '{currencies}'")
    result_dict = []
    for currency in currencies:
        result = {
            "currency": currency,
            "rate": get_apilayer_convert_rates(date_obj, code_to="RUB", code_from=currency),
        }
        result_dict.append(result)
    utils_logger.info(f"Функция с валютами '{currencies}' прошла успешно")
    return result_dict

    # except Exception as exc_info:
    #     error_message = f"Что-то пошло не так. {str(exc_info)}"
    #     utils_logger.error(error_message)
    #     raise Exception(error_message)


def filter_operations_by_month_and_date(df: pd.DataFrame, date_obj: datetime.datetime) -> pd.DataFrame:
    """
    Функция принимает DataFrame и дату: фильтрует операции по дате с 1 числа по дату, так же операции по статусу Ok.
    Возвращает отфильтрованный DataFrame
    """
    # try:
    utils_logger.info("Началась функция фильтрации")
    year = date_obj.year
    month = date_obj.month
    date_to = date_obj
    date_from = datetime.datetime(year, month, 1)
    # переводим дату (DD.MM.YYYY HH:MM:SS) в datetime
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    filtered_df = df[
        (df["Дата операции"] >= date_from) & (df["Дата операции"] <= date_to) & (df["Статус"] == "OK")
        ]
    utils_logger.info("Фильтрация прошла успешно")
    return filtered_df

    # except Exception as exc_info:
    #     error_message = f"Что-то пошло не так. {str(exc_info)}"
    #     utils_logger.error(error_message)
    #     raise Exception(error_message)


# def filter_operations_by_month_and_date(
#     operations: List[Dict[str, Any]], date_obj: datetime.datetime
# ) -> List[Dict[str, Any]]:
#     """Функция принимает операции и дату запроса, выводит список транзакций с 1 числа месяца по введенное число"""
#     # определяем месяц и год запроса
#     year = date_obj.year
#     month = date_obj.month
#     # дата начала и дата конца фильтрации
#     date_to = date_obj
#     date_from = datetime.datetime(year, month, 1)
#     # "Дата операции": "31.12.2021 16:44:00"
#     return [
#         operation
#         for operation in operations
#         if date_from <= datetime.datetime.strptime(operation["Дата операции"], "%d.%m.%Y %H:%M:%S") <= date_to
#     ]


def generate_card_report(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Функция принимает DataFrame, выводит список {"last_digits": X, "total_spent": X, "cashback": X}"""
    if df.empty:
        utils_logger.info("DataFrame пуст")
        return []

    try:
        filtered_df = df[df["Сумма платежа"] < 0]  # фильтруем только расходы
        grouped_number_card = filtered_df.groupby("Номер карты").agg({"Сумма платежа": "sum", "Кэшбэк": "sum"})
        cards_dict = grouped_number_card.to_dict(orient="index")
        # [{"*4556": {"Сумма операции": -1776.0, "Кэшбэк": 69.0}, ...]

        # переводим данные в формат:
        # [{"last_digits": "4556", "total_spent": 1776.0, "cashback": 17.76}, ...]
        result = []
        for key, value in cards_dict.items():
            last_digits = str(key)[-4:]
            total_spent = abs(round(value["Сумма платежа"], 2))
            cashback = round(total_spent / 100, 2)  # (1 рубль на каждые 100 рублей)
            card = {
                "last_digits": last_digits,
                "total_spent": total_spent,
                "cashback": cashback,
            }
            result.append(card)
        return result

    except KeyError as exc_info:
        raise ValueError(f"Отсутствует необходимый столбец: {str(exc_info)}") from exc_info

    # except Exception as exc_info:
    #     error_message = f"Что-то пошло не так. {str(exc_info)}"
    #     utils_logger.error(error_message)
    #     raise Exception(error_message)


def get_stocks_price(*, stocks: str) -> float:
    """Функция курса акций за предыдущий день, Alpha Vantage:
    https://www.alphavantage.co/"""
    utils_logger.info("Выполняем запрос у Exchange Rates Data API GET/convert")
    load_dotenv("../.env")
    api_key = os.getenv("ALPHAVANTAGE_KEY")

    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stocks}&apikey={api_key}"
    try:
        utils_logger.info("Выполняем запрос у Alpha Vantage/TIME_SERIES_DAILY")
        r = requests.get(url)
        data = r.json()

        if r.status_code != 200:
            error_message = f"Ошибка API: {r.status_code} - {r.text}"
            utils_logger.error(error_message)
            raise Exception(error_message)

        date_str = data["Meta Data"]["3. Last Refreshed"]
        result = round(float(data["Time Series (Daily)"][date_str]["4. close"]), 2)
        utils_logger.info("Получение данный у Alpha Vantage/TIME_SERIES_DAILY - прошло успешно")
        return result

    except KeyError as exc_info:
        # We have detected your API key as ************* and our standard API rate limit is 25 requests per day.
        # Please subscribe to any of the premium plans at https://www.alphavantage.co/premium/
        # to instantly remove all daily rate limits.
        error_message = f"Ошибка при обработке данных: {str(exc_info)}"
        utils_logger.error(error_message)
        if "Information" in data:
            error_message = data["Information"]
            utils_logger.error(error_message)
        raise KeyError(error_message)

    except requests.exceptions.ConnectionError:
        error_message = "Connection Error. Please check your network connection"
        utils_logger.error(error_message)
        raise Exception(error_message)

    # except Exception as exc_info:
    #     error_message = f"Что-то пошло не так. {str(exc_info)}"
    #     utils_logger.error(error_message)
    #     raise Exception(error_message)


def get_stocks_in_usd(stocks_list: List[str]) -> List[Dict[str, Any]]:
    """Функция принимает список акций и возвращает курсы акции в долларах(последнее закрытие дня), с запросом в API"""
    if not stocks_list:
        utils_logger.info("Список пуст")
        return []

    # try:
    utils_logger.info(f"Началась функция курса акций началась. Акции '{stocks_list}'")
    result = []
    for stocks in stocks_list:
        price = get_stocks_price(stocks=stocks)
        result_dict = {"stock": stocks, "price": price}
        result.append(result_dict)
    utils_logger.info(f"Функция с акциями '{stocks_list}' - прошла успешно")
    return result

    # except Exception as exc_info:
    #     error_message = f"Что-то пошло не так. {str(exc_info)}"
    #     utils_logger.error(error_message)
    #     raise Exception(error_message)


def generator_top_five_transactions(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Топ-5 транзакций по сумме платежа."""
    if df.empty:
        utils_logger.info("DataFrame пуст")
        return []

    try:
        columns = df.loc[:, ["Дата платежа", "Сумма платежа", "Категория", "Описание"]]
        top_five_transactions = columns.sort_values(by="Сумма платежа", ascending=False).head(5)
        result = top_five_transactions.to_dict(orient="records")
        # {"Дата платежа": '16.01.2020',
        # "Сумма платежа": 3100.0,
        # "Категория": 'Пополнения',
        # "Описание": 'Внесение наличных через банкомат Тинькофф'}

        # переводим данные в формат:
        # [{"last_digits": "4556", "total_spent": 1776.0, "cashback": 17.76}, ...]
        formatted_result = []
        for category in result:
            top_transactions = {
                "date": category["Дата платежа"],
                "amount": category["Сумма платежа"],
                "category": category["Категория"],
                "description": category["Описание"],
            }
            formatted_result.append(top_transactions)
        return formatted_result

    except KeyError as exc_info:
        raise ValueError(f"Отсутствует необходимый столбец: {str(exc_info)}") from exc_info

    # except Exception as exc_info:
    #     error_message = f"Что-то пошло не так. {str(exc_info)}"
    #     utils_logger.error(error_message)
    #     raise Exception(error_message)

# if __name__ == "__main__":
#     date_obj = datetime.datetime(2020, 1, 5, 6, 0, 0)
#     print(greeting_from_time_to_time(date_obj))
#
#     file_path_excel = "../data/operations.xlsx"
#     print(get_transactions_from_excel(file_path_excel)[0])
#
#     file_path_json = "../user_settings.json"
#     user_settings = get_user_settings_from_json(file_path_json)
#     print(user_settings)
#
#     df = pd.DataFrame(get_transactions_from_excel(file_path_excel))
#     filter_df = filter_operations_by_month_and_date(df, date_obj)
#     print(filter_df)
#
#     cards = generate_card_report(filter_df)
#     print(cards)
#
#     top_transactions = generator_top_five_transactions(filter_df)
#     print(top_transactions)
#
#     print(get_apilayer_convert_rates(code_to = "RUB", code_from = "USD"))
#     print(get_currencies_rates_in_rub(["USD", "EUR", "CNY"]))
#     stocks_list = user_settings[0].get("user_stocks", [])
#     print(get_stocks_in_usd(stocks_list))
#
#     print(get_stocks_price(stocks="AAPL"))
#     print(get_stocks_in_usd(["AAPL", "AMZN", "GOOGL"]))
#     currencies = user_settings[0].get("user_currencies", [])
#     print(get_currencies_rates_in_rub(currencies))
