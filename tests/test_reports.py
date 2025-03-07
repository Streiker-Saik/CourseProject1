import datetime
from typing import Optional
import pandas as pd
from unittest.mock import MagicMock, patch
import pytest
from src.reports import spending_by_category


@pytest.mark.parametrize(
    "category, date, expected", [
        ("ООО ДОМ", "2018-06-15", pd.DataFrame({
            "Дата операции": pd.to_datetime(["01.06.2018 00:00:00"], dayfirst=True),
            "Статус": ["OK"],
            "Сумма платежа": [-150.5],
            "Категория": ["ООО ДОМ"]})),
        ("Аптеки", "2018-05-15", pd.DataFrame({
            "Дата операции": pd.to_datetime(["10.05.2018 00:00:00"], dayfirst=True),
            "Статус": ["OK"],
            "Сумма платежа": [-100.93],
            "Категория": ["Аптеки"]})),
        ("Аптеки", None, pd.DataFrame({
            "Дата операции": pd.Series(dtype='datetime64[ns]'),  # Указываем тип для "Дата операции"
            "Статус": pd.Series(dtype='object'),  # Указываем тип для "Статус"
            "Сумма платежа": pd.Series(dtype='float'),  # Указываем тип для "Сумма платежа"
            "Категория": pd.Series(dtype='object')  # Указываем тип для "Категория"
        })),
    ]
)

def test_spending_by_category(date: Optional[str], category: str,  expected: pd.DataFrame) -> pd.DataFrame:
    """Тестирование проверяет фильтрацию по категории с датой и при не указании даты"""
    transactions = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(
                ["10.05.2018 00:00:00", "10.06.2018 00:00:00", "01.06.2018 00:00:00"], dayfirst=True
            ),
            "Статус": ["OK", "FAILED", "OK"],
            "Сумма платежа": [-100.93, -150.5, -150.5],
            "Категория": ["Аптеки", "ООО ДОМ", "ООО ДОМ",]
        }
    )
    result = spending_by_category(transactions, category, date).reset_index(drop=True)

    # сравнение с помощью pandas
    pd.testing.assert_frame_equal(result, expected)


def test_spending_by_category_missing_columns() -> None:
    """Тестирование при отсутствии нужного столбца"""
    transactions = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(
                ["10.05.2018 00:00:00", "10.06.2018 00:00:00", "01.06.2018 00:00:00"], dayfirst=True
            ),
            "Сумма платежа": [-100.93, -150.5, -150.5],
            "Категория": ["Аптеки", "ООО ДОМ", "ООО ДОМ",]
        }
    )
    with pytest.raises(ValueError) as exc_info:
        spending_by_category(transactions, "Аптеки")
    columns = ["Дата операции", "Статус", "Сумма платежа", "Категория"]
    assert f"DataFrame должен содержать столбцы: {columns}" in str(exc_info)