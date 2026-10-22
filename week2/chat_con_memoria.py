from dotenv import load_dotenv
load_dotenv()

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser

modelo = ChatAnthropic(model="claude-haiku-4-5", temperature=0)

# MessagesPlaceholder reserva un espacio para insertar
# el historial completo de mensajes dentro del prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente amigable que recuerda todo lo que el usuario dice."),
    MessagesPlaceholder(variable_name="historial"),
    ("human", "{entrada}")
])

# Conectamos todo con el operador pipe
chain = prompt | modelo | StrOutputParser()

# El historial empieza vacío
historial = []

print("Chat con memoria y template. Escribe 'salir' para terminar.\n")

while True:
    entrada = input("Tú: ")

    if entrada.lower() == "salir":
        print("¡Hasta luego!")
        break

    # Ejecutamos la chain pasando el historial y la entrada actual
    respuesta = chain.invoke({
        "historial": historial,
        "entrada": entrada
    })

    print(f"Claude: {respuesta}\n")

    # Actualizamos el historial con el nuevo turno
    historial.append(HumanMessage(content=entrada))
    historial.append(AIMessage(content=respuesta))