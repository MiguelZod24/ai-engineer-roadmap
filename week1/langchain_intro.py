import os
from dotenv import load_dotenv

# Importamos el modelo de Anthropic a través de LangChain
# LangChain actúa como capa intermedia entre tu código y la API
from langchain_anthropic import ChatAnthropic

# Importamos los tipos de mensajes de LangChain
# HumanMessage = mensaje del usuario
# SystemMessage = system prompt
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

# Inicializamos el modelo a través de LangChain
# En lugar de anthropic.Anthropic(), usamos ChatAnthropic()
# El concepto es el mismo, la sintaxis es más limpia
llm = ChatAnthropic(
    model="claude-haiku-4-5",
    max_tokens=300
)

# Creamos la lista de mensajes usando los tipos de LangChain
# Mismo concepto que antes: system prompt + mensaje del usuario
mensajes = [
    SystemMessage(content="Eres un asistente experto en Python. Respondes en español y de forma concisa."),
    HumanMessage(content="¿Qué es LangChain y para qué sirve?")
]

# Llamamos al modelo con invoke() — equivalente al messages.create() de antes
response = llm.invoke(mensajes)

# En LangChain la respuesta viene en response.content directamente
print(response.content)