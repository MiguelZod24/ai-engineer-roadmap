import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

historial = []

# System prompt: define el rol del asistente
SYSTEM_PROMPT = """Eres un asistente experto en Python para AI Engineers.
Respondes siempre en español, de forma directa y con ejemplos de código cuando sea útil.
Si te preguntan algo que no es sobre programación o IA, redirige la conversación al tema."""

print("Chat con Claude (escribe 'salir' para terminar)\n")

while True:
    user_input = input("Tú: ")
    
    if user_input.lower() == "salir":
        break
    
    historial.append({"role": "user", "content": user_input})
    
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=historial
    )
    
    respuesta = response.content[0].text
    historial.append({"role": "assistant", "content": respuesta})
    
    print(f"Claude: {respuesta}\n")