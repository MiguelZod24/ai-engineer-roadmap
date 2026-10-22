# week3/rag_metadata_filter.py
# Día 6 (parte 2) - Semana 3: Metadata filtering en RAG

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
# PASOS 1-3: Igual que siempre — carga, chunks, embeddings
# ============================================================
print("Cargando PDF...")
loader = PyPDFLoader("Tutorial_EDIT.pdf")
documentos = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
pedazos = splitter.split_documents(documentos)

modelo_embeddings = HuggingFaceEmbeddings(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)
base_de_datos = Chroma.from_documents(
    documents=pedazos,
    embedding=modelo_embeddings
)
print("Base de datos lista.\n")

# ============================================================
# MODELO Y PROMPT
# ============================================================
modelo = ChatAnthropic(model="claude-haiku-4-5", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", """Eres un asistente experto en documentos.
    Responde usando SOLO la información del contexto proporcionado.
    Si la respuesta no está en el contexto, di 'No encontré esa información'.
    Responde en español.

    Contexto:
    {contexto}"""),
    ("human", "{pregunta}")
])

# ============================================================
# FUNCIÓN 1: Búsqueda sin filtro (en todo el PDF)
# Esta es la búsqueda normal que ya conocemos
# ============================================================
def buscar_sin_filtro(pregunta):
    resultados = base_de_datos.similarity_search(pregunta, k=3)

    print("🔍 Sin filtro — páginas encontradas:")
    for i, r in enumerate(resultados):
        pagina = r.metadata.get('page', '?')
        print(f"  [{i+1}] Página {pagina}: {r.page_content[:60]}...")

    contexto = "\n\n".join([r.page_content for r in resultados])
    chain = prompt | modelo | StrOutputParser()
    return chain.invoke({"contexto": contexto, "pregunta": pregunta})

# ============================================================
# FUNCIÓN 2: Búsqueda CON filtro de página
#
# filter={"page": numero} le dice a ChromaDB que SOLO busque
# en los fragmentos que vengan de esa página concreta.
#
# ¿Cuándo usarlo? Cuando sabes en qué parte del documento
# está la respuesta. Ejemplo: "las licencias están en las
# páginas 130-145, busca solo ahí".
#
# IMPORTANTE: PyPDFLoader numera las páginas desde 0,
# así que la página 1 del PDF = page 0 en metadata.
# ============================================================
def buscar_con_filtro(pregunta, pagina):
    resultados = base_de_datos.similarity_search(
        pregunta,
        k=3,
        filter={"page": pagina}  # solo busca en esta página
    )

    print(f"🔍 Con filtro página {pagina} — resultados:")
    for i, r in enumerate(resultados):
        pagina_real = r.metadata.get('page', '?')
        print(f"  [{i+1}] Página {pagina_real}: {r.page_content[:60]}...")

    if not resultados:
        return "No hay fragmentos en esa página."

    contexto = "\n\n".join([r.page_content for r in resultados])
    chain = prompt | modelo | StrOutputParser()
    return chain.invoke({"contexto": contexto, "pregunta": pregunta})

# ============================================================
# DEMO: Comparar búsqueda con y sin filtro
# Usamos la misma pregunta para ver la diferencia
# ============================================================
pregunta = "¿Qué menciona sobre licencias?"

print("=" * 50)
print("BÚSQUEDA SIN FILTRO")
print("=" * 50)
respuesta1 = buscar_sin_filtro(pregunta)
print(f"\nClaude: {respuesta1}\n")

print("=" * 50)
print("BÚSQUEDA CON FILTRO — solo página 136")
print("=" * 50)
respuesta2 = buscar_con_filtro(pregunta, pagina=136)
print(f"\nClaude: {respuesta2}\n")