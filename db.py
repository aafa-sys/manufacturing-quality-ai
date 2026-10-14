import psycopg2
from datetime import date,datetime
from config import DB_CONFIG
from exceptions import DatabaseError
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

import logging
logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(DatabaseError),
    reraise=True
)
def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection failed: {e}")
        raise DatabaseError(f"Tidak bisa koneksi ke database: {e}")

def fetch_all_batches(conn):
    """Ambil semua data batch_production."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT batch_id, batch_no, product_name, shift,
                   manufacturing_line, plan_qty, actual_qty,
                   reject_qty, qc_status
            FROM batch_production
            WHERE status != 'DELETED'
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
            AND status != 'DELETED'
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
def insert_analysis_log(conn,kesimpulan,status,kpi):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO analysis_log
                   (kesimpulan,status,kpi)
                   VALUES(%s,%s,%s)
                   RETURNING analysis_id """,(
            kesimpulan,
            status,
            json.dumps(kpi)
                   ))
            id_baru = cur.fetchone()[0]
            conn.commit()
            return id_baru
    except Exception as e:
        conn.rollback()
        import logging
        logging.getLogger(__name__).error(f"Gagal insert analysis log : {e}")
        return  None

def fetch_analysis(conn,analysis_id):
    try:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT analysis_id,kesimpulan,status,kpi,created_at
            FROM analysis_log
            WHERE analysis_id = %s""",(analysis_id,))

        
            return cur.fetchone()
    except Exception as e:
       
        logging.getLogger(__name__).error(f"gagal fetch analys :{e}")
        return None

def fetch_all_analysis(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT analysis_id,kesimpulan,status,kpi,created_at
            FROM analysis_log
            order by analysis_id DESC """)

            return cur.fetchall()
    except Exception as e:

        logging.getLogger(__name__).error(f"gagal fetch all analysis:{e}")
        return None


def insert_batch(conn, batch_no, product_code, product_name, shift, manufacturing_line, plan_qty):
    try:
        hari_ini = date.today()
        sekarang = datetime.now().timetz()
        
        with conn.cursor() as cur:
        
            cur.execute("""
                SELECT batch_id FROM batch_production 
                ORDER BY batch_id DESC 
                LIMIT 1
            """)
            row = cur.fetchone()
            
           
            if not row:
                batch_id_baru = "B000001"
            else:
                angka = int(row[0][1:]) + 1
                batch_id_baru = f"B{angka:06d}"
            
        
            cur.execute("""
                INSERT INTO batch_production 
                    (batch_id, batch_no, product_code, product_name, 
                     production_date, shift, start_time, end_time, 
                     manufacturing_line, plan_qty)
                VALUES 
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING batch_id
            """, (
                batch_id_baru,     
                batch_no,          
                product_code, 
                product_name,
                hari_ini, 
                shift, 
                sekarang, 
                sekarang,
                manufacturing_line, 
                plan_qty, 
                
            ))
            id_baru = cur.fetchone()[0]
        
        conn.commit()
        return id_baru
    except Exception as e:
        conn.rollback()
        print(f"DEBUG ERROR: {e}")
        logging.getLogger(__name__).error(f"Gagal insert batch: {e}")
        return None


def fetch_all_products(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT produk_code,produk_name,category,form,strength,unit,manufacturing_line
                FROM master_produk
                WHERE status = 'Active'
                ORDER BY produk_code""")

            return cur.fetchall()
    except Exception as e:
        logging.getLogger(__name__).error(f"gagal fetch all products:{e}")
        return None


        
def update_batch(conn,batch_id,actual_qty,reject_qty,qc_status):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                        UPDATE batch_production 
                        SET actual_qty = %s ,reject_qty = %s,qc_status = %s
                        WHERE batch_id = %s
                        RETURNING batch_id""",(actual_qty,reject_qty,qc_status,batch_id))
            row = cur.fetchone()
            if not row:
                return None
            id_baru = row[0]

        conn.commit()
        return id_baru
    except Exception as e:
        conn.rollback()  
        print(f" DEBUG ERROR : {e}")   
        logging.getLogger(__name__).error(f"gagal update batch :{e}")    
        return None        


def fetch_batch(conn,batch_id):
    try:
        with conn.cursor() as cur:
            cur.execute("""SELECT batch_id,batch_no,product_code,product_name,shift,manufacturing_line,
                       plan_qty,actual_qty,reject_qty,qc_status
                       FROM batch_production
                       WHERE batch_id = %s
                       AND status != 'DELETED'
                       """,(batch_id,))
            return cur.fetchone()
    except Exception as e:
        logging.getLogger(__name__).error(f"gagal fetch batch :{e}")
        return None


def delete_batch(conn,batch_id):
    try:
        with conn.cursor() as cur:
            cur.execute("""DELETE FROM batch_production
                        WHERE batch_id = %s
                        RETURNING batch_id""",(batch_id,))

            row = cur.fetchone()

            if not row:
                return None
            id_deleted= row[0]

        conn.commit()
        return id_deleted
    except Exception as e:
        conn.rollback()
        print(f" DEBUG ERROR : {e}")
        return None

def soft_delete_batch(conn,batch_id):
    try:
        with conn.cursor() as cur:
            cur.execute(""" UPDATE batch_production
                        SET status = 'DELETED'
                        WHERE batch_id = %s
                        RETURNING batch_id""",(batch_id,))
            row = cur.fetchone()

            if not row:
                return None
            id_dihapus = row[0]
        conn.commit()
        return id_dihapus
    except Exception as e:
        conn.rollback()
        print(f"DEBUG ERROR : {e}")
        return None