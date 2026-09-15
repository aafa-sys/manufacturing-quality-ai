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