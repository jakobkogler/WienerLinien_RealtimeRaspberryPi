import datetime
import json
from unittest.mock import patch

import pytest  # type: ignore
import pytz
from wiener_linien import Departure


def test_departure_init():
    exact = datetime.timedelta(minutes=5, seconds=1)
    departure = Departure(exact, 5)
    assert departure.exact == exact
    assert departure.countdown == 5


TZ_VIENNA = pytz.timezone("Europe/Vienna")
DATETIME_NOW = TZ_VIENNA.localize(datetime.datetime(2020, 1, 25, 20, 33, 59))

DEPARTURE_15_TEXT = """{"departureTime":{"timePlanned":"2020-01-25T20:49:00.000+0100","timeReal":"2020-01-25T20:49:00.000+0100","countdown":15}}"""
DEPARTURE_5_TEXT = """{"departureTime":{"timePlanned":"2020-01-25T20:49:00.000+0100","timeReal":"2020-01-25T20:39:00.000+0100","countdown":5}}"""
DEPARTURE_NEGATIVE_TEXT = """{"departureTime":{"timePlanned":"2020-01-25T20:49:00.000+0100","timeReal":"2020-01-25T20:33:00.000+0100","countdown":5}}"""
DEPARTURE_MISSING_REALTIME_TEXT = """{"departureTime":{"countdown":5}}"""

REPRESENTATION_TEST = [
    (DEPARTURE_15_TEXT, "15"),
    (DEPARTURE_5_TEXT, "5:01"),
    (DEPARTURE_NEGATIVE_TEXT, "0:00"),
    (DEPARTURE_MISSING_REALTIME_TEXT, "5"),
]


class TestDeparture:
    @classmethod
    def setup_class(cls):
        cls.mock_datetime_patcher = patch("wiener_linien.datetime")
        cls.mock_datetime = cls.mock_datetime_patcher.start()
        cls.mock_datetime.now.return_value = DATETIME_NOW

    @classmethod
    def teardown_class(cls):
        cls.mock_datetime_patcher.stop()

    def test_departure_create(self):
        departure_json = json.loads(DEPARTURE_15_TEXT)
        departure = Departure.from_json(departure_json)
        assert departure.countdown == 15
        expected_exact = datetime.timedelta(minutes=15, seconds=1)
        assert departure.exact == expected_exact

    @pytest.mark.parametrize("departure_text, expected_repr", REPRESENTATION_TEST)
    def test_departure_representation(self, departure_text, expected_repr):
        departure_json = json.loads(departure_text)
        departure = Departure.from_json(departure_json)
        assert repr(departure) == expected_repr
