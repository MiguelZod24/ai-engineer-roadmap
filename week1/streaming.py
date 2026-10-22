import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

print("Respuesta con streaming:\n")

# with client.messages.stream() abre una conexión de streaming
# en lugar de esperar toda la respuesta, recibimos fragmentos
with client.messages.stream(
    model="claude-haiku-4-5",
    max_tokens=300,
    messages=[
        {"role": "user", "content": "Explícame qué es el streaming en APIs en 5 frases."}
    ]
) as stream:
    # text_stream nos da cada fragmento de texto según llega
    # end="" evita saltos de línea entre fragmentos
    # flush=True fuerza que se muestre inmediatamente en pantalla
    for text in stream.text_stream:
        print(text, end="", flush=True)

# Salto de línea al final
print("\n\nStreaming completado.")