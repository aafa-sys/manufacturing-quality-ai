import logging
import os
from dotenv import load_dotenv

from db import (
    get_connection,
    fetch_all_batches,
    fetch_reject_details,
    fetch_problematic_batches,
)
from analisis import (
    calculate_reject_rates,
    find_worst_batch_by_reject,
    find_worst_batch_by_rate,
    calculate_total_batches,
    calculate_total_reject,
    calculate_total_actual,
    calculate_total_plan,
    calculate_average_reject,
    calculate_overall_reject_rate,
    evaluate_reject_rate,
    calculate_qc_priority,
    ringkas_reject_detail,
    ringkas_semua_batch,
    verifikasi_deteksi_batch
)
from services.llm_service import LLMService
from models import ProductionAnalysis
from decision import DecisionEngine
from action import ActionDispatcher
from logging.handlers import RotatingFileHandler

# Setup logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            'app.log',
            maxBytes=5 * 1024 * 1024,   # 5 MB per file
            backupCount=3,               # simpan 3 file lama (app.log.1, .2, .3)
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()


def build_prompt(all_batch_data, problematic_batches, reject_detail_data, reject_rates, kpi):
    """
    Membangun prompt untuk Gemini. Prompt meminta output JSON
    dengan struktur yang sesuai dengan models.py.
    """
    prompt = f"""
Kamu adalah AI Quality Analyst untuk sistem manufacturing.

Gunakan DATA di bawah ini sebagai satu-satunya sumber kebenaran.
Jangan mengarang angka. Jangan menghitung ulang. Gunakan apa adanya.

=== KPI ===
{kpi}

=== DATA BATCH BERMASALAH (reject_qty > 19) ===
{problematic_batches}

=== DATA SEMUA BATCH ===
{all_batch_data}

=== REJECT RATE SETIAP BATCH ===
{reject_rates}

=== DATA REJECT DETAIL ===
{reject_detail_data}

=== TUGAS ===
Kembalikan HANYA JSON dengan struktur berikut (tanpa teks tambahan):

{{
  "batch_reject_tertinggi": [
    {{
      "batch": "string",
      "product": "string",
      "reject_quantity": 0,
      "actual_quantity": 0,
      "reject_reason": "string",
      "qc_status": "string"
    }}
  ],
  "reject_rate_setiap_batch": [
    {{ "batch": "string", "reject_rate": 0.0 }}
  ],
  "batch_reject_rate_tertinggi": [
    {{
      "batch": "string",
      "reject_rate": 0.0,
      "reject_quantity": 0,
      "actual_quantity": 0
    }}
  ],
  "prioritas_qc": [
    {{
      "batch": "string",
      "reason": "string",
      "priority_level": "URGENT"
    }}
  ],
  "pola_produksi": {{
    "facts": ["..."],
    "analysis": ["..."],
    "assumptions": ["..."]
  }},
  "kesimpulan": "string"
}}

ATURAN:
- "priority_level" HANYA boleh: "URGENT", "HIGH", atau "NORMAL".
- "reject_rate_setiap_batch" harus memuat SEMUA batch dari data.
- Jangan menambah atau mengurangi field.
- Jangan membungkus JSON dengan markdown.
ATURAN KELENGKAPAN (WAJIB):
- WAJIB deteksi SEMUA batch dengan reject_qty > 19.
- JANGAN lewatkan batch apa pun, meskipun hanya 1.
- Setiap batch yang memenuhi kriteria HARUS masuk ke "prioritas_qc".
- Jika ada 6 batch bermasalah, tulis 6. Jika 10, tulis 10.
- Jangan berhenti di 2 atau 3 batch saja.
- Verifikasi ulang sebelum menjawab: hitung jumlah batch yang kamu tulis, 
  pastikan sama dengan jumlah di "DATA BATCH BERMASALAH.
"""
   

    return prompt
    


def main():
    # 1. Buka koneksi database
    conn = get_connection()
    try:
        # 2. Ambil data
        all_batch_data = fetch_all_batches(conn)
        reject_detail_data = fetch_reject_details(conn)
        problematic_batches = fetch_problematic_batches(conn)

        # 3. Hitung KPI
        reject_rates = calculate_reject_rates(all_batch_data)
        total_batches = calculate_total_batches(all_batch_data)
        total_reject = calculate_total_reject(all_batch_data)
        total_actual = calculate_total_actual(all_batch_data)
        total_plan = calculate_total_plan(all_batch_data)
        avg_reject = calculate_average_reject(total_reject, total_batches)
        overall_rate = calculate_overall_reject_rate(total_reject, total_actual)
        status = evaluate_reject_rate(overall_rate)

        worst_batch_qty = find_worst_batch_by_reject(all_batch_data)
        worst_batch_rate, worst_rate_value, valid_count = find_worst_batch_by_rate(all_batch_data)
        qc_priority = calculate_qc_priority(worst_rate_value)

        kpi = {
            "total_batch": total_batches,
            "total_reject": total_reject,
            "total_actual": total_actual,
            "total_plan": total_plan,
            "avg_reject": avg_reject,
            "reject_rate": overall_rate,
            "reject_status": status,
            "qc_priority": qc_priority,
            "worst_reject_rate": worst_rate_value if worst_rate_value else 0.0,
        }

        logger.info("=== KPI DIHITUNG ===")
        logger.info(f"Total Batch: {total_batches} | Total Reject: {total_reject}")
        logger.info(f"Overall Rate: {overall_rate}% | Status: {status}")

        # 4. Bangun prompt
        prompt = build_prompt(
            all_batch_data,
            problematic_batches,
            ringkas_reject_detail(reject_detail_data),
            reject_rates,
            kpi,
        )

        # 5. Panggil Gemini
        llm = LLMService()
        logger.info("Memanggil Gemini...")
        raw_json = llm.generate_structured_json(prompt)

        # 6. Validasi dengan Pydantic
        try:
            analisis = ProductionAnalysis(**raw_json)
            logger.info("Validasi Pydantic: OK")
        except Exception as e:
            logger.error(f"Output AI tidak sesuai skema Pydantic: {e}")
            raise

        seharusnya, dideteksi, hilang = verifikasi_deteksi_batch(problematic_batches, analisis)
        logger.info(f"Verifikasi: seharusnya {seharusnya}, dideteksi {dideteksi}")
        if hilang:
           logger.warning(f"Batch yang HILANG dari output AI: {hilang}")
        else:
         logger.info("Semua batch bermasalah terdeteksi ")

        # 7. Decision layer
        engine = DecisionEngine(kpi)
        decision = engine.evaluate(analisis)
        logger.info(f"Keputusan: {decision.status.value}")
        for reason in decision.reasons:
            logger.info(f" - {reason}")

        # 8. Trigger aksi
        dispatcher = ActionDispatcher(config={
    "smtp_enabled": False,
    "webhook_url": None,
    "kpi": kpi,
})
        dispatcher.dispatch(decision, analisis)

        # 9. Tampilkan kesimpulan AI
        logger.info(f"Kesimpulan AI: {analisis.kesimpulan}")

    except Exception as e:
        logger.error(f"Error di main: {e}", exc_info=True)
    finally:
        conn.close()
        logger.info("Koneksi database ditutup")


if __name__ == "__main__":
    main()