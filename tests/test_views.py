import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.views import greeting_from_time_to_time


@pytest.mark.parametrize(
    "mock_time, expected",
    [
        (datetime.datetime(2025, 1, 1, 0, 0), "Доброй ночи"),
        (datetime.datetime(2025, 1, 1, 6, 0), "Доброе утро"),
        (datetime.datetime(2025, 1, 1, 12, 0), "Добрый день"),
        (datetime.datetime(2025, 1, 1, 18, 0), "Добрый вечер"),
    ],
)
@patch("datetime.datetime")
def test_greeting_from_time_to_time(mock_datetime: MagicMock, mock_time: datetime.datetime, expected: str) -> None:
    """Тестирование, проверяем на разное время, вывод правильного приветствия"""
    mock_datetime.now.return_value = mock_time
    result = greeting_from_time_to_time(mock_datetime.now())
    assert result == expected
