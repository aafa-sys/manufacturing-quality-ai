from fastapi import FastAPI,HTTPException,Request
import db
import analisis
import main
from pydantic import BaseModel
import time
import logging
app = FastAPI()
rate_limit_store = {} 
logger = logging.getLogger(__name__)

allowed = {"PASS","FAIL","REWORK"}

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/batch/{batch_id}")
async def ambil_batch(batch_id: int):
    return {"batch_id":batch_id,"message":"data batch ini"}

@app.get("/batches")
def get_batches(shift: str = None, line: int = None):

    return {"shift": shift, "line": line}


class BatchInput(BaseModel):
    batch_no: str
    reject_qty: int
    qc_status: str




class BatchResponse(BaseModel):
    batch_no: str
    reject_qty : int
    qc_status : str
    message : str

def cek_rate_limit(ip,max_request=5,window_detik=60):
    sekarang = time.time()
    riwayat = rate_limit_store.get(ip,[])
    riwayat = [w for w in riwayat if sekarang - w < window_detik]  


    if len(riwayat) >= max_request:
        return False

    riwayat.append(sekarang)
    rate_limit_store[ip] = riwayat 
    return True

@app.post("/input-batch",response_model=BatchResponse)
async def input_batch(data: BatchInput):
    if data.reject_qty < 0:
        raise HTTPException(status_code=400,detail="reject no negatif")
    
    if data.qc_status not in allowed :
        raise HTTPException(status_code=400,detail="qc status harus sesuai di allowed")

    if not data.batch_no.strip():
        raise HTTPException(status_code=400,detail="batch_no tidak boleh kosong")

    return BatchResponse(
       batch_no=data.batch_no,
       reject_qty=data.reject_qty,
       qc_status=data.qc_status,
       message="Data diterima")

@app.get("/batches/db")
async def get_batch_from_db():
    conn = db.get_connection()
    try:
        data= db.fetch_all_batches(conn)
        return {"total":len(data),"batches":data}
    finally:
        conn.close()

@app.get("/rejects/db")
async def get_reject_from_db():
    conn = db.get_connection()
    try:
        data = db.fetch_reject_details(conn)
        return{"total":len(data),"reject":(data)}
    finally:
        conn.close()

@app.get("/problematic/db")
async def get_problematic_from_db(threshold: int=19):
    conn = db.get_connection()
    try:
        data = db.fetch_problematic_batches(conn,threshold)
        return{"total":len(data),"problematic":data}
    finally:
        conn.close()

@app.get("/kpi")
async def get_kpi_from_analisis():
    conn = db.get_connection()
    try:
        data = db.fetch_all_batches(conn)
        kpi,_ = analisis.hitung_kpi(data)
        return kpi
    finally:
        conn.close()



@app.post("/analyze")
async def get_analyze_from_analisis(request : Request):
    conn = db.get_connection()
    try:
       
        client_ip = request.client.host
        waktu_mulai = time.time()
        logger.info(f"Request dari {client_ip} - mulai")
        if not cek_rate_limit(client_ip):
            raise HTTPException(429, "Terlalu banyak request. Coba lagi nanti.")
        
        analisis,decision,kpi = main.jalankan_analisis(conn)
        id_baru = db.insert_analysis_log(conn,analisis.kesimpulan,decision.status.value,kpi)
        durasi = time.time()- waktu_mulai
        logger.info(f"Request dari {client_ip} selesai dalam {durasi:.2f} detik")
                
        return {"id":id_baru,
                "kesimpulan":analisis.kesimpulan,
                "status": decision.status.value,
                "kpi":kpi}
            
    except Exception as e:
        durasi = time.time()- waktu_mulai
        logger.error(f"Request dari {client_ip} - error setelah {durasi:.2f} detik: {e}")
        return {"status":"error","message":str(e)}
    finally:
        conn.close()
        

@app.get("/analyze")
async def get_all_analysis_from_db():
    conn = db.get_connection()
    try:
        data = db.fetch_all_analysis(conn)   
        if not data:
            return {"total": 0, "analyses": []}
        
        analyses = []                         
        for row in data:                      
            analyses.append({
                "id": row[0],
                "kesimpulan": row[1],
                "status": row[2],
                "kpi": row[3],
                "created_at": row[4],
            })
        
        return {
            "total": len(analyses),
            "analyses": analyses
        }
    finally:
        conn.close()






@app.get("/analyze/{analysis_id}")
async def get_fetch_analyze_from_db(analysis_id : int):
    conn = db.get_connection()
    try:
        data = db.fetch_analysis(conn,analysis_id)
        if not data:
            raise HTTPException(404,"data harus ada")
        return{
            "id" : data[0],
            "kesimpulan" : data[1],
            "status" : data[2],
            "kpi" : data[3],
            "created_at" : data[4],
        }
    finally:
        conn.close()


