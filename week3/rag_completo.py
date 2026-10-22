# week3/rag_completo.py
# Día 3 - Semana 3: RAG completo — documento + búsqueda + Claude responde

from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ============================================================
# PASOS 1, 2, 3, 4: Todo lo que ya aprendimos
# ============================================================
loader = TextLoader("documento.txt", encoding="utf-8")
documentos = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=30)
pedazos = splitter.split_documents(documentos)

modelo_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

base_de_datos = Chroma.from_documents(
    documents=pedazos,
    embedding=modelo_embeddings
)

# ============================================================
# PASO 5: Crear el modelo de lenguaje (Claude)
# ============================================================
modelo = ChatAnthropic(model="claude-haiku-4-5", temperature=0)

# ============================================================
# PASO 6: Crear el prompt que incluye el contexto encontrado
# {contexto} = los pedazos relevantes que encontró ChromaDB
# {pregunta} = la pregunta del usuario
# Claude solo puede responder con lo que está en el contexto
# ============================================================
prompt = ChatPromptTemplate.from_messages([
    ("system", """Eres un asistente útil. 
    Responde la pregunta usando SOLO la información del contexto.
    Si la respuesta no está en el contexto, di 'No tengo esa información'.
    
    Contexto:
    {contexto}"""),
    ("human", "{pregunta}")
])

# ============================================================
# PASO 7: Crear la función que conecta todo
# 1. Busca en ChromaDB los pedazos relevantes
# 2. Los une en un solo texto como contexto
# 3. Se los pasa a Claude junto con la pregunta
# ============================================================
def responder(pregunta):
    # Buscar los 2 pedazos más relevantes
    resultados = base_de_datos.similarity_search(pregunta, k=2)
    
    # Unir los pedazos en un solo texto
    contexto = "\n\n".join([r.page_content for r in resultados])
    
    # Crear la chain y ejecutarla
    chain = prompt | modelo | StrOutputParser()
    respuesta = chain.invoke({"contexto": contexto, "pregunta": pregunta})
    
    return respuesta

# ============================================================
# PASO 8: Probar con preguntas
# ============================================================
print("=== RAG Completo ===\n")

preguntas = [
    "¿Qué es RAG?",
    "¿Para qué sirve ChromaDB?",
    "¿Cuántas patas tiene un gato?"  # Esta no está en el documento
]

for pregunta in preguntas:
    print(f"Pregunta: {pregunta}")
    print(f"Respuesta: {responder(pregunta)}")
    print("---")