from fastapi import FastAPI,HTTPException
app = FastAPI()
import db
import analisis
import main
from pydantic import BaseModel

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
async def get_analyze_from_analisis():
    conn = db.get_connection()
    try:
        analisis,decision,kpi = main.jalankan_analisis(conn)
        return {"kesimpulan":analisis.kesimpulan,
                "status": decision.status.value,
                "kpi":kpi}
    except Exception as e:
        return {"status":"error","message":str(e)}
    finally:
        conn.close()