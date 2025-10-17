from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from typing import List

from app.core.domain.agent_model import AgentCreate, Agent, AgentList, AgentUpdate
from app.core.services.agent_service import AgentService
from app.adapters.repositories.agent_repository import AgentRepository
from app.adapters.repositories.storage_repository import StorageRepository
from app.infrastructure.database import get_db
from app.infrastructure.storage import get_blob_service_client

router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
)

# Helper para la inyección de dependencias
def get_agent_service(
    db=Depends(get_db),
    blob_client=Depends(get_blob_service_client)
) -> AgentService:
    agent_repo = AgentRepository(db)
    storage_repo = StorageRepository(blob_client)
    return AgentService(agent_repo, storage_repo)


ALLOWED_EXTENSIONS = {"pdf", "docx", "xlsx", "pptx"}

def is_allowed_file(filename: str):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@router.post("/", response_model=Agent, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    service: AgentService = Depends(get_agent_service)
):
    """
    Crea un nuevo agente de IA.
    """
    return await service.create_agent(agent_data)

@router.get("/", response_model=List[AgentList])
async def list_agents(service: AgentService = Depends(get_agent_service)):
    """
    Devuelve la lista de todos los agentes con un contador de sus documentos.
    """
    return await service.get_all_agents()

@router.get("/{agent_id}", response_model=Agent)
async def get_agent_details(
    agent_id: str,
    service: AgentService = Depends(get_agent_service)
):
    """
    Muestra los datos de un agente, incluyendo sus documentos.
    """
    return await service.get_agent_by_id(agent_id)

@router.put("/{agent_id}", response_model=Agent)
async def update_agent(
    agent_id: str,
    update_data: AgentUpdate,
    service: AgentService = Depends(get_agent_service)
):
    """
    Modifica el nombre y/o prompt de un agente existente.
    """
    return await service.update_agent(agent_id, update_data)

@router.post("/{agent_id}/documents", response_model=Agent)
async def upload_agent_document(
    agent_id: str,
    file: UploadFile = File(...),
    service: AgentService = Depends(get_agent_service)
):
    """
    Sube un documento para un agente específico.
    Valida la extensión del archivo.
    """
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension not allowed. Allowed extensions are: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    return await service.upload_document(agent_id, file)

@router.delete("/{agent_id}/documents/{file_name}", status_code=status.HTTP_200_OK)
async def delete_agent_document(
    agent_id: str,
    file_name: str,
    service: AgentService = Depends(get_agent_service)
):
    """
    Elimina un documento específico de un agente.
    """
    return await service.delete_document(agent_id, file_name)

@router.delete("/{agent_id}", status_code=status.HTTP_200_OK)
async def delete_agent(
    agent_id: str,
    service: AgentService = Depends(get_agent_service)
):
    """
    Elimina un agente y todos sus archivos asociados.
    """
    return await service.delete_agent(agent_id)