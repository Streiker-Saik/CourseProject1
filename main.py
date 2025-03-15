from pathlib import Path

import pandas as pd

from src.reports import spending_by_category, spending_by_weekday, spending_by_workday
from src.services import (get_profitable_cashback, investment_bank, search_by_phone, search_transfers_to_individuals,
                          simple_search)
from src.utils import get_transactions_from_excel
from src.views import get_views_events, get_views_home

BASEDIR = Path(__file__).resolve().parent


def main() -> None:
    "Функция собирает все остальные функции в одной"
    date = "2020-12-15 12:00:00"
    file_operations = str(BASEDIR / "data" / "operations.xlsx")
    file_user_settings = str(BASEDIR / "user_settings.json")

    print("Веб-страницы:")

    print("- Главная")
    views_home = get_views_home(date, file_operations, file_user_settings)
    print(views_home)

    print("- События")
    views_events = get_views_events(date, file_operations, file_user_settings, "W")
    print(views_events)

    print("Сервисы:")

    print("- Выгодные категории повышенного кешбэка(сколько на каждой категории можно заработать кешбэка 10 %)")
    transactions = get_transactions_from_excel(file_operations)
    top_three_category = get_profitable_cashback(transactions, 2020, 12)
    print(top_three_category)

    print("- Инвесткопилка")
    invest_savings = investment_bank("2020-12", transactions, 50)
    print(invest_savings)

    print("- Простой поиск")
    transactions_by_string = simple_search(transactions, "бонусы")
    print(transactions_by_string)

    print("- Поиск по телефонным номерам")
    transactions_by_phone = search_by_phone(transactions)
    print(transactions_by_phone)

    print("- Поиск переводов физическим лицам")
    transactions_by_individuals = search_transfers_to_individuals(transactions)
    print(transactions_by_individuals)

    print("Отчеты:")

    print("- Траты по категории.")
    transactions_df = pd.DataFrame(transactions)
    three_month_expense_category = spending_by_category(transactions_df, "Аптеки", date)
    print(three_month_expense_category)

    print("- Среднее количество трат в день недели.")
    spending_per_day_week = spending_by_weekday(transactions_df, date)
    print(spending_per_day_week)

    print("- Среднее количество траты в рабочий и выходной")
    spending_per_day_work_and_weekend = spending_by_workday(transactions_df, date)
    print(spending_per_day_work_and_weekend)


if __name__ == '__main__':
    main()
