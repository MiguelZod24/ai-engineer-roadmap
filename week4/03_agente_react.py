# week4/03_agente_react.py
# Agente ReAct: Claude decide si usar una herramienta o responder directo

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated  # Annotated es nuevo, lo explicamos después
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode   # Nodo especial que ejecuta herramientas
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, BaseMessage  # BaseMessage es nuevo
from langchain_core.tools import tool    # Decorador para crear herramientas
import operator                          # Para acumular mensajes en el estado

load_dotenv()

# Creamos una herramienta con el decorador @tool
# El decorador le dice a LangChain "esta función es una herramienta
# que Claude puede decidir usar"
@tool
def calculadora(expresion: str) -> str:
    """Calcula una expresión matemática. Ejemplo: '2 + 2' o '1234 * 5678'"""
    try:
        # eval() ejecuta la expresión matemática como código Python
        resultado = eval(expresion)
        return f"El resultado es: {resultado}"
    except:
        return "Error: expresión matemática inválida"

# Lista de herramientas disponibles para el agente
herramientas = [calculadora]

# El estado ahora guarda una LISTA de mensajes en lugar de strings sueltos
# Annotated con operator.add significa "cada vez que un nodo devuelva
# mensajes, añádelos a la lista en lugar de reemplazarla"
class MiEstado(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]

# Inicializamos Claude y le "atamos" las herramientas
# bind_tools le dice a Claude qué herramientas tiene disponibles
llm = ChatAnthropic(
    model="claude-haiku-4-5",
    api_key=os.getenv("ANTHROPIC_API_KEY")
).bind_tools(herramientas)


# Nodo 1: Claude piensa y decide
def nodo_agente(estado: MiEstado) -> dict:
    
    # Tomamos todos los mensajes acumulados en el estado
    mensajes = estado["messages"]
    
    # Claude los procesa y decide: responde o usa una herramienta
    respuesta = llm.invoke(mensajes)
    
    # Devolvemos la respuesta como lista para que se acumule
    return {"messages": [respuesta]}


# Nodo 2: ejecutar la herramienta que Claude eligió
# ToolNode es un nodo especial de LangGraph que sabe leer
# la decisión de Claude y ejecutar la herramienta correcta
nodo_herramienta = ToolNode(herramientas)

# Esta función decide a qué nodo ir después del nodo_agente
# Es el "cerebro" del flujo condicional
def debe_usar_herramienta(estado: MiEstado) -> str:
    
    # Miramos el último mensaje que generó Claude
    ultimo_mensaje = estado["messages"][-1]
    
    # Si Claude quiere usar una herramienta, su mensaje tendrá
    # el campo tool_calls con la herramienta que quiere usar
    if hasattr(ultimo_mensaje, "tool_calls") and ultimo_mensaje.tool_calls:
        return "usar_herramienta"  # → va al nodo_herramienta
    
    # Si no hay tool_calls, Claude ya tiene la respuesta
    return "terminar"  # → termina el grafo

# Construimos el grafo
grafo = StateGraph(MiEstado)

# Añadimos los dos nodos
grafo.add_node("agente", nodo_agente)
grafo.add_node("herramienta", nodo_herramienta)

# Punto de entrada: siempre empieza por el agente
grafo.set_entry_point("agente")

# Edge condicional: después del agente, la función decide a dónde ir
grafo.add_conditional_edges(
    "agente",                    # desde este nodo
    debe_usar_herramienta,       # esta función decide
    {
        "usar_herramienta": "herramienta",  # si devuelve "usar_herramienta" → va aquí
        "terminar": END                      # si devuelve "terminar" → acaba
    }
)

# Después de ejecutar la herramienta → vuelve al agente
# (para que Claude procese el resultado y responda)
grafo.add_edge("herramienta", "agente")

# Compilamos
app = grafo.compile()

# ── Ejecutar ──
if __name__ == "__main__":
    
    # Prueba 1: necesita herramienta
    print("=== Prueba 1: con calculadora ===")
    resultado = app.invoke({
        "messages": [HumanMessage(content="¿Cuánto es 1234 * 5678?")]
    })
    print(resultado["messages"][-1].content)
    
    # Prueba 2: no necesita herramienta
    print("\n=== Prueba 2: sin herramienta ===")
    resultado = app.invoke({
        "messages": [HumanMessage(content="¿Qué es Python?")]
    })
    print(resultado["messages"][-1].content)