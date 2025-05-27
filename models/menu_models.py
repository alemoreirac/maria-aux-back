# models/menu_models.py
from pydantic import BaseModel, Field
from typing import List, Optional
from models.enums import TipoParametro, TipoPrompt, LLM # Added LLM

class MenuParameter(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str] = None
    tipo: TipoParametro

class MenuPromptWithParams(BaseModel):
    id: int
    titulo: str
    descricao: str
    tipo: TipoPrompt
    llm_used: Optional[LLM] = None  # New field
    has_reasoning: bool = Field(default=False) # New field
    has_search: bool = Field(default=False)    # New field
    has_files: bool = Field(default=False)     # New field
    has_photo: bool = Field(default=False)     # New field
    parameters: List[MenuParameter]

    class Config:
        from_attributes = True # For Pydantic v2