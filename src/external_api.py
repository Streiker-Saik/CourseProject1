import logging
import os
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

# создание абсолютного пути из относительного
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
log_file = os.path.join(project_root, "logs", "external_api.log")
# создаем директорию и файл если она не существует
os.makedirs(os.path.dirname(log_file), exist_ok=True)

utils_logger = logging.getLogger("external_api")
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
file_formater = logging.Formatter("%(asctime)s - %(name)s: %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formater)
utils_logger.addHandler(file_handler)
utils_logger.setLevel(logging.DEBUG)


def get_apilayer_convert_rates(*, base: str, symbols: str) -> float:
    """Функция курса валюты, Exchange Rates Data API GET/latest: https://apilayer.com/marketplace/exchangerates_data-api"""
    load_dotenv("../.env")
    api_key = os.getenv("APILAYER_EDAPI_KEY")

    payload: Dict[Any, Any] = {}
    headers = {"apikey": api_key}

    url = f"https://api.apilayer.com/exchangerates_data/latest?symbols={symbols}&base={base}"

    try:
        utils_logger.info(f"Выполняем запрос у Exchange Rates Data API GET/latest")
        response = requests.request("GET", url, headers=headers, data=payload)
        # status_code = response.status_code
        # result = response.text

        if response.status_code != 200:
            error_message = f"Ошибка API: {response.status_code} - {response.text}"
            utils_logger.error(error_message)
            raise Exception(error_message)

        output_data = response.json()
        # {
        #     "base": "USD",
        #     "date": "2021-03-17",
        #     "rates": {
        #         "EUR": 0.813399,
        #         "GBP": 0.72007,
        #         "JPY": 107.346001
        #     },
        #     "success": true,
        #     "timestamp": 1519296206
        # }
        result = round(float(output_data["rates"][symbols]), 2)
        utils_logger.info(f"Получение данный у Exchange Rates Data API GET/latest - прошло успешно")
        return result

    except requests.exceptions.ConnectionError:
        error_message = "Connection Error. Please check your network connection"
        utils_logger.error(error_message)
        raise Exception(error_message)

    except Exception as exc_info:
        error_message = f"Что-то пошло не так. {str(exc_info)}"
        utils_logger.error(error_message)
        raise Exception(error_message)


def get_currencies_rates_in_rub(currencies: List[str]) -> List[Dict[str, Any]]:
    """Функция принимает список валют и возвращает курсы валют в рублях, с запросом в API"""
    try:
        utils_logger.info(f"Началась функция перевода валют '{currencies}'")
        result = []
        for currency in currencies:
            result_dict = {"currency": currency, "rate": get_apilayer_convert_rates(base=currency, symbols="RUB")}
            result.append(result_dict)
        utils_logger.info(f"Функция с валютами '{currencies}' прошла успешно")
        return result

    except Exception as exc_info:
        error_message = f"Что-то пошло не так. {str(exc_info)}"
        utils_logger.error(error_message)
        raise Exception(error_message)


# if __name__ == "__main__":
#     print(get_apilayer_convert_rates(base="USD", symbols="RUB"))
#     print(get_apilayer_convert_rates(base="EUR", symbols="RUB"))
#     print(get_apilayer_convert_rates(base="CNY", symbols="RUB"))
#     print(get_currencies_rates_in_rub(["USD", "EUR", "CNY"]))
