import datetime

def total_classes(start_date, end_date, schedule_days):
    # schedule_days like ["Monday", "Wednesday", "Friday"]
    total = 0
    current = start_date
    while current <= end_date:
        if current.strftime("%A") in schedule_days:
            total += 1
        current += datetime.timedelta(days=1)
    return total

start = datetime.date(2025, 8, 4)
today = datetime.date(2025, 8, 18)
print(total_classes(start, today, ["Monday", "Wednesday", "Friday"]))

