MANUFACTURING QUALITY AI

Sistem analisis kualitas produksi otomatis yang mengintegrasikan PostgreSQL, Google Gemini, dan Decision Layer untuk mendeteksi batch bermasalah pada lini manufaktur. Kini dilengkapi dengan arsitektur container dan sistem AI Agent cerdas.


DESKRIPSI

Sistem ini membantu tim Quality Control (QC) menganalisis data produksi secara otomatis. Saat ini, sistem dapat diakses melalui UI interaktif (Streamlit) di mana AI Agent akan:

1. Membaca data batch produksi dari PostgreSQL
2. Memproses bahasa natural dari user (Natural Language Processing)
3. Memanggil tools (fungsi Python) untuk mengambil data spesifik (Batch, KPI, Reject)
4. Memvalidasi parameter dan memfilter akses berdasarkan Role (Operator/Manager/Admin)
5. Meminta konfirmasi (HITL) sebelum mengeksekusi tindakan berbahaya
6. Menghasilkan laporan dan analisis


FITUR UTAMA

1. Agentic AI (Tool Calling): AI tidak hanya menjawab, tapi bisa mengeksekusi query ke database secara mandiri via tool.
2. Dockerized Architecture: Seluruh sistem (App & DB) berjalan di dalam container menggunakan Docker Compose.
3. Human-in-the-Loop (HITL): Pengaman ganda untuk mencegah AI menghapus data tanpa izin (butuh konfirmasi Ya/Tidak).
4. Dynamic Tool Allowlist: Pembatasan akses level kode (RBAC) berdasarkan role user.
5. Data Persistence: Menggunakan Docker Volumes agar data PostgreSQL aman saat container di-restart.
6. Analisis 100 batch produksi secara otomatis.
7. Decision layer deterministik: CRITICAL / WARNING / GOOD.
8. 29 unit test - lulus semua.
9. Cost tracking: estimasi biaya per panggilan AI.
10. Structured logging (JSON) dengan rotasi file.


TEKNOLOGI

1. Python 3.11 (Di dalam Docker)
2. PostgreSQL (via Docker Image)
3. Google Gemini API (SDK google-genai)
4. Streamlit (UI Chat Interaktif)
5. Docker & Docker Compose
6. Pydantic, psycopg2, tenacity, matplotlib, fpdf2


CARA MENJALANKAN

Prasyarat: Docker Desktop harus terinstal dan berjalan.

1. Clone repositori
git clone https://github.com/aafa-sys/manufacturing-quality-ai.git
cd manufacturing-quality-ai

2. Buat file .env di root folder (Pastikan file ini ada di .gitignore)
DB_USER=postgres
DB_PASSWORD=password_kamu
DB_NAME=manufacturing_ai_system
GEMINI_API_KEY=API_KEY_KAMU

3. Nyalakan sistem dengan Docker
docker compose up -d

4. Akses Web UI di browser: http://localhost:8501

5. (Opsional) Jika ingin menjalankan script Python murni di lokal (legacy):
python pipeline.py


STRUKTUR FOLDER

1. agent/ (Folder utama AI Agent)
   - agent.py (Orkestrator utama LLM & Tool Calling)
   - tools.py (Daftar fungsi yang bisa dipanggil AI)
   - prompts.py (System Prompt / Guardrails)

2. app.py (Web UI Streamlit)
3. Dockerfile & docker-compose.yml (Konfigurasi Container)
4. db.py, config.py, models.py (Konfigurasi & Model Database)
5. main.py, pipeline.py, analisis.py (Script analisis legacy)
6. test_*.py (Kumpulan Unit Test)


ROADMAP

- Sudah: Integrasi PostgreSQL + Gemini AI
- Sudah: Decision layer (CRITICAL/WARNING/GOOD)
- Sudah: PDF report QC & Structured logging
- Sudah: Unit test (29 passed)
- Sudah: AI Agent (Tool Calling, Memory, Guardrails)
- Sudah: Docker Deployment (Docker Compose & Volumes)
- Sudah: Web UI (Streamlit)
- Belum: FastAPI (REST API murni)
- Belum: MQTT / OPC UA integration (IoT)
- Belum: Computer Vision untuk defect detection


AUTHOR

Tofa - admust08@gmail.com
