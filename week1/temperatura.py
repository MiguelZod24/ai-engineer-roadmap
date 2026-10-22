import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

pregunta = "Dame un nombre creativo para una app de recetas de cocina."

# --- TEMPERATURA 0 ---
# El modelo elige siempre la palabra más probable
# Respuestas casi idénticas en cada intento
print("=== TEMPERATURA 0 (predecible) ===")
for i in range(3):
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=100,
        messages=[{"role": "user", "content": pregunta}],
        extra_body={"temperature": 0}  # temperatura via extra_body en SDK 1.x
    )
    print(f"Intento {i+1}: {response.content[0].text}\n")

# --- TEMPERATURA 1 ---
# El modelo tiene libertad de elegir palabras menos probables
# Respuestas distintas y más creativas en cada intento
print("=== TEMPERATURA 1 (creativo) ===")
for i in range(3):
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=100,
        messages=[{"role": "user", "content": pregunta}],
        extra_body={"temperature": 1}  # temperatura via extra_body en SDK 1.x
    )
    print(f"Intento {i+1}: {response.content[0].text}\n")