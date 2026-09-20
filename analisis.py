def calculate_reject_rates(all_batch_data):
    """Menghitung reject rate per batch. Return list of tuples (batch_no, rate)."""
    reject_rates = []
    for row in all_batch_data:
        batch_no = row[1]
        actual_qty = row[6]
        reject_qty = row[7]
        if actual_qty == 0:
            continue
        rate = (reject_qty / actual_qty) * 100
        reject_rates.append((batch_no, rate))
    return reject_rates


def find_worst_batch_by_reject(all_batch_data):
    """Return row batch dengan reject_qty tertinggi."""
    if not all_batch_data:
        return None
    return max(all_batch_data, key=lambda row: row[7])


def find_worst_batch_by_rate(all_batch_data):
    """Return (worst_batch_row, worst_reject_rate, valid_batch_count)."""
    if not all_batch_data:
        return None, None, 0
    worst_batch = None
    worst_rate = None
    valid_count = 0
    for row in all_batch_data:
        actual_qty = row[6]
        reject_qty = row[7]
        if actual_qty == 0:
            continue
        valid_count += 1
        rate = (reject_qty / actual_qty) * 100
        if worst_rate is None or rate > worst_rate: 
            worst_rate = rate
            worst_batch = row
    return worst_batch, worst_rate, valid_count


def calculate_total_batches(all_batch_data):
    return len(all_batch_data)


def calculate_total_reject(all_batch_data):
    return sum(row[7] for row in all_batch_data)


def calculate_total_actual(all_batch_data):
    return sum(row[6] for row in all_batch_data)


def calculate_total_plan(all_batch_data):
    return sum(row[5] for row in all_batch_data)


def calculate_average_reject(total_reject, total_batches):
    if total_batches == 0:
        return 0.0
    return total_reject / total_batches


def calculate_overall_reject_rate(total_reject, total_actual):
    if total_actual == 0:
        return 0.0
    return round((total_reject / total_actual) * 100, 2)


def evaluate_reject_rate(overall_reject_rate):
    if overall_reject_rate > 2:
        return "CRITICAL"
    elif 1 <= overall_reject_rate <= 2:
        return "WARNING"
    else:
        return "GOOD"


def calculate_qc_priority(worst_reject_rate):
    if worst_reject_rate > 5:
        return "URGENT"
    elif worst_reject_rate > 2:
        return "HIGH"
    else:
        return "NORMAL"
def ringkas_reject_detail(reject_detail_data, top_n=3):
    per_batch = {}
    for row in reject_detail_data:
        batch_id = row[0]
        kategori = row[1]
        qty = row[2]
        
        if batch_id not in per_batch:
            per_batch[batch_id] = []
        
        per_batch[batch_id].append((kategori, qty))
    
    hasil = {}
    for batch_id, kategori_list in per_batch.items():
        sorted_list = sorted(kategori_list, key=lambda x: x[1], reverse=True)
        hasil[batch_id] = sorted_list[:top_n]
    
    return hasil
def ringkas_semua_batch(all_batch_data, bottom_n=5):
    """
    Mengubah 100 baris batch menjadi statistik + bottom N reject terendah.
    Top reject tertinggi TIDAK dimasukkan karena sudah ada di 'batch bermasalah'.
    """
    if not all_batch_data:
        return {}
    
    # Ambil semua nilai reject
    reject_qty_list = [row[7] for row in all_batch_data]
    
    # Statistik
    statistik = {
        "total_batch": len(all_batch_data),
        "max_reject": max(reject_qty_list),
        "min_reject": min(reject_qty_list),
        "avg_reject": round(sum(reject_qty_list) / len(reject_qty_list), 2),
    }
    
    # Bottom N (reject terendah)
    sorted_by_reject = sorted(all_batch_data, key=lambda row: row[7])
    bottom_n_batch = [
        {
            "batch": row[1],
            "product": row[2],
            "reject": row[7],
            "actual": row[6]
        }
        for row in sorted_by_reject[:bottom_n]
    ]
    
    return {
        "statistik": statistik,
        "bottom_5_reject_terendah": bottom_n_batch
    }


def normalisasi_batch(batch_str):
    """Ambil 3 digit terakhir. BT26G009 -> 9, B000009 -> 9."""
    return int(batch_str[-3:])



def verifikasi_deteksi_batch(problematic_batches, analysis):
    """
    Cek apakah AI mendeteksi semua batch bermasalah.
    Pakai normalisasi biar format B000009 dan BT26G009 dianggap sama.
    """
    batch_seharusnya = set(normalisasi_batch(row[1]) for row in problematic_batches)
    batch_dideteksi = set(normalisasi_batch(qc.batch) for qc in analysis.prioritas_qc)
    
    hilang = batch_seharusnya - batch_dideteksi
    return len(batch_seharusnya), len(batch_dideteksi), list(hilang)