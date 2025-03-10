import pytest

from src.services import get_top_three_category


@pytest.mark.parametrize(
    "year, month, expected", [(2018, 5, '{\n    "Аптеки": 10.0\n}'), (2018, 6, '{\n    "ООО ДОМ": 250.0\n}')]
)
def test__get_top_three_category(year: int, month: int, expected: str) -> None:
    """Тестирование функции на ожидаемый ответ"""
    transactions = [
        {"Дата операции": "10.05.2018 00:00:00", "Статус": "FAILED", "Сумма платежа": -100, "Категория": "Аптеки"},
        {"Дата операции": "10.05.2018 00:00:00", "Статус": "OK", "Сумма платежа": -100, "Категория": "Аптеки"},
        {"Дата операции": "10.06.2018 00:00:00", "Статус": "OK", "Сумма платежа": -1500, "Категория": "ООО ДОМ"},
        {"Дата операции": "10.06.2018 00:00:00", "Статус": "OK", "Сумма платежа": -1000, "Категория": "ООО ДОМ"},
    ]
    result = get_top_three_category(transactions, year, month)
    assert result == expected


def test_get_top_three_category_missing_columns() -> None:
    """Тестирование при отсутствии нужного столбца"""
    transactions = [
        {"Дата операции": "10.05.2018 00:00:00", "Категория": "Аптеки"},
        {"Дата операции": "10.06.2018 00:00:00", "Категория": "ООО ДОМ"},
        {"Дата операции": "01.06.2018 00:00:00", "Категория": "ООО ДОМ"},
    ]

    with pytest.raises(ValueError) as exc_info:
        get_top_three_category(transactions, 2018, 6)

    assert "DataFrame должен содержать столбцы: ['Статус', 'Сумма платежа']" in str(exc_info)


def test_get_top_three_category_empty_filters() -> None:
    """Тестирование если отфильтрованные данные пустые"""
    transactions = [
        {"Дата операции": "10.05.2018 00:00:00", "Статус": "FAILED", "Сумма платежа": -100, "Категория": "Аптеки"},
    ]
    result = get_top_three_category(transactions, 2018, 5)
    assert result == "{}"
