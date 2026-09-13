from enum import Enum
from typing import List, Any, Dict
from models import ProductionAnalysis

class DecisionStatus(Enum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    GOOD = "GOOD"

class DecisionResult:
    def __init__(self, status, reasons, priority_batches, recommended_actions):
        self.status = status
        self.reasons = reasons
        self.priority_batches = priority_batches
        self.recommended_actions = recommended_actions

class DecisionEngine:
    def __init__(self, kpi: Dict[str, Any]):
        self.kpi = kpi

    def evaluate(self, analysis: ProductionAnalysis) -> DecisionResult:
        reasons = []
        priority_batches = []
        actions = []

        # Aturan 1: Overall reject rate (dari Python)
        overall_rate = self.kpi.get('reject_rate', 0.0)
        if overall_rate > 5.0:
            status = DecisionStatus.CRITICAL
            reasons.append(f"Overall reject rate {overall_rate:.2f}% > 2%")
            actions.append("Eskalasi ke Production Manager")
        elif overall_rate >= 1.0:
            status = DecisionStatus.WARNING
            reasons.append(f"Overall reject rate {overall_rate:.2f}% di zona warning (1-2%)")
            actions.append("Review proses produksi")
        else:
            status = DecisionStatus.GOOD

        # Aturan 2: Prioritas QC dari AI
        for qc in analysis.prioritas_qc:
            if qc.priority_level == "URGENT":
                status = DecisionStatus.CRITICAL
                priority_batches.append(qc.batch)
                reasons.append(f"Batch {qc.batch} butuh QC URGENT: {qc.reason}")
                actions.append(f"Jadwalkan QC segera untuk batch {qc.batch}")

        # Aturan 3: Worst reject rate dari Python
        worst_rate = self.kpi.get('worst_reject_rate', 0.0)
        if worst_rate > 5.0:
            if status != DecisionStatus.CRITICAL:
                status = DecisionStatus.CRITICAL
            reasons.append(f"Ada batch dengan reject rate {worst_rate:.2f}% (>5%)")
            actions.append("Investigasi akar masalah")

        # Jika tidak ada alasan, berarti GOOD
        if not reasons:
            reasons.append("Semua metrik dalam batas normal")

        return DecisionResult(
            status=status,
            reasons=reasons,
            priority_batches=priority_batches,
            recommended_actions=actions
        )