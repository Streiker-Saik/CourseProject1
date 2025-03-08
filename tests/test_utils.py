import datetime
import json
import os
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import numpy
import pandas as pd
import pytest
import requests

from src.utils import (filter_operations_by_month_and_date, generate_card_report, generator_top_five_transactions,
                       get_apilayer_convert_rates, get_currencies_rates_in_rub, get_stocks_in_usd, get_stocks_price,
                       get_transactions_from_excel, get_user_settings_from_json, greeting_from_time_to_time,
                       validate_and_format_date)


@pytest.mark.parametrize(
    "date, expected",
    [
        ("2025-01-01", (datetime.datetime(2025, 1, 1))),
        ("2025-01-01 06:00:00", (datetime.datetime(2025, 1, 1, 6, 0, 0))),
    ],
)
def test_validate_and_format_date(date: str, expected: datetime.datetime) -> None:
    """Тестирование преобразование строки в datetime"""
    result = validate_and_format_date(date)
    assert result == expected


def test_validate_and_format_date_none_format() -> None:
    """Тестирование при не нахождении формата"""
    date = "01-01-2020"

    with pytest.raises(ValueError) as exc_info:
        validate_and_format_date(date)

    assert "Данного формата не поддерживается" == str(exc_info.value)


@pytest.mark.parametrize(
    "mock_time, expected",
    [
        (datetime.datetime(2025, 1, 1, 0, 0), "Доброй ночи"),
        (datetime.datetime(2025, 1, 1, 6, 0), "Доброе утро"),
        (datetime.datetime(2025, 1, 1, 12, 0), "Добрый день"),
        (datetime.datetime(2025, 1, 1, 18, 0), "Добрый вечер"),
    ],
)
@patch("datetime.datetime")
def test_greeting_from_time_to_time(mock_datetime: MagicMock, mock_time: datetime.datetime, expected: str) -> None:
    """Тестирование, проверяем на разное время, вывод правильного приветствия"""
    mock_datetime.now.return_value = mock_time
    result = greeting_from_time_to_time(mock_datetime.now())
    assert result == expected


def test_get_transactions_from_excel_non_existent_file() -> None:
    """Тестирование, когда файл не найдет"""
    file_path = "test.xlsx"

    with pytest.raises(FileNotFoundError) as exc_info:
        get_transactions_from_excel(file_path)

    assert f"Файл '{file_path}' - не найден" == str(exc_info.value)


@patch("pandas.read_excel")
def test_read_excel_transactions(read_excel: MagicMock) -> None:
    """Тестирование, функция возвращает из файла (*.xlsx) список словарей"""
    read_excel.return_value = pd.DataFrame(
        {
            "Дата операции": ["31.12.2021 16:44:00"],
            "Дата платежа": ["31.12.2021"],
            "Номер карты": ["*7197"],
            "Статус": ["OK"],
            "Сумма операции": [-160.89],
            "Валюта операции": ["RUB"],
            "Сумма платежа": [-160.89],
            "Валюта платежа": ["RUB"],
            "Кэшбэк": [numpy.nan],
            "Категория": ["Супермаркеты"],
            "MCC": [5411.0],
            "Описание": ["Колхоз"],
            "Бонусы (включая кэшбэк)": [3],
            "Округление на инвесткопилку": [0],
            "Сумма операции с округлением": [160.89],
        }
    )
    expected = [
        {
            "Дата операции": "31.12.2021 16:44:00",
            "Дата платежа": "31.12.2021",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -160.89,
            "Валюта операции": "RUB",
            "Сумма платежа": -160.89,
            "Валюта платежа": "RUB",
            "Кэшбэк": None,
            "Категория": "Супермаркеты",
            "MCC": 5411.0,
            "Описание": "Колхоз",
            "Бонусы (включая кэшбэк)": 3,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 160.89,
        },
    ]
    assert get_transactions_from_excel("test.xlsx") == expected
    file_path = "test.xlsx"
    read_excel.assert_called_once_with(file_path)


def test_get_user_settings_from_json_non_existent_file() -> None:
    """Тест, если файл не найден"""
    assert get_user_settings_from_json("non.json") == []


@pytest.fixture
def user_settings() -> List[Dict[str, Any]]:
    return [
        {"operationAmount": {"amount": "31957.58", "currency": {"name": "руб.", "code": "RUB"}}},
        {"operationAmount": {"amount": "8221.37", "currency": {"name": "USD", "code": "USD"}}},
        {"operationAmount": {"amount": "9824.07", "currency": {"name": "USD", "code": "USD"}}},
    ]


