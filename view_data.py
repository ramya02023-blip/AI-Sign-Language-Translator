import sqlite3

conn = sqlite3.connect("gestures.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM gestures")

for row in cursor.fetchall():
    print(row)

conn.close()