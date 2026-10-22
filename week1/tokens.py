import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Llamada normal
response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=300,
    messages=[
        {"role": "user", "content": "Explícame qué es un LLM en 3 frases simples."}
    ]
)

# El objeto response incluye información de uso de tokens
print(f"Tokens de entrada (input):  {response.usage.input_tokens}")
print(f"Tokens de salida (output):  {response.usage.output_tokens}")
print(f"Total tokens:               {response.usage.input_tokens + response.usage.output_tokens}")
print(f"\nRespuesta:\n{response.content[0].text}")