def test_get_user_settings_from_json(user_settings: List[Dict[str, Any]]) -> None:
    """Тест работы функции"""
    file_path = "test.json"
    try:
        with open(file_path, "w", encoding="utf-8") as file_json:
            json.dump(user_settings, file_json, indent=4, ensure_ascii=False)

        assert get_user_settings_from_json(file_path) == user_settings
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


def test_get_user_settings_from_json_empty_list() -> None:
    """Тест, если файл с пустым списком"""
    file_path = "test.json"
    try:
        with open(file_path, "w", encoding="utf-8") as file_json:
            user_settings: List = []
            json.dump(user_settings, file_json, indent=4, ensure_ascii=False)

        assert get_user_settings_from_json(file_path) == user_settings
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


def test_get_user_settings_from_invalid_json() -> None:
    """Тест, если файл с некорректными данными"""
    file_path = "test.json"
    try:
        with open(file_path, "w", encoding="utf-8") as file_json:
            transactions_from_to = "некорректные данные"
            file_json.write(transactions_from_to)

        assert get_user_settings_from_json(file_path) == []
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


def test_get_user_settings_from_json_not_list() -> None:
    """Тест, если файл не со списком"""
    file_path = "test.json"
    try:
        with open(file_path, "w", encoding="utf-8") as file_json:
            transactions_from_to: str = ""
            json.dump(transactions_from_to, file_json, indent=4, ensure_ascii=False)

        assert get_user_settings_from_json(file_path) == []
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@patch("requests.request")
def test_get_apilayer_convert_rates(mock_request: MagicMock) -> None:
    """Тестирование, правильно ли функция возвращает при успешном запросе"""
    code_to = "RUB"
    code_from = "USD"
    amount = "1"
    date_str = "2025-03-01"
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    expected_result = 88.95

    mock_request.return_value.json.return_value = {"result": expected_result}
    mock_request.return_value.status_code = 200

    assert get_apilayer_convert_rates(date_obj, code_to=code_to, code_from=code_from, amount=amount) == expected_result
    api_key = os.getenv("APILAYER_EDAPI_KEY")
    url = (
        f"https://api.apilayer.com/exchangerates_data/convert?to={code_to}&from={code_from}&amount={amount}"
        f"&date={date_str}"
    )
    mock_request.assert_called_once_with("GET", url, headers={"apikey": api_key}, data={})


@patch("requests.request")
def test_get_apilayer_convert_rates_api_error(mock_request: MagicMock) -> None:
    """Тестирование, правильно ли функция обрабатывает ошибки API статуса"""
    code_to = "RUB"
    code_from = "USD"
    amount = "1"
    date_str = "2000-01-01"
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")

    mock_request.return_value.status_code = 429
    mock_request.return_value.text = "You have"

    with pytest.raises(Exception) as exc_info:
        get_apilayer_convert_rates(date_obj, code_to=code_to, code_from=code_from, amount=amount)

    assert "Ошибка API: 429 - You have" in str(exc_info)
    api_key = os.getenv("APILAYER_EDAPI_KEY")
    url = (
        f"https://api.apilayer.com/exchangerates_data/convert?to={code_to}&from={code_from}&amount={amount}"
        f"&date={date_str}"
    )
    mock_request.assert_called_once_with("GET", url, headers={"apikey": api_key}, data={})


@patch("requests.request")
def test_get_apilayer_convert_rates_connection_error(mock_request: MagicMock) -> None:
    """Тестирование, правильно ли функция обрабатывает ошибку соединения"""
    code_to = "RUB"
    code_from = "USD"
    amount = "1"
    date_str = "2000-01-01"
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")

    # имитация ошибки соединения
    mock_request.side_effect = requests.exceptions.ConnectionError

    with pytest.raises(Exception) as exc_info:
        get_apilayer_convert_rates(date_obj, code_to=code_to, code_from=code_from, amount=amount)

    assert "Connection Error. Please check your network connection" in str(exc_info)
    api_key = os.getenv("APILAYER_EDAPI_KEY")
    url = (
        f"https://api.apilayer.com/exchangerates_data/convert?to={code_to}&from={code_from}&amount={amount}"
        f"&date={date_str}"
    )
    mock_request.assert_called_once_with("GET", url, headers={"apikey": api_key}, data={})


