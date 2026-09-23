import matplotlib.pyplot as plt
import csv
import os


def baca_runs_csv(filename):
    """Baca runs.csv, return list of dict."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        print(f"File {filename} tidak ditemukan.")
        return []


def buat_grafik(data):
    """Bikin 3 grafik dari data runs.csv."""
    if not data:
        print("Data kosong, tidak bisa bikin grafik.")
        return
    
    # Siapkan data
    nomor_run = list(range(1, len(data) + 1))
    biaya_list = [float(row["biaya_idr"]) for row in data]
    
    # Siapkan figure dengan 3 subplot
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    # === Grafik 1: Line chart biaya per run ===
    axes[0].plot(nomor_run, biaya_list, marker="o", color="blue")
    axes[0].set_title("Biaya per Run")
    axes[0].set_xlabel("Nomor Run")
    axes[0].set_ylabel("Biaya (Rp)")
    axes[0].grid(True)
    
    # === Grafik 2 & 3: Bar chart v2 vs v3 ===
    # Hitung rata-rata per versi
    v2_biaya = [float(row["biaya_idr"]) for row in data if row["prompt_version"] == "v2"]
    v3_biaya = [float(row["biaya_idr"]) for row in data if row["prompt_version"] == "v3"]
    
    v2_batch = [int(row["batch_terdeteksi"]) for row in data if row["prompt_version"] == "v2"]
    v3_batch = [int(row["batch_terdeteksi"]) for row in data if row["prompt_version"] == "v3"]
    
    rata_v2_biaya = sum(v2_biaya) / len(v2_biaya) if v2_biaya else 0
    rata_v3_biaya = sum(v3_biaya) / len(v3_biaya) if v3_biaya else 0
    
    rata_v2_batch = sum(v2_batch) / len(v2_batch) if v2_batch else 0
    rata_v3_batch = sum(v3_batch) / len(v3_batch) if v3_batch else 0
    
    # Grafik 2: Rata-rata biaya
    axes[1].bar(["v2", "v3"], [rata_v2_biaya, rata_v3_biaya], color=["orange", "green"])
    axes[1].set_title("Rata-rata Biaya per Versi")
    axes[1].set_ylabel("Biaya (Rp)")
    
    # Grafik 3: Rata-rata batch terdeteksi
    axes[2].bar(["v2", "v3"], [rata_v2_batch, rata_v3_batch], color=["orange", "green"])
    axes[2].set_title("Rata-rata Batch Terdeteksi")
    axes[2].set_ylabel("Jumlah Batch")
    
    # Rapikan layout
    plt.tight_layout()
    
    # Simpan ke file
    plt.savefig("grafik_metrics.png", dpi=100)
    print("Grafik disimpan ke grafik_metrics.png")
    
    

if __name__ == "__main__":
    data = baca_runs_csv("runs.csv")
    buat_grafik(data)