# week4/01_primer_grafo.py
# Nuestro primer grafo con LangGraph

# TypedDict nos permite definir la "forma" del estado del grafo
# (qué campos tiene y de qué tipo son)
from typing import TypedDict

# StateGraph es el constructor del grafo
# END es un marcador especial que significa "el grafo termina aquí"
from langgraph.graph import StateGraph, END

# El Estado es el "paquete de datos" que viaja entre nodos
# TypedDict define qué campos tiene ese paquete y de qué tipo
class MiEstado(TypedDict):
    mensaje: str    # El texto que le mandamos al grafo
    respuesta: str  # La respuesta que generará el nodo

# Un nodo es simplemente una función Python que:
# - Recibe el estado actual completo
# - Devuelve un diccionario con solo los campos que quiere CAMBIAR
def nodo_saludo(estado: MiEstado) -> dict:
    
    # Leemos el mensaje que viene en el estado
    mensaje_recibido = estado["mensaje"]
    
    # Creamos una respuesta (de momento sin LLM, solo texto)
    respuesta = f"¡Hola! Recibí tu mensaje: '{mensaje_recibido}'"
    
    print(f"[Nodo Saludo] Procesando: {mensaje_recibido}")
    
    # Devolvemos solo el campo que queremos actualizar
    return {"respuesta": respuesta} 

# Creamos el grafo indicando qué tipo de estado va a manejar
grafo = StateGraph(MiEstado)

# Registramos el nodo en el grafo (nombre, función)
grafo.add_node("saludo", nodo_saludo)

# Definimos por dónde empieza el grafo
grafo.set_entry_point("saludo")

# Definimos la conexión: después de "saludo" → termina el grafo
grafo.add_edge("saludo", END)

# Compilamos: convierte la definición en algo ejecutable
app = grafo.compile()

# ── Ejecutar ──
if __name__ == "__main__":
    
    # Estado inicial con el que arranca el grafo
    estado_inicial = {
        "mensaje": "me llamo Miguel",
        "respuesta": ""
    }
    
    print("=== Ejecutando el grafo ===")
    
    # invoke() lanza el grafo y devuelve el estado final
    resultado = app.invoke(estado_inicial)
    
    print(f"\n=== Resultado final ===")
    print(f"Respuesta: {resultado['respuesta']}")   