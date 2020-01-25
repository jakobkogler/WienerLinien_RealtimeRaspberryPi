import datetime
import json
import pytest
from dateutil.tz import gettz
from wiener_linien_lib import Departure


def test_departure_init():
    exact = datetime.timedelta(minutes=5, seconds=1)
    departure = Departure(exact, 5)
    assert departure.exact == exact
    assert departure.countdown == 5


@pytest.fixture
def json_departure_15():
    departure_json = """{"departureTime":{"timePlanned":"2020-01-25T20:49:00.000+0100","timeReal":"2020-01-25T20:49:00.000+0100","countdown":15}}"""
    return json.loads(departure_json)


@pytest.fixture
def json_departure_5():
    departure_json = """{"departureTime":{"timePlanned":"2020-01-25T20:49:00.000+0100","timeReal":"2020-01-25T20:39:00.000+0100","countdown":5}}"""
    return json.loads(departure_json)

@pytest.fixture
def now_frozen(monkeypatch):
    def mockreturn():
        tz_vienna = gettz('Europe/Vienna')
        return datetime.datetime(2020, 1, 25, 20, 33, 59, tzinfo=tz_vienna)
    monkeypatch.setattr(Departure, "get_local_now", mockreturn) 


def test_departure_create(json_departure_15, now_frozen):
    departure = Departure.from_json(json_departure_15)
    assert departure.countdown == 15
    expected_exact = datetime.timedelta(minutes=15, seconds=1)
    assert departure.exact == expected_exact


def test_departure_repr15(json_departure_15, now_frozen):
    departure = Departure.from_json(json_departure_15)
    assert repr(departure) == "15"


def test_departure_repr5(json_departure_5, now_frozen):
    departure = Departure.from_json(json_departure_5)
    assert repr(departure) == "5:01"
