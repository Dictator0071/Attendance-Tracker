import sqlite3

conn = sqlite3.connect('attendance.db')
c = conn.cursor()

c.execute("""
    SELECT *
    FROM attendance a
    WHERE rowid = (
        SELECT MIN(rowid)
        FROM attendance b
        WHERE b.subject = a.subject
    )
""")

rows = c.fetchall()
print(rows)





