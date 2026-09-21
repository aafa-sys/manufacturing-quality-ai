import csv


def baca_runs_csv(filename):
    """Baca runs.csv, return list of dict."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        print(f"File {filename} tidak ditemukan.")
        return []



def hitung_statistik(data):
    if not data:
        return {"total_run": 0, "rata_rata_biaya": 0.0, "total_biaya": 0.0}
    
    biaya_list = [float(row["biaya_idr"]) for row in data]
    
    total_run = len(data)
    rata_rata = sum(biaya_list) / len(biaya_list)
    total_biaya = sum(biaya_list)
    
    return {
        "total_run": total_run,
        "rata_rata_biaya": rata_rata,
        "total_biaya": total_biaya,
    }

def bandingkan_versi(data):
    """Bandingkan v2 vs v3."""
    hasil = {}
    
    for versi in ["v2", "v3"]:
        # 1. Filter data untuk versi ini
        data_versi = [row for row in data if row["prompt_version"] == versi]
        
        # 2. Kalau kosong, isi 0
        if not data_versi:
            hasil[versi] = {
                "jumlah_run": 0,
                "rata_biaya": 0.0,
                "rata_batch": 0.0,
            }
            continue
        
        # 3. Ambil list biaya dan batch
        biaya_list = [float(row["biaya_idr"]) for row in data_versi]
        batch_list = [int(row["batch_terdeteksi"]) for row in data_versi]
        
        # 4. Hitung
        jumlah_run = len(data_versi)
        rata_biaya = sum(biaya_list) / len(biaya_list)
        rata_batch = sum(batch_list) / len(batch_list)
        
        # 5. Simpan ke hasil
        hasil[versi] = {
            "jumlah_run": jumlah_run,
            "rata_biaya": rata_biaya,
            "rata_batch": rata_batch,
        }
    
    return hasil


def tampilkan_laporan(stats, perbandingan, filename="laporan_metrics.txt"):
    """Tampilkan laporan + simpan ke file."""
    # 1. Buat string laporan
    laporan = f"""
=== LAPORAN METRICS ===

Total Run      : {stats['total_run']}
Rata-rata Biaya: Rp {stats['rata_rata_biaya']:.2f}
Total Biaya    : Rp {stats['total_biaya']:.2f}

--- Perbandingan Versi ---
v2: {perbandingan['v2']['jumlah_run']} run, Rp {perbandingan['v2']['rata_biaya']:.2f}/run, {perbandingan['v2']['rata_batch']:.1f} batch
v3: {perbandingan['v3']['jumlah_run']} run, Rp {perbandingan['v3']['rata_biaya']:.2f}/run, {perbandingan['v3']['rata_batch']:.1f} batch
"""
    # 2. Print ke terminal
    print(laporan)
    
    # 3. Simpan ke file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(laporan)
    
    print(f"Laporan disimpan ke {filename}")



if __name__ == "__main__":
    data = baca_runs_csv("runs.csv")
    print(f"Total baris: {len(data)}")
    if data:
        print("Baris pertama:", data[0])
    stats = hitung_statistik(data)
    print(f"Total run: {stats['total_run']}")
    print(f"Rata-rata biaya: Rp {stats['rata_rata_biaya']:.2f}")
    print(f"Total biaya: Rp {stats['total_biaya']:.2f}")


    print("\n=== Perbandingan v2 vs v3 ===")
    perbandingan = bandingkan_versi(data)
    for versi, info in perbandingan.items():
       print(f"{versi}: {info['jumlah_run']} run, rata-rata Rp {info['rata_biaya']:.2f}, rata batch {info['rata_batch']:.1f}")

    
    data = baca_runs_csv("runs.csv")
    stats = hitung_statistik(data)
    perbandingan = bandingkan_versi(data)
    tampilkan_laporan(stats, perbandingan)
