import json
import os
from pathlib import Path

import pandas as pd

from src.decorators import report_execution

BASEDIR = Path(__file__).resolve().parent.parent


def test_report_execution() -> None:
    """Тестирование функции на создание и заполнение файла"""

    @report_execution()
    def func_test() -> str:
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

    func_test()
    file_path = BASEDIR / "data" / f"{func_test.__name__}.json"

    with open(file_path, "r", encoding="utf-8") as file_json:
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
    os.remove(file_path)  # удаляем тестовый файл


def test_report_execution_crash() -> None:
    """Тестирование функции при ошибке преобразования файла в JSON"""

    @report_execution()
    def invalid_json() -> str:
        """Тестовая функция неправильный JSON"""
        return "Это не JSON"

    result = invalid_json()

    assert result == []
