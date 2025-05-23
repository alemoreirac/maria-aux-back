from pydantic import BaseModel, Field
from typing import Optional, Any
from models.enums import TipoParametroEnum # Importar o Enum

class ParameterBase(BaseModel):
    titulo: str = Field(..., max_length=255)
    descricao: Optional[str] = None
    tipo: TipoParametroEnum

class ParameterCreate(ParameterBase):
    prompt_id: int

class ParameterUpdate(BaseModel):
    titulo: Optional[str] = Field(None, max_length=255)
    descricao: Optional[str] = None
    tipo: Optional[TipoParametroEnum] = None

class ParameterResponse(ParameterBase):
    id: int
    prompt_id: int

    class Config:
        orm_mode = True # or from_attributes = True for Pydantic v2
