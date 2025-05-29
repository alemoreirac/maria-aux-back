from fastapi import APIRouter, HTTPException, Depends, Response, File, UploadFile, Form
from utils.token_util import verify_token
from models.prompt_models import PromptRequest 
from service.ai_service_new import AIService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ai_service = AIService()
router = APIRouter()

@router.post("/api/process/")
async def process_ai(
    req: PromptRequest, 
    token: dict = Depends(verify_token)
):
    try:
        user_id = token.get("uid") 
        
        if not user_id:
            raise HTTPException(status_code=403, detail="ID de usuário não encontrado no token ou token inválido.")
 
        response_content = await ai_service.route_ai(req, user_id)
         
        return response_content
 
    except HTTPException as he:  
        logger.error(f"HTTP Erro em /api/process: {str(he.detail)} (Status: {he.status_code})")
        raise he
    except Exception as e:
        logger.error(f"Erro genérico em /api/process: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")