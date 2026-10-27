import db
from analisis import hitung_kpi

def tool_get_batch(batch_id: str) :

    """Mengambil data batch dari database berdasarkan ID."""
    conn = db.get_connection()
    try:
        data = db.fetch_batch(conn, batch_id)
        if not data:
            return f"Batch {batch_id} tidak ditemukan."
        
        return f"Batch: {data[1]}, Produk: {data[3]}, Plan: {data[6]}, Actual: {data[7]}, Reject: {data[8]}, Status: {data[9]}"
    except Exception as e:
        return f"Error:  {e}"
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


def tool_get_kpi():
    conn = db.get_connection()
    try:
        data = db.fetch_all_batches(conn)
        if not data:
            return f"tidak ada batch yang terdeteksi"
        kpi,_ = hitung_kpi(data)



        return f" daftar kpi produksi keseluruhan : {str(kpi)}"
    except Exception as e:
        return f"Error: {e}"

    finally:
        conn.close()


def tool_analyze_rejects():
    conn = db.get_connection()
    try:
        data = db.fetch_reject_details(conn)
        if not data:
            return f"tidak ada reject"

        rekap ={}
        for row in data:
            kategori = row[1]
            qty = row[2]


            if kategori in rekap:
                rekap[kategori] += qty
            else:
                rekap[kategori] = qty
        hasil_urut = sorted(rekap.items(),key=lambda x: x[1], reverse=True)

        teks = "analisis kategori reject terbanyak:\n"
        for kat,total in hasil_urut:
            teks += f"- {kat}: {total} unit\n"

        return teks
    except Exception as e:
        return f"error analisis {e}"
    finally:
        conn.close()

def tool_generate_report(report_content: str):
    nama_file = "laporan_manufaktur.txt"
    try:
        with open(nama_file, "w",encoding="utf-8") as f:
            f.write(report_content)

        return f"laporan berhasil di simpan di{nama_file}"
    except Exception as e:
        return f"gagal menyimpan laporan {e}"

def tool_send_notification(penerima:str,pesan:str):
    """simulasi mengirim notifikasi (email/wa)"""

    try:

        print(f"[NOTIF] mengirim ke{penerima}: {pesan}")
        return f"notifikasi terkirim ke {penerima}"
    except Exception as e:
        return f"gagal mengirim notifikasi:{e}"

def tool_get_avg_reject():
    conn = db.get_connection()
    try:
        data =db.fetch_all_batches(conn)
        if not data:
            return f"tidak ada reject terdeteksi"

        total_reject = 0
        for row in data:
            total_reject += row[7]



        rata_rata = total_reject / len(data)
        return f" rata_rata reject adalah {rata_rata} "
    except Exception as e:
        return f"gagal menghitung rata_rata {e}"
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


    },


    {
    "name": "tool_get_kpi",
    "function": tool_get_kpi,
    "description": "Ambil dan hitung KPI produksi keseluruhan (total batch, reject rate, dll).",
    "parameters": {},
    "required": []
   },
   {
    "name": "tool_analyze_rejects",
    "function": tool_analyze_rejects,
    "description": "Gunakan ini untuk menganalisis kategori reject apa yang paling sering terjadi dan total unitnya.",
    "parameters": {},
    "required": []
   },

   {
    "name":"tool_generate_report",
    "function": tool_generate_report,
    "description":"membuat laporan otomatis dan di simpan di file yang telah ditentukan.",
    "parameters":{
        "report_content": {
            "type":"string",
            "description":"isi lengkap laporan yang akan di simpan"
        }
    },
    "required": ["report_content"]},

    {"name":"tool_send_notification",
     "function":tool_send_notification,
     "description":"mengirim atau pesanke orang lain",
     "parameters":{
         "penerima":{
             "type": "string",
             "description": "nama atau alamat email penerima"
         },

         "pesan":{
             "type": "string",
             "description": "isi pesan atau laporan yang mau di kirim "}
     },
     "required":["penerima","pesan"]},


    {"name":"tool_get_avg_reject",
     "function": tool_get_avg_reject,
     "description":"di gunakan untuk menghitung rata_rata reject",
     "parameters":{},
     "required": []
    }
]