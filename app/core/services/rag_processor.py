# app/core/services/rag_processor.py
import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, UnstructuredExcelLoader, UnstructuredPowerPointLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.infrastructure.vector_store import get_vector_store

LOADER_MAPPING = {
    ".pdf": PyPDFLoader,
    ".docx": UnstructuredWordDocumentLoader,
    ".xlsx": UnstructuredExcelLoader,
    ".pptx": UnstructuredPowerPointLoader,
}

async def process_and_embed_document(file_content: bytes, agent_id: str, file_name: str):
    print("\n--- INICIANDO PROCESO DE RAG ---")
    temp_file_path = None
    try:
        file_extension = f".{file_name.rsplit('.', 1)[1].lower()}"
        if file_extension not in LOADER_MAPPING:
            print(f"  [ERROR] Tipo de archivo no soportado: {file_extension}")
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        print(f"  [PASO 1/4] Archivo temporal creado en: {temp_file_path}")

        loader = LOADER_MAPPING[file_extension](temp_file_path)
        documents = loader.load()
        print(f"  [PASO 2/4] Documento cargado. Número de páginas/secciones: {len(documents)}")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        chunks = text_splitter.split_documents(documents)
        print(f"  [PASO 3/4] Documento dividido en {len(chunks)} chunks.")

        # Creamos una nueva lista para nuestros documentos limpios.
        cleaned_chunks = []
        for chunk in chunks:
            # Para cada chunk, creamos un nuevo objeto Document
            # que solo contiene el contenido y la metadata que nosotros controlamos.
            new_chunk = Document(
                page_content=chunk.page_content,
                metadata={
                    'source': file_name,  # Usamos el nombre original del archivo
                    'agent_id': agent_id
                }
            )
            cleaned_chunks.append(new_chunk)
        
        print("  [PASO 4/4] Chunks limpiados y preparados con la metadata correcta.")

        vector_store = get_vector_store()
        print("  Intentando guardar chunks limpios en la base de datos vectorial...")
        
        # Usamos la versión asíncrona para no bloquear
        await vector_store.aadd_documents(cleaned_chunks)
        
        print("  ✅ ¡ÉXITO! Los chunks fueron procesados y guardados en la base de datos.")
        print("--- FIN DEL PROCESO DE RAG ---\n")

    except Exception as e:
        print(f"  🚨🚨🚨 ERROR CRÍTICO durante el proceso de RAG: {e}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)