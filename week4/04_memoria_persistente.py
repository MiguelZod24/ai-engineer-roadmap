# week4/04_memoria_persistente.py
# El agente recuerda conversaciones entre ejecuciones con MemorySaver

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver  # Guarda el estado en memoria
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, BaseMessage
import operator

load_dotenv()

# El estado es igual que antes — una lista de mensajes acumulados
class MiEstado(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]


# Inicializamos Claude igual que siempre
llm = ChatAnthropic(
    model="claude-haiku-4-5",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


# El nodo es igual que en los archivos anteriores
# Recibe los mensajes acumulados y Claude responde
def nodo_agente(estado: MiEstado) -> dict:
    mensajes = estado["messages"]
    respuesta = llm.invoke(mensajes)
    return {"messages": [respuesta]}

# Creamos el checkpointer — es quien guarda el estado
memoria = MemorySaver()

# Construimos el grafo igual que siempre
grafo = StateGraph(MiEstado)
grafo.add_node("agente", nodo_agente)
grafo.set_entry_point("agente")
grafo.add_edge("agente", END)

# La única diferencia: pasamos el checkpointer al compilar
# Esto activa la memoria persistente
app = grafo.compile(checkpointer=memoria)

if __name__ == "__main__":
    
    # El thread_id identifica la conversación
    # Siempre que uses el mismo thread_id, el agente recuerda
    config = {"configurable": {"thread_id": "conversacion_miguel"}}
    
    # Turno 1: le decimos nuestro nombre
    print("=== Turno 1 ===")
    resultado = app.invoke(
        {"messages": [HumanMessage(content="Hola, me llamo Miguel")]},
        config=config  # ← aquí pasamos el thread_id
    )
    print(resultado["messages"][-1].content)
    
    # Turno 2: preguntamos algo que requiere recordar el turno 1
    print("\n=== Turno 2 ===")
    resultado = app.invoke(
        {"messages": [HumanMessage(content="¿Cómo me llamo?")]},
        config=config  # ← mismo thread_id = misma conversación
    )
    print(resultado["messages"][-1].content)
    
    # Turno 3: otra conversación distinta, sin memoria del turno 1 y 2
    print("\n=== Turno 3 (conversación nueva) ===")
    config_nueva = {"configurable": {"thread_id": "conversacion_nueva"}}
    resultado = app.invoke(
        {"messages": [HumanMessage(content="¿Cómo me llamo?")]},
        config=config_nueva  # ← thread_id diferente = no recuerda nada
    )
    print(resultado["messages"][-1].content)
