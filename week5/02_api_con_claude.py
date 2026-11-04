# week5/02_api_con_claude.py
# API REST que conecta FastAPI con Claude para responder preguntas

import os
from fastapi import FastAPI        # El framework de la API
from pydantic import BaseModel     # Para validar los datos que entran
from dotenv import load_dotenv     # Para cargar la API key
from langchain_anthropic import ChatAnthropic   # El modelo de Claude
from langchain_core.messages import HumanMessage  # Formato de mensaje

load_dotenv()

# Creamos la aplicación
app = FastAPI(
    title="API con Claude",
    description="Endpoint que responde preguntas usando Claude",
    version="1.0.0"
)

# Inicializamos Claude una sola vez al arrancar la API
# No dentro del endpoint para no crearlo en cada petición
llm = ChatAnthropic(
    model="claude-haiku-4-5",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Define qué datos espera el endpoint cuando alguien hace POST
# Pydantic valida automáticamente que vengan correctos
class PreguntaRequest(BaseModel):
    pregunta: str                    # La pregunta del usuario (obligatorio)
    system_prompt: str = "Eres un asistente útil y conciso. Responde en español."  # Opcional

# Define qué datos devuelve el endpoint
# Documenta la respuesta en el Swagger automáticamente
class PreguntaResponse(BaseModel):
    pregunta: str      # La pregunta original
    respuesta: str     # La respuesta de Claude
    modelo: str        # El modelo que respondió

# El endpoint recibe una pregunta y devuelve la respuesta de Claude
# response_model le dice a FastAPI qué estructura tendrá la respuesta
@app.post("/preguntar", response_model=PreguntaResponse)
def preguntar(request: PreguntaRequest):
    
    # Construimos los mensajes para Claude
    # SystemMessage define el comportamiento del modelo
    from langchain_core.messages import SystemMessage
    
    mensajes = [
        SystemMessage(content=request.system_prompt),  # Instrucciones para Claude
        HumanMessage(content=request.pregunta)          # La pregunta del usuario
    ]
    
    # Llamamos a Claude con los mensajes
    respuesta = llm.invoke(mensajes)
    
    # Devolvemos la respuesta con el formato de PreguntaResponse
    return PreguntaResponse(
        pregunta=request.pregunta,
        respuesta=respuesta.content,
        modelo="claude-haiku-4-5"
    )


# Endpoint de salud — para verificar que la API está viva
# Es una buena práctica en cualquier API de producción
@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    # Ahora apunta a este archivo: "02_api_con_claude"
    uvicorn.run("02_api_con_claude:app", host="0.0.0.0", port=8000, reload=True)