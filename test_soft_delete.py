from db import get_connection, soft_delete_batch

conn = get_connection()
hasil = soft_delete_batch(conn, "B000100")   
print(f"Hasil: {hasil}")
conn.close()