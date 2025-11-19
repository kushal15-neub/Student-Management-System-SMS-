import sqlite3
import os
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.sqlite3')
print('Using DB:', db_path)
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("PRAGMA table_info('student_subject')")
rows = cur.fetchall()
for r in rows:
    print(r)
conn.close()
