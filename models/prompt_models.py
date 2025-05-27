# models/prompt_models.py
from pydantic import BaseModel, Field
from typing import Any, List, Optional
from models.enums import TipoParametro, TipoPrompt, LLM, CategoriaPrompt

class PromptBase(BaseModel):
    titulo: str
    conteudo: str
    descricao: str
    categoria: CategoriaPrompt
    tipo: TipoPrompt
    llm_used: Optional[LLM] = None  
    has_reasoning: bool = Field(default=False) 
    has_search: bool = Field(default=False)    
    has_files: bool = Field(default=False)     
    has_photo: bool = Field(default=False)     

class PromptCreate(PromptBase):
    pass

class PromptUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    conteudo: Optional[str] = None
    tipo: Optional[TipoPrompt] = None
    categoria: Optional[CategoriaPrompt] = None      
    llm_used: Optional[LLM] = None         
    has_reasoning: Optional[bool] = None   
    has_search: Optional[bool] = None      
    has_files: Optional[bool] = None       
    has_photo: Optional[bool] = None       

class PromptResponse(PromptBase):
    id: int

    class Config:
        from_attributes = True # For Pydantic v2 (alias for orm_mode)

class FilledParameter(BaseModel):
    titulo: str
    tipo_param: TipoParametro
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