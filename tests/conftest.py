from typing import Any, Dict, List

import pandas as pd
import pytest


@pytest.fixture
def user_settings() -> List[Dict[str, Any]]:
    return [
        {"operationAmount": {"amount": "31957.58", "currency": {"name": "руб.", "code": "RUB"}}},
        {"operationAmount": {"amount": "8221.37", "currency": {"name": "USD", "code": "USD"}}},
        {"operationAmount": {"amount": "9824.07", "currency": {"name": "USD", "code": "USD"}}},
    ]


@pytest.fixture()
def transactions_list() -> List[Dict[str, Any]]:
    return [
        {"Дата операции": "10.05.2018 00:00:00", "Статус": "FAILED", "Сумма платежа": -100, "Категория": "Аптеки"},
        {"Дата операции": "10.05.2018 00:00:00", "Статус": "OK", "Сумма платежа": -100, "Категория": "Аптеки"},
        {"Дата операции": "10.06.2018 00:00:00", "Статус": "OK", "Сумма платежа": -1500, "Категория": "ООО ДОМ"},
        {"Дата операции": "10.06.2018 00:00:00", "Статус": "OK", "Сумма платежа": -1000, "Категория": "ООО ДОМ"},
    ]


@pytest.fixture()
def transactions_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Номер карты": ["*1234", "*4321", "*1234"],
            "Дата операции": ["10.05.2018 00:00:00", "10.06.2018 00:00:00", "01.06.2018 00:00:00"],
            "Статус": ["OK", "FAILED", "OK"],
            "Сумма платежа": [-100.93, -150.5, -150.5],
            "Категория": ["Аптеки", "ООО ДОМ", "ООО ДОМ"],
        }
    )
