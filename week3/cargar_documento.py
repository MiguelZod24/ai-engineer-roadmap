# week3/cargar_documento.py
# Día 1 - Semana 3: Cargar y dividir un documento

from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ============================================================
# PASO 1: Cargar un documento de texto
# TextLoader lee el archivo y lo convierte en objetos Document
# ============================================================
loader = TextLoader("documento.txt", encoding="utf-8")
documentos = loader.load()


print(f"Documento cargado. Páginas: {len(documentos)}")
print(f"Primeros 200 caracteres:\n{documentos[0].page_content[:200]}")
print("---")

# ============================================================
# PASO 2: Dividir el documento en pedazos (chunks)
# chunk_size = tamaño máximo de cada pedazo (en caracteres)
# chunk_overlap = cuántos caracteres se repiten entre pedazos
#                 (para no perder contexto en los bordes)
# ============================================================
splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=30
)

pedazos = splitter.split_documents(documentos)

print(f"Total de pedazos creados: {len(pedazos)}")
print(f"\nPrimer pedazo:\n{pedazos[0].page_content}")
print(f"\nSegundo pedazo:\n{pedazos[1].page_content}")