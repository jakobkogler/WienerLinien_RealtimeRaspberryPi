from typing import List, Dict
import requests
from requests.exceptions import HTTPError
import json
from dateutil import parser
from datetime import datetime, timedelta
import pytz


tz = pytz.timezone('Europe/Vienna')


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
