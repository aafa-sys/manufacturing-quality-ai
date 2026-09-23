import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
from db import get_connection, fetch_problematic_batches

# Warna profesional
C_NAVY = (31, 56, 100)
C_RED = (192, 0, 0)
C_ORANGE = (237, 125, 49)
C_GREEN = (112, 173, 71)
C_LIGHT = (245, 245, 245)


def ambil_decision(conn):
    """Ambil 1 decision terbaru dari database."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT created_at, status, summary, kpi_snapshot
            FROM decision_log ORDER BY id DESC LIMIT 1
        """)
        row = cur.fetchone()
        if not row:
            return None
        return {
            "created_at": row[0],
            "status": row[1],
            "summary": row[2],
            "kpi": row[3] if row[3] else {},
        }


def bikin_grafik(batches, filename="grafik_batch.png"):
    """Grafik bar: reject per batch."""
    batch_no = [row[1] for row in batches[:10]]
    reject_qty = [row[7] for row in batches[:10]]
    
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(batch_no, reject_qty, color="#C00000", edgecolor="white")
    ax.set_title("Top 10 Batch Reject Tertinggi", fontsize=13, fontweight="bold", color="#1F3864")
    ax.set_xlabel("Batch")
    ax.set_ylabel("Reject Quantity")
    plt.xticks(rotation=45, ha="right")
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width()/2, h + 0.5, f"{int(h)}",
                ha="center", fontsize=9, fontweight="bold")
    plt.tight_layout()
    plt.savefig(filename, dpi=120, bbox_inches="tight")
    plt.close()
    return filename


def kotak_kpi(pdf, x, y, w, h, label, value, color):
    """Gambar 1 kotak KPI."""
    r, g, b = color
    # Background abu muda
    pdf.set_fill_color(*C_LIGHT)
    pdf.rect(x, y, w, h, "F")
    # Border kiri warna
    pdf.set_fill_color(r, g, b)
    pdf.rect(x, y, 2, h, "F")
    # Label
    pdf.set_xy(x + 4, y + 2)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(w - 4, 4, label.upper())
    # Value
    pdf.set_xy(x + 4, y + 7)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(r, g, b)
    pdf.cell(w - 4, 8, str(value))


