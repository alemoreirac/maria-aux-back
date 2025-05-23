from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth
import requests 

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token  # Retorna os dados decodificados, como uid, etc.
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")



FIREBASE_API_KEY = "AIzaSyCqaMsOhx8MiMbjMkgvMDkcngDvZl9F0nQ"  # Substitua pela sua chave da API do Firebase

def validate_password(email: str, password: str) -> dict:
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code != 200:
        # Caso as credenciais estejam erradas ou ocorra algum outro erro,
        # o Firebase retorna um status de erro, então tratamos o erro.
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    return response.json()
 
