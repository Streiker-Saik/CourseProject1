import json
import logging
import os
from typing import Any, Dict, List, cast

import pandas as pd

# создание абсолютного пути из относительного
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
log_file = os.path.join(project_root, "logs", "utils.log")
# создаем директорию и файл если она не существует
os.makedirs(os.path.dirname(log_file), exist_ok=True)

utils_logger = logging.getLogger("utils")
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
file_formater = logging.Formatter("%(asctime)s - %(name)s: %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formater)
utils_logger.addHandler(file_handler)
utils_logger.setLevel(logging.DEBUG)


def get_transactions_from_excel(file_path: str) -> List[Dict[str, Any]]:
    """Функция принимает файл (*.xlsx) и выводит список словарей"""
    try:
        utils_logger.info(f'Выполняем преобразование EXCEL-файла "{file_path}" в объект Python')
        data = pd.read_excel(file_path)
        records = data.to_dict(orient="records")

        # Заменяем пустые значения NaN на None
        for record in records:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = 0
        result = cast(List[Dict[str, Any]], records)
        utils_logger.info(f'Преобразование JSON-файла "{file_path}" в объект Python выполнено')
        return result

    except FileNotFoundError:
        error_message = f"Файл '{file_path}' - не найден"
        utils_logger.error(error_message)
        raise FileNotFoundError(error_message)

    except Exception as exc_info:
        error_message = f"Что-то пошло не так при чтении {file_path}. Ошибка {exc_info}"
        utils_logger.error(error_message)
        raise Exception(error_message)


def get_user_settings_from_json(file_path: str) -> List[Dict[str, Any]]:
    """Функцию, принимает на вход путь до JSON-файла и возвращает список словарей с данными убирая пустые словари"""
    if not os.path.exists(file_path):
        utils_logger.error(f"Файл '{file_path}' - не найден")
        return []

    try:
        utils_logger.info(f'Выполняем преобразование JSON-файла "{file_path}" в объект Python')
        with open(file_path, "r", encoding="utf-8") as json_file:
            transactions: List[Dict[str, Any]] = json.load(json_file)

            if type(transactions) is not list:
                utils_logger.error("Файл содержит не список")
                return []

            # убираем пустые словари
            result = list(filter(bool, transactions))
            utils_logger.info(f'Преобразование JSON-файла "{file_path}" в объект Python выполнено')
            return result

    except json.JSONDecodeError as exc_info:
        utils_logger.error(f"Невозможно преобразовать json дынные: {exc_info}")
        return []

    except Exception as exc_info:
        error_message = f"Что-то пошло не так при чтении {file_path}. Ошибка {exc_info}"
        utils_logger.error(error_message)
        raise Exception(error_message)


# if __name__ == "__main__":
#     print(get_transactions_from_excel("../data/operations.xlsx")[0])
#     transactions = get_transactions_from_excel("../data/operations.xlsx")
#     for transaction in transactions:
#         print(transaction["Номер карты"])
#     print(get_transactions_from_json("../user_settings.json"))
