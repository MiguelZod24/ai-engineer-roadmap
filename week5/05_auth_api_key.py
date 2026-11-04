import os
from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

# Importamos la función que acabamos de crear en auth.py
# Como auth.py está en la misma carpeta, Python lo encuentra solo
from auth import verificar_api_key

# Cargamos las variables del .env (ANTHROPIC_API_KEY y API_KEY)
load_dotenv()

API_KEY_CORRECTA = os.getenv("API_KEY")

# La app FastAPI — igual que en 04_streaming.py, solo cambia el título
app = FastAPI(
    title="API con Autenticación",
    description="Streaming protegido con API key",
    version="1.0.0"
)

# El LLM de Anthropic — sin cambios respecto a 04_streaming.py
llm = ChatAnthropic(
    model="claude-haiku-4-5",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Define la forma que debe tener el JSON que nos manda el cliente
# FastAPI usa esto para validar automáticamente los datos de entrada
class PreguntaRequest(BaseModel):
    pregunta: str  # Obligatorio: el texto que el usuario quiere preguntar

    # Opcional: si el cliente no lo manda, se usa este valor por defecto
    system_prompt: str = "Eres un asistente útil y conciso. Responde en español."

# Un generador: en vez de "return" usa "yield" para entregar
# valores de a uno, sin esperar a tener la respuesta completa
def generar_stream(pregunta: str, system_prompt: str):

    # Armamos la lista de mensajes para el LLM: system + pregunta del usuario
    mensajes = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=pregunta)
    ]

    # .stream() en vez de .invoke() — Claude va mandando pedazos de texto
    # a medida que los genera, no espera a terminar toda la respuesta
    for chunk in llm.stream(mensajes):

        # Cada "chunk" trae un trocito de texto (puede venir vacío a veces)
        if chunk.content:
            # yield entrega ese trocito al que llamó la función y se pausa
            # hasta que le pidan el siguiente
            yield chunk.content

# Este es el endpoint que de verdad queremos proteger
@app.post("/preguntar-stream")
def preguntar_stream(
    request: PreguntaRequest,

    # AQUÍ está la autenticación en acción:
    # Depends() le dice a FastAPI "antes de ejecutar esta función,
    # corre verificar_api_key() primero"
    # Si verificar_api_key() lanza un HTTPException (401 o 403),
    # FastAPI corta la ejecución AHÍ y nunca llega a este código
    api_key: str = Depends(verificar_api_key)
):

    # Si llegamos hasta aquí, significa que la API key era correcta.
    # El resto es exactamente igual que en 04_streaming.py
    return StreamingResponse(
        generar_stream(request.pregunta, request.system_prompt),
        media_type="text/plain"
    )

if __name__ == "__main__":
    import uvicorn

    # Puerto 8002 — distinto a los anteriores (8000 para RAG, 8001 para streaming)
    # así puedes tener varias APIs corriendo a la vez sin que choquen
    uvicorn.run("05_auth_api_key:app", host="0.0.0.0", port=8002, reload=True)