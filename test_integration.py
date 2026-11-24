import pytest
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()


"""
Integration test: menguji beberapa fungsi bekerja bersama.
Fokus: alur dari KPI -> Decision Engine -> hasil keputusan.
"""
from decision import DecisionEngine, DecisionStatus


def test_decision_engine_critical_karena_overall_rate():
    """
    Skenario: overall reject rate 5% (di atas 2%).
    Harapan: status CRITICAL.
    """
    # 1. Siapkan KPI (data contoh)
    kpi = {
        "reject_rate": 5.0,
        "worst_reject_rate": 5.0,
    }
    
    # 2. Siapkan analysis dummy (tidak ada prioritas QC)
    class DummyAnalysis:
        prioritas_qc = []  # kosong
    
    # 3. Jalankan decision engine
    engine = DecisionEngine(kpi)
    hasil = engine.evaluate(DummyAnalysis())
    
    # 4. Cek hasil
    assert hasil.status == DecisionStatus.CRITICAL


def test_decision_engine_warning_karena_overall_rate():
    """
    Skenario: overall reject rate 1.5% (antara 1% - 2%).
    Harapan: status WARNING.
    """
    kpi = {
        "reject_rate": 1.5,
        "worst_reject_rate": 1.5,
    }
    
    class DummyAnalysis:
        prioritas_qc = []
    
    engine = DecisionEngine(kpi)
    hasil = engine.evaluate(DummyAnalysis())
    
    assert hasil.status == DecisionStatus.WARNING


def test_decision_engine_good_karena_overall_rate():
    """
    Skenario: overall reject rate 0.5% (di bawah 1%).
    Harapan: status GOOD.
    """
    kpi = {
        "reject_rate": 0.5,
        "worst_reject_rate": 0.5,
    }
    
    class DummyAnalysis:
        prioritas_qc = []
    
    engine = DecisionEngine(kpi)
    hasil = engine.evaluate(DummyAnalysis())
    
    assert hasil.status == DecisionStatus.GOOD


def test_koneksi_database_gateway():
    """test untuk memastikan python bisa connect ke postgresql"""

    try:
        conn = psycopg2.connect(
            host= os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")

        )

        assert conn is not None
        conn.close()

    except Exception as e:
        pytest.fail(f"koneksi ke database gagal: {e}")
def test_tabel_sensor_data_ada():
    """test untuk memastikan tabel sensor data bener2 ada"""
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT EXISTS (
        SELECT FROM information_schema.tables
        WHERE table_name = 'sensor_data');""")

    tabel_ada = cur.fetchone()[0]
    cur.close()
    conn.close()
    assert tabel_ada is True,"tabel sensor_data tidak di temukan"