# managers/prompt_mgr.py
import logging
from typing import List, Optional, Any, Dict
from database.prompt_repo import PromptRepository
from models.prompt_models import FilledParameter, PromptCreate, PromptRequest, PromptUpdate, PromptResponse, PromptWithParams # Atualizado
from models.enums import TipoParametro 
logger = logging.getLogger(__name__)

class PromptManager:
    def __init__(self):
        self.prompt_repo = PromptRepository()

    async def create_prompt(self, prompt_data: PromptCreate) -> Optional[PromptResponse]:
       
        return await self.prompt_repo.create_prompt(prompt_data)

    async def get(self, prompt_id: int) -> Optional[PromptResponse]:
        if prompt_id <= 0:
            logger.warning("ID do prompt inválido.")
            return None
        result = await self.prompt_repo.get_prompt(prompt_id) 
        return result

    async def get_all(self) -> List[PromptResponse]: # Alterado para retornar List[PromptResponse]
        prompts = await self.prompt_repo.get_prompts() # Repo agora retorna List[PromptResponse]
        return prompts
  
    async def update(self, prompt_id: int, prompt_update_data: PromptUpdate) -> Optional[PromptResponse]:
        if prompt_id <= 0:
            logger.warning("ID do prompt inválido para atualização.")
            return None
        # if not prompt_update_data.model_dump(exclude_unset=True): # No Pydantic V2 é model_dump
        if not prompt_update_data.model_dump(exclude_unset=True):
            logger.warning("Nenhum dado fornecido para atualização do prompt.")
            # Retornar o prompt existente se nenhum dado for fornecido para atualização
            return await self.prompt_repo.get_prompt(prompt_id)
        return await self.prompt_repo.update_prompt(prompt_id, prompt_update_data)

    # Ajustar delete_prompt para não requerer user_id se não for usado, ou passá-lo corretamente
    async def delete(self, prompt_id: int) -> bool: # Removido user_id se não vier do controller
        if prompt_id <= 0:
            logger.warning("ID do prompt inválido para exclusão.")
            return False

        # logger.info(f"Tentando deletar prompt {prompt_id} para o usuário {user_id}") # Se usar user_id
        logger.info(f"Tentando deletar prompt {prompt_id}")
        was_deleted = await self.prompt_repo.delete_prompt(prompt_id) # Ajustado
        if was_deleted:
            logger.info(f"Prompt {prompt_id} deletado com sucesso.")
        else:
            logger.warning(f"Falha ao deletar prompt {prompt_id} ou prompt não encontrado.")
        return was_deleted
     
         