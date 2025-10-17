from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional
from datetime import datetime

from app.core.domain.agent_model import Agent, AgentCreate, Document, AgentUpdate
from app.core.ports.agent_repository_port import IAgentRepository

class AgentRepository(IAgentRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.agents

    async def create_agent(self, agent_data: AgentCreate) -> dict:
        # 1. Convierte el modelo de entrada (solo name y prompt) a un diccionario.
        agent_dict = agent_data.model_dump()
        
        # 2. ¡Aquí está la clave! Añade los campos que el servidor debe gestionar.
        agent_dict["created_at"] = datetime.utcnow()
        agent_dict["documents"] = [] # Inicializa la lista de documentos vacía.
        
        # 3. Inserta el diccionario completo en la base de datos.
        result = await self.collection.insert_one(agent_dict)
        
        # 4. Busca y devuelve el documento recién creado.
        created_agent = await self.collection.find_one({"_id": result.inserted_id})
        
        return created_agent

    async def find_agent_by_id(self, agent_id: str) -> Optional[dict]:
        return await self.collection.find_one({"_id": ObjectId(agent_id)})

    async def get_all_agents(self) -> List[dict]:
        # Usamos una agregación para contar los documentos eficientemente
        pipeline = [
            {"$project": {
                "name": 1,
                "prompt": 1,
                "document_count": {"$size": "$documents"}
            }}
        ]
        agents_cursor = self.collection.aggregate(pipeline)
        return await agents_cursor.to_list(length=None)

    async def update_agent(self, agent_id: str, update_data: AgentUpdate) -> Optional[dict]:
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        if not update_dict:
            return await self.find_agent_by_id(agent_id)
            
        await self.collection.update_one(
            {"_id": ObjectId(agent_id)},
            {"$set": update_dict}
        )
        return await self.find_agent_by_id(agent_id)

    async def add_document_to_agent(self, agent_id: str, document: Document) -> bool:
        result = await self.collection.update_one(
            {"_id": ObjectId(agent_id)},
            {"$push": {"documents": document.model_dump()}}
        )
        return result.modified_count > 0
    
    async def remove_document_from_agent(self, agent_id: str, file_name: str) -> bool:
        result = await self.collection.update_one(
            {"_id": ObjectId(agent_id)},
            {"$pull": {"documents": {"file_name": file_name}}}
        )
        return result.modified_count > 0

    async def delete_agent(self, agent_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(agent_id)})
        return result.deleted_count > 0