def buat_pdf(decision, batches, filename="laporan_qc.pdf"):
    """Bikin PDF laporan QC."""
    pdf = FPDF()
    pdf.add_page()
    
    kpi = decision["kpi"]
    
    # ============ HEADER ============
    pdf.set_fill_color(*C_NAVY)
    pdf.rect(0, 0, 210, 22, "F")
    pdf.set_xy(10, 5)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 8, "LAPORAN QC PRODUKSI", ln=True, align="C")
    pdf.set_xy(10, 14)
    pdf.set_font("Helvetica", "", 9)
    tanggal = decision["created_at"].strftime("%d %B %Y, %H:%M") if decision["created_at"] else "-"
    pdf.cell(0, 5, f"Tanggal: {tanggal}", ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(28)
    
    # ============ KPI CARDS (4 kotak) ============
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*C_NAVY)
    pdf.cell(0, 7, "1. RINGKASAN KPI PRODUKSI", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(1)
    
    y = pdf.get_y()
    w = 46
    h = 18
    kotak_kpi(pdf, 10, y, w, h, "Total Batch", kpi.get("total_batch", "-"), C_NAVY)
    kotak_kpi(pdf, 58, y, w, h, "Total Reject", kpi.get("total_reject", "-"), C_RED)
    kotak_kpi(pdf, 106, y, w, h, "Reject Rate", f"{kpi.get('reject_rate', '-')}%", C_ORANGE)
    kotak_kpi(pdf, 154, y, w, h, "Status", kpi.get("reject_status", "-"), C_GREEN)
    
    pdf.set_y(y + h + 4)
    
    # ============ GRAFIK ============
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*C_NAVY)
    pdf.cell(0, 7, "2. GRAFIK BATCH BERMASALAH", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.image(bikin_grafik(batches), x=12, w=185)
    pdf.ln(2)
    
    # ============ TABEL BATCH ============
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*C_NAVY)
    pdf.cell(0, 7, f"3. DAFTAR BATCH BERMASALAH ({len(batches)} BATCH)", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(1)
    
    # Header tabel
    pdf.set_fill_color(*C_NAVY)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(10, 7, "No", border=1, fill=True, align="C")
    pdf.cell(35, 7, "Batch No", border=1, fill=True, align="C")
    pdf.cell(50, 7, "Produk", border=1, fill=True, align="C")
    pdf.cell(22, 7, "Reject", border=1, fill=True, align="C")
    pdf.cell(22, 7, "Actual", border=1, fill=True, align="C")
    pdf.cell(22, 7, "Rate (%)", border=1, fill=True, align="C")
    pdf.cell(25, 7, "Status QC", border=1, fill=True, align="C")
    pdf.ln()
    
    # Isi tabel
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 8)
    
    for i, row in enumerate(batches[:15], 1):
        batch_no = row[1]
        product = row[2][:28]
        reject_qty = row[7]
        actual_qty = row[6]
        rate = (reject_qty / actual_qty * 100) if actual_qty > 0 else 0
        status = row[8] if len(row) > 8 else "-"
        
        fill = (i % 2 == 0)
        pdf.set_fill_color(248, 248, 248)
        
        pdf.cell(10, 6, str(i), border=1, fill=fill, align="C")
        pdf.cell(35, 6, batch_no, border=1, fill=fill)
        pdf.cell(50, 6, product, border=1, fill=fill)
        pdf.cell(22, 6, str(reject_qty), border=1, fill=fill, align="C")
        pdf.cell(22, 6, str(actual_qty), border=1, fill=fill, align="C")
        pdf.cell(22, 6, f"{rate:.2f}", border=1, fill=fill, align="C")
        pdf.cell(25, 6, str(status), border=1, fill=fill, align="C")
        pdf.ln()
    
    if len(batches) > 15:
        pdf.set_font("Helvetica", "I", 8)
        pdf.cell(0, 5, f"... dan {len(batches) - 15} batch lainnya.", ln=True)
    pdf.ln(3)
    
    # ============ KEPUTUSAN ============
    status = decision["status"]
    warna_status = C_RED if status == "CRITICAL" else (C_ORANGE if status == "WARNING" else C_GREEN)
    
    pdf.set_fill_color(*warna_status)
    pdf.rect(10, pdf.get_y(), 190, 12, "F")
    pdf.set_xy(10, pdf.get_y() + 3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 6, f"KEPUTUSAN: {status}", align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(14)
    
    # ============ KESIMPULAN AI ============
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*C_NAVY)
    pdf.cell(0, 7, "4. KESIMPULAN AI", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_fill_color(240, 248, 255)
    pdf.multi_cell(0, 5, decision["summary"] or "-", fill=True)
    pdf.ln(3)
    
    # ============ REKOMENDASI ============
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*C_NAVY)
    pdf.cell(0, 7, "5. REKOMENDASI AKSI", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9)
    
    if status == "CRITICAL":
        rekomendasi = [
            "1. Segera investigasi batch dengan reject tertinggi.",
            "2. Periksa material dari supplier terkait.",
            "3. Review setting mesin di line bermasalah.",
            "4. Dokumentasikan temuan dan tindakan korektif.",
        ]
    elif status == "WARNING":
        rekomendasi = [
            "1. Pantau batch bermasalah dalam 24 jam.",
            "2. Review proses produksi shift terkait.",
            "3. Siapkan tindakan preventif.",
        ]
    else:
        rekomendasi = ["Semua metrik dalam batas normal. Lanjutkan produksi."]
    
    for r in rekomendasi:
        pdf.cell(0, 5, f"   {r}", ln=True)
    
    # ============ FOOTER ============
    pdf.set_y(-15)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, "Dibuat otomatis oleh Manufacturing Quality AI System | Confidential", align="C")
    
    pdf.output(filename)
    print(f"PDF disimpan ke {filename}")


if __name__ == "__main__":
    conn = get_connection()
    try:
        decision = ambil_decision(conn)
        if not decision:
            print("Tidak ada data di decision_log.")
        else:
            batches = fetch_problematic_batches(conn)
            buat_pdf(decision, batches)
    finally:
        conn.close()