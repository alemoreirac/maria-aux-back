# models/prompt_models.py
from pydantic import BaseModel, Field
from typing import Any, List, Optional
from models.enums import TipoParametroEnum, TipoPromptEnum, LLM # Added LLM

class PromptBase(BaseModel):
    titulo: str
    conteudo: str
    tipo: TipoPromptEnum
    llm_used: Optional[LLM] = None  # New field
    has_reasoning: bool = Field(default=False) # New field
    has_search: bool = Field(default=False)    # New field
    has_files: bool = Field(default=False)     # New field
    has_photo: bool = Field(default=False)     # New field

class PromptCreate(PromptBase):
    pass

class PromptUpdate(BaseModel):
    titulo: Optional[str] = None
    conteudo: Optional[str] = None
    tipo: Optional[TipoPromptEnum] = None
    llm_used: Optional[LLM] = None          # New field, can be None to unset
    has_reasoning: Optional[bool] = None    # New field
    has_search: Optional[bool] = None       # New field
    has_files: Optional[bool] = None        # New field
    has_photo: Optional[bool] = None        # New field

class PromptResponse(PromptBase):
    id: int

    class Config:
        from_attributes = True # For Pydantic v2 (alias for orm_mode)

class FilledParameter(BaseModel):
    titulo: str
    tipo_param: TipoParametroEnum
    valor: Any

class PromptRequest(BaseModel):
    prompt_id: int
    llm_id: int # This refers to the LLM selected for the current request
    parameters: List[FilledParameter]

class PromptWithParams(PromptBase):
    id: int
    parameters: List[FilledParameter]

    class Config:
        from_attributes = True # For Pydantic v2