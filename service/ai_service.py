import logging

from fastapi import HTTPException
from database.credits_repo import UserCreditRepository
from database.llm_history_repo import LLMHistoryRepository
from typing import List, Dict, Optional, Tuple, Union, Any
from managers.gemini_mgr import process as gemini_process
from managers.chatgpt_mgr import process as chatgpt_process
from managers.claude_mgr import process as claude_process
from models.prompt_models import PromptRequest
from models.enums import LLM

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.llm_log = LLMHistoryRepository()
        self.credits_repo = UserCreditRepository()
        pass
    
    async def route_ai(self, req: PromptRequest, user_id: str) -> str:
        
        if not await self.credits_repo.has_credits(user_id):
            raise HTTPException(status_code=402, detail="Créditos insuficientes para realizar esta operação.")

        if req.llm_id == LLM.CHAT_GPT:
            result = chatgpt_process(req)

        if req.llm_id == LLM.CLAUDE:
            result = claude_process(req)

        if req.llm_id == LLM.GEMINI:
            result = gemini_process(req)

        if result: 
            await self.credits_repo.deduct_credit(user_id)
            return result