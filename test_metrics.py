"""Test untuk fungsi catat_metrik_run.
Pakai file temporary (bukan runs.csv asli) biar aman.
"""
import os
import csv
import tempfile
import pytest

from main import catat_metrik_run


@pytest.fixture
def tmp_csv(monkeypatch, tmp_path):
    """
    Fixture: bikin file CSV temporary untuk test.
    Setelah test, otomatis dihapus.
    """
    file_path = tmp_path / "test_runs.csv"
    monkeypatch.chdir(tmp_path)  # pindah working dir ke folder temp
    yield file_path
    # cleanup otomatis oleh tmp_path


def test_file_dibuat_dan_header_ditulis(tmp_csv):
    """Kalau file belum ada, harus dibuat + tulis header."""
    usage = {"input": 13000, "output": 7000, "total": 20000}
    
    catat_metrik_run(
        prompt_version="v2",
        usage=usage,
        total_batch=100,
        batch_terdeteksi=23,
        status="CRITICAL",
    )
    
    # Cek file ada
    assert os.path.exists("runs.csv")
    
    # Cek isi: 1 header + 1 data
    with open("runs.csv", "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
    
    assert len(reader) == 2
    assert reader[0][0] == "timestamp"  # header
    assert reader[1][1] == "v2"          # prompt_version
    assert reader[1][7] == "100"         # total_batch


def test_run_kedua_append(tmp_csv):
    """Kalau file sudah ada, harus append (tambah baris)."""
    usage = {"input": 13000, "output": 7000, "total": 20000}
    
    # Run pertama
    catat_metrik_run("v2", usage, 100, 23, "CRITICAL")
    # Run kedua
    catat_metrik_run("v3", usage, 100, 23, "WARNING")
    
    with open("runs.csv", "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
    
    # Harus 1 header + 2 data = 3 baris
    assert len(reader) == 3
    assert reader[1][1] == "v2"
    assert reader[2][1] == "v3"
    assert reader[2][9] == "WARNING"