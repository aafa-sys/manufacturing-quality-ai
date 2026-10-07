from db import get_connection, fetch_analysis

conn = get_connection()
data = fetch_analysis(conn, 1)
print("Data:", data)
conn.close()
