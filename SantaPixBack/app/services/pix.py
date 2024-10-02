import requests
from uuid import uuid4
from fastapi import HTTPException

def create_pix_value(access_token: str, pix_duration: int, pix_key: str, value: str, api_url: str, caminho_certificado: str, solicitacao_pagador: str = "") -> dict:
    payload = {
        "calendario": {
        "expiracao": int(pix_duration)
        },
        "valor": {
            "original": value
        },
        "chave": pix_key,
        "solicitacaoPagador": solicitacao_pagador,
    }
    
    txid = str(uuid4()).replace("-", "")
    print(txid)
    
    url = f"{api_url}/cob/{txid}"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.put(url, json=payload, headers=headers, cert=caminho_certificado)
    
    if response.status_code != 201:
        raise HTTPException(status_code=400, detail="Erro ao criar o Pix")
    
    return response.json()

def get_pix(access_token: str, txid: str, api_url: str, caminho_certificado: str) -> dict:
    url = f"{api_url}/cob/{txid}"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers, cert=caminho_certificado)
    
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Erro ao pegar o Pix")
    
    return response.json()

def delete_pix(access_token: str, txid: str, api_url: str, caminho_certificado: str) -> dict:
    url = f"{api_url}/cob/{txid}"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # Encontra o Pix
    response = requests.get(url, headers=headers, cert=caminho_certificado)
    
    # Verifica se o Pix foi encontrado e está ativo
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Pix não encontrado")
    
    pix_data = response.json()
    print(pix_data)
    
    # Verifica se o Pix está ativo
    if pix_data["status"] != "ATIVA":
        raise HTTPException(status_code=400, detail="Pix não está ativo")
    
    payload = {
        "status": "REMOVIDA_PELO_USUARIO_RECEBEDOR"
    }
    
    # Deleta o Pix
    response = requests.patch(url, headers=headers, cert=caminho_certificado, json=payload)
    
    
    return response.json()

def create_copy_paste_pix(value: str, city: str, business_name: str, pix_link:str):
    len_value = len(value)
    len_city = len(city)
    len_business_name = len(business_name)
    
    if len_city < 10:
        len_city = f"0{len_city}"
    
    if len_business_name < 10:
        len_business_name = f"0{len_business_name}"
    
    if len_value < 10:
        len_value = f"0{len_value}"
    
    pix_copy_paste = f"00020126850014br.gov.bcb.pix2563{pix_link}5204000053039865802BR59{len_business_name}{business_name}60{len_city}{city}62070503***6304"
    
    crc = calculate_crc16_ccitt(pix_copy_paste)
    
    pix_copy_paste = f"{pix_copy_paste}{crc}"
        
    return pix_copy_paste

def calculate_crc16_ccitt(pix_copy_paste: str) -> str:    
    poly = 0x1021
    crc = 0xFFFF
    xor = 0x0000
    
    crc = crc ^ xor
    
    for byte in pix_copy_paste:
        crc = crc ^ (ord(byte) << 8)
        
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ poly
            else:
                crc = crc << 1
                
    # Ultimos 4 bytes
    crc = crc & 0xFFFF
    
    # Acrescenta 0s a esquerda para completar 4 bytes
    crc = crc << 16
    
    return hex(crc)[2:6].upper()