@patch("src.utils.get_apilayer_convert_rates")
def test_get_currencies_rates_in_rub(mock_get: MagicMock) -> None:
    """Тестирование при запросе разных валют"""
    currencies = ["USD", "EUR", "CNY"]

    mock_get.side_effect = [89.3, 93.93, 12.26]
    date_str = "2025-03-01"
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    result = get_currencies_rates_in_rub(currencies, date_obj)
    expected_result = [
        {"currency": "USD", "rate": 89.3},
        {"currency": "EUR", "rate": 93.93},
        {"currency": "CNY", "rate": 12.26},
    ]
    assert result == expected_result
    # Проверяем, что функция была вызвана хотя бы один раз с каждой из валют
    for currency in currencies:
        mock_get.assert_any_call(date_obj, code_to="RUB", code_from=currency)


def test_get_currencies_rates_in_rub_empty_list() -> None:
    """Тестирование когда список пустой"""
    result = get_currencies_rates_in_rub([])
    assert result == []


def test_filter_operations_by_month_and_date() -> None:
    """Тестирование правильно ли функция фильтрует DataFrame"""
    df = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(
                ["10.05.2018 00:00:00", "10.06.2018 00:00:00", "01.06.2018 00:00:00"], dayfirst=True
            ),
            "Статус": ["OK", "FAILED", "OK"],
        }
    )

    expected = pd.DataFrame(
        {"Дата операции": pd.to_datetime(["01.06.2018 00:00:00"], dayfirst=True), "Статус": ["OK"]}
    )
    date_obj = datetime.datetime(2018, 6, 10, 0, 0)

    result = filter_operations_by_month_and_date(df, date_obj).reset_index(drop=True)

    # сравнение с помощью pandas
    pd.testing.assert_frame_equal(result, expected)


def test_generate_card_report() -> None:
    """Тестирование работы функции на вывод требуемого словаря"""
    df = pd.DataFrame(
        {
            "Номер карты": ["*1234", "*4321", "*1234"],
            "Сумма платежа": [-10.5, 100.9, -20.55],
            "Кэшбэк": [1.5, None, 2.5],
        }
    )
    expected = [{"last_digits": "1234", "total_spent": 31.05, "cashback": 0.31}]
    assert generate_card_report(df) == expected


def test_generate_card_report_empty_dataframe() -> None:
    """Тестирование когда DataFrame пустой"""
    df = pd.DataFrame(columns=["Номер карты", "Сумма платежа", "Кэшбэк"])
    assert generate_card_report(df) == []


def test_generate_card_report_missing_columns() -> None:
    df = pd.DataFrame({"Номер карты": ["*1234", "*4321", "*1234"], "Сумма платежа": [-10.5, 100.9, -20.55]})
    with pytest.raises(ValueError) as exc_info:
        generate_card_report(df)
    assert "Отсутствует необходимый столбец" in str(exc_info)


@patch("requests.get")
def test_get_stocks_price(mock_request: MagicMock) -> None:
    """Тестирование, правильно ли функция возвращает при успешном запросе"""
    stocks = "AAPL"
    expected_result = 235.93
    date_str = "2025-03-05"
    mock_request.return_value.json.return_value = {
        "Meta Data": {"3. Last Refreshed": date_str},
        "Time Series (Daily)": {date_str: {"4. close": expected_result}},
    }
    mock_request.return_value.status_code = 200
    assert get_stocks_price(stocks=stocks) == expected_result
    api_key = os.getenv("ALPHAVANTAGE_KEY")
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stocks}&apikey={api_key}"
    mock_request.assert_called_once_with(url)


@patch("requests.get")
def test_get_stocks_price_api_error(mock_request: MagicMock) -> None:
    """Тестирование, правильно ли функция обрабатывает ошибки API статуса"""
    stocks = "AAPL"

    mock_request.return_value.status_code = 429
    mock_request.return_value.text = "You have"

    with pytest.raises(Exception) as exc_info:
        get_stocks_price(stocks=stocks)

    assert "Ошибка API: 429 - You have" in str(exc_info)


@patch("requests.get")
def test_get_stocks_price_connection_error(mock_request: MagicMock) -> None:
    """Тестирование, правильно ли функция обрабатывает ошибку соединения"""
    stocks = "AAPL"

    # имитация ошибки соединения
    mock_request.side_effect = requests.exceptions.ConnectionError

    with pytest.raises(Exception) as exc_info:
        get_stocks_price(stocks=stocks)

    assert "Connection Error. Please check your network connection" in str(exc_info)


