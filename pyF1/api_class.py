from logging import exception
from urllib.error import HTTPError
from urllib.request import urlopen
from time import sleep
import json

API_DATA_TYPES = {
  "common": [
    "date",
    "driver_number",
    "meeting_key",
    "session_key"
  ],
  "car_data": [
    "brake",
    "drs",
    "n_gear",
    "rpm",
    "speed",
    "throttle"
  ],
  "drivers": [
    "broadcast_name",
    "country_code",
    "driver_number",
    "first_name",
    "full_name",
    "headshot_url",
    "last_name",
    "meeting_key",
    "name_acronym",
    "session_key",
    "team_colour",
    "team_name"
  ],
  "intervals": [
    "gap_to_leader",
    "interval"
  ],
  "laps": [
    "date_start",
    "duration_sector_1",
    "duration_sector_2",
    "duration_sector_3",
    "i1_speed",
    "i2_speed",
    "is_pit_out_lap",
    "lap_duration",
    "lap_number",
    "segments_sector_1",
    "segments_sector_2",
    "segments_sector_3",
    "st_speed"
  ],
  "location": [
    "x",
    "y",
    "z"
  ],
  "meetings": [
    "circuit_key",
    "circuit_short_name",
    "country_code",
    "country_key",
    "country_name",
    "date_start",
    "gmt_offset",
    "location",
    "meeting_name",
    "meeting_official_name",
    "year"
  ],
  "pit": [
    "lap_number",
    "pit_duration"
  ],
  "position": [
    "position"
  ],
  "race_control": [
    "category",
    "flag",
    "lap_number",
    "message",
    "scope",
    "sector"
  ],
  "sessions": [
    "circuit_key",
    "circuit_short_name",
    "country_code",
    "country_key",
    "country_name",
    "date_end",
    "date_start",
    "gmt_offset",
    "location",
    "session_name",
    "session_type",
    "year"
  ],
  "stints": [
    "compound",
    "lap_end",
    "lap_start",
    "stint_number",
    "tyre_age_at_start"
  ],
  "team_radio": [
    "recording_url"
  ],
  "weather": [
    "air_temperature",
    "humidity",
    "pressure",
    "rainfall",
    "track_temperature",
    "wind_direction",
    "wind_speed"
  ]
}

class F1API:
    def __init__(self, session_key):
        self.session_key = session_key
        self.BASE_URL= "https://api.openf1.org/v1/"
        self.TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

    @staticmethod
    def fetch_result(url, retries=0):
        try:
            response = urlopen(url)
            data = json.loads(response.read().decode('utf-8'))
            return data

        except HTTPError as e:
            response_code = e.getcode()
            match response_code:
                case 429:
                    if retries < 5:
                        sleep(0.5)
                        retries += 1
                        print("429 retry", retries)
                        return F1API.fetch_result(url, retries)
                    else:
                        return None



    def call_api(self, data_type, data_filter=None):
        if data_type not in API_DATA_TYPES:
            raise TypeError(f'data type {data_type} not available')
        api_url = f'{self.BASE_URL}{data_type}?session_key={self.session_key}'

        if data_filter:
            type_filter = API_DATA_TYPES[data_type] + API_DATA_TYPES["common"]

            for f in data_filter:
                if f["key"] not in type_filter:
                    raise TypeError(f'{f["key"]} is not valid for type {data_type}')

                url_addon = f'&{f["key"]}{f["value"]}'
                api_url += url_addon

        return self.fetch_result(api_url)

    def get_drivers(self):
        api_url = f'{self.BASE_URL}drivers?session_key={self.session_key}'
        ans = self.fetch_result(api_url)
        return ans

    def get_driver_position(self, driver_number, time_end):
        e_string = time_end.strftime(self.TIME_FORMAT)
        api_url = f'{self.BASE_URL}position?session_key={self.session_key}&driver_number={driver_number}&date<{e_string}'
        ans = self.fetch_result(api_url)
        return ans

    def get_driver_interval(self, driver_number, time_start, time_end):
        s_string = time_start.strftime(self.TIME_FORMAT)
        e_string = time_end.strftime(self.TIME_FORMAT)
        api_url = f'{self.BASE_URL}intervals?session_key={self.session_key}&driver_number={driver_number}&date>={s_string}&date<{e_string}'

        ans = self.fetch_result(api_url)
        return ans

    def get_driver_laps(self, driver_number, time_end):
        e_string = time_end.strftime(self.TIME_FORMAT)
        api_url = f'{self.BASE_URL}laps?session_key={self.session_key}&driver_number={driver_number}&date_start<{e_string}'
        print(api_url)
        ans = self.fetch_result(api_url)
        return ans
