from pydantic import BaseModel, Field
from typing import Optional, Any
from models.enums import TipoParametro # Importar o Enum

class ParameterBase(BaseModel):
    titulo: str = Field(..., max_length=255)
    descricao: Optional[str] = None
    tipo: TipoParametro

class ParameterCreate(ParameterBase):
    prompt_id: int

class ParameterUpdate(BaseModel):
    titulo: Optional[str] = Field(None, max_length=255)
    descricao: Optional[str] = None
    tipo: Optional[TipoParametro] = None

class ParameterResponse(ParameterBase):
    id: int
    prompt_id: int

class Config:
    from_attributes = True
