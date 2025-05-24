from pydantic import BaseModel, Field
from typing import Any, List, Optional
from models.enums import TipoParametroEnum ,TipoPromptEnum

class PromptBase(BaseModel):
    titulo: str
    conteudo: str
    tipo: TipoPromptEnum 

class PromptCreate(PromptBase): 
    pass

class PromptUpdate(BaseModel):  
    titulo: Optional[str] = None
    conteudo: Optional[str] = None
    tipo: Optional[TipoPromptEnum] = None

class PromptResponse(PromptBase):
    pass 
  
class FilledParameter(BaseModel): 
    titulo: str
    tipo_param: TipoParametroEnum
    valor: Any
    
class PromptRequest(BaseModel):
    prompt_id: int
    llm_id: int
    parameters: List[FilledParameter]
    
class PromptWithParams(PromptBase): 
    parameters: List[FilledParameter]