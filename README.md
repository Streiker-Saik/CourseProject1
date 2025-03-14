# Проект "Курсовая работа №1"

## Описание:

Приложение для анализа транзакций из Excel файла. Генерирует JSON данные:
- Веб-страницы: 
- - Главная: 
- - - Приветствие, 
- - - О каждой карте:
- - - - последние 4 цифры карты, 
- - - - общая сумма расходов, 
- - - - кешбэк (1 рубль на каждые 100 рублей))
- - - Топ-5 транзакций по сумме платежа.
- - - Курс валют.
- - - Стоимость акций
- - События:
- - - Расходы:
- - - - общая сумма расходов,
- - - - раздел «Основные», в котором траты по категориям отсортированы по убыванию. Данные предоставляются по 7 
категориям с наибольшими тратами, траты по остальным категориям суммируются и попадают в категорию «Остальное».
- - - - раздел «Переводы и наличные», в котором сумма по категориям «Наличные» и «Переводы» отсортирована по убыванию.
- - - Поступления:
- - - - общая сумма поступлений, 
- - - - раздел «Основные», в котором поступления по категориям отсортированы по убыванию
- - - Курс валют.
- - - Стоимость акций
- Сервисы: 
- - Выгодные категории повышенного кешбэк
- - Инвесткопилка
- - Простой поиск
- - Поиск по телефонным номерам
- - Поиск переводов физическим лицам
- Отчеты: 
- - Траты по категории, 
- - Траты по дням недели, 
- - Траты в рабочий/выходной день

## Проверить версию Python:

Убедитесь, что у вас установлен Python (версия 3.x). Вы можете проверить установленную версию Python, выполнив команду:
```
python --version
```

## Установка Poetry:
Если у вас еще не установлен Poetry, вы можете установить его, выполнив следующую команду
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
Проверить Poetry добавлен в ваш PATH.
```bash
poetry --version
```

## Установка:
- Клонируйте репозиторий:
```bash
git clone git@github.com:Streiker-Saik/CourseProject1.git
```
- Перейдите в директорию проекта:
```
cd "ваш-репозиторий"
```
- Установите необходимые зависимости:
```bash
poetry add pip python-dotenv requests pandas openpyxl 
poetry add --group lint flake8 black isort mypy types-requests pandas-stubs
poetry add --group dev pytest pytest-cov
```

## Примеры работы функций:

