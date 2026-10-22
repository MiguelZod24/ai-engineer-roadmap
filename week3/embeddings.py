# week3/embeddings.py
# Día 1 - Semana 3: Crear embeddings de los pedazos del documento

from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

# ============================================================
# PASO 1 y 2: Cargar y dividir (igual que antes)
# ============================================================
loader = TextLoader("documento.txt", encoding="utf-8")
documentos = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=30)
pedazos = splitter.split_documents(documentos)

# ============================================================
# PASO 3: Crear el modelo de embeddings
# HuggingFaceEmbeddings usa un modelo gratuito y local
# No necesita API key ni cuesta dinero
# El modelo "all-MiniLM-L6-v2" es pequeño pero muy bueno
# Se descarga automáticamente la primera vez
# ============================================================
modelo_embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

# ============================================================
# PASO 4: Convertir el primer pedazo en números (embedding)
# embed_query convierte UN texto en su lista de números
# ============================================================
texto_prueba = pedazos[0].page_content
numeros = modelo_embeddings.embed_query(texto_prueba)

print(f"Texto original:\n{texto_prueba}")
print(f"\nCantidad de números en el embedding: {len(numeros)}")
print(f"\nPrimeros 5 números: {numeros[:5]}")