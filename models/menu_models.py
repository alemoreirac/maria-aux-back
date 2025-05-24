from pydantic import BaseModel
from models.enums import TipoParametroEnum, TipoPromptEnum
from typing import List

# Modelo simples para o parâmetro no menu
class MenuParameter(BaseModel):
    id: int
    titulo: str
    descricao: str
    tipo: TipoParametroEnum

# Modelo para o prompt com seus parâmetros
class MenuPromptWithParams(BaseModel):
    id: int
    titulo: str
    conteudo: str
    tipo: TipoPromptEnum
    parameters: List[MenuParameter]