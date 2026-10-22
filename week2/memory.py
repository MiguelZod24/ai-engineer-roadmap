from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_anthropic import ChatAnthropic

modelo = ChatAnthropic(model="claude-haiku-4-5", temperature=0)

# El historial empieza con un mensaje de sistema
historial = [
    SystemMessage(content="Eres un asistente amigable que recuerda todo lo que el usuario dice.")
]

print("Chat con memoria. Escribe 'salir' para terminar.\n")

# Bucle infinito — se repite hasta que el usuario escriba 'salir'
while True:
    # El usuario escribe su mensaje
    entrada = input("Tú: ")

    # Condición de salida
    if entrada.lower() == "salir":
        print("¡Hasta luego!")
        break

    # Agregamos el mensaje del usuario al historial
    historial.append(HumanMessage(content=entrada))

    # Le mandamos el historial completo a Claude
    respuesta = modelo.invoke(historial)

    # Mostramos la respuesta
    print(f"Claude: {respuesta.content}\n")

    # Guardamos la respuesta de Claude en el historial
    historial.append(AIMessage(content=respuesta.content))
