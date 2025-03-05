import datetime
import json
import logging
import os
from typing import Any, Dict, List


from src.utils import get_transactions_from_excel, get_user_settings_from_json
from src.operations_filters import filter_operations_by_month_and_date

# создание абсолютного пути из относительного
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
log_file = os.path.join(project_root, "logs", "views.log")
# создаем директорию и файл если она не существует
os.makedirs(os.path.dirname(log_file), exist_ok=True)

utils_logger = logging.getLogger("views")
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
file_formater = logging.Formatter("%(asctime)s - %(name)s: %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formater)
utils_logger.addHandler(file_handler)
utils_logger.setLevel(logging.DEBUG)


def views_home(date_obj: datetime.datetime, file_operations: str, file_user_settings: str) -> str:
    """Функция принимает дату (YYYY-MM-DD HH:MM:SS), пути к списку операций и пользовательским настройкам и выводит JSON файла главной страницы сайта"""
    # 1. Приветствие
    greeting = greeting_from_time_to_time(date_obj)

    # 2. По каждой карте:
    # последние 4 цифры карты;
    # общая сумма расходов;
    # кешбэк (1 рубль на каждые 100 рублей)
    operations = get_transactions_from_excel(file_operations)
    operations_new = filter_operations_by_month_and_date(operations, date_obj)
    cards = {}
    # 3. Топ - 5 транзакций по сумме платежа
    top_transactions = []

    # # 4. Курс валют
    # user_settings = get_user_settings_from_json(file_user_settings)
    # currencies = user_settings[0].get("user_currencies", [])
    # currency_rates = get_currencies_rates_in_rub(currencies)

    # 5. Стоимость акций из S&P500
    stock_prices = []
    data_output = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        # "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
    return json.dumps(data_output, indent=4)


def greeting_from_time_to_time(date_obj: datetime.datetime) -> str:
    """Функция выводит сообщение приветствия согласно времени суток"""
    try:
        # utils_logger.info(f"Функция началась")
        # date_obj = datetime.datetime.now()
        # # hours = datetime.datetime.now().hour
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

    except Exception as exc_info:
        error_message = f"Что-то пошло не так. {str(exc_info)}"
        utils_logger.error(error_message)
        raise Exception(error_message)


def get_last_digit_and_total_spent_and_cashback(operations):
    operations_by_card = {}
    for operation in operations:
        number_card = str(operation.get("Номер карты", ""))

        if number_card not in operations_by_card:
            operations_by_card["card"] = {"last_digits": number_card[-4:]}
            print(operations_by_card)


            # last_digits = number_card[-4:]
            # sum_operation = operation.get("Сумма операции")
            # cashback = operation.get("Кэшбэк")
            # if number_card in operations_by_card:
            #
            #     operations_by_card["total_spent"] += sum_operation
            #     operations_by_card["cashback"] += cashback
            # else:
            #
            #     operations_by_card["last_digits"] = last_digits
            #     operations_by_card["total_spent"] = sum_operation
            #     operations_by_card["cashback"] =cashback


    return operations_by_card



if __name__ == "__main__":
    date_obj = datetime.datetime(2020, 12, 20, 20, 17, 35)
    file_operations = "../data/operations.xlsx"
    operations = get_transactions_from_excel(file_operations)

    operations = filter_operations_by_month_and_date(operations, date_obj)
    print(get_last_digit_and_total_spent_and_cashback(operations))
    # print(greeting_from_time_to_time(datetime.datetime.now()))
    # print(views_home("../data/operations.xlsx", "../user_settings.json"))
    # "cards": [
    #     {
    #         "last_digits": "5814",
    #         "total_spent": 1262.00,
    #         "cashback": 12.62
    #     },
    #     {
    #         "last_digits": "7512",
    #         "total_spent": 7.94,
    #         "cashback": 0.08
    #     }
    # ],