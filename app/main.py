from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.adapters.controllers import agent_controller
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Gestor de Agentes de IA",
    description="Una API para gestionar agentes de IA y su base de conocimiento.",
    version="1.0.0"
)

# Orígenes permitidos 
origins = [
    "http://localhost:3000", # La URL por defecto de Next.js
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],
)

# Incluir el router de los agentes
app.include_router(agent_controller.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido al Gestor de Agentes de IA"}