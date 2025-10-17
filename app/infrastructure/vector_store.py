# app/infrastructure/vector_store.py
import os
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings

# Solo define las constantes aquí
DB_NAME = os.getenv("MONGO_DB_NAME")
COLLECTION_NAME = "knowledge_vectors"
INDEX_NAME = "vector_index"
MONGO_URI = os.getenv("MONGO_URI")

def get_vector_store() -> MongoDBAtlasVectorSearch:
    """
    Inicializa y devuelve una instancia de MongoDBAtlasVectorSearch.
    La conexión se crea cuando se llama a la función.
    """
    # La conexión y los clientes se crean aquí, no al importar el archivo
    client = MongoClient(MONGO_URI)
    collection = client[DB_NAME][COLLECTION_NAME]
    
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    return MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embeddings,
        index_name=INDEX_NAME
    )