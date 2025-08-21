import sqlite3
import datetime

conn = sqlite3.connect('attendance.db')
c = conn.cursor()
# x = (datetime.datetime.now()).strftime("%A")
x = "Maths"

c.execute("SELECT * FROM attendance WHERE subject = ? COLLATE NOCASE", (x,))
items = c.fetchall()
for item in items:
    r = list(item)
    print(r[2])
