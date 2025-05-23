from fastapi import APIRouter, HTTPException, Depends, Response, File, UploadFile, Form 
from utils.token_util import verify_token
from models.prompt_models import PromptRequest
from service.ai_service import AIService 
import logging
 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ai_service = AIService()
router = APIRouter()  
 
@router.post("/api/process/")
async def process_ai( 
    token: dict = Depends(verify_token),
    req: PromptRequest = None
):
    try:
        user_id = token.get("uid")
        
        if not user_id or req:
            raise HTTPException(status_code=403, detail="ID de usuário não encontrado no token.")
        
        if not req:
            raise HTTPException(status_code=400, detail="Requisição vazia")
 
        response = await ai_service.route_ai(req,user_id)
        
        return Response(
            content=response,
            media_type="application/json"
        )
 
    except Exception as e:
        logger.error(f"Erro api/process: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")
         