from db import get_connection, insert_analysis_log

conn = get_connection()
id_baru = insert_analysis_log(conn, "Tes V2", "GOOD", {"x": 1})
print(f"ID: {id_baru}")
conn.close()

# Baru buka koneksi baru untuk cek
conn2 = get_connection()
cur = conn2.cursor()
cur.execute("SELECT * FROM analysis_log")
rows = cur.fetchall()
print(f"Jumlah baris: {len(rows)}")
for row in rows:
    print(row)
conn2.close()