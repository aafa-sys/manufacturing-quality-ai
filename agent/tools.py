import db

TOOLS = [ ]

def tool_get_batch(batch_id: str) :
    """Fungsi untuk mengambil data batch dari database"""

    conn = db.get_connection()
    try:
        data = db.fetch_batch(conn,batch_id)

        if not data:
            return f"batch{batch_id} tidak di temukan"

        return f"batch:{data[1]}, produk: {data[3]}, plan: {data[6]}, actual: {data[7]}, reject: {data[8]}, status: {data[9]}"

    except Exception as e:
        return f"Error: {e}"

    finally:
        conn.close()

TOOLS =[
    {"name" : "tool_get_batch",
     "funtion" : tool_get_batch,
     "description" : "ambil data batch berdasarkan ID "}
]