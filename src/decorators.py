import datetime
import json
import logging
import os
from functools import wraps
from pathlib import Path
from time import perf_counter, sleep
from typing import Any, Callable, Optional

BASEDIR = Path(__file__).resolve().parent.parent
log_file = BASEDIR / "logs" / "decorators.log"

# создаем директорию и файл если она не существует
os.makedirs(os.path.dirname(log_file), exist_ok=True)

decorators_logger = logging.getLogger("decorators")
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
file_formater = logging.Formatter("%(asctime)s - %(name)s: %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formater)
decorators_logger.addHandler(file_handler)
decorators_logger.setLevel(logging.DEBUG)


def report_execution(fail_path: Optional[str] = None) -> Callable:
    """
    Декоратор выводящий результат выполнения функции(с json строки) в файл *.json, по умолчанию data/имя_функции.json
    """

    def decorator(func: Callable) -> Callable:
        decorators_logger.info(f"Декоратор выводящий результат в json файл, применен к функции {func.__name__}")

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            if not fail_path:
                names_path = BASEDIR / "data" / f"{func.__name__}.json"
            else:
                names_path = Path(fail_path)

            try:
                data = json.loads(result)
                with open(names_path, "w", encoding="UTF-8") as file_json:
                    json.dump(data, file_json, indent=4, ensure_ascii=False)
                decorators_logger.info(
                    f"Декоратор выводящий результат в json файл, функции {func.__name__}. " f"Выполнен успешно"
                )

            except json.JSONDecodeError as exc_info:
                decorators_logger.error(f"Невозможно преобразовать json дынные: {exc_info}")
                return []

            return result

        return wrapper

    return decorator
