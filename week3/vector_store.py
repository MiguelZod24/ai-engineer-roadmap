# week3/vector_store.py
# Día 2 - Semana 3: Guardar embeddings en ChromaDB y buscar por significado

from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# ============================================================
# PASOS 1, 2 y 3: Cargar, dividir y preparar embeddings
# (igual que antes, pero ahora los guardamos en ChromaDB)
# ============================================================
loader = TextLoader("documento.txt", encoding="utf-8")
documentos = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=30)
pedazos = splitter.split_documents(documentos)

modelo_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# ============================================================
# PASO 4: Crear la base de datos vectorial con ChromaDB
# from_documents hace tres cosas a la vez:
#   1. Toma los pedazos de texto
#   2. Los convierte en embeddings usando nuestro modelo
#   3. Los guarda en la base de datos
# ============================================================
base_de_datos = Chroma.from_documents(
    documents=pedazos,
    embedding=modelo_embeddings
)

print(f"Base de datos creada con {len(pedazos)} pedazos\n")

# ============================================================
# PASO 5: Buscar por significado
# similarity_search busca los pedazos más similares a la pregunta
# k=2 significa que devuelve los 2 más relevantes
# No busca palabras exactas — busca por SIGNIFICADO
# ============================================================
pregunta = "¿Qué es RAG?"
resultados = base_de_datos.similarity_search(pregunta, k=2)

print(f"Pregunta: {pregunta}")
print(f"\nPedazos más relevantes encontrados:")
for i, resultado in enumerate(resultados):
    print(f"\n--- Resultado {i+1} ---")
    print(resultado.page_content)