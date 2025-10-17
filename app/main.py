from fastapi import FastAPI
from app.adapters.controllers import agent_controller
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = FastAPI(
    title="Gestor de Agentes de IA",
    description="Una API para gestionar agentes de IA y su base de conocimiento.",
    version="1.0.0"
)

# Incluir el router de los agentes
app.include_router(agent_controller.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido al Gestor de Agentes de IA"}