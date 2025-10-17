from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Document(BaseModel):
    file_name: str
    url: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class AgentBase(BaseModel):
    name: str = Field(..., min_length=3, description="Nombre del agente de IA")
    prompt: str = Field(..., min_length=10, description="Prompt descriptivo del agente")

class AgentCreate(AgentBase):
    pass

class Agent(AgentBase):
    id: str = Field(alias="_id")
    documents: List[Document] = []
    created_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }

class AgentList(BaseModel):
    id: str = Field(alias="_id")
    name: str
    prompt: str
    document_count: int

    class Config:
        populate_by_name = True

class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3)
    prompt: Optional[str] = Field(None, min_length=10)