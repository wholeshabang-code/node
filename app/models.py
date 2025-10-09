from sqlalchemy import Column, String, DateTime
from datetime import datetime
from .database import Base

class Note(Base):
    __tablename__ = "notes"

    uuid = Column(String, primary_key=True, index=True)
    content_type = Column(String)  # "url", "text", or "image"
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)