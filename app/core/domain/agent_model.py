from pydantic import BaseModel, BeforeValidator, Field
from typing import Annotated, List, Optional
from datetime import datetime
from bson import ObjectId

# Le decimos a Pydantic que cualquier cosa que llegue aquí, antes de validarla,
# la pase por la función str().
PyObjectId = Annotated[str, BeforeValidator(str)]

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
    # Aquí aplicamos nuestro nuevo tipo PyObjectId
    id: PyObjectId = Field(alias="_id")
    documents: List[Document] = []
    created_at: datetime

    class Config:
        populate_by_name = True
        # ¡IMPORTANTE! Añade esta línea para permitir el tipo ObjectId
        arbitrary_types_allowed = True 
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }

class AgentList(BaseModel):
    id: PyObjectId = Field(alias="_id")
    name: str
    prompt: str
    document_count: int

    class Config:
        populate_by_name = True

class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3)
    prompt: Optional[str] = Field(None, min_length=10)

class ChatQuery(BaseModel):
    query: str = Field(..., min_length=1, description="Pregunta del usuario")

class ChatResponse(BaseModel):
    answer: str
    retrieved_sources: List[str] # Para saber qué documentos se usaron