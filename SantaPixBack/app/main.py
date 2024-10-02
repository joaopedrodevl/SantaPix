import os
from typing import List
from fastapi import FastAPI, BackgroundTasks
from services import access_token, pix
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

base_url = os.getenv("BASE_URL")
api_url = os.getenv("API_URL")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
pix_key = os.getenv("PIX_KEY")
pix_duration = os.getenv("PIX_DURATION")

caminho_certificado = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cert.pem"))

class PixBody(BaseModel):
    value: str
    solicitacao_pagador: str

@app.get("/")
def read_root():
    response = {
        "version": "1.0",
        "message": "API is running 🌎"
    }
    return response

@app.post("/pix")
def create_pix(pixBody: PixBody):
    token = access_token.get_access_token(base_url, client_id, client_secret, caminho_certificado)
    
    value = pixBody.value
    solicitacao_pagador = pixBody.solicitacao_pagador
    
    pix_data = pix.create_pix_value(token, pix_duration, pix_key, value, api_url, caminho_certificado, solicitacao_pagador)
    
    response = {
        "message": "Pix criado com sucesso 🚀",
        "data": pix_data
    }
    
    return response

@app.get("/pix/qr/{txid}")
def get_pix(txid: str):
    token = access_token.get_access_token(base_url, client_id, client_secret, caminho_certificado)
    
    pixt = pix.get_pix(token, txid, api_url, caminho_certificado)
    
    pix_copy_paste = pix.create_copy_paste_pix(pixt["valor"]["original"], "Campina Grande", "FJI Motos", pixt["location"])
    
    return {
        "message": "Pix encontrado",
        "data": pix_copy_paste
    }

@app.get("/pix/{txid}/status")
def get_pix_status(txid: str, background_tasks: BackgroundTasks):
    token = access_token.get_access_token(base_url, client_id, client_secret, caminho_certificado)
    
    pixt = pix.get_pix(token, txid, api_url, caminho_certificado)
    
    if pixt["status"] == "CONCLUIDA" and len(pixt["pix"]) > 0:
        return {
            "message": "PAGO",
            "data": pixt["pix"]
        }
    
    if pixt["status"] == "CONCLUIDA" and len(pixt["pix"]) == 0:
        return {
            "message": "CANCELADO",
            "data": pixt["pix"]
        }
    
    if pixt["status"] == "ATIVA":
        return {
            "message": "PENDENTE",
            "data": pixt["pix"]
        }
        
    if pixt["status"] == "REMOVIDA_PELO_USUARIO_RECEBEDOR" or pixt["status"] == "REMOVIDA_PELO_PSP":
        return {
            "message": "CANCELADO",
            "data": pixt["pix"]
        }
    
    raise HTTPException(status_code=400, detail="Erro ao pegar o Pix")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

