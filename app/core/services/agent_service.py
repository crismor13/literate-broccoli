from fastapi import UploadFile, HTTPException, status
from typing import List

from app.core.domain.agent_model import AgentCreate, Agent, Document, AgentUpdate, AgentList
from app.adapters.repositories.agent_repository import AgentRepository
from app.adapters.repositories.storage_repository import StorageRepository
from fastapi import BackgroundTasks 
from .rag_processor import process_and_embed_document

class AgentService:
    def __init__(self, agent_repo: AgentRepository, storage_repo: StorageRepository):
        self.agent_repo = agent_repo
        self.storage_repo = storage_repo

    async def create_agent(self, agent_data: AgentCreate) -> Agent:
        created_agent = await self.agent_repo.create_agent(agent_data)
        # Aquí podrías iniciar la creación de la "carpeta" en el storage si fuera necesario,
        # aunque Azure Blob Storage crea la estructura virtualmente con el nombre del blob.
        return Agent.model_validate(created_agent)

    async def get_agent_by_id(self, agent_id: str) -> Agent:
        agent = await self.agent_repo.find_agent_by_id(agent_id)
        if not agent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
        return Agent.model_validate(agent)

    async def get_all_agents(self) -> List[AgentList]:
        agents = await self.agent_repo.get_all_agents()
        return [AgentList.model_validate(agent) for agent in agents]

    async def update_agent(self, agent_id: str, update_data: AgentUpdate) -> Agent:
        # Primero, verifica que el agente exista
        await self.get_agent_by_id(agent_id) 
        updated_agent = await self.agent_repo.update_agent(agent_id, update_data)
        return Agent.model_validate(updated_agent)

    async def upload_document(self, agent_id: str, file: UploadFile, background_tasks: BackgroundTasks) -> Agent:
        # Verifica que el agente exista
        agent = await self.get_agent_by_id(agent_id)
        
        # Sube el archivo al storage
        file_content = await file.read()
        file_url = await self.storage_repo.upload_file(agent_id, file.filename, file_content)

        # Crea el objeto Document y lo añade a la base de datos
        new_document = Document(file_name=file.filename, url=file_url)
        await self.agent_repo.add_document_to_agent(agent_id, new_document)

        background_tasks.add_task(
            process_and_embed_document, 
            document_url=file_url, 
            agent_id=agent_id, 
            file_name=file.filename
        )
        
        # Devuelve el agente actualizado
        return await self.get_agent_by_id(agent_id)

    async def delete_document(self, agent_id: str, file_name: str):
        agent = await self.get_agent_by_id(agent_id)
        
        # Elimina del storage
        deleted_from_storage = await self.storage_repo.delete_file(agent_id, file_name)
        if not deleted_from_storage:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete file from storage")

        # Elimina de la base de datos
        await self.agent_repo.remove_document_from_agent(agent_id, file_name)
        return {"message": "Document deleted successfully"}
        
    async def delete_agent(self, agent_id: str):
        agent = await self.get_agent_by_id(agent_id)

        # Elimina la carpeta y sus contenidos del storage
        await self.storage_repo.delete_agent_folder(agent_id)
        
        # Elimina el agente de la base de datos
        deleted = await self.agent_repo.delete_agent(agent_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete agent from database")
            
        return {"message": "Agent and associated files deleted successfully"}