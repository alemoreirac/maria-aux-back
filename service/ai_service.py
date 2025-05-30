import logging
from fastapi import HTTPException
from database.credits_repo import UserCreditRepository
from managers import gemini_mgr, chatgpt_mgr, claude_mgr 
from models.prompt_models import PromptRequest, AIResponse
from models.enums import LLM, TipoParametro, TipoPrompt
from managers.prompt_mgr import PromptManager
from managers.log_mgr import log_llm

logger = logging.getLogger(__name__)
 
class AIService:
    def __init__(self):
        self.credits_repo = UserCreditRepository()
        self.prompt_mgr = PromptManager() 
        pass
    
    async def route_ai(self, req: PromptRequest, user_id: str) -> AIResponse:
        
        if not await self.credits_repo.has_credits(user_id):
            raise HTTPException(status_code=402, detail="Créditos insuficientes para realizar esta operação.")

        full_prompt = await self.prompt_mgr.get(req.prompt_id)
        if not full_prompt:
            raise HTTPException(status_code=404, detail=f"Prompt com ID {req.prompt_id} não encontrado.")

        result = None
        prompt_content_for_llm = full_prompt.conteudo 

        if full_prompt.tipo == TipoPrompt.TEXTO:
            if req.llm_id == LLM.CHAT_GPT:
                result = await chatgpt_mgr.process(req)
            elif req.llm_id == LLM.CLAUDE:
                result = await claude_mgr.process(req)
            elif req.llm_id == LLM.GEMINI:
                result = await gemini_mgr.process(req)
            else:
                raise HTTPException(status_code=400, detail="LLM ID inválido para prompt de texto.")

        elif full_prompt.tipo == TipoPrompt.IMAGEM:
            image_base64 = None
            image_media_type = "image/jpeg" 
            for param in req.parameters:
                if param.tipo == TipoParametro.IMAGEM:
                    image_base64 = param.valor
                    
                    break
            
            if not image_base64:
                raise HTTPException(status_code=400, detail="Dados da imagem não fornecidos nos parâmetros para prompt de imagem.")

            if req.llm_id == LLM.CHAT_GPT:
                result = await chatgpt_mgr.process_image_base64(image_base64, prompt_content_for_llm, image_media_type)
            elif req.llm_id == LLM.CLAUDE:
                result = await claude_mgr.process_image_base64(image_base64, prompt_content_for_llm, image_media_type)
            elif req.llm_id == LLM.GEMINI:
                result = await gemini_mgr.process_image_base64(image_base64, prompt_content_for_llm, image_media_type)
            else:
                raise HTTPException(status_code=400, detail="LLM ID inválido para prompt de imagem.")
                
        elif full_prompt.tipo == TipoPrompt.PDF:
            pdf_base64 = None
            for param in req.parameters:
                if param.tipo == TipoParametro.ARQUIVO_PDF: 
                    pdf_base64 = param.valor
                    break
            
            if not pdf_base64:
                raise HTTPException(status_code=400, detail="Dados do PDF não fornecidos nos parâmetros para prompt de PDF.")

            if req.llm_id == LLM.CHAT_GPT:
                result = await chatgpt_mgr.process_pdf_base64(pdf_base64, prompt_content_for_llm)
            elif req.llm_id == LLM.CLAUDE:
                result = await claude_mgr.process_pdf_base64(pdf_base64, prompt_content_for_llm)
            elif req.llm_id == LLM.GEMINI:
                result = await gemini_mgr.process_pdf_base64(pdf_base64, prompt_content_for_llm)
            else:
                raise HTTPException(status_code=400, detail="LLM ID inválido para prompt de PDF.")
        
        elif full_prompt.tipo == TipoPrompt.BUSCA:
            if req.llm_id == LLM.GEMINI:
                result = await gemini_mgr.process_web_search(req)
            if req.llm_id == LLM.CHAT_GPT:
                result = await chatgpt_mgr.process_web_search(req)    
            if req.llm_id == LLM.CLAUDE:
                result = await claude_mgr.process_web_search(req)
            else:
                raise HTTPException(status_code=400, detail="LLM ID inválido para busca na web.")
            
        else:
            raise HTTPException(status_code=400, detail="Tipo de prompt não suportado.")

        if result is not None:
            req_id = await log_llm(user_id,str(req.parameters),result[:150])
            response = AIResponse(llm_response=result, request_id=req_id)
            await self.credits_repo.deduct_credit(user_id)
            return response
        else:

            raise HTTPException(status_code=500, detail="Falha no processamento da IA ou rota não encontrada.")