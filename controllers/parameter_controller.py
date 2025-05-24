# controllers/parameter_controller.py
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models.parameter_models import ParameterCreate, ParameterUpdate, ParameterResponse
from managers.parameter_mgr import ParameterManager
from utils.token_util import verify_token # Se for usar autenticação

router = APIRouter(
    prefix="/api", # Prefixo base, as rotas específicas definirão o resto
    tags=["Parameters"]
    # dependencies=[Depends(verify_token)] # Se aplicável a todas
)

parameter_mgr = ParameterManager()

# Criar um parâmetro associado a um prompt específico
@router.post("/prompts/{prompt_id}/parameters/", response_model=ParameterResponse, status_code=status.HTTP_201_CREATED)
async def create_parameter_for_prompt(
    prompt_id: int,
    parameter_payload: ParameterCreate,
    token: dict = Depends(verify_token)
):
    if prompt_id != parameter_payload.prompt_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O ID do prompt na URL não corresponde ao ID do prompt no payload."
        )
    # O manager pode ter uma lógica para verificar se o prompt_id existe
    created_parameter = await parameter_mgr.create_parameter(parameter_payload)
    if not created_parameter:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao criar o parâmetro."
        )
    return created_parameter

# Obter todos os parâmetros de um prompt específico
@router.get("/prompts/{prompt_id}/parameters/", response_model=List[ParameterResponse])
async def get_parameters_for_prompt(prompt_id: int,
    token: dict = Depends(verify_token) # Descomente se usar token por rota
):
    parameters = await parameter_mgr.get_parameters_for_prompt(prompt_id)
    # O manager já retorna lista vazia se não encontrar ou erro
    return parameters

# Obter um parâmetro específico pelo seu ID
@router.get("/parameters/{parameter_id}", response_model=ParameterResponse)
async def get_parameter(parameter_id: int,
    token: dict = Depends(verify_token) # Descomente se usar token por rota
):
    parameter = await parameter_mgr.get_parameter(parameter_id)
    if not parameter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parâmetro com ID {parameter_id} não encontrado."
        )
    return parameter

# Atualizar um parâmetro específico
@router.put("/parameters/{parameter_id}", response_model=ParameterResponse)
async def update_parameter(
    parameter_id: int,
    parameter_update_data: ParameterUpdate,
    token: dict = Depends(verify_token) # Descomente se usar token por rota
):
    updated_parameter = await parameter_mgr.update_parameter(parameter_id, parameter_update_data)
    if not updated_parameter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parâmetro com ID {parameter_id} não encontrado ou falha na atualização."
        )
    return updated_parameter

# Deletar um parâmetro específico
@router.delete("/parameters/{parameter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_parameter(parameter_id: int,
    token: dict = Depends(verify_token) 
):
    success = await parameter_mgr.delete_parameter(parameter_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parâmetro com ID {parameter_id} não encontrado ou falha ao deletar."
        )
    return None