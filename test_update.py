from db import get_connection, update_batch

conn = get_connection()

# Test update batch yang ada
hasil = update_batch(conn, "B000101", 998, 2, "PASS")
print(f"Hasil update: {hasil}")

# Test update batch yang TIDAK ada
hasil2 = update_batch(conn, "B999999", 100, 0, "PASS")
print(f"Hasil update tidak ada: {hasil2}")

conn.close()