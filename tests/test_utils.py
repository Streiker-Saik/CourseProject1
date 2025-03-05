import json
import os
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import numpy
import pandas as pd
import pytest

from src.utils import get_transactions_from_excel, get_user_settings_from_json


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
