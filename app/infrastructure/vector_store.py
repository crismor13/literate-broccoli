import os
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings

# Conexión a la base de datos
client = MongoClient(os.getenv("MONGO_URI"))
db_name = os.getenv("MONGO_DB_NAME")
collection_name = "knowledge_vectors" # La colección que configuraste en Atlas Search
collection = client[db_name][collection_name]

# Modelo de Embeddings
# Usamos el modelo más reciente y eficiente de OpenAI
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Función para obtener la Vector Store
def get_vector_store() -> MongoDBAtlasVectorSearch:
    """
    Inicializa y devuelve una instancia de MongoDBAtlasVectorSearch.
    """
    return MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embeddings,
        index_name="vector_index" # El nombre que le diste al índice en Atlas
    )