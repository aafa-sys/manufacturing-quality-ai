from db import get_connection

conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT * FROM analysis_log")
rows = cur.fetchall()
print(f"Jumlah baris: {len(rows)}")
for row in rows:
    print(row)
conn.close()