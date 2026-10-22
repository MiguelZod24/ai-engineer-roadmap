import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

message = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=300,
    messages=[
        {"role": "user", "content": "Explícame qué es un LLM en 3 frases simples."}
    ]
)

print(message.content[0].text)