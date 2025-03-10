import json
import os
from typing import Optional

import pandas as pd
import pytest

from src.reports import report_execution, spending_by_category


@pytest.mark.parametrize(
    "category, date, expected",
    [
        (
            "ООО ДОМ",
            "2018-06-15",
            '[{"Дата операции": "01.06.2018 00:00:00", '
            '"Статус": "OK", '
            '"Сумма платежа": -150.5, '
            '"Категория": "ООО ДОМ"}]',
        ),
        (
            "Аптеки",
            "2018-05-15",
            '[{"Дата операции": "10.05.2018 00:00:00", '
            '"Статус": "OK", '
            '"Сумма платежа": -100.93, '
            '"Категория": "Аптеки"}]',
        ),
        ("Аптеки", None, "[]"),
    ],
)
def test_spending_by_category(date: Optional[str], category: str, expected: str) -> None:
    """Тестирование проверяет фильтрацию по категории с датой и при не указании даты"""
    transactions = pd.DataFrame(
        {
            "Дата операции": ["10.05.2018 00:00:00", "10.06.2018 00:00:00", "01.06.2018 00:00:00"],
            "Статус": ["OK", "FAILED", "OK"],
            "Сумма платежа": [-100.93, -150.5, -150.5],
            "Категория": ["Аптеки", "ООО ДОМ", "ООО ДОМ"],
        }
    )
    result = spending_by_category(transactions, category, date)
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


def test_report_execution() -> None:
    """Тестирование функции на создание и заполнение файла"""

    @report_execution()
    def func() -> str:
        """Тестовая функция DadaFrame"""
        transactions = pd.DataFrame(
            {
                "Дата операции": ["10.05.2018 00:00:00", "10.06.2018 00:00:00", "01.06.2018 00:00:00"],
                "Статус": ["OK", "FAILED", "OK"],
                "Сумма платежа": [-100.93, -150.5, -150.5],
                "Категория": ["Аптеки", "ООО ДОМ", "ООО ДОМ"],
            }
        )
        transactions_list = transactions.to_dict(orient="records")
        result = json.dumps(transactions_list, ensure_ascii=False)
        return result

    func()

    with open(f"data/{func.__name__}.json", "r", encoding="utf-8") as file_json:
        data = json.load(file_json)
        expected = [
            {"Дата операции": "10.05.2018 00:00:00", "Статус": "OK", "Сумма платежа": -100.93, "Категория": "Аптеки"},
            {
                "Дата операции": "10.06.2018 00:00:00",
                "Категория": "ООО ДОМ",
                "Статус": "FAILED",
                "Сумма платежа": -150.5,
            },
            {"Дата операции": "01.06.2018 00:00:00", "Статус": "OK", "Сумма платежа": -150.5, "Категория": "ООО ДОМ"},
        ]
        assert data == expected
    os.remove(f"data/{func.__name__}.json")  # удаляем тестовый файл
