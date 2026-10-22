# Cargamos las variables de entorno (API key de Anthropic)
from dotenv import load_dotenv
load_dotenv()

# ChatPromptTemplate: para definir el molde del prompt
# MessagesPlaceholder: para insertar el historial dentro del prompt
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# HumanMessage y AIMessage: para construir el historial de mensajes
from langchain_core.messages import HumanMessage, AIMessage

# ChatAnthropic: el modelo Claude dentro de LangChain
from langchain_anthropic import ChatAnthropic

# StrOutputParser: convierte la respuesta de Claude a texto plano
from langchain_core.output_parsers import StrOutputParser

# Creamos la conexión con Claude
# temperature=0 para respuestas consistentes y sin aleatoriedad
modelo = ChatAnthropic(model="claude-haiku-4-5", temperature=0)

# Definimos el prompt con tres partes:
# 1. system: le dice a Claude cómo debe comportarse
# 2. MessagesPlaceholder: aquí se insertará el historial de la conversación
# 3. human: la pregunta actual del usuario
prompt = ChatPromptTemplate.from_messages([
    ("system", """Eres un asistente de aprendizaje especializado en tecnología e IA.
    Cuando el usuario mencione un tema, explícalo de forma clara y simple.
    Al finalizar cada explicación, genera una pregunta de práctica sobre el tema."""),
    MessagesPlaceholder(variable_name="historial"),
    ("human", "{entrada}")
])

# Conectamos las piezas: prompt -> modelo -> texto plano
chain = prompt | modelo | StrOutputParser()

# El historial empieza vacío, se irá llenando con cada turno
historial = []

print("=== Asistente de Aprendizaje ===")
print("Escribe cualquier tema tecnológico que quieras aprender.")
print("Escribe 'salir' para terminar.\n")

while True:
    # Leemos lo que escribe el usuario
    entrada = input("Tú: ")

    if entrada.lower() == "salir":
        print("¡Hasta luego! Sigue aprendiendo.")
        break

    # Ejecutamos la chain con el historial actual y la entrada del usuario
    respuesta = chain.invoke({
        "historial": historial,
        "entrada": entrada
    })

    print(f"\nAsistente: {respuesta}\n")

    # Guardamos el turno actual en el historial
    # Así Claude recordará esta conversación en el siguiente turno
    historial.append(HumanMessage(content=entrada))
    historial.append(AIMessage(content=respuesta))