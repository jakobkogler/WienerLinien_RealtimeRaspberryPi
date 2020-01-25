from typing import List, Dict
import requests
from requests.exceptions import HTTPError
import json
from dateutil import parser
from dateutil.tz import gettz
from datetime import datetime, timedelta


tz_vienna = gettz('Europe/Vienna')


DepartureInfos = Dict[str, List[str]]


class WienerLinien:
    def __init__(self):
        self.apiurl = 'https://www.wienerlinien.at/ogd_realtime/monitor'

    def get_departures(self, RBL_numbers: List[int]) -> DepartureInfos:
        params = {'rbl': RBL_numbers}
        try:
            resp = requests.get(self.apiurl, params=params)
            resp.raise_for_status()
            json_resp = resp.json()
            return self.parse_departures(json_resp)
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Unknown error occurred: {err}')
        return {}

    def parse_departures(self, json_resp: Dict) -> DepartureInfos:
        assert json_resp['message']['value'] == 'OK'

        server_time = parser.parse(json_resp['message']['serverTime'])
        now = datetime.now(tz)
        assert(abs(now - server_time).seconds < 5)
        print(now)
        print(server_time)

        data = {}
        for rbl in json_resp['data']['monitors']:
            for line in rbl['lines']:
                name = f'''{line['name']} {line['towards']}'''
                departures = [self.get_departure_string(departure['departureTime'], now)
                              for departure in line['departures']['departure']]
                data[name] = departures
        return data

    def get_departure_string(self, departure: Dict, now: datetime) -> str:
        if 'timeReal' in departure:
            departure_time = parser.parse(departure['timeReal'])
            diff_total = max(departure_time - now, timedelta(0)).seconds
            if diff_total > 10 * 60:
                return f"{diff_total // 60}"
            return f"{diff_total // 60}:{diff_total % 60:02}"
        else:
            return str(departure['countdown'])


class Departure:
    def __init__(self, exact: timedelta, countdown: int):
        """exact: timedelta object that specifies when the train departures
        countdown: approxiate departure in minutes"""
        self.exact = exact
        self.countdown = countdown

    @classmethod
    def from_json(cls, json_repr: Dict) -> "Departure":
        time_real = parser.parse(json_repr['departureTime']['timeReal']).astimezone(tz_vienna)
        exact = time_real - cls.get_local_now()
        countdown = json_repr['departureTime']['countdown']
        return cls(exact=exact, countdown=countdown)

    def __repr__(self):
        if self.exact < timedelta(minutes=10):
            seconds = self.exact.seconds
            return f"{seconds//60}:{seconds%60:02d}"
        return f"{self.countdown}"
   
    @staticmethod
    def get_local_now():
        return datetime.now(tz_vienna)


