# routes/menu_routes.py
from fastapi import APIRouter, HTTPException, Depends
from database.menu_repo import MenuRepository, MenuPromptWithParams
from typing import List
from utils.token_util import verify_token

router = APIRouter(prefix="/menu", tags=["menu"])

async def get_menu_repository():
    return MenuRepository()

@router.get("/prompts", response_model=List[MenuPromptWithParams])
async def get_menu_prompts(repo: MenuRepository = Depends(get_menu_repository),
    token: dict = Depends(verify_token) # Descomente se usar token por rota
):
    '''Endpoint para buscar todos os prompts com parâmetros para montar o menu'''
    try:
        prompts = await repo.get_prompts_with_parameters()
        return prompts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar prompts: {str(e)}")

@router.get("/prompts/{prompt_id}", response_model=MenuPromptWithParams)
async def get_menu_prompt(prompt_id: int, repo: MenuRepository = Depends(get_menu_repository),
    token: dict = Depends(verify_token) # Descomente se usar token por rota
):
    '''Endpoint para buscar um prompt específico com seus parâmetros'''
    try:
        prompt = await repo.get_prompt_with_parameters(prompt_id)
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt não encontrado")
        return prompt
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar prompt: {str(e)}")
