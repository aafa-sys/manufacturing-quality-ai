from db import get_connection, insert_analysis_log

conn = get_connection()
id_baru = insert_analysis_log(conn, "Tes", "GOOD", {"total_batch": 100})
print(f"ID baru: {id_baru}")
conn.close()