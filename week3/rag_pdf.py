# week3/rag_pdf.py
# Día 6 - Semana 3: RAG con MMR + fuentes por página

from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ============================================================
# PASO 1: Cargar el PDF
# PyPDFLoader lee el PDF página por página
# Cada página se convierte en un objeto Document separado
# ============================================================
print("Cargando PDF...")
loader = PyPDFLoader("Tutorial_EDIT.pdf")
documentos = loader.load()
print(f"PDF cargado. Total de páginas: {len(documentos)}")

# ============================================================
# PASO 2: Dividir en pedazos
# chunk_size=500 porque el PDF tiene más contenido por página
# chunk_overlap=50 para no perder contexto entre pedazos
# ============================================================
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
pedazos = splitter.split_documents(documentos)
print(f"Total de pedazos creados: {len(pedazos)}")

# ============================================================
# PASO 3: Crear embeddings y guardar en ChromaDB
#
# CAMBIO CLAVE - Modelo multiidioma:
# Antes usábamos "all-MiniLM-L6-v2" (solo inglés, ~90MB)
# Ahora usamos "paraphrase-multilingual-MiniLM-L12-v2" (~470MB)
#
# ¿Qué cambia? Este modelo entiende 50+ idiomas a la vez.
# Resultado: "El perro come" y "The dog eats" producen
# vectores casi idénticos → la búsqueda funciona entre idiomas.
#
# NOTA: La primera ejecución descargará ~470MB automáticamente.
# ============================================================
print("Creando base de datos vectorial...")
modelo_embeddings = HuggingFaceEmbeddings(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)
base_de_datos = Chroma.from_documents(
    documents=pedazos,
    embedding=modelo_embeddings
)
print("Base de datos lista.\n")

# ============================================================
# PASO 4: Crear el modelo y el prompt
# ============================================================
modelo = ChatAnthropic(model="claude-haiku-4-5", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", """Eres un asistente experto que responde preguntas sobre documentos.
    Responde usando SOLO la información del contexto proporcionado.
    Si la respuesta no está en el contexto, di 'No encontré esa información en el documento'.
    Responde en español.

    Contexto:
    {contexto}"""),
    ("human", "{pregunta}")
])

# ============================================================
# PASO 5: Función que conecta búsqueda + Claude
#
# MEJORA: MMR (Maximal Marginal Relevance)
# En vez de similarity_search (devuelve los más similares,
# aunque sean repetitivos), usamos max_marginal_relevance_search.
#
# ¿Cómo funciona?
#   1. Recupera fetch_k=10 candidatos relevantes
#   2. De esos 10, elige k=3 que sean lo más DISTINTOS entre sí
# Resultado: fragmentos relevantes Y con información variada.
# ============================================================
def preguntar_al_pdf(pregunta):
    # MMR: busca 10 candidatos y devuelve los 3 más diversos
    resultados = base_de_datos.max_marginal_relevance_search(
        pregunta,
        k=3,        # cuántos fragmentos queremos al final
        fetch_k=10  # tamaño del pool inicial de candidatos
    )

    # Mostrar de qué página viene cada fragmento
    # r.metadata es un diccionario que añade PyPDFLoader automáticamente
    # 'page' contiene el número de página del PDF
    print("\n📄 Fragmentos usados como contexto:")
    for i, r in enumerate(resultados):
        pagina = r.metadata.get('page', '?')  # '?' si no tiene página
        preview = r.page_content[:80]          # primeros 80 caracteres
        print(f"  [{i+1}] Página {pagina}: {preview}...")
    print()

    # Unir los 3 fragmentos en un solo bloque de contexto para Claude
    contexto = "\n\n".join([r.page_content for r in resultados])

    # Claude responde usando ese contexto
    chain = prompt | modelo | StrOutputParser()
    return chain.invoke({"contexto": contexto, "pregunta": pregunta})

# ============================================================
# PASO 6: Chat interactivo con el PDF
# ============================================================
print("=== Chat con tu PDF (multiidioma) ===")
print("Escribe 'salir' para terminar.\n")

while True:
    pregunta = input("Tú: ")
    if pregunta.lower() == "salir":
        print("¡Hasta luego!")
        break
    respuesta = preguntar_al_pdf(pregunta)
    print(f"\nClaude: {respuesta}\n")
