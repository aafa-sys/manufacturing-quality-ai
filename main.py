import logging
import argparse
import os
from dotenv import load_dotenv
import csv
import json
from datetime import datetime


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
from logger_config import setup_logger

#setup logging pakai json formatter
setup_logger()
logger = logging.getLogger(__name__)






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

def validasi_output_ai(raw_json, problematic_batches):
    """
    Validasi output AI dengan Pydantic + verifikasi kelengkapan batch.
    Return: objek ProductionAnalysis yang sudah tervalidasi.
    Raise: Exception kalau tidak valid.
    """
    try:
        analisis = ProductionAnalysis(**raw_json)
        logger.info("Validasi Pydantic: OK")
    except Exception as e:
        logger.error(f"Output AI tidak sesuai skema Pydantic: {e}")
        raise
    
    # Verifikasi kelengkapan
    seharusnya, dideteksi, hilang = verifikasi_deteksi_batch(problematic_batches, analisis)
    logger.info(f"Verifikasi: seharusnya {seharusnya}, dideteksi {dideteksi}")
    if hilang:
        logger.warning(f"Batch yang HILANG dari output AI: {hilang}")
    else:
        logger.info("Semua batch bermasalah terdeteksi")
    
    return analisis
def proses_keputusan(kpi, analisis):
    """
    Jalankan decision engine, kembalikan objek DecisionResult.
    """
    engine = DecisionEngine(kpi)
    decision = engine.evaluate(analisis)
    logger.info(f"Keputusan: {decision.status.value}")
    for reason in decision.reasons:
        logger.info(f" - {reason}")
    return decision


def jalankan_aksi(decision, analisis, kpi):
    """
    Dispatch aksi berdasarkan keputusan (email, webhook, DB).
    """
    dispatcher = ActionDispatcher(config={
        "smtp_enabled": False,
        "webhook_url": None,
        "kpi": kpi,
    })
    dispatcher.dispatch(decision, analisis)
def parse_arguments():
    """
    Baca argumen dari command line.
    Contoh: python main.py --prompt-version v3
    """
    parser = argparse.ArgumentParser(
        description="Manufacturing Quality AI - Analisis kualitas produksi"
    )
    parser.add_argument(
        "--prompt-version",
        type=str,
        default=None,
        help="Versi prompt yang dipakai (contoh: v2, v3). Kalau tidak diisi, pakai dari .env",
    )
    args = parser.parse_args()
    return args
    


def catat_metrik_run(prompt_version, usage, total_batch, batch_terdeteksi, status):
    """
    Catat metrik run ke file runs.csv.
    Kalau file belum ada, buat + tulis header.
    """
    file_path = "runs.csv"
    file_exists = os.path.exists(file_path)
    
    biaya_usd = (usage["input"] / 1_000_000 * 0.10) + (usage["output"] / 1_000_000 * 0.40)
    biaya_idr = biaya_usd * 16000
    
    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # Kalau file baru, tulis header dulu
        if not file_exists:
            writer.writerow([
                "timestamp", "prompt_version", "input_token", "output_token",
                "total_token", "biaya_usd", "biaya_idr", "total_batch",
                "batch_terdeteksi", "status"
            ])
        
        # Tulis baris data
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            prompt_version,
            usage["input"],
            usage["output"],
            usage["total"],
            round(biaya_usd, 6),
            round(biaya_idr, 2),
            total_batch,
            batch_terdeteksi,
            status,
        ]) 
def hitung_kpi(all_batch_data):
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
    return kpi,reject_rates

def ambil_data(conn):
    all_batch_data = fetch_all_batches(conn)
    reject_detail_data = fetch_reject_details(conn)
       
    problematic_batches = fetch_problematic_batches(conn)

    return all_batch_data,reject_detail_data,problematic_batches
    
    



def main():
    args = parse_arguments()
    if args.prompt_version:
        logger.info(f"Prompt version dari CLI: {args.prompt_version}")
        os.environ["PROMPT_VERSION"] = args.prompt_version
    
    # 1. Buka koneksi database
    conn = None       
    try:
        conn = get_connection()   # PINDAH KE DALAM try
       

        # 2. Ambil data
        all_batch_data,reject_detail_data,problematic_batches =ambil_data(conn)

        kpi,reject_rates = hitung_kpi(all_batch_data)
        
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
        raw_json,usage= llm.generate_structured_json(prompt)

        # 6. Validasi + verifikasi
        analisis = validasi_output_ai(raw_json, problematic_batches)
        # 7. Decision + aksi
        decision = proses_keputusan(kpi, analisis)
        jalankan_aksi(decision, analisis, kpi)
       
    
        # 9. Tampilkan kesimpulan AI
        logger.info(f"Kesimpulan AI: {analisis.kesimpulan}")

        # 10. Catat metrik run
        prompt_version = os.getenv("PROMPT_VERSION", "v2")
        seharusnya, dideteksi, _ = verifikasi_deteksi_batch(problematic_batches, analisis)
        catat_metrik_run(
            prompt_version=prompt_version,
            usage=usage,
            total_batch=kpi["total_batch"],
            batch_terdeteksi=dideteksi,
            status=decision.status.value,
        )
        logger.info(f"Metrik dicatat ke runs.csv")

    except Exception as e:
        logger.error(f"Error di main: {e}", exc_info=True)
    finally:
        if conn:
          conn.close()
          logger.info("Koneksi database ditutup")


if __name__ == "__main__":
    main()