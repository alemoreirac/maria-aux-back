from typing import List
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from firebase_admin import auth
from utils.token_util import validate_password,verify_token
from managers.user_mgr import UserManager
import logging
from managers.credits_mgr import get_user_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()
user_mgr = UserManager() 
# Modelos de dados
class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    uid: str
    email: str

class TokenResponse(BaseModel):
    token: str

class LLMHistoryItem(BaseModel):
    user_query: str = ""
    gpt_response: str = ""

class UserCreditsAndLLMHistory(BaseModel):
    items: List[LLMHistoryItem]
    credits: int 
 

# Endpoint de criação de usuário (aberto)
@router.post("/api/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    try:
        fb_user = await user_mgr.create_user(user.email, user.password)
        return {"uid": fb_user.uid, "email": fb_user.email}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

  
# Endpoint para obter usuário (protegido)
@router.get("/api/users", response_model=UserResponse)
def get_user(token=Depends(verify_token)): 
    try:
        user_id = token.get("uid")
        fb_user = user_mgr.get_user(user_id)
        return {"uid": fb_user.uid, "email": fb_user.email}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# Endpoint para atualizar usuário (protegido)
@router.put("/api/users", response_model=UserResponse)
def update_user(user: UserCreate, token=Depends(verify_token)):
    try: 
        user_id = token.get("uid")
        fb_user = user_mgr.update_user(user_id, email=user.email, password=user.password)
        return {"uid": fb_user.uid, "email": fb_user.email}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para deletar usuário (protegido)
@router.delete("/api/users")
def delete_user( token=Depends(verify_token)):
    try:
        user_id = token.get("uid")
        user_mgr.delete_user(user_id)
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
  
  
@router.post("/api/auth/login", response_model=TokenResponse)
def login(credentials: UserCreate):
    try:
        auth_response = validate_password(credentials.email, credentials.password)
        
        id_token = auth_response.get("idToken")
        if not id_token:
            raise HTTPException(status_code=401, detail="Falha ao obter token")
        return {"token": id_token}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


# Endpoint para obter usuário (protegido)
@router.get("/api/users/dashboard")
async def get_usage_data(token=Depends(verify_token)):
    try:
        user_id = token.get("uid")
        user_data = await get_user_data(user_id)
        return user_data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))