import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.external_api import get_apilayer_convert_rates, get_currencies_rates_in_rub


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
