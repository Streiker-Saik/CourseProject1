import datetime
from typing import Optional, Tuple
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.reports import calculate_date_range, spending_by_category, spending_by_weekday, spending_by_workday


@pytest.mark.parametrize(
    "date, number_of_days, expected",
    [
        ("2025-03-11", 90, (datetime.datetime(2025, 3, 11), datetime.datetime(2024, 12, 11))),
        ("2025-03-11", 10, (datetime.datetime(2025, 3, 11), datetime.datetime(2025, 3, 1))),
        ("2025-03-11", 30, (datetime.datetime(2025, 3, 11), datetime.datetime(2025, 2, 9))),
    ],
)
def test_calculate_date_range(
    date: str, number_of_days: int, expected: Tuple[datetime.datetime, datetime.datetime]
) -> None:
    """Тестирование работы функции получение дат с указанием даты"""
    result = calculate_date_range(date, number_of_days)
    assert result == expected


@patch("datetime.datetime")
def test_calculate_date_range_empy_date(mock_datetime: MagicMock) -> None:
    """Тестирование работы функции получение дат с неуказанной датой"""
    mock_datetime.now.return_value = datetime.datetime(2025, 3, 12)
    date_to = datetime.datetime(2025, 3, 12)
    date_from = date_to - datetime.timedelta(days=90)
    expected = (date_to, date_from)
    result = calculate_date_range(number_of_days=90)
    assert result == expected


def test_spending_by_category_missing_columns() -> None:
    """Тестирование при отсутствии нужного столбца"""
    transactions = pd.DataFrame(
        {
            "Дата операции": ["10.05.2018 00:00:00", "10.06.2018 00:00:00", "01.06.2018 00:00:00"],
            "Сумма платежа": [-100.93, -150.5, -150.5],
            "Категория": ["Аптеки", "ООО ДОМ", "ООО ДОМ"],
        }
    )
    with pytest.raises(ValueError) as exc_info:
        spending_by_category(transactions, "Аптеки")

    assert "DataFrame должен содержать столбцы: ['Статус']" in str(exc_info)


@pytest.mark.parametrize(
    "mock_date, date, expected",
    [
        (
            (datetime.datetime(2018, 5, 10), datetime.datetime(2018, 2, 9)),
            "2018-05-10",
            '{"Monday": 0, "Tuesday": 0, "Wednesday": 0, "Thursday": 100.93, "Friday": 0, "Saturday": 0, "Sunday": 0}',
        ),
        (
            (datetime.datetime(2018, 6, 15), datetime.datetime(2018, 3, 17)),
            "2018-06-15",
            '{"Monday": 0, "Tuesday": 0, "Wednesday": 0, "Thursday": 100.93, "Friday": 150.5, "Saturday": 0, '
            '"Sunday": 0}',
        ),
        (
            (datetime.datetime(2025, 3, 11), datetime.datetime(2024, 12, 11)),
            None,
            '{"Monday": 0, "Tuesday": 0, "Wednesday": 0, "Thursday": 0, "Friday": 0, "Saturday": 0, "Sunday": 0}',
        ),
    ],
)
@patch("src.reports.calculate_date_range")
def test_spending_by_weekday(
    mock_get: MagicMock,
    transactions_df: pd.DataFrame,
    mock_date: Tuple[datetime.datetime, datetime.datetime],
    date: Optional[str],
    expected: str,
) -> None:
    """Тестирование проверяет фильтрацию по категории с датой и при не указании даты"""
    mock_get.return_value = mock_date

    result = spending_by_weekday(transactions_df, date)
    assert result == expected


def test_spending_by_weekday_missing_columns() -> None:
    """Тестирование при отсутствии нужного столбца"""
    date = "2018-06-15"
    transactions = pd.DataFrame(
        {
            "Дата операции": ["10.05.2018 00:00:00", "10.06.2018 00:00:00", "01.06.2018 00:00:00"],
            "Сумма платежа": [-100.93, -150.5, -150.5],
        }
    )
    with pytest.raises(ValueError) as exc_info:
        spending_by_weekday(transactions, date)

    assert "DataFrame должен содержать столбцы: ['Статус']" in str(exc_info)


@pytest.mark.parametrize(
    "category, date, mock_date, expected",
    [
        (
            "ООО ДОМ",
            "2018-06-15",
            (datetime.datetime(2018, 6, 15), datetime.datetime(2018, 3, 17)),
            '[{"Номер карты": "*1234", '
            '"Дата операции": "01.06.2018 00:00:00", '
            '"Статус": "OK", '
            '"Сумма платежа": -150.5, '
            '"Категория": "ООО ДОМ"}]',
        ),
        (
            "Аптеки",
            "2018-05-15",
            (datetime.datetime(2018, 5, 15), datetime.datetime(2018, 2, 14)),
            '[{"Номер карты": "*1234", '
            '"Дата операции": "10.05.2018 00:00:00", '
            '"Статус": "OK", '
            '"Сумма платежа": -100.93, '
            '"Категория": "Аптеки"}]',
        ),
        ("Аптеки", None, (datetime.datetime(2025, 3, 11), datetime.datetime(2024, 12, 11)), "[]"),
    ],
)
@patch("src.reports.calculate_date_range")
def test_spending_by_category(
    mock_get: MagicMock,
    transactions_df: pd.DataFrame,
    mock_date: Tuple[datetime.datetime, datetime.datetime],
    date: Optional[str],
    category: str,
    expected: str,
) -> None:
    """Тестирование проверяет фильтрацию по категории с датой и при не указании даты"""
    mock_get.return_value = mock_date

    result = spending_by_category(transactions_df, category, date)
    assert result == expected


@pytest.mark.parametrize(
    "mock_date, date, expected",
    [
        (
            (datetime.datetime(2018, 5, 10), datetime.datetime(2018, 2, 9)),
            "2018-05-10",
            '{"working day": 100.93, "weekend": 0}',
        ),
        (
            (datetime.datetime(2018, 6, 15), datetime.datetime(2018, 3, 17)),
            "2018-06-15",
            '{"working day": 125.72, "weekend": 0}',
        ),
        (
            (datetime.datetime(2025, 3, 11), datetime.datetime(2024, 12, 11)),
            None,
            '{"working day": 0, "weekend": 0}',
        ),
    ],
)
@patch("src.reports.calculate_date_range")
def test_spending_by_workday(
    mock_get: MagicMock,
    transactions_df: pd.DataFrame,
    mock_date: Tuple[datetime.datetime, datetime.datetime],
    date: Optional[str],
    expected: str,
) -> None:
    """Тестирование проверяет фильтрацию по категории с датой и при не указании даты"""
    mock_get.return_value = mock_date

    result = spending_by_workday(transactions_df, date)
    assert result == expected


def test_spending_by_workday_missing_columns() -> None:
    """Тестирование при отсутствии нужного столбца"""
    date = "2018-06-15"
    transactions = pd.DataFrame(
        {
            "Дата операции": ["10.05.2018 00:00:00", "10.06.2018 00:00:00", "01.06.2018 00:00:00"],
            "Сумма платежа": [-100.93, -150.5, -150.5],
        }
    )
    with pytest.raises(ValueError) as exc_info:
        spending_by_workday(transactions, date)

    assert "DataFrame должен содержать столбцы: ['Статус']" in str(exc_info)
