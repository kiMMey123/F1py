import datetime
from turtledemo.penrose import start
from urllib.request import urlopen
import json
import os
from time import sleep
from api_class import F1API
from driver_class import F1Driver
import threading
start_time = datetime.datetime.now()

api = F1API(session_key=9141)
drivers_data = api.get_drivers()
drivers = [F1Driver(d, api) for d in drivers_data]

print("start fetch")
for key in ['laps', 'position', 'intervals', 'pit', 'stints']:
    all_data = api.call_api(key)
    dr_th = [threading.Thread(target=d.set_session_data,args=[all_data, key]) for d in drivers]

    for t in dr_th:
        t.start()

    for t in dr_th:
        t.join()

print("start sort")
dr_th = [threading.Thread(target=d.sort_session_data) for d in drivers]

for t in dr_th:
    t.start()

for t in dr_th:
    t.join()

print("done")