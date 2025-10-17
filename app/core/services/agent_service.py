from fastapi import UploadFile, HTTPException, status
from typing import List

from app.core.domain.agent_model import AgentCreate, Agent, Document, AgentUpdate, AgentList
from app.adapters.repositories.agent_repository import AgentRepository
from app.adapters.repositories.storage_repository import StorageRepository
from fastapi import BackgroundTasks 
from .rag_processor import process_and_embed_document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from app.infrastructure.vector_store import get_vector_store
from app.core.domain.agent_model import ChatQuery, ChatResponse
from app.infrastructure.database import get_db

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
        agent = await self.get_agent_by_id(agent_id)
        
        file_content = await file.read() # Ya tenemos el contenido aquí
        file_url = await self.storage_repo.upload_file(agent_id, file.filename, file_content)

        new_document = Document(file_name=file.filename, url=file_url)
        await self.agent_repo.add_document_to_agent(agent_id, new_document)
        
        # Pasamos el contenido del archivo en lugar de la URL
        background_tasks.add_task(
            process_and_embed_document, 
            file_content=file_content, # Pasamos los bytes
            agent_id=agent_id, 
            file_name=file.filename
        )
        
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
    

    async def chat_with_agent(self, agent_id: str, chat_query: ChatQuery) -> ChatResponse:
        # 1. Verificar que el agente existe
        agent = await self.get_agent_by_id(agent_id)
        
        # 2. Obtener la instancia del Vector Store asíncrono
        vector_store = get_vector_store()

        # 3. Le decimos que solo busque en los documentos donde agent_id sea igual al que queremos.
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 5,  # El número de documentos más relevantes a recuperar
                "pre_filter": {"agent_id": agent_id}
            }
        )

        # 4. Definir el prompt template
        template = f"""
        System Prompt: {agent.prompt}
        Usa la siguiente información de contexto para responder la pregunta. Si no sabes la respuesta basándote en el contexto, di que no tienes suficiente información. No inventes una respuesta.
        
        Contexto:
        {{context}}
        
        Pregunta:
        {{question}}
        
        Respuesta útil:
        """
        prompt = ChatPromptTemplate.from_template(template)
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        
        def format_docs(docs):
            # Esta función concatena el contenido de los documentos recuperados
            return "\n\n".join(doc.page_content for doc in docs)

        # 5. Construir la cadena RAG usando LangChain Expression Language (LCEL)
        rag_chain = (
            # El retriever se invoca primero para obtener los documentos
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        # 6. Invocar la cadena de forma asíncrona
        print(f"Buscando en documentos para el agente: {agent_id} con la pregunta: '{chat_query.query}'")
        answer = await rag_chain.ainvoke(chat_query.query)
        
        # 7. Recuperar las fuentes para la respuesta
        retrieved_docs = await retriever.ainvoke(chat_query.query)
        if not retrieved_docs:
            print("ADVERTENCIA: El retriever no devolvió ningún documento.")
            return ChatResponse(
                answer="Lo siento, no pude encontrar información relevante en los documentos para responder a tu pregunta.",
                retrieved_sources=[]
            )
            
        sources = list(set([doc.metadata.get("source", "unknown") for doc in retrieved_docs]))

        return ChatResponse(answer=answer, retrieved_sources=sources)