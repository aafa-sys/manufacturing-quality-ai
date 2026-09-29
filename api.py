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

