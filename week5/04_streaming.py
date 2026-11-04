import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse  # Respuesta que llega en partes
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

# La app FastAPI de siempre
app = FastAPI(
    title="API con Streaming",
    description="Respuestas en tiempo real token por token",
    version="1.0.0"
)

# El LLM — igual que siempre
llm = ChatAnthropic(
    model="claude-haiku-4-5",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# El modelo de la petición — igual que antes
class PreguntaRequest(BaseModel):
    pregunta: str
    system_prompt: str = "Eres un asistente útil y conciso. Responde en español."

# Un generador es una función que produce valores de a uno
# En vez de return, usa "yield" — entrega un valor y pausa
def generar_stream(pregunta: str, system_prompt: str):
    
    mensajes = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=pregunta)
    ]
    
    # .stream() en vez de .invoke() — Claude manda tokens de a poco
    for chunk in llm.stream(mensajes):
        
        # Cada chunk tiene una parte del texto
        if chunk.content:
            # yield entrega ese pedacito y sigue esperando el siguiente
            yield chunk.content


# El endpoint que usa streaming
@app.post("/preguntar-stream")
def preguntar_stream(request: PreguntaRequest):
    
    # StreamingResponse recibe el generador y va mandando cada yield al cliente
    return StreamingResponse(
        generar_stream(request.pregunta, request.system_prompt),
        media_type="text/plain"  # Texto plano, llega como stream
    )

if __name__ == "__main__":
    import uvicorn
    
    # Puerto 8001 para no chocar con el 03_api_rag.py que usa 8000
    uvicorn.run("04_streaming:app", host="0.0.0.0", port=8001, reload=True)

