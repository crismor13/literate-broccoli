# 🤖 Gestor de Agentes de IA - Backend

Este proyecto contiene el **backend** para la aplicación de **gestión de Agentes de Inteligencia Artificial**.  
Está desarrollado en **Python** utilizando **FastAPI**, y sigue los principios de la **Arquitectura Hexagonal (Puertos y Adaptadores)** para garantizar un código **limpio**, **desacoplado** y **altamente mantenible**.

---

## 📋 Características Principales

- **Gestión Completa de Agentes (CRUD):** crear, leer, actualizar y eliminar agentes de IA.  
- **Base de Conocimiento Dinámica:** carga de documentos asociados a cada agente (.pdf, .docx, .xlsx, .pptx).  
- **Almacenamiento en la Nube:** integración con **Azure Blob Storage** para el almacenamiento seguro de archivos.  
- **RAG (Retrieval-Augmented Generation):** endpoint de chat que utiliza una **base de datos vectorial en MongoDB Atlas** para responder preguntas basándose únicamente en el contenido de los documentos del agente.  
- **Arquitectura Limpia:** aplicación del patrón **Puertos y Adaptadores**, separando la lógica de negocio del código dependiente de infraestructura.  

---

## 🏗️ Arquitectura del Proyecto

La estructura sigue los principios de la **Arquitectura Hexagonal**, dividiendo el código en capas claramente definidas:

```
app/
├── core/              # Núcleo de la aplicación (el "hexágono")
│   ├── domain/        # Modelos de negocio (Pydantic)
│   ├── ports/         # Interfaces (contratos) del dominio
│   └── services/      # Lógica de negocio y orquestación
│
├── adapters/          # Implementaciones concretas
│   ├── controllers/   # Adaptadores de entrada (endpoints FastAPI)
│   └── repositories/  # Adaptadores de salida (MongoDB, Azure)
│
└── infrastructure/    # Configuración y dependencias externas
```

---

## 🛠️ Tecnologías Utilizadas

| Categoría | Tecnología |
|------------|-------------|
| **Framework** | FastAPI (Python 3.11+) |
| **Base de Datos** | MongoDB (con Motor para operaciones asíncronas) |
| **Vector Search** | MongoDB Atlas Vector Search |
| **Almacenamiento de Archivos** | Azure Blob Storage |
| **Orquestación de IA** | LangChain |
| **Servidor ASGI** | Uvicorn |

---

## 🚀 Instalación y Puesta en Marcha

Sigue estos pasos para ejecutar el proyecto localmente:

### 1️⃣ Prerrequisitos
- Python **3.11 o superior**  
- Una cuenta de **MongoDB Atlas** (con un índice vectorial configurado)  
- Una cuenta de **Azure Storage** (con un contenedor activo)  
- Una **API Key de OpenAI**

---

### 2️⃣ Clonar el Repositorio
```bash
git clone <URL_DEL_REPOSITORIO>
cd backend-folder
```

---

### 3️⃣ Configurar el Entorno Virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar en Windows
.env\Scriptsctivate

# Activar en macOS/Linux
source venv/bin/activate
```

---

### 4️⃣ Instalar Dependencias
```bash
pip install -r requirements.txt
```

---

### 5️⃣ Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
OPENAI_API_KEY="sk-..."
MONGO_URI="mongodb+srv://..."
MONGO_DB_NAME="nombre_de_tu_db"
AZURE_STORAGE_CONNECTION_STRING="..."
AZURE_CONTAINER_NAME="nombre_de_tu_contenedor"
```

---

### 6️⃣ Ejecutar la Aplicación
```bash
uvicorn app.main:app --reload
```

La API estará disponible en:  
👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

Documentación interactiva Swagger:  
👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🌐 Endpoints de la API

| Método | Endpoint | Descripción |
|--------|-----------|-------------|
| **GET** | `/agents/` | Lista todos los agentes |
| **POST** | `/agents/` | Crea un nuevo agente |
| **GET** | `/agents/{agent_id}` | Obtiene los detalles de un agente |
| **PUT** | `/agents/{agent_id}` | Actualiza un agente |
| **DELETE** | `/agents/{agent_id}` | Elimina un agente y sus archivos |
| **POST** | `/agents/{agent_id}/documents` | Sube un documento para un agente |
| **DELETE** | `/agents/{agent_id}/documents/{file_name}` | Elimina un documento de un agente |
| **POST** | `/agents/{agent_id}/chat` | Permite conversar con el agente (RAG) |

---

## 📁 Licencia

Este proyecto es de código privado y está protegido bajo los derechos de su respectivo autor o entidad propietaria.  
Para uso interno o académico, se recomienda solicitar autorización previa.
