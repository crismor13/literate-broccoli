# app/core/ports/agent_repository_port.py

from abc import ABC, abstractmethod
from typing import List, Optional
from app.core.domain.agent_model import AgentCreate, AgentUpdate, Document

class IAgentRepository(ABC):
    """
    Defines the contract (puerto) for the operations of agent persistence.
    The core of the application (AgentService) will depend on this abstraction.
    """

    @abstractmethod
    async def create_agent(self, agent_data: AgentCreate) -> dict:
        pass

    @abstractmethod
    async def find_agent_by_id(self, agent_id: str) -> Optional[dict]:
        pass

    @abstractmethod
    async def get_all_agents(self) -> List[dict]:
        pass

    @abstractmethod
    async def update_agent(self, agent_id: str, update_data: AgentUpdate) -> Optional[dict]:
        pass

    @abstractmethod
    async def add_document_to_agent(self, agent_id: str, document: Document) -> bool:
        pass

    @abstractmethod
    async def remove_document_from_agent(self, agent_id: str, file_name: str) -> bool:
        pass

    @abstractmethod
    async def delete_agent(self, agent_id: str) -> bool:
        pass