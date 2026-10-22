from dotenv import load_dotenv
load_dotenv()

from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser

modelo = ChatAnthropic(model="claude-haiku-4-5", temperature=0)
parser = StrOutputParser()

# CHAIN 1: explica el concepto en español
prompt_explicar = ChatPromptTemplate.from_messages([
    ("system", "Eres un experto en tecnología."),
    ("human", "Explica qué es {concepto} en 3 oraciones simples.")
])

chain_explicar = prompt_explicar | modelo | parser

# CHAIN 2: traduce la explicación al inglés
prompt_traducir = ChatPromptTemplate.from_messages([
    ("system", "Eres un traductor experto."),
    ("human", "Traduce este texto al inglés: {texto}")
])

chain_traducir = prompt_traducir | modelo | parser

# Conectamos las dos chains
# La salida de chain_explicar entra como {texto} en chain_traducir
chain_completa = chain_explicar | (lambda texto: {"texto": texto}) | chain_traducir

# Ejecutamos
resultado = chain_completa.invoke({"concepto": "Docker"})
print(resultado)
