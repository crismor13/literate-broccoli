import os
from azure.storage.blob.aio import BlobServiceClient
from app.core.ports.storage_repository_port import IStorageRepository

AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME", "knowledge-base")

class StorageRepository(IStorageRepository):
    def __init__(self, client: BlobServiceClient):
        self.client = client

    async def upload_file(self, agent_id: str, file_name: str, file_content: bytes) -> str:
        blob_name = f"{agent_id}/{file_name}"
        blob_client = self.client.get_blob_client(container=AZURE_CONTAINER_NAME, blob=blob_name)
        await blob_client.upload_blob(file_content, overwrite=True)
        return blob_client.url

    async def delete_file(self, agent_id: str, file_name: str) -> bool:
        blob_name = f"{agent_id}/{file_name}"
        blob_client = self.client.get_blob_client(container=AZURE_CONTAINER_NAME, blob=blob_name)
        try:
            await blob_client.delete_blob()
            return True
        except Exception:
            # Puedes manejar excepciones más específicas de Azure si lo necesitas
            return False
            
    async def delete_agent_folder(self, agent_id: str) -> bool:
        container_client = self.client.get_container_client(AZURE_CONTAINER_NAME)
        blobs = container_client.list_blobs(name_starts_with=f"{agent_id}/")
        try:
            async for blob in blobs:
                await container_client.delete_blob(blob.name)
            return True
        except Exception:
            return False