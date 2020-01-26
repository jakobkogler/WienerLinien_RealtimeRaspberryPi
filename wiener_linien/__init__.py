import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests
from dateutil import parser
import pytz
from requests.exceptions import HTTPError


tz_vienna = pytz.timezone("Europe/Vienna")


def get_local_now():
    return datetime.now(tz_vienna)


def parse_local(time):
    return tz_vienna.localize(parser.parse(time, ignoretz=True))


class Departure:
    def __init__(self, exact: Optional[timedelta], countdown: int):
        """exact: timedelta object that specifies when the train departures
        countdown: approxiate departure in minutes"""
        self.exact = exact
        self.countdown = countdown

    @classmethod
    def from_json(cls, json_repr: Dict) -> "Departure":
        departure_dict = json_repr["departureTime"]
        exact = None
        if "timeReal" in departure_dict:
            time_real = parse_local(departure_dict["timeReal"])
            exact = time_real - get_local_now()
        countdown = departure_dict["countdown"]
        return cls(exact=exact, countdown=countdown)

    def __repr__(self):
        if self.exact is not None:
            seconds = max(timedelta(0), self.exact).seconds
            if self.exact < timedelta(minutes=10):
                return f"{seconds//60}:{seconds%60:02d}"
            else:
                return f"{int(round(seconds/60))}"
        return f"{self.countdown}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Departure):
            return False
        return (self.exact, self.countdown) == (other.exact, other.countdown)


DepartureInfos = Dict[str, List[Departure]]


class WienerLinien:
    def __init__(self):
        self.apiurl = "https://www.wienerlinien.at/ogd_realtime/monitor"

    def get_departures(self, RBL_numbers: List[int]) -> DepartureInfos:
        params = {"rbl": RBL_numbers}
        try:
            resp = requests.get(self.apiurl, params=params)
            resp.raise_for_status()
            json_resp = resp.json()
            return self.parse_departures(json_resp)
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Unknown error occurred: {err}")
        return {}

    def parse_departures(self, json_resp: Dict) -> DepartureInfos:
        assert json_resp["message"]["value"] == "OK"

        server_time = parse_local(json_resp["message"]["serverTime"])
        now = get_local_now()
        assert abs(now - server_time).seconds < 5

        data = {}
        for rbl in json_resp["data"]["monitors"]:
            for line in rbl["lines"]:
                name = f"""{line['name']} {line['towards']}"""
                departures = [
                    Departure.from_json(departure_dict)
                    for departure_dict in line["departures"]["departure"]
                ]
                data[name] = departures
        return data
