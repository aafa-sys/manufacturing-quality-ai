import db

def tool_get_batch(batch_id: str) :
    """Mengambil data batch dari database berdasarkan ID."""
    conn = db.get_connection()
    try:
        data = db.fetch_batch(conn, batch_id)
        if not data:
            return f"Batch {batch_id} tidak ditemukan."
        
        return f"Batch: {data[1]}, Produk: {data[3]}, Plan: {data[6]}, Actual: {data[7]}, Reject: {data[8]}, Status: {data[9]}"
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()

TOOLS = [
    {
        "name": "tool_get_batch",
        "function": tool_get_batch, 
        "description": "Ambil data batch berdasarkan ID (contoh: B000001)."
    }
]