from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FavouritePromptCreate(BaseModel):
    user_id: str
    prompt_id: int

class FavouritePromptResponse(BaseModel):
    id: str
    user_id: str
    prompt_id: int
    favourited_at: datetime