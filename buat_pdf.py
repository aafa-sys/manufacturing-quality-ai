from fpdf import FPDF
import csv
from datetime import datetime


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
    """Hitung total run, rata-rata biaya, total biaya."""
    if not data:
        return {"total_run": 0, "rata_rata_biaya": 0.0, "total_biaya": 0.0}
    
    biaya_list = [float(row["biaya_idr"]) for row in data]
    
    return {
        "total_run": len(data),
        "rata_rata_biaya": sum(biaya_list) / len(biaya_list),
        "total_biaya": sum(biaya_list),
    }


def bandingkan_versi(data):
    """Bandingkan v2 vs v3."""
    hasil = {}
    for versi in ["v2", "v3"]:
        data_versi = [row for row in data if row["prompt_version"] == versi]
        if not data_versi:
            hasil[versi] = {"jumlah_run": 0, "rata_biaya": 0.0, "rata_batch": 0.0}
            continue
        
        biaya_list = [float(row["biaya_idr"]) for row in data_versi]
        batch_list = [int(row["batch_terdeteksi"]) for row in data_versi]
        
        hasil[versi] = {
            "jumlah_run": len(data_versi),
            "rata_biaya": sum(biaya_list) / len(biaya_list),
            "rata_batch": sum(batch_list) / len(batch_list),
        }
    return hasil


def buat_pdf(stats, perbandingan, filename="laporan_qc.pdf"):
    """Bikin PDF laporan QC."""
    pdf = FPDF()
    pdf.add_page()
    
    # === Judul ===
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "LAPORAN QUALITY CONTROL", ln=True, align="C")
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Tanggal: {datetime.now().strftime('%d %B %Y')}", ln=True, align="C")
    pdf.ln(5)
    
    # === Ringkasan KPI ===
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "1. Ringkasan KPI", ln=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Total Run       : {stats['total_run']}", ln=True)
    pdf.cell(0, 6, f"Rata-rata Biaya : Rp {stats['rata_rata_biaya']:.2f}", ln=True)
    pdf.cell(0, 6, f"Total Biaya     : Rp {stats['total_biaya']:.2f}", ln=True)
    pdf.ln(5)
    
    # === Grafik ===
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "2. Grafik Metrics", ln=True)
    try:
        pdf.image("grafik_metrics.png", x=10, w=190)
    except Exception as e:
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"(Grafik tidak tersedia: {e})", ln=True)
    pdf.ln(5)
    
    # === Perbandingan Versi ===
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "3. Perbandingan Versi Prompt", ln=True)
    
    pdf.set_font("Arial", "", 10)
    for versi, info in perbandingan.items():
        pdf.cell(0, 6,
            f"{versi}: {info['jumlah_run']} run, "
            f"Rp {info['rata_biaya']:.2f}/run, "
            f"{info['rata_batch']:.1f} batch terdeteksi",
            ln=True)
    pdf.ln(5)
    
    # === Rekomendasi ===
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "4. Rekomendasi", ln=True)
    
    pdf.set_font("Arial", "", 10)
    v2_batch = perbandingan["v2"]["rata_batch"]
    v3_batch = perbandingan["v3"]["rata_batch"]
    
    if v3_batch > v2_batch:
        rekomendasi = (
            f"v3 mendeteksi {v3_batch:.1f} batch per run, "
            f"sedangkan v2 hanya {v2_batch:.1f}. "
            f"v3 lebih akurat, disarankan pakai v3 sebagai default."
        )
    else:
        rekomendasi = "v2 dan v3 setara. Pakai yang lebih murah (v2)."
    
    pdf.multi_cell(0, 6, rekomendasi)
    pdf.ln(5)
    
    # === Footer ===
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 6, "Dibuat otomatis oleh Manufacturing Quality AI System", ln=True, align="C")
    
    # Simpan
    pdf.output(filename)
    print(f"PDF disimpan ke {filename}")


if __name__ == "__main__":
    data = baca_runs_csv("runs.csv")
    stats = hitung_statistik(data)
    perbandingan = bandingkan_versi(data)
    buat_pdf(stats, perbandingan)