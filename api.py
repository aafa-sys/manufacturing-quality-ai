from fastapi import FastAPI,HTTPException
app = FastAPI()
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