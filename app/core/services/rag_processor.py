import tempfile
import requests
from langchain_community.document_loaders import (
    PyPDFLoader, 
    UnstructuredWordDocumentLoader, 
    UnstructuredExcelLoader, 
    UnstructuredPowerPointLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.infrastructure.vector_store import get_vector_store

# Mapeo de extensiones a cargadores de documentos
LOADER_MAPPING = {
    ".pdf": PyPDFLoader,
    ".docx": UnstructuredWordDocumentLoader,
    ".xlsx": UnstructuredExcelLoader,
    ".pptx": UnstructuredPowerPointLoader,
}

def process_and_embed_document(document_url: str, agent_id: str, file_name: str):
    """
    Proceso completo de RAG:
    1. Descarga el archivo desde una URL.
    2. Lo carga en memoria según su tipo.
    3. Lo divide en chunks.
    4. Crea embeddings y los guarda en la base de datos vectorial.
    """
    try:
        # Extrae la extensión para seleccionar el cargador adecuado
        file_extension = f".{file_name.rsplit('.', 1)[1].lower()}"
        if file_extension not in LOADER_MAPPING:
            print(f"Error: Tipo de archivo no soportado {file_extension}")
            return

        # Descarga el archivo a un directorio temporal
        response = requests.get(document_url)
        response.raise_for_status() # Lanza un error si la descarga falla

        with tempfile.NamedTemporaryFile(delete=True, suffix=file_extension) as temp_file:
            temp_file.write(response.content)
            temp_file.flush()

            # 1. Carga el documento
            loader = LOADER_MAPPING[file_extension](temp_file.name)
            documents = loader.load()

            # 2. Divide el documento en chunks
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
            chunks = text_splitter.split_documents(documents)

            # 3. Añade metadatos cruciales a cada chunk para poder filtrar
            for chunk in chunks:
                chunk.metadata["agent_id"] = agent_id
                chunk.metadata["source"] = file_name
            
            # 4. Obtiene la vector store y guarda los chunks
            vector_store = get_vector_store()
            vector_store.add_documents(chunks)
            print(f"Documento '{file_name}' procesado y vectorizado para el agente {agent_id}.")

    except Exception as e:
        # Es importante registrar el error en un sistema de logging real
        print(f"Error procesando el documento {file_name} para el agente {agent_id}: {e}")