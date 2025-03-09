# Проект "Курсовая работа №1"

## Описание:

Приложение для анализа транзакций из Excel файла. Генерирует JSON данные:
- Веб-страницы: Главная
- Сервисы: Выгодные категории повышенного кешбэка
- Отчеты: Траты по категории

## Проверить версию Python:

Убедитесь, что у вас установлен Python (версия 3.x). Вы можете проверить установленную версию Python, выполнив команду:
```
python --version
```

## Установка Poerty:
Если у вас еще не установлен Poetry, вы можете установить его, выполнив следующую команду
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
Проверить Poetry добавлен в ваш PATH.
```bash
poetry --version
```

## Установка:
1. Клонируйте репозиторий:
```bash
git clone git@github.com:Streiker-Saik/CourseProject1.git
```
2. Перейдите в директорию проекта:
```
cd ваш-репозиторий
```
3. Установите необходимые зависимости:
```bash
poetry add pip python-dotenv requests pandas openpyxl 
poetry add --group lint flake8 black isort mypy types-requests pandas-stubs
poetry add --group dev pytest pytest-cov
```

## Примеры работы функций:

Модуль src.views.py
- views_home:
- - принимает дату("YYYY-MM-DD HH:MM:SS", путь к файлу данных, путь к настройкам пользователя,
- - возвращает JSON(str) ответ
```
views_home("2021-12-21 12:00:00", "../data/operations.xlsx", "../user_settings.json")
>>>
{
    "greeting": "Добрый день",
    "cards": [
        {
            "last_digits": "4556",
            "total_spent": 952.9,
            "cashback": 9.53
        },
        {
            "last_digits": "5091",
            "total_spent": 11854.47,
            "cashback": 118.54
        },
        {
            "last_digits": "7197",
            "total_spent": 14597.07,
            "cashback": 145.97
        }
    ],
    "top_transactions": [
        {
            "date": "16.12.2021",
            "amount": 14216.42,
            "category": "ЖКХ",
            "description": "ЖКУ Квартира"
        },
        {
            "date": "02.12.2021",
            "amount": 5510.8,
            "category": "Каршеринг",
            "description": "Ситидрайв"
        },
        {
            "date": "14.12.2021",
            "amount": 5000.0,
            "category": "Переводы",
            "description": "Светлана Т."
        },
        {
            "date": "04.12.2021",
            "amount": 3499.0,
            "category": "Электроника и техника",
            "description": "DNS"
        },
        {
            "date": "21.12.2021",
            "amount": 1400.0,
            "category": "Дом и ремонт",
            "description": "YM*o481"
        }
    ],
    "currency_rates": [
        {
            "currency": "USD",
            "rate": 89.05
        },
        {
            "currency": "EUR",
            "rate": 96.5
        }
    ],
    "stock_prices": [
        {
            "stock": "AAPL",
            "price": 239.07
        },
        {
            "stock": "AMZN",
            "price": 199.25
        },
        {
            "stock": "GOOGL",
            "price": 173.86
        },
        {
            "stock": "MSFT",
            "price": 393.31
        },
        {
            "stock": "TSLA",
            "price": 262.67
        }
    ]
}
```
---
Модуль src.utils.py
- validate_and_format_date
- - принимает дату ("YYYY-MM-DD" или "YYYY-MM-DD HH:MM:SS"),
- - возвращает объект datetime
```
validate_and_format_date("2020-01-05 06:00:00")
>>>
2020-01-05 06:00:00
```
- greeting_from_time_to_time
- - принимает объект datetime,
- - возвращает приветствие, согласно времени суток
```
greeting_from_time_to_time(datetime.datetime(2020, 1, 5, 6, 0, 0)))
>>>
Доброе утро
```
- get_transactions_from_excel
- - принимает путь Excel файлу транзакций,
- - возвращает список транзакций
```
get_transactions_from_excel("../data/operations.xlsx")
>>>
[
{'Дата операции': '31.12.2021 16:44:00', 
'Дата платежа': '31.12.2021', 
'Номер карты': '*7197', 
'Статус': 'OK', 
'Сумма операции': -160.89, 
'Валюта операции': 'RUB', 
'Сумма платежа': -160.89, 
'Валюта платежа': 'RUB', 
'Кэшбэк': None, 
'Категория': 
'Супермаркеты', 
'MCC': 5411.0, 
'Описание': 
'Колхоз', 
'Бонусы (включая кэшбэк)': 3, 
'Округление на инвесткопилку': 0, 
'Сумма операции с округлением': 160.89},
...
]
```
- get_user_settings_from_json
- - принимает путь JSON файлу,
- - возвращает список
```
get_user_settings_from_json("../user_settings.json")
>>>
[{'user_currencies': ['USD', 'EUR'], 'user_stocks': ['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'TSLA']}]
```
- get_apilayer_convert_rates (API: https://apilayer.com/marketplace/exchangerates_data-api)
- - принимает объект datetime, именованные аргументы: код валюты, код валюты какую 
нужно перевести и сколько(по умолчанию 1)
- - возвращает курс валюты (число с плавающей точкой, с двумя знаками после запятой)
```
date_obj = datetime.datetime(2020, 1, 5, 6, 0, 0)
get_apilayer_convert_rates(date_obj, code_to = "RUB", code_from = "USD")
>>>
62.08
```
- get_currencies_rates_in_rub (использует функцию get_apilayer_convert_rates)
- - принимает список валют и объект datetime(по умолчанию сегодня)
- - возвращает список словарей с курсами валют({'currency': XXX, 'rate': XXX})
```
get_currencies_rates_in_rub(["USD", "EUR", "CNY"]))
>>>
[
{'currency': 'USD', 'rate': 89.05}, 
{'currency': 'EUR', 'rate': 96.5}, 
{'currency': 'CNY', 'rate': 12.31}
]
```
- filter_operations_by_month_and_date(df: pd.DataFrame, date_obj: datetime.datetime)
- - принимает DataFrame и объект datetime
- - возвращает отфильтрованный DataFrame по дате с 1 числа месяца по указанное
```
date_obj = datetime.datetime(2020, 1, 5, 6, 0, 0)
df = pd.DataFrame(get_transactions_from_excel("../data/operations.xlsx"))
filter_operations_by_month_and_date(df, date_obj)
>>>
           Дата операции  ... Сумма операции с округлением
3279 2020-01-04 18:22:55  ...                       1123.0
...
3284 2020-01-01 14:47:42  ...                        362.0
```
- generate_card_report
- - принимает DataFrame 
- - возвращает выводит список [{"last_digits": X, "total_spent": X, "cashback": X}]
- Примечание: кешбэк 1%
```
df = pd.DataFrame(get_transactions_from_excel("../data/operations.xlsx"))
generate_card_report(df)
>>>
[{'last_digits': '4556', 'total_spent': 1776.0, 'cashback': 17.76}, 
{'last_digits': '7197', 'total_spent': 216.0, 'cashback': 2.16}]
```
- get_stocks_price (API: https://www.alphavantage.co/)
- - принимает именованные аргумент stocks
- - возвращает курс акции (число с плавающей точкой, с двумя знаками после запятой)
Примечание: в долларах
```
get_stocks_price(stocks="AAPL")
>>>
239.07
```
- get_stocks_in_usd
- - принимает список акций (использует функцию get_stocks_price)
- - возвращает курсы акции в долларах(последнее закрытие дня) [{'stock': XXX, 'price': XXX}]
```
get_stocks_in_usd(["AAPL", "AMZN", "GOOGL"])
>>>
[{'stock': 'AAPL', 'price': 239.07}, 
{'stock': 'AMZN', 'price': 199.25}, 
{'stock': 'GOOGL', 'price': 173.86}]
```
- generator_top_five_transactions
- - принимает DataFrame
- - возвращает список топ-5 транзакций по стоимости платежа
```
date_obj = datetime.datetime(2020, 1, 5, 6, 0, 0)
df = pd.DataFrame(get_transactions_from_excel("../data/operations.xlsx"))
filter_df = filter_operations_by_month_and_date(df, date_obj)
generator_top_five_transactions(filter_df)
>>>
[
{'date': '06.01.2020', 'amount': -1123.0, 'category': 'Ж/д билеты', 'description': 'РЖД'}, 
{'date': '04.01.2020', 'amount': -362.0, 'category': 'Красота', 'description': 'OOO Balid'},
{'date': '06.01.2020', 'amount': -203.0, 'category': 'Аптеки', 'description': 'OOO Dobrodeya'}, 
{'date': '04.01.2020', 'amount': -149.0, 'category': 'Топливо', 'description': 'Circle K'}, 
{'date': '06.01.2020', 'amount': -88.0, 'category': 'Супермаркеты', 'description': 'Magazin 25'}]
]
```
---
Модуль src.services.py
- get_top_three_category
- - принимает данные с транзакциями, год и месяц за который проводится анализ
- - возвращает JSON строку 3 лучших(возможному кешбэк 10%) категорий
    (исключены категории: "Другое", "Наличные", "Переводы")
```
transactions = get_transactions_from_excel("../data/operations.xlsx")
get_top_three_category(transactions, 2018, 5)
>>>
{
    "Супермаркеты": 1196.04,
    "Рестораны": 755.92,
    "Фастфуд": 376.17
}
```
---
Модуль src.reports.py
- spending_by_category
- - принимает DataFrame с транзакциями, название категории и опциональную дату(YYYY-MM-DD)
- - возвращает DataFrame траты по заданной категории за последние 90 дней (от переданной даты)
```
transactions = get_transactions_from_excel("../data/operations.xlsx")
spending_by_category(transactions, "Аптеки", "2020-01-01")
>>>
           Дата операции  ... Сумма операции с округлением
3462 2019-11-21 11:07:06  ...                        642.0
...
3727 2019-10-04 21:37:14  ...                        180.0
```
- report_execution (декоратор)
- - принимает путь к файлу 
(по умолчанию там же и называется "имя_функции".csv)
- - выводящий результат выполнения функции(с DataFrame) в файл *.csv"""
```
transactions = get_transactions_from_excel("../data/operations.xlsx")
decoder_get_mask_card_number = report_execution()(spending_by_category)
spending_by_category(transactions, "Аптеки", "2020-01-01")
>>>
with open('spending_byc_ategory.csv', encoding="UTF-8") as file:
    reader = csv.reader(file, delimiter='\t')
    for row in reader:
        print(row)
['Дата операции', 'Дата платежа', 'Номер карты', 'Статус', 'Сумма операции', 'Валюта операции', 'Сумма платежа', 'Валюта платежа', 'Кэшбэк', 'Категория', 'MCC', 'Описание', 'Бонусы (включая кэшбэк)', 'Округление на инвесткопилку', 'Сумма операции с округлением']
['2019-11-21 11:07:06', '23.11.2019', '*4556', 'OK', '-642.0', 'RUB', '-642.0', 'RUB', '6.0', 'Аптеки', '5912.0', 'Apteka 7', '6', '0', '642.0']
['2019-11-14 17:19:35', '16.11.2019', '*4556', 'OK', '-30.0', 'RUB', '-30.0', 'RUB', '', 'Аптеки', '5912.0', 'Apteka 7', '0', '0', '30.0']
['2019-11-10 22:37:53', '12.11.2019', '*4556', 'OK', '-520.0', 'RUB', '-520.0', 'RUB', '5.0', 'Аптеки', '5912.0', 'Apteka 7', '5', '0', '520.0']
['2019-10-17 14:39:46', '21.10.2019', '*4556', 'OK', '-12.9', 'RUB', '-12.9', 'RUB', '', 'Аптеки', '5912.0', 'Аптека Вита', '0', '0', '12.9']
['2019-10-04 21:37:14', '07.10.2019', '*4556', 'OK', '-180.0', 'RUB', '-180.0', 'RUB', '1.0', 'Аптеки', '5912.0', 'Аптека Вита', '1', '0', '180.0']
```

## Тестирование:
Этот проект использует pytest для тестирования. Чтобы запустить тесты, выполните следующие шаги:
```
1. Запустите тесты с помощью команды:
```bash
pytest
```
2. Для получения подробного отчета о тестировании запустите:
```bash
pytest -v
```
3. Запустите mypy для проверки типов:
```
mypy ваш_скрипт.py
```