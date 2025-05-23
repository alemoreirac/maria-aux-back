# controllers/prompt_controller.py
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models.prompt_models import PromptCreate, PromptUpdate, PromptResponse # Atualizado
from managers.prompt_mgr import PromptManager
# from utils.token_util import verify_token # Mantido se você usar

router = APIRouter(
    prefix="/api/prompts",
    tags=["Prompts"]
    # dependencies=[Depends(verify_token)] # Adicionar dependência global se aplicável a todas as rotas
)

prompt_mgr = PromptManager()

@router.post("/", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    prompt_data_payload: PromptCreate # Usar PromptCreate
    # , token: dict = Depends(verify_token) # Descomente se usar token por rota
):
    # prompt_data_for_creation já está no formato correto (PromptCreate)
    created_prompt = await prompt_mgr.create_prompt(prompt_data_payload)
    if not created_prompt:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao criar o prompt. Verifique os dados fornecidos."
        )
    return created_prompt

@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: int
    # , token: dict = Depends(verify_token)
):
    prompt = await prompt_mgr.get(prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt com ID {prompt_id} não encontrado"
        )
    return prompt

@router.get("/", response_model=List[PromptResponse]) # Especificar o response_model
async def get_prompts(
    # token: dict = Depends(verify_token)
):
    prompts = await prompt_mgr.get_all() # mgr.get_prompts agora deve retornar List[PromptResponse]
    # A verificação de "if not prompts: return []" já é tratada pelo repo/mgr que retorna lista vazia
    return prompts


# Rota para o menu, se a lógica for diferente de get_prompts
@router.get("/menu/", response_model=List[Dict[str, Any]]) # Mantendo o retorno original se for específico
async def get_prompts_menu(
    # token: dict = Depends(verify_token)
):
    prompts_menu = await prompt_mgr.get_menu()
    if not prompts_menu:
        return []
    return prompts_menu


@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: int,
    prompt_update_data: PromptUpdate # Usar PromptUpdate
    # , token: dict = Depends(verify_token)
):
    updated_prompt = await prompt_mgr.update(prompt_id, prompt_update_data)
    if not updated_prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt com ID {prompt_id} não encontrado ou falha na atualização"
        )
    return updated_prompt

@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(
    prompt_id: int
    # , token: dict = Depends(verify_token) # Se o user_id vier do token, precisará dele
):
    # Se delete_prompt no manager precisar de user_id, você terá que obtê-lo do token
    # Exemplo: user_id = token.get("user_id")
    # success = await prompt_mgr.delete_prompt(prompt_id, user_id) # Se precisar de user_id
    success = await prompt_mgr.delete(prompt_id) # Se não precisar de user_id na camada do controller
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt com ID {prompt_id} não encontrado ou falha ao deletar"
        )
    return None # Para status 204, não deve haver corpo na resposta