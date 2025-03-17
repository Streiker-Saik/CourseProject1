from typing import Any, Dict, List

import pytest

from src.services import (get_profitable_cashback, investment_bank, search_by_phone, search_transfers_to_individuals,
                          simple_search)


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


@pytest.mark.parametrize(
    "date, limit, expected",
    [
        ("2018-05", 50, '{"invest_savings": 49.43}'),
        ("2018-05", 100, '{"invest_savings": 99.43}'),
        ("2018-06", 50, '{"invest_savings": 39.5}'),
    ],
)
def test_investment_bank(date: str, limit: int, expected: str) -> None:
    """Тестирование функции возможных накоплений в 'Инвесткопилку'"""
    transactions_list = [
        {"Дата операции": "10.05.2018 00:01:00", "Статус": "OK", "Сумма платежа": 100, "Категория": "Другое"},
        {"Дата операции": "10.05.2018 00:02:00", "Статус": "FAILED", "Сумма платежа": -100.57, "Категория": "Аптеки"},
        {"Дата операции": "10.05.2018 00:03:00", "Статус": "OK", "Сумма платежа": -100.57, "Категория": "Аптеки"},
        {"Дата операции": "10.06.2018 00:01:00", "Статус": "OK", "Сумма платежа": -1510.5, "Категория": "ООО ДОМ"},
        {"Дата операции": "10.06.2018 00:02:00", "Статус": "OK", "Сумма платежа": -1100.0, "Категория": "ООО ДОМ"},
        {"Дата операции": "10.05.2018 00:03:00", "Статус": "OK", "Сумма платежа": 100, "Категория": "Другое"},
    ]
    result = investment_bank(date, transactions_list, limit)
    assert result == expected


def test_investment_bank_empty_key() -> None:
    """Тестирование если ключ не найден"""
    transactions = [
        {"Дата операции": "10.05.2018 00:00:00", "Статус": "FAILED", "Сумма платежа": -100.57},
    ]
    with pytest.raises(ValueError) as exc_info:
        investment_bank("2018-05", transactions, 100)

    assert "Отсутствует необходимый ключ в словаре:" in str(exc_info)


def test_simple_search(search_transactions: List[Dict[str, Any]]) -> None:
    """Тестирование простого поиска по фразе"""
    result = simple_search(search_transactions, "Магнит")
    expected = '[{"Категория": "Супермаркеты", "Описание": "Магнит"}]'
    assert result == expected


def test_search_by_phone(search_transactions: List[Dict[str, Any]]) -> None:
    """Тестирование функции поиска и фильтрации с наличием номеров телефона"""
    result = search_by_phone(search_transactions)
    expected = (
        '[{"Категория": "Мобильная связь", "Описание": "Тинькофф Мобайл +7 995 555-55-55"}, '
        '{"Категория": "Мобильная связь", "Описание": "МТС Mobile +7 981 333-44-55"}]'
    )
    assert result == expected


def test_search_transfers_to_individuals(search_transactions: List[Dict[str, Any]]) -> None:
    """Тестирование функции поиска и фильтрации с наличием перевода физическим лицам"""
    result = search_transfers_to_individuals(search_transactions)
    expected = (
        '[{"Категория": "Переводы", "Описание": "Валерий А."}, '
        '{"Категория": "Переводы", "Описание": "Сергей З."}, '
        '{"Категория": "Переводы", "Описание": "Артем П."}]'
    )
    assert result == expected
