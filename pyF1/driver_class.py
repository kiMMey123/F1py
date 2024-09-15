from datetime import datetime, timedelta
from turtledemo.penrose import start

from api_class import F1API
from timer import Timer

class F1Driver:
    def __init__(self, driver_data, api_class):
        self.api_class = api_class
        self.data = driver_data
        self.name = self.data["full_name"]
        self.number = self.data["driver_number"]
        self.short_name = self.data["name_acronym"]

        self.session_data = {
            'laps' : [],
            'position': [],
            'intervals': [],
            'stints': [],
            'pit': [],
        }

        self.session_timeline = []
        self.timeline_index = 0
        self.current_data = {
            "lap": 1,
            "lap_sectors": 1,
            "lap_sector_segment": 1,
            "last_lap_time": None,
            "best_lap_time": None,
            "position": None,
            "gap_to_leader": None,
            "interval": None,
            "in_pit": False,
            "out_lap": False,
            "current_stint": 1,
            "current_tyre_compound": None,
            "current_tyre_age": 0,
        }
        self.current_time_stamp = None

    def set_session_data(self, data, key):
        for line in data:
            if self.number == line["driver_number"]:
                self.session_data[key].append(line)

    def sort_session_data(self, race_start):
        start_time = datetime.fromisoformat(self.session_data['position'][0]['date']) - timedelta(seconds=5)
        self.current_time_stamp = start_time

        end_time = start_time + timedelta(milliseconds=100)
        first_lap = self.session_data['laps'][0]
        self.session_timeline.append(first_lap)

        lap_timeline = []

        for i, lap in enumerate(self.session_data["laps"]):
            if lap["lap_number"] == 1 and not lap["date_start"]:
                lap_start = race_start
                prev_lap = None
                if not lap["duration"]:
                    lap_time = (datetime.fromisoformat(self.session_data["laps"][i + 1]) - lap_start).total_seconds()
                else:
                    lap_time = lap["lap_duration"]
            else:
                lap_start = datetime.fromisoformat(lap["date_start"])
                lap_time = lap["lap_duration"]
                prev_lap = self.session_data["laps"][i -1]["duration"]

            this_lap = {
                "type": "lap",
                "lap_number": 1,
                "time": lap_start,
                "lap_duration": lap_time,
                "prev_lap": prev_lap,
                "out_lap": lap["is_pit_out_lap"]
            }

            lap_timeline.append(this_lap)
            sector_timer = lap_start

            for s in range(1, 4):
                sector = f'sector_{s}'
                if lap[f'duration_{sector}']:
                    sector_time = lap[f'duration_{sector}']
                else:
                    sector_time = this_lap["lap_duration"] - sum([lap[f'duration_sector_{x}'] for x in range(1,4) if x != s])

                this_sector = {
                    "type": "sector",
                    "time": sector_timer,
                    "sector_number": s,
                    "sector_time": sector_time,
                    "lap_number": this_lap["lap_number"]
                }

                lap_timeline.append(this_sector)

                segments = lap[f'segments_{sector}']
                segment_time = sector_time / len(segments)

                for index, seg in enumerate(segments):
                    this_segment = {
                        "type": "segment",
                        "time": sector_timer,
                        "segment_number": index + 1,
                        "sector_number": s,
                        "lap_number": this_lap["lap_number"]
                    }
                    lap_timeline += this_segment
                    sector_timer += timedelta(seconds=segment_time)



        indexes = {
            'laps': 1,
            'position': 0,
            'intervals': 0,
            'pit': 0
        }

        while any([indexes[j] != 'done' for j in indexes]):
            for key in indexes:
                current_tick = {}
                i = indexes[key]
                if i == 'done':
                    continue
                try:
                    if key == 'laps':
                        time = datetime.fromisoformat(self.session_data[key][i]['date_start'])
                    else:
                        time = datetime.fromisoformat(self.session_data[key][i]['date'])
                except IndexError:
                    indexes[key] = 'done'
                    continue

                if start_time <= time < end_time:
                    current_tick["time"] = start_time
                    current_tick["type"] = key
                    for data in self.session_data[key][i]:
                        if data not in ['date', 'date_start', 'driver_number', 'session_key', 'meeting_key']:
                            current_tick[data] = self.session_data[key][i][data]

                    indexes[key] += 1
                    if indexes[key] >= len(self.session_data[key]):
                        indexes[key] = 'done'
                    self.session_timeline.append(current_tick)
            start_time = end_time
            end_time = start_time + timedelta(milliseconds=100)

    def set_current_data(self, sync_to_time):
        next_event = self.session_timeline[self.timeline_index]
        event_time = next_event["time"]
        if event_time <= sync_to_time:
            match next_event["type"]:
                case "test"; pass
                case "interval":
                    self.current_data["interval"] = next_event["interval"]

