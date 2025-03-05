import json
import os
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import numpy
import pandas as pd
import pytest
import requests

from src.utils import get_transactions_from_excel, get_user_settings_from_json, get_apilayer_convert_rates, get_currencies_rates_in_rub


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
    symbols = "RUB"
    base = "USD"
    expected_result = 89.3

    mock_request.return_value.json.return_value = {"rates": {"RUB": expected_result}}
    mock_request.return_value.status_code = 200

    assert get_apilayer_convert_rates(base=base, symbols=symbols) == expected_result
    # Проверяем был ли вызван один раз
    api_key = os.getenv("APILAYER_EDAPI_KEY")
    url = f"https://api.apilayer.com/exchangerates_data/latest?symbols={symbols}&base={base}"
    mock_request.assert_called_once_with("GET", url, headers={"apikey": api_key}, data={})


@patch("requests.request")
def test_get_apilayer_convert_rates_api_error(mock_request: MagicMock) -> None:
    """Тестирование, правильно ли функция обрабатывает ошибки"""
    symbols = "RUB"
    base = "USD"

    mock_request.return_value.status_code = 429
    mock_request.return_value.text = "You have"

    with pytest.raises(Exception) as exc_info:
        get_apilayer_convert_rates(base=base, symbols=symbols)

    assert "Что-то пошло не так. Ошибка API: 429 - You have" in str(exc_info)
    # Проверяем был ли вызван один раз
    api_key = os.getenv("APILAYER_EDAPI_KEY")
    url = f"https://api.apilayer.com/exchangerates_data/latest?symbols={symbols}&base={base}"
    mock_request.assert_called_once_with("GET", url, headers={"apikey": api_key}, data={})


@patch("requests.request")
def test_get_apilayer_convert_rates_connection_error(mock_request: MagicMock) -> None:
    """Тестирование, правильно ли функция обрабатывает ошибку соединения"""
    symbols = "RUB"
    base = "USD"

    # имитация ошибки соединения
    mock_request.side_effect = requests.exceptions.ConnectionError

    with pytest.raises(Exception) as exc_info:
        get_apilayer_convert_rates(base=base, symbols=symbols)

    assert "Connection Error. Please check your network connection" in str(exc_info)
    # Проверяем был ли вызван один раз
    api_key = os.getenv("APILAYER_EDAPI_KEY")
    url = f"https://api.apilayer.com/exchangerates_data/latest?symbols={symbols}&base={base}"
    mock_request.assert_called_once_with("GET", url, headers={"apikey": api_key}, data={})


@patch("src.external_api.get_apilayer_convert_rates")
def test_get_currencies_rates_in_rub(mock_get: MagicMock) -> None:
    """Тестирование при запросе разных"""
    currencies = ["USD", "EUR", "CNY"]

    mock_get.side_effect = [89.3, 93.93, 12.26]
    result = get_currencies_rates_in_rub(currencies)
    expected_result = [{"USD": 89.3}, {"EUR": 93.93}, {"CNY": 12.26}]
    assert result == expected_result
    # Проверяем, что функция была вызвана хотя бы один раз с каждым из валют
    for currency in currencies:
        mock_get.assert_any_call(base=currency, symbols="RUB")

