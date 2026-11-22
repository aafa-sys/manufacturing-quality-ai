from fastapi import FastAPI
from pydantic import BaseModel
from agent.agent import jalankan_agent

#membuat restoran fast api

app = FastAPI(title="Manufacturing AI API")

#membuat buku menu =(format data yang di terima api)
class ChatRequest(BaseModel):
    prompt: str
    role: str = "operator"

#membuat pintu masuk (endpoint)untuk ngetes

@app.get("/")
def read_root():
    return {"message":  "API Manufacturing AI sudah menyala."}

#membuat endpoint untuk caht ai yang nanti akan di sambungkan ke gemini
@app.post("/chat")
def chat_ai(request: ChatRequest):
    jawaban_ai = jalankan_agent(request.prompt,role=request.role)
    return {
        "status": "sukses",
        "jawaban": jawaban_ai
    }