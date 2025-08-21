import datetime
import sqlite3
conn = sqlite3.connect('attendance.db')
c = conn.cursor()
def total_classes(start_date, end_date, subject):
    # schedule_days like ["Monday", "Wednesday", "Friday"]
    c.execute("Select * FROM attendance WHERE subject = ?", (subject,))
    items = c.fetchall()
    conn.commit()
    schedule = []
    for item in items:
        schedule.append(item[2])
    total = 0
    current = start_date
    while current <= end_date:
        if current.strftime("%A") in schedule:
            total += 1
        current += datetime.timedelta(days=1)
    return total

start = datetime.date(2025, 8, 4)
today = datetime.date(2025, 8, 22)

c.execute("Select * from attendance")
items = c.fetchall()
c.execute(f"UPDATE attendance SET classes_held = ? WHERE subject =?", (0, 'Maths'))
conn.commit()

