import os
import logging
import json
import datetime
from typing import Any, Dict, List

# создание абсолютного пути из относительного
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
log_file = os.path.join(project_root, "logs", "services.log")
# создаем директорию и файл если она не существует
os.makedirs(os.path.dirname(log_file), exist_ok=True)

services_logger = logging.getLogger("services")
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
file_formater = logging.Formatter("%(asctime)s - %(name)s: %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formater)
services_logger.addHandler(file_handler)
services_logger.setLevel(logging.DEBUG)


def get_high_cashback_categories(data: List[Dict[str, Any]], year: str, month: str) -> None:
    """
    Функция принимает данные с транзакциями, год и месяц за который проводится анализ,
    выводит JSON строку 3 лучших категорий
    """
    pass