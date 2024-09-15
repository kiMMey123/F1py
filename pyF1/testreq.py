from datetime import timedelta, datetime
sector_time = timedelta(seconds=(63.958 / 12))
print(sector_time)
second = timedelta(seconds=63.958)
print(second)

lap_1 = datetime.fromisoformat('2023-07-30T13:03:46+00:00')
lap_2 = datetime.fromisoformat('2023-07-30T13:05:41.722000+00:00')

print(lap_2 + timedelta(seconds=15))

print(timedelta(seconds=113.103).total_seconds())

for s in range(1, 4):
    print([f'yo: {x}' for x in range(1,4) if x != s])