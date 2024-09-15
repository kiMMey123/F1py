from api_class import F1API
from driver_class import F1Driver
from datetime import datetime, timedelta
import time
import threading


class F1RaceControl:
    def __init__(self):
        self.api = F1API(session_key=9141)
        self.drivers = self.get_drivers()
        self.session_active = False
        self.race_control = None
        self.sync_time = time.perf_counter()
        self.now_time = None
        self.sync_thread = threading.Thread(target=self.start_sync)

    def get_drivers(self):
        session_drivers = self.api.get_drivers()
        if session_drivers:
            return [F1Driver(d, self.api) for d in session_drivers]

    def set_driver_data(self):
        for key in ['laps', 'position', 'intervals', 'pit', 'stints']:
            all_data = self.api.call_api(key)
            driver_threads = [threading.Thread(target=d.set_session_data, args=[all_data, key]) for d in self.drivers]

            for t in driver_threads:
                t.start()

            for t in driver_threads:
                t.join()

    def start_sync(self):
        ticks = 0
        tick_millis = 200
        tick_seconds = tick_millis / 1000
        control_sync = time.perf_counter()

        while self.session_active:
            ticks += 1
            self.sync_time += tick_seconds
            time.sleep(tick_seconds)

            if ticks >= 25:
                drift = time.perf_counter() - (control_sync + (tick_seconds * ticks))
                ticks = 0
                print("drifted", drift)
                self.sync_time = self.sync_time + drift
                control_sync = time.perf_counter()


        done = time.perf_counter()
        drift = self.sync_time - done
        print(f'drift: {drift:.6f} s - sync: {self.sync_time} - actual: {done}')


    def start_race(self):
        self.sync_thread.start()

if __name__ == "__main__":
    controller = F1RaceControl()
    # controller.start_race()