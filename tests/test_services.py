import pandas as pd
import pytest

from src.services import get_top_three_category


@pytest.mark.parametrize(
    "year, month, expected", [(2018, 5, '{\n    "Аптеки": 10.0\n}'), (2018, 6, '{\n    "ООО ДОМ": 250.0\n}')]
)
def test__get_top_three_category(year: int, month: int, expected: pd.DataFrame) -> None:
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
    # columns = ["Дата операции", "Статус", "Сумма платежа", "Категория"]
    assert "DataFrame должен содержать столбцы: ['Статус', 'Сумма платежа']" in str(exc_info)


def test_get_top_three_category_empty_filters() -> None:
    """Тестирование если отфильтрованные данные пустые"""
    transactions = [
        {"Дата операции": "10.05.2018 00:00:00", "Статус": "FAILED", "Сумма платежа": -100, "Категория": "Аптеки"},
    ]
    result = get_top_three_category(transactions, 2018, 5)
    assert result == "{}"


# def test_get_top_three_category_empty_data() -> None:
#     """Тестирование проверяет на корректные вводные данные"""
#     with pytest.raises(TypeError) as exc_info:
#         get_top_three_category(None, None, None)
#     assert str(exc_info.value) == "Вводные дынные отсутствуют"
#
#
# def test_get_top_three_category_wrong_type() -> None:
#     """Тестирование проверяет на корректные вводные данные"""
#     with pytest.raises(TypeError) as exc_info:
#         get_top_three_category([{"test": "go"}], "2025", 12)
#     assert str(exc_info.value) == "Введено не числовое значение"
#
#
# def test_get_top_three_category_error_month() -> None:
#     """Тестирование проверяет на корректный месяц"""
#     with pytest.raises(ValueError) as exc_info:
#         get_top_three_category([{"test": "go"}], 2025, 13)
#     assert str(exc_info.value) == "Месяц должен быть в диапазоне от 1 до 12"
