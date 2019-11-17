from typing import List, Dict
import requests
from requests.exceptions import HTTPError
import json


DepartureInfos = Dict[str, List[int]]


class WienerLinien:
    def __init__(self, apikey):
        self.apikey = apikey
        self.apiurl = 'https://www.wienerlinien.at/ogd_realtime/monitor'

    def get_departures(self, RBL_numbers: List[int]) -> DepartureInfos:
        params = {'sender': self.apikey, 'rbl': RBL_numbers}
        try:
            resp = requests.get(self.apiurl, params=params)
            resp.raise_for_status()
            json_resp = resp.json()
            return self.parse_departure(json_resp)
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Unknown error occurred: {err}')
        return {}

    def parse_departure(self, json_resp: Dict) -> DepartureInfos:
        assert json_resp['message']['value'] == 'OK'
        data = {}
        for rbl in json_resp['data']['monitors']:
            for line in rbl['lines']:
                name = f'''{line['name']} {line['towards']}'''
                departures = [departure['departureTime']['countdown'] for departure in line['departures']['departure']]
                data[name] = departures
        return data
