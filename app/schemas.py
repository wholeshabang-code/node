from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NoteBase(BaseModel):
    content_type: str
    content: str

class NoteCreate(NoteBase):
    pass

class Note(NoteBase):
    uuid: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True