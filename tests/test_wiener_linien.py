import json
from datetime import datetime, timedelta

import pytest  # type: ignore
import pytz
import requests

import wiener_linien
from wiener_linien import Departure, WienerLinien


class MockedResponse:
    def json(self):
        with open("tests/response_stephansplatz.json", "r") as f:
            return json.load(f)

    def raise_for_status(self):
        pass


@pytest.fixture
def now_frozen(monkeypatch):
    def mockreturn():
        tz_vienna = pytz.timezone("Europe/Vienna")
        return tz_vienna.localize(datetime(2020, 1, 1, 12, 0, 0))

    monkeypatch.setattr(wiener_linien, "get_local_now", mockreturn)


@pytest.fixture
def request_mock(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: MockedResponse())


def test_get_departures(request_mock, now_frozen):
    wl = WienerLinien()
    departure3 = Departure(timedelta(minutes=3, seconds=3), 3)
    departure6 = Departure(timedelta(minutes=6, seconds=6), 6)
    expected_departures = {"U1 LEOPOLDAU": [departure3], "U1 ALAUDAGASSE": [departure3, departure6]}
    assert wl.get_departures([4111, 4118]) == expected_departures
