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
    Membangun prompt untuk Gemini dengan membaca template dari file.
    Versi prompt dipilih dari environment variable PROMPT_VERSION.
    """
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    versi = os.getenv("PROMPT_VERSION", "v2")  # default v2
    template_path = os.path.join("prompts", f"{versi}_quality_analysis.txt")
    
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    
    prompt = template.replace("{{KPI}}", str(kpi))
    prompt = prompt.replace("{{PROBLEMATIC_BATCHES}}", str(problematic_batches))
    prompt = prompt.replace("{{ALL_BATCHES}}", str(all_batch_data))
    prompt = prompt.replace("{{REJECT_RATES}}", str(reject_rates))
    prompt = prompt.replace("{{REJECT_DETAIL}}", str(reject_detail_data))
    
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