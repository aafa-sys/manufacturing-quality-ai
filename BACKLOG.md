# BACKLOG PROYEK (Daftar Pekerjaan Rumah)

Catatan hal-hal yang harus dikerjakan nanti (Technical Debt & Future Features).

## 1. Keamanan (Security)
- [ ] Pindahkan semua hardcoded password di `subscriber_db.py`, `agent/agent.py`, dan `agent/tools.py` ke file `.env`.
- [ ] Pastikan file `.env` sudah masuk ke `.gitignore` (JANGAN sampai ke-commit ke GitHub).
- [ ] Rotate (ganti) password PostgreSQL jika pernah tidak sengaja ter-commit.

## 2. Refactoring (Perapihan Kode)
- [ ] Ubah endpoint FastAPI agar Role (Operator/Manager) diambil dari JWT Token, bukan dari input body request.
- [ ] Update library `pymodbus` ke versi terbaru (SimData) untuk menghindari warning.

## 3. Fitur Selanjutnya
- [ ] Integrasi IoT Gateway (MQTT + OPC UA + Modbus) jadi satu kesatuan di `industrial_data`.
- [ ] Deploy aplikasi ke Cloud/VPS pakai Docker Compose.## Day 334 CLOSED 2026-11-27 
