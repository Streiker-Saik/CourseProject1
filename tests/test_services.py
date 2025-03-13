from typing import Any, Dict, List

import pytest

from src.services import get_profitable_cashback


@pytest.mark.parametrize(
    "year, month, expected", [(2018, 5, '{\n    "Аптеки": 10.0\n}'), (2018, 6, '{\n    "ООО ДОМ": 250.0\n}')]
)
def test_get_profitable_cashback(
    transactions_list: List[Dict[str, Any]], year: int, month: int, expected: str
) -> None:
    """Тестирование функции на ожидаемый ответ"""
    result = get_profitable_cashback(transactions_list, year, month)
    assert result == expected


def test_get_profitable_cashback_missing_columns() -> None:
    """Тестирование при отсутствии нужного столбца"""
    transactions = [
        {"Дата операции": "10.05.2018 00:00:00", "Категория": "Аптеки"},
        {"Дата операции": "10.06.2018 00:00:00", "Категория": "ООО ДОМ"},
        {"Дата операции": "01.06.2018 00:00:00", "Категория": "ООО ДОМ"},
    ]

    with pytest.raises(ValueError) as exc_info:
        get_profitable_cashback(transactions, 2018, 6)

    assert "DataFrame должен содержать столбцы: ['Статус', 'Сумма платежа']" in str(exc_info)


def test_get_profitable_cashback_empty_filters() -> None:
    """Тестирование если отфильтрованные данные пустые"""
    transactions = [
        {"Дата операции": "10.05.2018 00:00:00", "Статус": "FAILED", "Сумма платежа": -100, "Категория": "Аптеки"},
    ]
    result = get_profitable_cashback(transactions, 2018, 5)
    assert result == "{}"
