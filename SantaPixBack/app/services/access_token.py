from fastapi import HTTPException
import requests

# Pega o token de acesso
def get_access_token(base_url: str, client_id: str, client_secret: str, caminho_certificado: str):
    # Fazendo a requisição www-form-urlencoded
    url = f"{base_url}/oauth/token"
    params = {
        "grant_type": "client_credentials"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(url, params=params, data=data, headers=headers, auth=(client_id, client_secret), cert=caminho_certificado)
    
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Erro ao pegar o token de acesso")
        
    return response.json()["access_token"]