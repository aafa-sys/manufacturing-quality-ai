from analisis import calculate_total_batches
from analisis import calculate_reject_rates


def test_calculate_total_batches_dengan_3_batch():
    """Test: 3 batch harus return 3."""
    data = [
        (1, "BT001", "Kecap", "A", "Line1", 100, 95, 5, "Pass"),
        (2, "BT002", "Kecap", "A", "Line1", 100, 93, 7, "Pass"),
        (3, "BT003", "Kecap", "A", "Line1", 100, 90, 10, "Pass"),
    ]
    hasil = calculate_total_batches(data)
    assert hasil == 3


def test_calculate_total_batches_kosong():
    """Test: list kosong harus return 0."""
    data = []
    hasil = calculate_total_batches(data)
    assert hasil == 0



def test_calculate_reject_rates_normal():
    """Test: 2 batch harus return 2 rate."""
    data = [
        (1, "BT001", "Kecap", "A", "Line1", 100, 100, 10, "Pass"),  # rate = 10%
        (2, "BT002", "Kecap", "A", "Line1", 100, 200, 20, "Pass"),  # rate = 10%
    ]
    hasil = calculate_reject_rates(data)
    assert len(hasil) == 2
    assert hasil[0] == ("BT001", 10.0)
    assert hasil[1] == ("BT002", 10.0)


def test_calculate_reject_rates_skip_actual_nol():
    """Test: batch dengan actual_qty = 0 harus di-skip."""
    data = [
        (1, "BT001", "Kecap", "A", "Line1", 100, 100, 10, "Pass"),
        (2, "BT002", "Kecap", "A", "Line1", 100, 0, 0, "Pass"),  # actual = 0, skip
    ]
    hasil = calculate_reject_rates(data)
    assert len(hasil) == 1  # cuma 1 yang valid


def test_calculate_reject_rates_kosong():
    """Test: list kosong harus return []."""
    data = []
    hasil = calculate_reject_rates(data)
    assert hasil == []


from analisis import find_worst_batch_by_rate


def test_find_worst_batch_by_rate_normal():
    """Test: cari batch dengan reject rate tertinggi."""
    data = [
        (1, "BT001", "Kecap", "A", "Line1", 100, 100, 10, "Pass"),  # 10%
        (2, "BT002", "Kecap", "A", "Line1", 100, 100, 30, "Pass"),  # 30% <- terburuk
        (3, "BT003", "Kecap", "A", "Line1", 100, 100, 20, "Pass"),  # 20%
    ]
    worst_batch, worst_rate, valid_count = find_worst_batch_by_rate(data)
    assert worst_batch[1] == "BT002"
    assert worst_rate == 30.0
    assert valid_count == 3


def test_find_worst_batch_by_rate_kosong():
    """Test: list kosong harus return (None, None, 0)."""
    data = []
    worst_batch, worst_rate, valid_count = find_worst_batch_by_rate(data)
    assert worst_batch is None
    assert worst_rate is None
    assert valid_count == 0

from analisis import normalisasi_batch


def test_normalisasi_bt26g009():
    """A: BT26G009 -> 9."""
    hasil = normalisasi_batch("BT26G009")

    assert hasil == 9


    


def test_normalisasi_b000009():
    """B: B000009 -> 9."""
    hasil = normalisasi_batch("B000009")

    assert hasil == 9


def test_normalisasi_format_sama():
    """E: BT26G009 == B000009."""
    a = normalisasi_batch("BT26G009")
    b = normalisasi_batch("B000009")
    assert a == b


def test_normalisasi_format_aneh():
    """F: format aneh tidak error."""

    hasil = normalisasi_batch("XX999")
    assert hasil == 999

def test_normalisasi_tanpa_angka():
    """F2: input tanpa angka return -1."""
    hasil = normalisasi_batch("XXX")
    assert hasil == -1