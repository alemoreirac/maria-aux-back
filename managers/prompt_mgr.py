# managers/prompt_mgr.py
import logging
from typing import List, Optional, Any, Dict
from database.prompt_repo import PromptRepository
from models.prompt_models import FilledParameter, PromptCreate, PromptRequest, PromptUpdate, PromptResponse, PromptWithParams # Atualizado
from models.enums import TipoParametroEnum

logger = logging.getLogger(__name__)

class PromptManager:
    def __init__(self):
        self.prompt_repo = PromptRepository()

    async def create_prompt(self, prompt_data: PromptCreate) -> Optional[PromptResponse]:
        # A validação de campos obrigatórios é feita pelo Pydantic em PromptCreate
        # if not prompt_data.titulo or not prompt_data.conteudo or not prompt_data.tipo:
        # logger.warning("Título, conteúdo e tipo do prompt são obrigatórios.")
        # return None
        # Validações adicionais podem ser adicionadas aqui
        return await self.prompt_repo.create_prompt(prompt_data)

    async def get(self, prompt_id: int) -> Optional[PromptResponse]:
        if prompt_id <= 0:
            logger.warning("ID do prompt inválido.")
            return None
        return await self.prompt_repo.get_prompt(prompt_id)

    async def get_all(self) -> List[PromptResponse]: # Alterado para retornar List[PromptResponse]
        prompts = await self.prompt_repo.get_prompts() # Repo agora retorna List[PromptResponse]
        return prompts

    async def get_menu(self) -> List[Dict[str, Any]]:
        all_prompts_responses = await self.prompt_repo.get_prompts_with_params() # Retorna List[PromptResponse]

        # filtered_prompts = []
        # for prompt_response in all_prompts_responses:
        #     filtered_prompts.append({
        #         "id": prompt_response.id,
        #         "title": prompt_response.titulo # Acessando atributos do objeto Pydantic
        #     })
        return all_prompts_responses

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
     
    async def mount(self, req: PromptRequest) -> str:
        if req.prompt_id <= 0:
            logger.warning("ID do prompt inválido.")
            return ""
        prompt = self.prompt_repo.get_prompt(req.prompt_id)
        
        result = prompt.conteudo
        param_values = ""
        for param in req.parameters:
            placeholder = "{" + param.titulo + "}: "
            param_value_str = str(param.valor) + "\n"
            param_values = param_values + placeholder + param_value_str
        
        result = result + param_values
        
        return result
    
async def get_menu_with_params(self) -> List[PromptWithParams]:
    try:
        # Busca dados via JOIN no repository
        prompts_data = await self.prompt_repo.get_prompts_with_params()
        
        logger.info(f"Repository retornou {len(prompts_data)} prompts")
        
        if not prompts_data:
            logger.warning("Nenhum prompt encontrado no repository")
            return []
        
        prompts_with_params = []
        
        for i, data in enumerate(prompts_data):
            try:
                logger.info(f"Processando prompt {i+1}: {data.get('titulo', 'N/A')}")
                logger.info(f"Parâmetros encontrados: {len(data.get('parameters', []))}")
                
                filled_parameters = []
                
                # Verificar se parameters existe e é uma lista
                parameters = data.get("parameters", [])
                if not isinstance(parameters, list):
                    logger.warning(f"Parameters não é uma lista para prompt {data.get('id')}: {type(parameters)}")
                    parameters = []
                
                for j, param_data in enumerate(parameters):
                    try:
                        logger.info(f"  Param {j+1}: {param_data}")
                        
                        # Verificar se param_data tem as chaves necessárias
                        if not isinstance(param_data, dict):
                            logger.error(f"param_data não é um dict: {type(param_data)}")
                            continue
                            
                        if "tipo_param" not in param_data:
                            logger.error(f"tipo_param não encontrado em param_data: {param_data.keys()}")
                            continue
                            
                        if "valor" not in param_data:
                            logger.error(f"valor não encontrado em param_data: {param_data.keys()}")
                            continue
                        
                        filled_param = FilledParameter(
                            tipo_param=TipoParametroEnum(int(param_data["tipo_param"])),
                            valor=param_data["valor"]
                        )
                        filled_parameters.append(filled_param)
                        
                    except Exception as param_error:
                        logger.error(f"Erro ao processar parâmetro {j} do prompt {data.get('id')}: {param_error}")
                        logger.error(f"Dados do parâmetro: {param_data}")
                        continue
                
                # Criar o prompt com parâmetros
                prompt_with_params = PromptWithParams(
                    titulo=data["titulo"],
                    conteudo=data["conteudo"],
                    tipo=TipoParametroEnum(int(data["tipo"])),
                    parameters=filled_parameters
                )
                prompts_with_params.append(prompt_with_params)
                
                logger.info(f"Prompt processado com sucesso: {len(filled_parameters)} parâmetros")
                
            except Exception as prompt_error:
                logger.error(f"Erro ao processar prompt {i}: {prompt_error}")
                logger.error(f"Dados do prompt: {data}")
                continue
        
        logger.info(f"Retornando {len(prompts_with_params)} prompts com parâmetros")
        return prompts_with_params
        
    except Exception as e:
        logger.error(f"Erro geral ao buscar prompts com parâmetros: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return []
