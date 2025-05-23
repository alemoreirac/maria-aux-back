# managers/parameter_mgr.py
import logging
from typing import List, Optional
from database.parameter_repo import ParameterRepository
from models.parameter_models import ParameterCreate, ParameterUpdate, ParameterResponse
# Você pode precisar verificar se o prompt_id existe antes de criar um parâmetro.
# from database.prompt_repo import PromptRepository # Para verificar existência do prompt

logger = logging.getLogger(__name__)

class ParameterManager:
    def __init__(self):
        self.parameter_repo = ParameterRepository()
        # self.prompt_repo = PromptRepository() # Opcional: para validar prompt_id

    async def create_parameter(self, parameter_data: ParameterCreate) -> Optional[ParameterResponse]:
        # Opcional: Verificar se o prompt_id associado existe
        # prompt_exists = await self.prompt_repo.get_prompt(parameter_data.prompt_id)
        # if not prompt_exists:
        #     logger.warning(f"Tentativa de criar parâmetro para prompt inexistente ID: {parameter_data.prompt_id}")
        #     return None
        return await self.parameter_repo.create_parameter(parameter_data)

    async def get_parameter(self, parameter_id: int) -> Optional[ParameterResponse]:
        if parameter_id <= 0:
            logger.warning("ID do parâmetro inválido.")
            return None
        return await self.parameter_repo.get_parameter(parameter_id)

    async def get_parameters_for_prompt(self, prompt_id: int) -> List[ParameterResponse]:
        if prompt_id <= 0:
            logger.warning("ID do prompt inválido para buscar parâmetros.")
            return []
        return await self.parameter_repo.get_parameters_for_prompt(prompt_id)

    async def update_parameter(self, parameter_id: int, parameter_data: ParameterUpdate) -> Optional[ParameterResponse]:
        if parameter_id <= 0:
            logger.warning("ID do parâmetro inválido para atualização.")
            return None
        if not parameter_data.model_dump(exclude_unset=True):
            logger.warning("Nenhum dado fornecido para atualização do parâmetro.")
            return await self.parameter_repo.get_parameter(parameter_id) # Retorna o atual
        return await self.parameter_repo.update_parameter(parameter_id, parameter_data)

    async def delete_parameter(self, parameter_id: int) -> bool:
        if parameter_id <= 0:
            logger.warning("ID do parâmetro inválido para exclusão.")
            return False
        return await self.parameter_repo.delete_parameter(parameter_id)