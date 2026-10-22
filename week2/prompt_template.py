from dotenv import load_dotenv
load_dotenv()
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser

# Definimos el molde con un hueco: {concepto}
prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un experto en tecnología."),
    ("human", "Explícame qué es {concepto} con un nivel {nivel} de detalle.")
])

# El modelo Claude
modelo = ChatAnthropic(model="claude-haiku-4-5", temperature=0)

# Conectamos las tres piezas con |
chain = prompt | modelo | StrOutputParser()

# Ejecutamos
respuesta1 = chain.invoke({"concepto": "Docker", "nivel": "básico"})
print(respuesta1)

respuesta2 = chain.invoke({"concepto": "lo que acabo de preguntar", "nivel": "básico"})
print(respuesta2)