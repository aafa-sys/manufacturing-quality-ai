Manufacturing Quality AI

Sistem analisis kualitas produksi otomatis yang mengintegrasikan PostgreSQL, Google Gemini, dan decision layer untuk mendeteksi batch bermasalah pada lini manufaktur.

Deskripsi

Sistem ini membantu tim Quality Control (QC) menganalisis data produksi secara otomatis. Setiap kali dijalankan, sistem akan:

1. Membaca data batch produksi dari PostgreSQL
2. Menghitung KPI kualitas (reject rate, total reject, worst batch)
3. Mengirim data ke Google Gemini untuk analisis AI
4. Memvalidasi output AI dengan Pydantic
5. Menentukan keputusan (CRITICAL / WARNING / GOOD)
6. Menyimpan hasil keputusan ke database
7. Menghasilkan laporan PDF otomatis
8. Mencatat metrik biaya per panggilan AI

Fitur

· Analisis 100 batch produksi secara otomatis
· Deteksi batch bermasalah berdasarkan reject quantity dan reject rate
· Analisis AI dengan Google Gemini
· Validasi output AI dengan Pydantic
· Decision layer deterministik: CRITICAL / WARNING / GOOD
· Simpan log keputusan ke tabel decision_log di PostgreSQL
· PDF report QC otomatis dengan header profesional
· Grafik metrics (matplotlib) — bar, pie, line chart
· Pipeline orchestrator — satu perintah, semua jalan
· Cost tracking — estimasi biaya per panggilan AI
· Retry otomatis saat API gagal
· Structured logging (JSON) dengan rotasi file
· 22 unit test — lulus semua

Teknologi

· Python 3.13
· PostgreSQL
· Google Gemini API
· Pydantic
· psycopg2
· tenacity
· python-dotenv
· matplotlib
· fpdf2
· Power BI (dashboard visualisasi)

Cara Menjalankan

1. Clone repositori

git clone https://github.com/aafa-sys/manufacturing-quality-ai.git
cd manufacturing-quality-ai

2. Install dependency

pip install python-dotenv psycopg2-binary google-genai pydantic tenacity matplotlib fpdf2 pytest

3. Buat file .env di root folder

DB_HOST=localhost
DB_PORT=5432
DB_NAME=masystem
DB_USER=postgres
DB_PASSWORD=password_kamu
GEMINI_API_KEY=API_KEY_KAMU

4. Jalankan program

python main.py

Atau jalankan pipeline lengkap (analisis + metrics + grafik + PDF):

python pipeline.py

5. Jalankan test

python -m pytest -v

Struktur Folder

manufacturing_ai/

· main.py                    (Orchestrator utama)
· config.py                  (Baca .env)
· db.py                      (Koneksi & query database)
· analisis.py                (Perhitungan KPI)
· models.py                  (Pydantic models)
· decision.py                (Decision layer)
· action.py                  (Action dispatcher)
· exceptions.py              (Custom exception)
· logger_config.py           (Structured logging JSON)
· buat_pdf.py                (PDF report generation)
· grafik.py                  (Visualisasi metrics)
· analisis_metrics.py        (Analisis runs.csv)
· pipeline.py                (Pipeline orchestrator)
· test_analisis.py           (Unit test)
· test_integration.py        (Integration test)
· test_error_handling.py     (Error handling test)
· test_metrics.py            (Metrics test)
· prompts/                   (Prompt template versioned)
· services/                  (llm_service.py - Integrasi Gemini)
· logs/                      (Log output)

Output

Setiap kali dijalankan, sistem menghasilkan:

· Terminal log — JSON terstruktur
· logs/app.log — arsip log dengan rotasi
· runs.csv — metrik setiap run (token, biaya, status)
· laporan_qc.pdf — laporan QC produksi profesional
· grafik_batch.png — visualisasi batch bermasalah
· decision_log — tabel database berisi keputusan

Test

· 22 unit test — lulus semua
· Jalankan: python -m pytest -v

Roadmap

☑ Integrasi PostgreSQL + Gemini AI
☑ Decision layer (CRITICAL/WARNING/GOOD)
☑ PDF report QC
☑ Structured logging (JSON)
☑ Unit test (22 passed)
☐ FastAPI (REST API)
☐ Docker deployment
☐ AI Agent (LangGraph)
☐ MQTT / OPC UA integration
☐ Computer Vision untuk defect detection

Author

Tofa — admust08@gmail.com