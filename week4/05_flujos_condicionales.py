# week4/05_flujos_condicionales.py
# El agente clasifica el mensaje y toma un camino diferente según el tipo

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, BaseMessage
import operator

load_dotenv()

# El estado ahora tiene un campo extra: "categoria"
# Este campo lo rellenará Claude después de analizar el mensaje
class MiEstado(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    categoria: str  # "bug", "duda" o "urgente"


# Inicializamos Claude
llm = ChatAnthropic(
    model="claude-haiku-4-5",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Nodo 1: Claude clasifica el mensaje del usuario
def nodo_clasificar(estado: MiEstado) -> dict:
    
    mensaje = estado["messages"][-1].content
    
    # Le pedimos a Claude que clasifique el mensaje
    # Le damos instrucciones muy claras para que responda
    # solo con una palabra
    prompt = f"""Clasifica este mensaje en una de estas categorías:
- bug: si reporta un error o problema técnico
- duda: si hace una pregunta general
- urgente: si es crítico o necesita atención inmediata

Responde SOLO con una palabra: bug, duda o urgente.

Mensaje: {mensaje}"""
    
    respuesta = llm.invoke([HumanMessage(content=prompt)])
    categoria = respuesta.content.strip().lower()
    
    print(f"[Clasificador] Categoría detectada: {categoria}")
    
    return {"categoria": categoria}


# Nodo 2: gestionar un bug
def nodo_bug(estado: MiEstado) -> dict:
    mensaje = estado["messages"][-1].content
    respuesta = llm.invoke([HumanMessage(
        content=f"El usuario reportó este bug: '{mensaje}'. Responde con empatía y pide más detalles técnicos."
    )])
    return {"messages": [respuesta]}


# Nodo 3: resolver una duda
def nodo_duda(estado: MiEstado) -> dict:
    mensaje = estado["messages"][-1].content
    respuesta = llm.invoke([HumanMessage(
        content=f"El usuario tiene esta duda: '{mensaje}'. Responde de forma clara y concisa."
    )])
    return {"messages": [respuesta]}


# Nodo 4: gestionar urgencia
def nodo_urgente(estado: MiEstado) -> dict:
    mensaje = estado["messages"][-1].content
    respuesta = llm.invoke([HumanMessage(
        content=f"URGENTE: '{mensaje}'. Responde con prioridad máxima e indica que un humano revisará esto."
    )])
    return {"messages": [respuesta]}

# Esta función mira la categoría que detectó Claude
# y decide a qué nodo ir
def decidir_ruta(estado: MiEstado) -> str:
    
    categoria = estado["categoria"]
    
    if categoria == "bug":
        return "es_bug"
    elif categoria == "urgente":
        return "es_urgente"
    else:
        return "es_duda"  # por defecto si no reconoce la categoría

    # Construimos el grafo
grafo = StateGraph(MiEstado)

# Añadimos los cuatro nodos
grafo.add_node("clasificar", nodo_clasificar)
grafo.add_node("bug", nodo_bug)
grafo.add_node("duda", nodo_duda)
grafo.add_node("urgente", nodo_urgente)

# Empezamos siempre por el clasificador
grafo.set_entry_point("clasificar")

# Edge condicional: después de clasificar, decidir_ruta elige el camino
grafo.add_conditional_edges(
    "clasificar",
    decidir_ruta,
    {
        "es_bug":     "bug",
        "es_duda":    "duda",
        "es_urgente": "urgente"
    }
)

# Los tres nodos de respuesta terminan el grafo
grafo.add_edge("bug",     END)
grafo.add_edge("duda",    END)
grafo.add_edge("urgente", END)

app = grafo.compile()

# ── Ejecutar ──
if __name__ == "__main__":
    
    pruebas = [
        "La aplicación se cae cuando hago login",
        "¿Cómo puedo cambiar mi contraseña?",
        "¡El servidor de producción está caído y hay 1000 usuarios sin acceso!"
    ]
    
    for mensaje in pruebas:
        print(f"\n=== Mensaje: '{mensaje}' ===")
        resultado = app.invoke({
            "messages": [HumanMessage(content=mensaje)],
            "categoria": ""
        })
        print(resultado["messages"][-1].content)