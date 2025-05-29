
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReportCreate(BaseModel):
    user_id: str
    request_id: str
    report_text: Optional[str] = None # Optional field

class ReportResponse(BaseModel):
    id: str
    user_id: str
    request_id: str
    report_text: Optional[str] = None
    created_at: datetime # Pydantic will serialize datetime objects to ISO format