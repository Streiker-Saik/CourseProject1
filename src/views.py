import json
import logging
import os

import pandas as pd

from src.utils import (filter_operations_by_date, filter_operations_by_month_and_date, generate_card_report,
                       generator_top_five_transactions, get_currencies_rates_in_rub, get_stocks_in_usd,
                       get_transactions_from_excel, get_user_settings_from_json, greeting_from_time_to_time,
                       validate_and_format_date)

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
    Функция выдает JSON строку: Страница "Главная"
    :param date: дата формата YYYY-MM-DD HH:MM:SS
    :param file_operations: путь к списку операций
    :param file_user_settings: путь к пользовательским настройкам
    :return: JSON строка:
    '{
        "greeting": ...,
        "cards": ...,
        "top_transactions": ...,
        "currency_rates": ...,
        "stock_prices": ...
    }'
    """
    views_logger.info("Функция получение JSON файла главной страницы - начата")

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


def views_events(
    date: str,
    file_operations: str,
    file_user_settings: str,
    data_range: str = "M",
) -> str:
    """
    Функция выдает JSON строку: Страница "События"
    :param date: дата формата YYYY-MM-DD HH:MM:SS
    :param file_operations: путь к списку операций
    :param file_user_settings: путь к пользовательским настройкам
    :param data_range: диапазон, необязательный параметр:
        W - неделя, на которую приходится дата;
        M - месяц, на который приходится дата (по умолчанию);
        Y - год, на который приходится дата;
        ALL - все данные до указанной даты.
    :return: JSON строку:
    '{
        "expenses": {
            "total_amount": ...,
            "main": ...,
            "transfers_and_cash": ...,
        },
        "income": {
            "total_amount": ...,
            "main": ...
        },
        "currency_rates": ...,
        "stock_prices": ...,
    }'
    """
    views_logger.info("Функция получение JSON файла главной страницы - начата")

    views_logger.info("Использует функцию src.validate_and_format_date")
    date_obj = validate_and_format_date(date)

    views_logger.info("Использует функцию src.get_transactions_from_excel")
    operations = get_transactions_from_excel(file_operations)

    views_logger.info("Использует функцию src.get_user_settings_from_json")
    user_settings = get_user_settings_from_json(file_user_settings)

    df = pd.DataFrame(operations)
    views_logger.info("Использует функцию src.filter_operations_by_date")
    transactions_df = filter_operations_by_date(df, date_obj, data_range)

    # 1. Расходы:
    # - общая сумма расходов,
    # - раздел «Основные», в котором траты по категориям отсортированы по убыванию.Данные предоставляются
    #   по 7 категориям с наибольшими тратами, траты по остальным категориям суммируются и попадают
    #   в категорию «Остальное»
    # - раздел «Переводы и наличные», в котором сумма по категориям «Наличные» и «Переводы» отсортирована по убыванию

    # 2. Поступления:
    # - общая сумма поступлений,
    # - раздел «Основные» (в котором поступления по категориям отсортированы по убыванию)

    # 3. Курс валют
    currencies = user_settings[0].get("user_currencies", [])
    views_logger.info("Использует функцию src.get_currencies_rates_in_rub")
    currency_rates = get_currencies_rates_in_rub(currencies)

    # 4. Стоимость акций из S&P500
    stocks_list = user_settings[0].get("user_stocks", [])
    views_logger.info("Использует функцию src.get_stocks_in_usd")
    stock_prices = get_stocks_in_usd(stocks_list)
    data_output = {
        # "expenses": {
        #     "total_amount": total_amount_expenses,
        #     "main": main_expenses,
        #     "transfers_and_cash": transfers_and_cash,
        # },
        # "income": {"total_amount": total_amount_income, "main": main_income},
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    result = json.dumps(data_output, indent=4, ensure_ascii=False)
    views_logger.info("Функция получение JSON файла страницы событий - выполнена")
    return result
