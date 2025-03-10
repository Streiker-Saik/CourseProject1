import json
from unittest.mock import MagicMock, patch

from src.views import views_home


@patch("src.views.get_stocks_in_usd")
@patch("src.views.get_currencies_rates_in_rub")
@patch("src.views.generator_top_five_transactions")
@patch("src.views.generate_card_report")
@patch("src.views.greeting_from_time_to_time")
@patch("src.views.get_user_settings_from_json")
@patch("src.views.get_transactions_from_excel")
def test_views_home(
    mock_get_transactions_from_excel: MagicMock,
    mock_get_user_settings_from_json: MagicMock,
    mock_greeting_from_time_to_time: MagicMock,
    mock_generate_card_report: MagicMock,
    mock_generator_top_five_transactions: MagicMock,
    mock_get_currencies_rates_in_rub: MagicMock,
    mock_get_stocks_in_usd: MagicMock,
) -> None:
    """Тестирование работы функции на вывод требуемого JSON"""
    date = "2018-01-04 13:00:00"
    file_operations = "test_path.xlsx"
    file_user_settings = "test_path.json"
    mock_get_transactions_from_excel.return_value = [
        {
            "Дата операции": "01.01.2018 20:27:51",
            "Дата платежа": "01.01.2018",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -316.0,
            "Валюта операции": "RUB",
            "Сумма платежа": -316.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": None,
            "Категория": "Красота",
            "MCC": 5977.0,
            "Описание": "OOO Balid",
            "Бонусы (включая кэшбэк)": 6,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 316.0,
        }
    ]
    mock_get_user_settings_from_json.return_value = [
        {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]}
    ]
    mock_greeting_from_time_to_time.return_value = "Добрый день"
    mock_generate_card_report.return_value = [{"last_digits": "7197", "total_spent": 316.0, "cashback": 3.16}]
    mock_generator_top_five_transactions.return_value = [
        {"date": "01.01.2018", "amount": -316.0, "category": "Красота", "description": "OOO Balid"}
    ]
    mock_get_currencies_rates_in_rub.return_value = [
        {"currency": "USD", "rate": 89.7},
        {"currency": "EUR", "rate": 96.93},
    ]
    mock_get_stocks_in_usd.return_value = [
        {"stock": "AAPL", "price": 235.74},
        {"stock": "AMZN", "price": 208.36},
        {"stock": "GOOGL", "price": 173.02},
        {"stock": "MSFT", "price": 401.02},
        {"stock": "TSLA", "price": 279.1},
    ]
    # .return_value =

    expected_output = {
        "greeting": "Добрый день",
        "cards": [{"last_digits": "7197", "total_spent": 316.0, "cashback": 3.16}],
        "top_transactions": [
            {"date": "01.01.2018", "amount": -316.0, "category": "Красота", "description": "OOO Balid"}
        ],
        "currency_rates": [{"currency": "USD", "rate": 89.7}, {"currency": "EUR", "rate": 96.93}],
        "stock_prices": [
            {"stock": "AAPL", "price": 235.74},
            {"stock": "AMZN", "price": 208.36},
            {"stock": "GOOGL", "price": 173.02},
            {"stock": "MSFT", "price": 401.02},
            {"stock": "TSLA", "price": 279.1},
        ],
    }
    expected = json.dumps(expected_output, indent=4, ensure_ascii=False)
    assert views_home(date, file_operations, file_user_settings) == expected
