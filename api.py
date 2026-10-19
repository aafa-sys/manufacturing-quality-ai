from fastapi import FastAPI,HTTPException,Request,Header,Depends,Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import db
import analisis
import main
from pydantic import BaseModel
from typing import Literal
import time
import logging
app = FastAPI()
rate_limit_store = {} 

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         
    allow_credentials=True,
    allow_methods=["*"],           
    allow_headers=["*"],          
)

@app.exception_handler(Exception)
async def global_exception_handler(request:Request,exc:Exception):
    logger.error(f"Error di {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error" :True,
            "message": "terjadi kesalahan server",
            "status_code": 500
        }
    )
def verify_api_key(x_api_key :str = Header(...)):
    expected = os.getenv("API_KEY")

    if x_api_key != expected:
        raise HTTPException(401,"API key tidak valid")

    return x_api_key

logger = logging.getLogger(__name__)

allowed = {"PASS","FAIL","REWORK","HOLD"}

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/batch/{batch_id}")
async def ambil_batch(batch_id: str):
    conn = db.get_connection()
    try:
        data = db.fetch_batch(conn,batch_id)
        if not data:
            raise HTTPException(404,"batch tidak di temukan")

        
        return {"batch_id": data[0],
                "batch_no" : data[1],
                "product_code": data[2],
                "product_name": data[3],
                "shift": data[4],
                "manufacturing_line": data[5],
                "plan_qty":data[6],
                "actual_qty": data[7],
                "reject_qty": data[8],
                "qc_status": data[9],}
    finally:
        conn.close()

@app.get("/batches")
def get_batches(shift: str = None, line: int = None):

    return {"shift": shift, "line": line}


class BatchInput(BaseModel):
    batch_no: str
    product_code : str
    product_name : str
    shift : str
    manufacturing_line : str
    plan_qty : int
    



class BatchResponse(BaseModel):
    batch_id : str
    batch_no: str
    message : str

class BatchUpdate(BaseModel):
    actual_qty : int
    reject_qty : int
    qc_status : Literal["PASS","FAIL","REWORK","HOLD"]

def cek_rate_limit(ip,max_request=5,window_detik=60):
    sekarang = time.time()
    riwayat = rate_limit_store.get(ip,[])
    riwayat = [w for w in riwayat if sekarang - w < window_detik]  


    if len(riwayat) >= max_request:
        return False

    riwayat.append(sekarang)
    rate_limit_store[ip] = riwayat 
    return True



@app.get("/batches/db")
async def get_batch_from_db(page : int= Query(1,ge=1),limit :int =Query(10,ge=1, le=100)):
    conn = db.get_connection()
    try:

        offset = (page-1) * limit

        data= db.fetch_all_batches(conn,limit,offset)

        total = db.count_batch(conn)


        return {
            
            "total":total,
            "page": page,
            "limit" : limit,
            "batches":data }
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
async def get_analyze_from_analisis(request : Request,api_key: str=Depends(verify_api_key)):

    
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

@app.post("/input-batch", response_model=BatchResponse)
async def input_batch(data: BatchInput,api_key: str=Depends(verify_api_key)):
    
    
    if not data.batch_no.strip():
        raise HTTPException(status_code=400,detail="batch_no tidak boleh kosong")
    
    
    conn = db.get_connection()
    try:
      
        id_baru = db.insert_batch(
            conn,
            data.batch_no,
            data.product_code,
            data.product_name,
            data.shift,
            data.manufacturing_line,
            data.plan_qty,
            
        )

        if not id_baru:
            raise HTTPException(500, "Gagal menyimpan data ke database")


        
       
        return BatchResponse(
            batch_id = id_baru,
            batch_no=data.batch_no,
            message=f"Data tersimpan dengan ID {id_baru}"
        )
    finally:
        conn.close()

@app.get("/products/db")
async def get_produk_from_db():
    conn = db.get_connection()
    try:
        data= db.fetch_all_products(conn)

                  
        if not data :
            return {"total" : 0,"products" : []}
        

        products = []
        for row in data :
            products.append ({
                "produk_code": row[0],
                "produk_name":row[1],
                "category":row[2],
                "form": row[3],
                "strength":row[4],
                "unit":row[5],
                "manufacturing_line":row[6],})

        return{
            "total" : len(products),
            "products" : products }
 
    finally:
        conn.close()


@app.put("/batch/{batch_id}")
async def update_batch_endpoint(batch_id: str,data:BatchUpdate,api_key: str=Depends(verify_api_key)):
    conn = db.get_connection()

    try:
        hasil = db.update_batch(conn,batch_id,data.actual_qty,data.reject_qty,data.qc_status)

        if not hasil:
            raise HTTPException(404,"batch tidak di temukan")

        batch = db.fetch_batch(conn,batch_id)

        return{
            "batch_id" : batch[0],
            "batch_no" : batch[1],
            "product_code": batch[2],
            "product_name": batch[3],
            "shift" : batch[4],
            "manufacturing_line" : batch[5],
            "plan_qty" : batch[6],
            "actual_qty": batch[7],
            "reject_qty" : batch[8],
            "qc_status" : batch[9],
        }
    finally:
        conn.close()

@app.delete("/batch/{batch_id}")
async def soft_delete_batch_from_db(batch_id : str,api_key: str=Depends(verify_api_key)):
    conn = db.get_connection()
    try:
        hasil = db.soft_delete_batch(conn,batch_id)
        if not hasil:
            raise HTTPException(404,"batch delete tidak di temukan")

        return{"message" : f"batch {hasil} berhasil di hapus"}
    finally:
        conn.close()





