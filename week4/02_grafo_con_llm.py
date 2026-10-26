# week4/02_grafo_con_llm.py
# Igual que el anterior pero ahora el nodo usa Claude para responder

import os                          # Para leer la API key del entorno
from dotenv import load_dotenv     # Para cargar el archivo .env
from typing import TypedDict       # Para definir la estructura del estado
from langgraph.graph import StateGraph, END  # El grafo y el nodo final
from langchain_anthropic import ChatAnthropic  # El modelo de Claude
from langchain_core.messages import HumanMessage  # Formato de mensaje

# Cargamos las variables del archivo .env (donde está la API key)
load_dotenv()

# El estado ahora tiene un campo extra: "historial"
# para guardar los mensajes que van pasando por el grafo
class MiEstado(TypedDict):
    mensaje: str     # Lo que escribe el usuario
    respuesta: str   # Lo que responderá Claude

# Inicializamos el modelo de Claude
# Lo sacamos de fuera del nodo para no crearlo en cada llamada
llm = ChatAnthropic(
    model="claude-haiku-4-5",         # El modelo más rápido y barato
    api_key=os.getenv("ANTHROPIC_API_KEY")  # La key del .env
)

# Este nodo ya no genera una respuesta de texto fijo
# sino que le pasa el mensaje a Claude y devuelve su respuesta
def nodo_claude(estado: MiEstado) -> dict:
    
    # Leemos el mensaje del usuario desde el estado
    mensaje_usuario = estado["mensaje"]
    
    print(f"[Nodo Claude] Enviando a Claude: {mensaje_usuario}")
    
    # HumanMessage es el formato que entiende LangChain/Claude
    # Es equivalente al rol "user" que ya conoces de la semana 1
    mensaje = HumanMessage(content=mensaje_usuario)
    
    # Llamamos a Claude con el mensaje
    # .invoke() es la llamada síncrona (espera la respuesta completa)
    respuesta_claude = llm.invoke([mensaje])
    
    # respuesta_claude.content tiene el texto de la respuesta
    return {"respuesta": respuesta_claude.content}

# Construimos el grafo igual que antes, pero ahora el nodo usa Claude
grafo = StateGraph(MiEstado)

# Registramos el nodo (ahora se llama "claude" y usa nodo_claude)
grafo.add_node("claude", nodo_claude)

# Punto de entrada
grafo.set_entry_point("claude")

# Conexión: después de "claude" → termina
grafo.add_edge("claude", END)

# Compilamos
app = grafo.compile()

# ── Ejecutar ──
if __name__ == "__main__":
    
    estado_inicial = {
        "mensaje": "Explícame en una frase qué es Python",
        "respuesta": ""
    }
    
    print("=== Ejecutando el grafo con Claude ===")
    
    resultado = app.invoke(estado_inicial)
    
    print(f"\n=== Respuesta de Claude ===")
    print(resultado["respuesta"])