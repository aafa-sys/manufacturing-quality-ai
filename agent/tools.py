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



def tool_get_problematic(threshold :int = 20):
    "mengaambil batch bermasalah dengan reject di atas 20 bisa dicustom thresholdnya"
    conn = db.get_connection()

    try:
        

        data = db.fetch_problematic_batches(conn,threshold)
        if not data:
            return f"tidak ada batch bermasalah > {threshold} "

        daftar_batch = []
        for row in data:
            teks = f" batch_no {row[1]}, produk {row[2]}, reject {row[7]}"
            daftar_batch.append(teks)

        hasil = f"ditemukan {len(data)} batch bermaslah(reject > {threshold}):\n"
        hasil += "\n".join(daftar_batch)

        return hasil
        

      
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()

TOOLS = [
    {
        "name": "tool_get_batch",
        "function": tool_get_batch,
        "description": "Ambil data batch berdasarkan ID.",
        "parameters": {
            "batch_id": {
                "type": "string", 
                "description": "ID batch, contoh: B000001."
            }
        },
        "required": ["batch_id"]
    },
    {
        "name": "tool_get_problematic",
        "function": tool_get_problematic,
        "description": "Ambil semua batch bermasalah dengan reject di atas threshold.",
        "parameters": {
            "threshold": {
                "type": "integer", 
                "description": "Batas minimal reject."
            }
        },
        "required": []  # Kosong karena parameter threshold di fungsi punya default (= 20)
    }
]