@patch("requests.get")
def test_get_stocks_price_test_api_empty_key(mock_request: MagicMock) -> None:
    """Тестирование при отсутствии нужного ключа"""
    stocks = "AAPL"
    date_str = "2025-03-05"
    mock_request.return_value.json.return_value = {
        "Meta Data": {"3. Last Refreshed": date_str},
        "Time Series (Daily)": {date_str: {}},
    }
    mock_request.return_value.status_code = 200
    with pytest.raises(Exception) as exc_info:
        get_stocks_price(stocks=stocks)

    assert "Ошибка при обработке данных: '4. close'" in str(exc_info)


@patch("requests.get")
def test_get_stocks_price_test_api_error_information(mock_request: MagicMock) -> None:
    stocks = "AAPL"
    mock_request.return_value.json.return_value = {"Information": "API rate limit is 25 requests per day"}
    mock_request.return_value.status_code = 200
    with pytest.raises(KeyError) as exc_info:
        get_stocks_price(stocks=stocks)

    assert "API rate limit is 25 requests per day" in str(exc_info)


@patch("src.utils.get_stocks_price")
def test_get_stocks_in_usd(mock_get: MagicMock) -> None:
    """Тестирование при запросе разных акций"""
    stocks_list = ["AAPL", "AMZN", "GOOGL"]
    mock_get.side_effect = [235.93, 203.8, 170.92]
    result = get_stocks_in_usd(stocks_list)
    expected_result = [
        {"stock": "AAPL", "price": 235.93},
        {"stock": "AMZN", "price": 203.8},
        {"stock": "GOOGL", "price": 170.92},
    ]
    assert result == expected_result
    # Проверяем, что функция была вызвана хотя бы один раз с каждой акцией
    for stocks in stocks_list:
        mock_get.assert_any_call(stocks=stocks)


def test_get_stocks_in_usd_empty_list() -> None:
    """Тестирование когда список пустой"""
    result = get_stocks_in_usd([])
    assert result == []


def test_generator_top_five_transactions() -> None:
    """Тестирование работы функции на вывод требуемого словаря"""
    df = pd.DataFrame(
        {
            "Дата платежа": ["06.01.2020", "06.01.2020", "04.01.2020", "06.01.2020", "04.01.2020"],
            "Сумма платежа": [-67.0, -88.0, -149.0, -203.0, -362.0],
            "Категория": ["Супермаркеты", "Супермаркеты", "Топливо", "Аптеки", "Красота"],
            "Описание": ["Magazin 25", "Magazin 25", "Circle K", "OOO Dobrodeya", "OOO Balid"],
        }
    )
    expected = [
        {"date": "06.01.2020", "amount": -67.0, "category": "Супермаркеты", "description": "Magazin 25"},
        {"date": "06.01.2020", "amount": -88.0, "category": "Супермаркеты", "description": "Magazin 25"},
        {"date": "04.01.2020", "amount": -149.0, "category": "Топливо", "description": "Circle K"},
        {"date": "06.01.2020", "amount": -203.0, "category": "Аптеки", "description": "OOO Dobrodeya"},
        {"date": "04.01.2020", "amount": -362.0, "category": "Красота", "description": "OOO Balid"},
    ]
    assert generator_top_five_transactions(df) == expected


#
def test_generator_top_five_transactions_empty_dataframe() -> None:
    """Тестирование когда DataFrame пустой"""
    df = pd.DataFrame(columns=["Дата платежа", "Сумма платежа", "Категория", "Описание"])
    assert generator_top_five_transactions(df) == []


def test_generator_top_five_transactions_missing_columns() -> None:
    """Тестирование при отсутствии нужного столбца"""
    df = pd.DataFrame(
        {
            "Дата платежа": ["06.01.2020", "06.01.2020", "04.01.2020", "06.01.2020", "04.01.2020"],
            "Сумма платежа": [-67.0, -88.0, -149.0, -203.0, -362.0],
            "Категория": ["Супермаркеты", "Супермаркеты", "Топливо", "Аптеки", "Красота"],
        }
    )
    with pytest.raises(ValueError) as exc_info:
        generator_top_five_transactions(df)
    assert "Отсутствует необходимый столбец" in str(exc_info)
