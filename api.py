from fastapi import FastAPI
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/batch/{batch_id}")
async def ambil_batch(batch_id: int):
    return {"batch_id":batch_id,"message":"data batch ini"}

@app.get("/batches")
def get_batches(shift: str = None, line: int = None):

    return {"shift": shift, "line": line}

from pydantic import BaseModel

class BatchInput(BaseModel):
    batch_no: str
    reject_qty: int
    qc_status: str

@app.post("/input-batch")
async def input_batch(data: BatchInput):
    return {"received":data.batch_no,"reject":data.reject_qty,"qc_status":data.qc_status} 

class BatchResponse(BaseModel):
    batch_no: str
    reject_qty : int
    qc_status : str
    message : str

@app.post("/input-batch",response_model=BatchResponse)
async def input_batch(data: BatchInput):
    return BatchResponse(
        batch_no=data.batch_no,reject_qty=data.reject_qty,qc_status=data.qc_status,message="data diterima"
    )
