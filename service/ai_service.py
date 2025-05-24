import logging
from fastapi import HTTPException
from database.credits_repo import UserCreditRepository
# from database.llm_history_repo import LLMHistoryRepository # Not used in route_ai
from typing import List, Dict, Optional, Tuple, Union, Any # Keep Any for FilledParameter.valor
from managers import gemini_mgr, chatgpt_mgr, claude_mgr # Import modules directly
from models.prompt_models import PromptRequest, FilledParameter # Import FilledParameter
from models.enums import LLM, TipoParametroEnum, TipoPromptEnum
from managers.prompt_mgr import PromptManager # To fetch prompt details

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        # self.llm_log = LLMHistoryRepository() # Not currently used in route_ai
        self.credits_repo = UserCreditRepository()
        self.prompt_mgr = PromptManager() # Instantiate PromptManager
        pass
    
    async def route_ai(self, req: PromptRequest, user_id: str) -> str:
        
        if not await self.credits_repo.has_credits(user_id):
            raise HTTPException(status_code=402, detail="Créditos insuficientes para realizar esta operação.")

        full_prompt = await self.prompt_mgr.get(req.prompt_id)
        if not full_prompt:
            raise HTTPException(status_code=404, detail=f"Prompt com ID {req.prompt_id} não encontrado.")

        result = None
        prompt_content_for_llm = full_prompt.conteudo # Default prompt text from the prompt's content

        if full_prompt.tipo == TipoPromptEnum.TEXTO:
            if req.llm_id == LLM.CHAT_GPT:
                result = await chatgpt_mgr.process(req)
            elif req.llm_id == LLM.CLAUDE:
                result = await claude_mgr.process(req)
            elif req.llm_id == LLM.GEMINI:
                result = await gemini_mgr.process(req)
            else:
                raise HTTPException(status_code=400, detail="LLM ID inválido para prompt de texto.")

        elif full_prompt.tipo == TipoPromptEnum.IMAGEM:
            image_base64 = None
            image_media_type = "image/jpeg" # Default, can be made dynamic if needed
            for param in req.parameters:
                if param.tipo_param == TipoParametroEnum.IMAGEM:
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
                
        elif full_prompt.tipo == TipoPromptEnum.PDF:
            pdf_base64 = None
            for param in req.parameters:
                if param.tipo_param == TipoParametroEnum.ARQUIVO_PDF: # Ensure this enum value matches your definition
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
        
        else:
            raise HTTPException(status_code=400, detail="Tipo de prompt não suportado.")


        if result is not None: # Check if result was set (i.e., processing happened)
            await self.credits_repo.deduct_credit(user_id)
            return result
        else:
            # This case should ideally be caught by earlier checks, but as a fallback:
            raise HTTPException(status_code=500, detail="Falha no processamento da IA ou rota não encontrada.")