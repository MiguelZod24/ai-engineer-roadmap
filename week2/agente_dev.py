# Cargamos las variables de entorno (API key)
from dotenv import load_dotenv
load_dotenv()

# tool: decorador para crear herramientas que Claude puede usar
from langchain_core.tools import tool

# El modelo Claude
from langchain_anthropic import ChatAnthropic

# create_agent: crea el agente con LangChain 1.x
from langchain.agents import create_agent

# Path: para manejar rutas de archivos de forma segura
from pathlib import Path


# Tool que lee el contenido de un archivo de código
# Claude la usará cuando necesite ver el contenido de un archivo
@tool
def leer_archivo(ruta: str) -> str:
    """Lee el contenido de un archivo de código y lo devuelve como texto.
    Ejemplo de ruta: 'week2/tools_basicas.py'"""
    try:
        # Construimos la ruta desde la carpeta del proyecto
        archivo = Path("C:/Users/migue/ai-engineer-roadmap") / ruta
        return archivo.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error al leer el archivo: {str(e)}"
    
# Creamos el modelo Claude
modelo = ChatAnthropic(model="claude-haiku-4-5", temperature=0)

# Tool que lista los archivos de una carpeta
# Claude la usará para explorar el proyecto sin saber los nombres exactos
@tool
def listar_archivos(carpeta: str) -> str:
    """Lista todos los archivos de una carpeta del proyecto.
    Ejemplo de carpeta: 'week1', 'week2'"""
    try:
        ruta = Path("C:/Users/migue/ai-engineer-roadmap") / carpeta
        archivos = [f.name for f in ruta.iterdir() if f.is_file()]
        return "\n".join(archivos)
    except Exception as e:
        return f"Error al listar la carpeta: {str(e)}"

# Creamos el agente con la tool de leer archivos
agente = create_agent(modelo, [leer_archivo, listar_archivos])

# Probamos pidiéndole que lea uno de tus archivos de la semana 2
respuesta = agente.invoke({
    "messages": [("human", "¿Qué archivos hay en la carpeta week1?")]
})

# Mostramos todos los mensajes del proceso, no solo el final
for mensaje in respuesta["messages"]:
    print(f"[{mensaje.type.upper()}]: {mensaje.content}\n")
