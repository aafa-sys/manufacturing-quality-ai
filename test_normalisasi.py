import unittest
from unittest.mock import patch
from agent.agent import normalisasi_batch_id

class TestNormalisasiBatch(unittest.TestCase):

    # 1. Test format B biasa
    def test_format_b_angka(self):
        self.assertEqual(normalisasi_batch_id("B1"), "B000001")
        self.assertEqual(normalisasi_batch_id("B01"), "B000001")
        self.assertEqual(normalisasi_batch_id("B000001"), "B000001")
        self.assertEqual(normalisasi_batch_id("  b001  "), "B000001")

    # 2. Test format aneh (harus balik apa adanya)
    def test_format_aneh(self):
        self.assertEqual(normalisasi_batch_id("X001"), "X001")
        self.assertEqual(normalisasi_batch_id(None), None)

    # 3. Test format BT (ini yang pakai database)
    @patch('agent.agent.cari_id_dari_batch_no')
    def test_format_bt_database(self, mock_cari_db):
        #  bohongin: jika fungsi cari_id_dari_batch_no dipanggil, 
        #  balikin dan akan"B000099" tanpa beneran nembak DB   
        mock_cari_db.return_value = "B000099"
        
        hasil = normalisasi_batch_id("BT26G099")
        
        # Cek apakah hasilnya sesuai bohongan kita
        self.assertEqual(hasil, "B000099")
        
        # Cek apakah sistem beneran manggil database pakai ID yang bener
        mock_cari_db.assert_called_once_with("BT26G099")

if __name__ == '__main__':
    unittest.main()