# managers/prompt_mgr.py
import logging
from typing import Any, Dict

from fastapi import HTTPException
from database.menu_repo import MenuRepository
from models.prompt_models import PromptRequest
from models.enums import TipoParametroEnum 
logger = logging.getLogger(__name__)

class MenuManager:
    def __init__(self):
        self.menu_repo = MenuRepository()
        
    async def mount(self, req: PromptRequest) -> str:
        if req.prompt_id <= 0:
            logger.warning("ID do prompt inválido.")
            return ""
        
        prompt = await self.menu_repo.get_prompt_with_parameters(req.prompt_id)
        
        result = prompt.conteudo
        param_values = ""
        for param in req.parameters:
            placeholder = "{" + param.titulo + "}: "
            param_value_str = str(param.valor) + "\n"
            param_values = param_values + placeholder + param_value_str
        
        result = result + param_values
        
        return result
    
    async def mount2(self, req: PromptRequest) -> str:
      if req.prompt_id <= 0:
          logger.warning("ID do prompt inválido.")
          return ""
      
      # Pega o menu do banco
      menu = await self.menu_repo.get_prompt_with_parameters(req.prompt_id)
      
      # Começa com o conteúdo do prompt
      result = menu['conteudo']
      
      # Cria mapa dos parâmetros do request por ID
      request_params = {param.id: param.valor for param in req.parameters}
      
      # Para cada parâmetro do menu, adiciona titulo + valor do request
      for menu_param in menu['parameters']:
          param_id = menu_param['id']
          param_titulo = menu_param['titulo']
          param_valor = request_params.get(param_id, "")
          
          if param_valor:  # Só adiciona se tiver valor
              result += f"\n{param_titulo}: {param_valor}"
      
      return result