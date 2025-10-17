from abc import ABC, abstractmethod

class IStorageRepository(ABC):
    """
    Define el contrato (puerto) para las operaciones de almacenamiento de archivos.
    El núcleo de la aplicación (AgentService) dependerá de esta abstracción.
    """
    
    @abstractmethod
    async def upload_file(self, agent_id: str, file_name: str, file_content: bytes) -> str:
        pass

    @abstractmethod
    async def delete_file(self, agent_id: str, file_name: str) -> bool:
        pass
        
    @abstractmethod
    async def delete_agent_folder(self, agent_id: str) -> bool:
        pass

