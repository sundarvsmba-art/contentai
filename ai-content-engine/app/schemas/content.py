from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ContentCreate(BaseModel):
    topic: str
    category: Optional[str] = None


class ContentOut(BaseModel):
    id: int
    topic: str
    script: str
    status: str
    created_at: datetime

    class Config:
        orm_mode = True
