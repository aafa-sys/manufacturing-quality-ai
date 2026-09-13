from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class RejectRateItem(BaseModel):
    batch: str
    reject_rate: float = Field(..., ge=0)

class BatchRejectHighest(BaseModel):
    batch: str
    product: str
    reject_quantity: int = Field(..., ge=0)
    actual_quantity: int = Field(..., ge=0)
    reject_reason: str
    qc_status: str

class BatchRejectRateHighest(BaseModel):
    batch: str
    reject_rate: float = Field(..., ge=0)
    reject_quantity: int
    actual_quantity: int

class QCPriority(BaseModel):
    batch: str
    reason: str
    priority_level: Literal["URGENT", "HIGH", "NORMAL"]

class ProductionPattern(BaseModel):
    facts: List[str]
    analysis: List[str]
    assumptions: List[str]

class ProductionAnalysis(BaseModel):
    batch_reject_tertinggi: List[BatchRejectHighest]
    reject_rate_setiap_batch: List[RejectRateItem]
    batch_reject_rate_tertinggi: List[BatchRejectRateHighest]
    prioritas_qc: List[QCPriority]
    pola_produksi: ProductionPattern
    kesimpulan: str