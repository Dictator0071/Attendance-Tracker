import sqlite3

conn = sqlite3.connect('attendance.db')
c = conn.cursor()

c.execute("SELECT * FROM attendance")
items = c.fetchall()
for item in items:
    print(item[0])
