
import psycopg2
from config import DB_CONFIG

def get_connection():
    """Membuka koneksi ke PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Database connection failed: {e}")
        raise

def fetch_all_batches(conn):
    """Ambil semua data batch_production."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT batch_id, batch_no, product_name, shift,
                   manufacturing_line, plan_qty, actual_qty,
                   reject_qty, qc_status
            FROM batch_production
        """)
        return cur.fetchall()

def fetch_reject_details(conn):
    """Ambil semua data reject_detail."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT batch_id, reject_category, reject_qty, reject_source
            FROM reject_detail
            ORDER BY reject_qty DESC
        """)
        return cur.fetchall()

def fetch_problematic_batches(conn, threshold=19):
    """Ambil batch dengan reject_qty > threshold."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT batch_id, batch_no, product_name, shift,
                   manufacturing_line, plan_qty, actual_qty,
                   reject_qty, qc_status
            FROM batch_production
            WHERE reject_qty > %s
            ORDER BY reject_qty DESC
        """, (threshold,))
        return cur.fetchall()
import json

def insert_decision_log(conn, decision, analisis, kpi):
    """
    Menyimpan hasil keputusan ke tabel decision_log.
    Mengembalikan True jika sukses, False jika gagal.
    """
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO decision_log
                    (status, reasons, priority_batches, recommended_actions, summary, kpi_snapshot)
                VALUES
                    (%s, %s, %s, %s, %s, %s)
            """, (
                decision.status.value,
                json.dumps(decision.reasons),
                json.dumps(decision.priority_batches),
                json.dumps(decision.recommended_actions),
                analisis.kesimpulan,
                json.dumps(kpi),
            ))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        # Log error kalau perlu
        import logging
        logging.getLogger(__name__).error(f"Gagal insert decision_log: {e}")
        return False