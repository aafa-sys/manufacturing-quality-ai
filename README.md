"Manufacturing Quality AI"

Sistem analisis kualitas produksi otomatis yang mengintegrasikan PostgreSQL, Google Gemini, dan decision layer untuk mendeteksi batch bermasalah pada lini manufaktur.

---Deskripsi---

Sistem ini membantu tim Quality Control (QC) dalam menganalisis data produksi secara otomatis. Setiap kali dijalankan, sistem akan:

1. Membaca data batch produksi dari PostgreSQL
2. Menghitung KPI kualitas (reject rate, total reject, worst batch)
3. Mengirim data ke Google Gemini untuk analisis AI
4. Memvalidasi output AI dengan Pydantic
5. Menentukan keputusan (CRITICAL / WARNING / GOOD)
6. Menyimpan hasil keputusan ke database
7. Menampilkan laporan dan estimasi biaya AI

---Fitur---

- Analisis 100 batch produksi secara otomatis
- Deteksi batch bermasalah berdasarkan reject quantity dan reject rate
- Analisis AI dengan Google Gemini
- Validasi output AI dengan Pydantic
- Decision layer: CRITICAL / WARNING / GOOD
- Simpan log keputusan ke tabel decision_log di PostgreSQL
- Dashboard Power BI terhubung ke PostgreSQL
- Cost tracking (estimasi biaya per panggilan AI)
- Retry otomatis saat API gagal
- Logging dengan rotasi file

 ---Teknologi---

- Python 3.13
- PostgreSQL
- Google Gemini API
- Pydantic
- psycopg2
- tenacity
- python-dotenv
- Power BI

---Cara Menjalankan---

1. Clone repositori ini:
   git clone https://github.com/tofa/manufacturing-quality-ai.git
   cd manufacturing-quality-ai

2. Install dependency:
   pip install python-dotenv psycopg2 google-genai pydantic tenacity

3. Buat file .env di root folder:
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=masystem
   DB_USER=postgres
   DB_PASSWORD=password_kamu
   GEMINI_API_KEY=API_KEY_KAMU

4. Jalankan program:
   python main.py

---Struktur Folder---

- main.py           (Orchestrator utama)
- config.py         (Baca .env)
- db.py             (Koneksi & query database)
- analysis.py       (Perhitungan KPI)
- models.py         (Pydantic models)
- decision.py       (Decision layer)
- actions.py        (Action dispatcher)
- services/llm_service.py  (Integrasi Gemini)

---Author---

Tofa - admust08@gmail.com