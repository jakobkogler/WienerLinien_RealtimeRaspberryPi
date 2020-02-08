import json
from datetime import datetime, timedelta
from unittest.mock import patch

import pytz

from wiener_linien import Departure, WienerLinien


TZ_VIENNA = pytz.timezone("Europe/Vienna")
DATETIME_NOW = TZ_VIENNA.localize(datetime(2020, 1, 1, 12, 0, 0))


@patch("wiener_linien.datetime")
@patch("wiener_linien.requests")
def test_get_departures(mock_requests, mock_datetime):
    with open("tests/response_stephansplatz.json", "r") as f:
        stephans_platz_json = json.load(f)
    mock_requests.get.return_value.json.return_value = stephans_platz_json
    mock_datetime.now.return_value = DATETIME_NOW

    wl = WienerLinien()
    departure3 = Departure(timedelta(minutes=3, seconds=3), 3)
    departure6 = Departure(timedelta(minutes=6, seconds=6), 6)
    expected_departures = {"U1 LEOPOLDAU": [departure3], "U1 ALAUDAGASSE": [departure3, departure6]}
    assert wl.get_departures([4111, 4118]) == expected_departures