Модуль src.views.py
- views_home (использует функции src.utils: validate_and_format_date, get_transactions_from_excel, 
get_user_settings_from_json, filter_operations_by_month_and_date, greeting_from_time_to_time, generate_card_report,
generator_top_five_transactions, get_currencies_rates_in_rub, get_stocks_in_usd)
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
- views_events (использует функции src.utils: validate_and_format_date, get_transactions_from_excel, 
get_user_settings_from_json, filter_operations_by_date, get_expenses_report, ..., 
get_currencies_rates_in_rub, get_stocks_in_usd)
- - принимает дату("YYYY-MM-DD HH:MM:SS", путь к файлу данных, путь к настройкам пользователя, диапазон, необязательный 
параметр: W - неделя, на которую приходится дата; M - месяц, на который приходится дата (по умолчанию); Y - год, на 
который приходится дата; ALL - все данные до указанной даты.
- - возвращает JSON(str) ответ
```
views_home("2021-12-21 12:00:00", "../data/operations.xlsx", "../user_settings.json", "W")
>>>
{
    "expenses": {
        "total_amount": 1726.69,
        "main": [
            {
                "category": "Дом и ремонт",
                "amount": 1400.0
            },
            {
                "category": "Супермаркеты",
                "amount": 172.69
            },
            {
                "category": "Фастфуд",
                "amount": 154.0
            }
        ],
        "transfers_and_cash": []
    },
    "income": {
        "total_amount": 1148.96,
        "main": [
            {
                "category": "Бонусы",
                "amount": 727.96
            },
            {
                "category": "Различные товары",
                "amount": 421.0
            }
    },
    "currency_rates": [
        {
            "currency": "USD",
            "rate": 86.09
        },
        {
            "currency": "EUR",
            "rate": 93.54
        }
    ],
    "stock_prices": [
        {
            "stock": "AAPL",
            "price": 216.98
        },
        {
            "stock": "AMZN",
            "price": 198.89
        },
        {
            "stock": "GOOGL",
            "price": 167.11
        },
        {
            "stock": "MSFT",
            "price": 383.27
        },
        {
            "stock": "TSLA",
            "price": 248.09
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
- filter_operations_by_week_and_date
- - принимает DataFrame и объект datetime
- - возвращает отфильтрованный DataFrame по дате с 1 дня недели по указанное
```
date_obj = datetime.datetime(2020, 1, 10, 6, 0, 0)
df = pd.DataFrame(get_transactions_from_excel("../data/operations.xlsx"))
filter_operations_by_month_and_date(df, date_obj)
>>>
           Дата операции  ... Сумма операции с округлением
3275 2020-01-09 17:30:18  ...                         31.0
...
3278 2020-01-06 13:51:25  ...                        416.3
```
- filter_operations_by_month_and_date
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
- filter_operations_by_year_and_date
- - принимает DataFrame и объект datetime
- - возвращает отфильтрованный DataFrame по дате с 1 числа года по указанное
```
date_obj = datetime.datetime(2020, 2, 10, 6, 0, 0)
df = pd.DataFrame(get_transactions_from_excel("../data/operations.xlsx"))
filter_operations_by_year_and_date(df, date_obj)
>>>
3127 2020-02-09 13:20:51  ...                        99.99
...
3284 2020-01-01 14:47:42  ...                       362.00
```
- filter_operations_by_date (использует функции: filter_operations_by_week_and_date | 
filter_operations_by_month_and_date | filter_operations_by_year_and_date)
- - принимает DataFrame, объект datetime и диапазон фильтрации:
- - - W - неделя, на которую приходится дата;
- - - M - месяц, на который приходится дата (по умолчанию); 
- - - Y - год, на который приходится дата;
- - - ALL - все данные до указанной даты.
- - возвращает отфильтрованный DataFrame по дате с 1 числа (диапазон) по указанное
```
date_obj = datetime.datetime(2020, 2, 10, 6, 0, 0)
df = pd.DataFrame(get_transactions_from_excel("../data/operations.xlsx"))
filter_operations_by_date(df, date_obj, "M")
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
- filter_expenses
- - принимает DataFrame
- - возвращает отфильтрованный DataFrame только расходы
```
           Дата операции  ... Сумма платежа
1 2020-01-04 18:22:55  ...          -1123.0
2 2020-01-01 14:47:42  ...            362.0
filter_expenses(df)
>>>
           Дата операции  ... Сумма платежа
1 2020-01-04 18:22:55  ...          -1123.0
```
- filter_income
- - принимает DataFrame
- - возвращает отфильтрованный DataFrame только доходы
```
           Дата операции  ... Сумма платежа
1 2020-01-04 18:22:55  ...          -1123.0
2 2020-01-01 14:47:42  ...            362.0
filter_income(df)
>>>
           Дата операции  ... Сумма платежа
2 2020-01-01 14:47:42  ...            362.0
```
- calculate_total_amount
- - принимает DataFrame
- - возвращает cумму
```
           Дата операции  ... Сумма платежа
1 2020-01-04 18:22:55  ...          -1123.0
calculate_total_expenses(df)
>>>
1123.0
```
- get_main_expenses
- - принимает DataFrame
- - возвращает сумму основных расходов, первые 7, далее суммирует в "Остальные"
```
   Категория    Сумма платежа
1  Аптеки       -100.5
2  Наличные     -900.0
3  Переводы     -550.0
4  Супермаркеты -453.9
...
get_main_expenses(df)
>>>
{"category": 'Супермаркеты', "amount": 453.9}
{"category": 'Аптеки', "amount": 100.5}
```
- get_transfers_and_cash
- - принимает DataFrame
- - возвращает сумму расходов по переводам и наличным
```
   Категория  Сумма платежа
1  Аптеки     -100.5
2  Наличные   -900.0
3  Переводы   -550.0
...
get_transfers_and_cash(df)
>>>
{"category": 'Наличные', "amount": 900.0}
{"category": 'Переводы', "amount": 550.0}
```
- get_expenses_report (использует функции: filter_expenses, calculate_total_expenses, get_main_expenses, 
get_transfers_and_cash)
- - принимает DataFrame
- - возвращает отчет словарей о расходах
```    
get_expenses_report(df)
   Категория  Сумма платежа
1  Аптеки     -100.5
2  Наличные   -900.0
3  Переводы   -550.0
>>>
{
    "total_amount": 1550.5, 
    "main": [
        {"category": 'Аптеки', "amount": 100.5}
    ], 
    "transfers_and_cash": [
        {"category": 'Наличные', "amount": 900.0}
        {"category": 'Переводы', "amount": 550.0}
    ]
}
```
- get_main_income
- - принимает DataFrame
- - возвращает сумму основных доходов
```
   Категория    Сумма платежа
1  Наличные     1000.0
2  Переводы     550.0
...
get_main_income(df)
>>>
{"category": 'Наличные', "amount": 1000.0}
{"category": 'Переводы', "amount": 550.0}
```
- get_income_report (использует функции: filter_income, calculate_total_amount, get_main_income)
- - принимает DataFrame
- - возвращает отчет словарей о доходах
```    
get_income_report(df)
   Категория    Сумма платежа
1  Наличные     1000.0
2  Переводы     550.0
>>>
{
    "total_amount": 1500.0,
    "main": [
        {"category": 'Наличные', "amount": 1000.0}
        {"category": 'Переводы', "amount": 550.0}
    ]
}
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
- investment_bank
- - принимает 
- - возвращает JSON строку
```

>>>

```
- simple_search
- - принимает 
- - возвращает JSON строку
```

>>>

```
- search_by_phone
- - принимает 
- - возвращает JSON строку
```

>>>

```
- search_transfers_to_individuals
- - принимает 
- - возвращает JSON строку
```

>>>

```
---
Модуль src.reports.py
- calculate_date_range
- - принимает опциональную дату(YYYY-MM-DD) и количество дней(по умолчанию 90)
- - Возвращает кортеж datetime: даты (по умолчанию текущей) и даты, которая на указанное количество дней назад).
```
calculate_date_range("2018-05-10")
>>>
(datetime.datetime(2018, 5, 10, 0, 0), datetime.datetime(2018, 2, 9, 0, 0))
```
- spending_by_category
- - принимает DataFrame с транзакциями, название категории и опциональную дату(YYYY-MM-DD)
- - возвращает JSON строку - траты по заданной категории за последние 90 дней (от переданной даты)
```
transactions = get_transactions_from_excel("../data/operations.xlsx")
transactions_df = pd.DataFrame(transactions)
spending_by_category(transactions_df, "Аптеки", "2020-01-01")
>>>
'[{"Дата операции": "21.11.2019 11:07:06", "Дата платежа": "23.11.2019",...}, ...]'
```
- spending_by_weekday
- - принимает DataFrame с транзакциями и опциональную дату(YYYY-MM-DD)
- - возвращает JSON строку - средние траты за каждый день недели за последние 90 дней (от переданной даты)
```
transactions = get_transactions_from_excel("../data/operations.xlsx")
transactions_df = pd.DataFrame(transactions)
spending_by_weekday(transactions_df, "2020-01-01")
>>>
'{"Monday": 1322.72, "Tuesday": 1307.09, "Wednesday": 185.56, "Thursday": 197.42, "Friday": 377.2, "Saturday": 505.96, "Sunday": 305.62}'
```
- spending_by_workday
- - принимает DataFrame с транзакциями и опциональную дату(YYYY-MM-DD)
- - возвращает JSON строку - средние траты в рабочий и в выходной день за последние 90 дней (от переданной даты)
```
spending_by_workday(transactions_df, "2020-01-01")
>>>  
'{"working day": 709.04, "weekend": 410.24}'
```
---
Модуль src.decorators.py
- report_execution (декоратор)
- - принимает путь к файлу 
(по умолчанию и называется "data/имя_функции.json")
- - выводящий результат выполнения функции в файл *.json:
```
transactions = get_transactions_from_excel("../data/operations.xlsx")
transactions_df = pd.DataFrame(transactions)
spending_by_category(transactions_df, "Аптеки", "2020-01-01")
>>>  
with open('../data/spending_by_category.json', "r", encoding="UTF-8") as file_json:
    data = json.load(file_json)
    print(data)
[{'Дата операции': '21.11.2019 11:07:06', 'Дата платежа': '23.11.2019', 'Номер карты': '*4556', ...},...]
```


## Тестирование:
Этот проект использует pytest для тестирования. Чтобы запустить тесты, выполните следующие шаги:

- Запустите тесты с помощью команды:
```bash
pytest
```
- Для получения подробного отчета о тестировании запустите:
```bash
pytest -v
```
- Запустите mypy для проверки типов:
```
mypy "ваш_скрипт".py
```