import logging
from database.prompt_repo import PromptRepository
from models.prompt_models import PromptRequest


logger = logging.getLogger(__name__)

class MenuManager:
    def __init__(self):
        self.prompt_repo = PromptRepository()
        
    async def mount(self, req: PromptRequest) -> str:
        if req.prompt_id <= 0:
            logger.warning("ID do prompt inválido.")
            return ""
        
        prompt = await self.prompt_repo.get_prompt(req.prompt_id)
        
        result = prompt.conteudo
        param_values = ""
        for param in req.parameters:
            placeholder = "{" + param.titulo + "}: "
            param_value_str = str(param.valor) + "\n"
            param_values = param_values + placeholder + param_value_str
        
        result = result + param_values
        
        return result
     