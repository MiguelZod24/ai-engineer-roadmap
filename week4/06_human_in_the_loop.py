# week4/06_human_in_the_loop.py
# El agente se pausa y espera confirmación humana antes de actuar

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver  # Necesario para pausar el grafo
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, BaseMessage
import operator

load_dotenv()

# El estado tiene un campo "accion" que guarda lo que el agente
# quiere hacer antes de pedir confirmación
class MiEstado(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    accion_propuesta: str  # Lo que el agente quiere hacer
    aprobado: bool         # Si el humano aprobó o no


# Inicializamos Claude
llm = ChatAnthropic(
    model="claude-haiku-4-5",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Nodo 1: el agente analiza el mensaje y propone una acción
def nodo_agente(estado: MiEstado) -> dict:
    
    mensaje = estado["messages"][-1].content
    
    # Claude decide qué acción tomar pero NO la ejecuta todavía
    prompt = f"""El usuario dice: '{mensaje}'
    
Propón una acción concreta para responder. Sé específico y breve.
Ejemplo: 'Crear un ticket de bug con prioridad alta'
Responde SOLO con la acción propuesta, sin explicaciones."""
    
    respuesta = llm.invoke([HumanMessage(content=prompt)])
    accion = respuesta.content.strip()
    
    print(f"\n[Agente] Acción propuesta: {accion}")
    
    return {"accion_propuesta": accion}


# Nodo 2: ejecutar la acción aprobada
def nodo_ejecutar(estado: MiEstado) -> dict:
    
    accion = estado["accion_propuesta"]
    
    # Aquí iría el código real (crear ticket, enviar email, etc.)
    # Por ahora simulamos la ejecución
    print(f"[Ejecutar] Ejecutando: {accion}")
    
    respuesta = llm.invoke([HumanMessage(
        content=f"Confirma que ejecutaste esta acción: '{accion}'. Responde brevemente."
    )])
    
    return {"messages": [respuesta]}


# Nodo 3: acción cancelada por el humano
def nodo_cancelar(estado: MiEstado) -> dict:
    
    print("[Cancelar] Acción cancelada por el usuario")
    
    from langchain_core.messages import AIMessage
    return {"messages": [AIMessage(content="Acción cancelada. ¿En qué más puedo ayudarte?")]}


# Función condicional: mira si el humano aprobó o no
# Función condicional: mira si el humano aprobó o no
# Esta función se ejecuta DESPUÉS de que el humano responde
# gracias al interrupt_after que pausa el grafo
def decision_humano(estado: MiEstado) -> str:
    
    # Si aprobado es True el humano dijo "s"
    if estado.get("aprobado", False):
        return "ejecutar"
    
    # Si aprobado es False o no existe → cancelar
    return "cancelar"

# El checkpointer es obligatorio para poder pausar el grafo
memoria = MemorySaver()

# Construimos el grafo
grafo = StateGraph(MiEstado)

# Añadimos los tres nodos
grafo.add_node("agente", nodo_agente)
grafo.add_node("ejecutar", nodo_ejecutar)
grafo.add_node("cancelar", nodo_cancelar)

# Empezamos siempre por el agente
grafo.set_entry_point("agente")

# Solo usamos el edge condicional — eliminamos los add_edge duplicados
# que causaban que el agente se ejecutara dos veces
grafo.add_conditional_edges(
    "agente",          # desde este nodo
    decision_humano,   # esta función lee "aprobado" y decide el camino
    {
        "ejecutar": "ejecutar",  # aprobado=True → ejecutar la acción
        "cancelar": "cancelar"   # aprobado=False → cancelar
    }
)

# Después de ejecutar o cancelar → termina el grafo
grafo.add_edge("ejecutar", END)
grafo.add_edge("cancelar", END)

# Compilamos con memoria y con pausa después del nodo "agente"
app = grafo.compile(
    checkpointer=memoria,
    interrupt_after=["agente"]  # pausa aquí y espera al humano
)

if __name__ == "__main__":
    
    config = {"configurable": {"thread_id": "sesion_hitl"}}
    
    # ── Paso 1: lanzamos el grafo, se pausa después del nodo agente ──
    print("=== Paso 1: El agente propone una acción ===")
    app.invoke(
        {
            "messages": [HumanMessage(content="El servidor de producción está caído")],
            "accion_propuesta": "",
            "aprobado": False
        },
        config=config
    )
    
    # En este punto el grafo está PAUSADO
    # El humano decide si aprobar o no
    print("\n=== Paso 2: Decisión humana ===")
    confirmacion = input("¿Apruebas esta acción? (s/n): ").strip().lower()
    aprobado = confirmacion == "s"
    
    # Paso 3: actualizamos el estado con la decisión del humano
    # update_state inyecta el valor directamente en el estado pausado
    # sin relanzar el nodo agente
    app.update_state(
    config,
        {"aprobado": aprobado}  # solo actualizamos este campo
    )

# Reanudamos el grafo desde donde se pausó
resultado = app.invoke(None, config=config)
    
print("\n=== Resultado final ===")
print(resultado["messages"][-1].content)