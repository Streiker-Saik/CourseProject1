import json
import logging
import os

import pandas as pd

from src.utils import (filter_operations_by_month_and_date, generate_card_report, generator_top_five_transactions,
                       get_currencies_rates_in_rub, get_stocks_in_usd, get_transactions_from_excel,
                       get_user_settings_from_json, greeting_from_time_to_time, validate_and_format_date)

# создание абсолютного пути из относительного
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
log_file = os.path.join(project_root, "logs", "views.log")
# создаем директорию и файл если она не существует
os.makedirs(os.path.dirname(log_file), exist_ok=True)

views_logger = logging.getLogger("views")
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
file_formater = logging.Formatter("%(asctime)s - %(name)s: %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formater)
views_logger.addHandler(file_handler)
views_logger.setLevel(logging.DEBUG)


def views_home(date: str, file_operations: str, file_user_settings: str) -> str:
    """
    Функция принимает дату (YYYY-MM-DD HH:MM:SS), пути к списку операций и
    пользовательским настройкам и выводит JSON файла главной страницы сайта
    """
    views_logger.info("Функция получение JSON файла главной страницы - начата")
    # if date is None or file_operations is None or file_user_settings is None:
    #     error_message = "Вводные дынные отсутствуют"
    #     views_logger.error(error_message)
    #     raise TypeError(error_message)
    #
    # if not all(isinstance(arg, str) for arg in (date, file_operations, file_user_settings)):
    #     error_message = "Введено не строковое значение"
    #     views_logger.error(error_message)
    #     raise TypeError(error_message)

    views_logger.info("Использует функцию src.validate_and_format_date")
    date_obj = validate_and_format_date(date)
    views_logger.info("Использует функцию src.get_transactions_from_excel")
    operations = get_transactions_from_excel(file_operations)
    views_logger.info("Использует функцию src.get_user_settings_from_json")
    user_settings = get_user_settings_from_json(file_user_settings)
    df = pd.DataFrame(operations)
    views_logger.info("Использует функцию src.filter_operations_by_month_and_date")
    filter_df = filter_operations_by_month_and_date(df, date_obj)

    # 1. Приветствие
    views_logger.info("Использует функцию src.greeting_from_time_to_time")
    greeting = greeting_from_time_to_time(date_obj)

    # 2. По каждой карте: последние 4 цифры карты; общая сумма расходов; кешбэк (1 рубль на каждые 100 рублей)
    views_logger.info("Использует функцию src.generate_card_report")
    cards = generate_card_report(filter_df)

    # 3. Топ - 5 транзакций по сумме платежа
    views_logger.info("Использует функцию src.generator_top_five_transactions")
    top_transactions = generator_top_five_transactions(filter_df)

    # 4. Курс валют
    currencies = user_settings[0].get("user_currencies", [])
    views_logger.info("Использует функцию src.get_currencies_rates_in_rub")
    currency_rates = get_currencies_rates_in_rub(currencies)

    # 5. Стоимость акций из S&P500
    stocks_list = user_settings[0].get("user_stocks", [])
    views_logger.info("Использует функцию src.get_stocks_in_usd")
    stock_prices = get_stocks_in_usd(stocks_list)

    data_output = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    result = json.dumps(data_output, indent=4, ensure_ascii=False)
    views_logger.info("Функция получение JSON файла главной страницы - выполнена")
    return result


# if __name__ == "__main__":
#     date = "2021-12-21 12:00:00"
#     file_operations = "../data/operations.xlsx"
#     file_user_settings = "../user_settings.json"
#     result = views_home(date, file_operations, file_user_settings)
#     print(result)
