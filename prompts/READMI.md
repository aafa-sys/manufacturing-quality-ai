# Prompt Versions

Dokumentasi versi prompt yang dipakai di proyek ini.

## Cara Ganti Versi

Ubah di file `.env`:

    PROMPT_VERSION=v2

## Daftar Versi

### v2_quality_analysis.txt (Aktif)

- Tanggal: 14 September 2026
- Perubahan: Perkuat aturan kelengkapan deteksi batch
- Hasil: AI deteksi 23 batch (sebelumnya cuma 6)
- Catatan: Temperature 0.0 untuk konsistensi

### v1_quality_analysis.txt (Arsip)

- Tanggal: 13 September 2026
- Catatan: Versi awal, prompt langsung di main.py
- Masalah: AI sering lewatkan batch bermasalah