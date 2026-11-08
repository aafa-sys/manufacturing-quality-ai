# 1. Pakai Linux dasar yang udah ada Python 3.11
FROM python:3.11-slim

# 2. Bikin folder kerja di dalam Linux
WORKDIR /app

# 3. Copy daftar belanjaan (requirements) ke dalam kardus
COPY requirements.txt .

# 4. Install semua library di dalam kardus (kayak pip install)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy semua kode  dari laptop ke dalam kardus
COPY . .

# 6. Kasih tau kalo aplikasi ini pakai port 8501 (port Streamlit)
EXPOSE 8501

# 7. Perintah buat ngejalanin aplikasinya pas kardus dibuka
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]