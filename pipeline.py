import subprocess
import sys
import time


def jalankan_script(nama_file, max_retry=3):
    """Jalankan script Python, retry kalau gagal."""
    for attempt in range(1, max_retry + 1):
        print(f"\n=== Menjalankan {nama_file} (percobaan {attempt}/{max_retry}) ===")
        hasil = subprocess.run(
            [sys.executable, nama_file],
            capture_output=False,
        )
        
        if hasil.returncode == 0:
            print(f" {nama_file} berhasil.")
            return True
        else:
            print(f" {nama_file} gagal (kode: {hasil.returncode}).")
            if attempt < max_retry:
                print(f"   Menunggu 5 detik sebelum retry...")
                time.sleep(5)
    
    print(f" {nama_file} gagal setelah {max_retry} percobaan.")
    return False


def main():
    print("=" * 50)
    print("PIPELINE MANUFACTURING QUALITY AI")
    print("=" * 50)
    
    scripts = [
        "main.py",
        "analisis_metrics.py",
        "grafik.py",
        "buat_pdf.py",
    ]
    
    for script in scripts:
        sukses = jalankan_script(script)
        if not sukses:
            print(f"\n Pipeline berhenti di {script}.")
            print("Perbaiki dulu, baru jalankan ulang pipeline.")
            return
    
    print("\n" + "=" * 50)
    print(" PIPELINE SELESAI!")
    print("=" * 50)


if __name__ == "__main__":
    main()