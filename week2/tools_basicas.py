# Cargamos las variables de entorno (API key)
from dotenv import load_dotenv
load_dotenv()

# tool: decorador que convierte una función Python en una herramienta para Claude
from langchain_core.tools import tool

# El modelo Claude
from langchain_anthropic import ChatAnthropic

# En LangChain 1.x los agentes se crean con LangGraph
from langchain.agents import create_agent

# ChatOllama: el wrapper de LangChain para modelos locales con Ollama
from langchain_ollama import ChatOllama


# Definimos la tool con su docstring — Claude lo lee para saber para qué sirve
@tool
def calcular(operacion: str) -> str:
    """Calcula el resultado de una operación matemática.
    Ejemplo: '2 + 2', '10 * 5', '100 / 4'"""
    resultado = eval(operacion)
    return str(resultado)

# Segunda tool: convierte texto a mayúsculas
# Claude la usará cuando el usuario pida algo en mayúsculas
@tool
def mayusculas(texto: str) -> str:
    """Convierte un texto a mayúsculas."""
    return texto.upper()


# Creamos el modelo
#modelo = ChatAnthropic(model="claude-haiku-4-5", temperature=0)

# create_agent combina el modelo y las tools automáticamente
# No necesita prompt ni AgentExecutor — LangGraph lo gestiona todo
#agente = create_agent(modelo, [calcular, mayusculas])

# Ejecutamos con un mensaje
#respuesta = agente.invoke({
#    "messages": [("human", "¿Cuánto es 15 por 4? Y también escribe 'hola mundo' en mayúsculas.")]
#})

# La respuesta está en el último mensaje
#print(respuesta["messages"][-1].content)

# Creamos el mismo agente pero con llama3.2 corriendo en Ollama
modelo_ollama = ChatOllama(model="llama3.2")
agente_ollama = create_agent(modelo_ollama, [calcular, mayusculas])

respuesta_ollama = agente_ollama.invoke({
   "messages": [("human", "¿Cuánto es 15 por 4? Y también escribe 'hola mundo' en mayúsculas.")]
})

print("\n--- Respuesta con Ollama (llama3.2) ---")
print(respuesta_ollama["messages"][-1].content)