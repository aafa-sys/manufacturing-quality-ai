"""
Custom exception untuk proyek Manufacturing Quality AI.
Setiap jenis error punya class sendiri, biar mudah di-handle.
"""


class ManufacturingAIError(Exception):
    """Base exception untuk semua error proyek ini."""
    pass


class DatabaseError(ManufacturingAIError):
    """Error saat ada masalah di database."""
    pass


class AIError(ManufacturingAIError):
    """Error saat panggil Gemini atau proses AI."""
    pass


class ValidationError(ManufacturingAIError):
    """Error saat output AI tidak sesuai skema."""
    pass


class DataError(ManufacturingAIError):
    """Error saat data dari DB tidak valid atau kosong."""
    pass