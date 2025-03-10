from pathlib import Path

import pandas as pd

from src.reports import spending_by_category
from src.services import get_top_three_category
from src.utils import get_transactions_from_excel
from src.views import views_home

BASEDIR = Path(__file__).resolve().parent


def main() -> None:
    "Функция собирает все остальные функции в одной"
    date = "2020-12-15 12:00:00"
    file_operations = str(BASEDIR / "data" / "operations.xlsx")
    file_user_settings = str(BASEDIR / "user_settings.json")
    print("Веб-страницы: Главная")
    views = views_home(date, file_operations, file_user_settings)
    print(views)

    print("Сервисы: Выгодные категории повышенного кешбэка")
    transactions = get_transactions_from_excel(file_operations)
    top_three_category = get_top_three_category(transactions, 2020, 12)
    print(top_three_category)

    print("Отчеты: Траты по категории(сколько на каждой категории можно заработать кешбэка 10 %)")
    transactions_df = pd.DataFrame(transactions)
    three_month_expense_category = spending_by_category(transactions_df, "Аптеки", date)
    print(three_month_expense_category)


if __name__ == "__main__":
    main()
