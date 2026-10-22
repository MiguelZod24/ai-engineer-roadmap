# Importamos el SDK de OpenAI — Ollama es compatible con su formato
from openai import OpenAI

# Creamos el cliente apuntando a Ollama en tu máquina
# Ollama expone una API compatible con OpenAI en el puerto 11434
# api_key: no se usa pero el SDK lo exige — ponemos cualquier texto
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

# Llamada al modelo local — mismo concepto que con Claude y OpenAI
# model: llama3.2 que descargamos antes
# max_tokens: límite de la respuesta
response = client.chat.completions.create(
    model="llama3.2",
    max_tokens=300,
    messages=[
        {"role": "user", "content": "Explícame qué es un LLM en 3 frases simples."}
    ]
)

# Extraemos e imprimimos la respuesta
print(response.choices[0].message.content)