# controllers/prompt_controller.py
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models.prompt_models import PromptCreate, PromptUpdate, PromptResponse, PromptWithParams # Atualizado
from managers.prompt_mgr import PromptManager
from utils.token_util import verify_token 

router = APIRouter(
    prefix="/api/prompts",
    tags=["Prompts"]
)

prompt_mgr = PromptManager()

@router.post("/", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    prompt_data_payload: PromptCreate ,
    token: dict = Depends(verify_token) # Descomente se usar token por rota
):
    created_prompt = await prompt_mgr.create_prompt(prompt_data_payload)
    if not created_prompt:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao criar o prompt. Verifique os dados fornecidos."
        )
    return created_prompt

@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: int,
    token: dict = Depends(verify_token)
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
    token: dict = Depends(verify_token)
):
    prompts = await prompt_mgr.get_all()

    return prompts

@router.get("/menu/", response_model=List[PromptWithParams])
async def get_prompts_menu(
    token: dict = Depends(verify_token)
):
    prompts_with_params = await prompt_mgr.get_menu_with_params()
    if not prompts_with_params:
        return []
    return prompts_with_params

@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: int,
    prompt_update_data: PromptUpdate,
    token: dict = Depends(verify_token)
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
    prompt_id: int,
    token: dict = Depends(verify_token) # Se o user_id vier do token, precisará dele
):
    success = await prompt_mgr.delete(prompt_id) # Se não precisar de user_id na camada do controller
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt com ID {prompt_id} não encontrado ou falha ao deletar"
        )
    return None # Para status 204, não deve haver corpo na resposta