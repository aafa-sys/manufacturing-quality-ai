"""
Test untuk custom exception.
Memastikan exception bisa di-raise, di-catch, dan inheritance bekerja.
"""
import pytest

from exceptions import (
    ManufacturingAIError,
    DatabaseError,
    AIError,
    ValidationError,
    DataError,
)


def test_database_error_bisa_di_raise():
    """DatabaseError harus bisa di-raise dan di-catch."""
    with pytest.raises(DatabaseError):
        raise DatabaseError("Tidak bisa koneksi")


def test_ai_error_bisa_di_raise():
    """AIError harus bisa di-raise dan di-catch."""
    with pytest.raises(AIError):
        raise AIError("Gemini down")


def test_catch_induk_menangkap_anak():
    """ManufacturingAIError harus bisa menangkap DatabaseError."""
    with pytest.raises(ManufacturingAIError):
        raise DatabaseError("Tidak bisa koneksi")


def test_ai_error_bukan_database_error():
    """AIError BUKAN turunan DatabaseError."""
    with pytest.raises(AIError):
        try:
            raise AIError("Gemini down")
        except DatabaseError:
            # Tidak akan masuk sini
            pass