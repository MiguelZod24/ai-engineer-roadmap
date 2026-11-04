# week5/03_api_rag.py
# El agente RAG de la semana 3 convertido en API REST

import os
from fastapi import FastAPI, HTTPException  # HTTPException para manejar errores
from pydantic import BaseModel
from dotenv import load_dotenv

# Importamos todo lo del RAG de la semana 3
from langchain_anthropic import ChatAnthropic
from langchain_community.document_loaders import PyPDFLoader      # Cargar PDFs
# En versiones nuevas de LangChain, text_splitter está en su propio paquete
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_huggingface import HuggingFaceEmbeddings            # Embeddings locales
from langchain_chroma import Chroma                                 # Vector
from langchain_core.messages import HumanMessage, SystemMessage    # Tipos de mensajes

load_dotenv()

app = FastAPI(
    title="API RAG",
    description="Responde preguntas sobre documentos PDF usando RAG",
    version="1.0.0"
)

# Inicializamos los componentes del RAG una sola vez al arrancar
# No dentro del endpoint para no recargar el PDF en cada petición

# El modelo de Claude
llm = ChatAnthropic(
    model="claude-haiku-4-5",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Los embeddings locales y gratuitos (los mismos de la semana 3)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# Variable global para guardar el retriever
# Empieza vacío — se rellena cuando cargas un PDF
retriever = None

# Modelo para cargar un PDF — recibe la ruta del archivo
class PDFRequest(BaseModel):
    ruta_pdf: str  # Ruta local al archivo PDF, ej: "docs/manual.pdf"

# Modelo para hacer una pregunta
class PreguntaRequest(BaseModel):
    pregunta: str  # La pregunta sobre el PDF cargado

# Modelo de respuesta
class RespuestaResponse(BaseModel):
    pregunta: str   # La pregunta original
    respuesta: str  # La respuesta basada en el PDF
    fuente: str     # De qué parte del PDF viene la respuesta

# Endpoint 1: cargar un PDF en el sistema RAG
@app.post("/cargar-pdf")
def cargar_pdf(request: PDFRequest):
    
    # global indica que vamos a modificar la variable global "retriever"
    # sin esto Python crearía una variable local nueva
    global retriever
    
    # Verificamos que el archivo existe antes de cargarlo
    if not os.path.exists(request.ruta_pdf):
        # HTTPException devuelve un error HTTP 404 con mensaje claro
        raise HTTPException(status_code=404, detail=f"PDF no encontrado: {request.ruta_pdf}")
    
    # Cargamos y procesamos el PDF (igual que en semana 3)
    loader = PyPDFLoader(request.ruta_pdf)
    documentos = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documentos)
    
    # Creamos el vector store con los chunks
    vectorstore = Chroma.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    return {"mensaje": f"PDF cargado correctamente. {len(chunks)} chunks indexados."}


# Endpoint 2: hacer preguntas sobre el PDF cargado
@app.post("/preguntar", response_model=RespuestaResponse)
def preguntar(request: PreguntaRequest):
    
    # Si no hay PDF cargado, devolvemos error 400
    if retriever is None:
        raise HTTPException(status_code=400, detail="Primero debes cargar un PDF con /cargar-pdf")
    
    # Obtenemos los documentos relevantes del retriever
    docs = retriever.invoke(request.pregunta)
    
    # Armamos el contexto con el contenido de esos documentos
    contexto = "\n\n".join(doc.page_content for doc in docs)
    
    # Le preguntamos a Claude usando el contexto como referencia
    mensajes = [
        SystemMessage(content=f"Responde basándote en este contexto:\n\n{contexto}"),
        HumanMessage(content=request.pregunta)
    ]
    respuesta_llm = llm.invoke(mensajes)
    
    # Tomamos la página del primer documento encontrado
    fuente = f"Página {docs[0].metadata.get('page', '?') + 1}" if docs else "No encontrado"
    
    return RespuestaResponse(
        pregunta=request.pregunta,
        respuesta=respuesta_llm.content,
        fuente=fuente
    )


# Endpoint de salud
@app.get("/health")
def health():
    return {
        "status": "ok",
        "pdf_cargado": retriever is not None  # True si hay PDF cargado, False si no
    }

# ==========================================
# ARRANQUE DEL SERVIDOR
# ==========================================

if __name__ == "__main__":
    import uvicorn
    
    # "03_api_rag:app" significa:
    # - "03_api_rag" → el nombre del archivo (sin .py)
    # - "app" → la variable FastAPI que creamos arriba
    uvicorn.run("03_api_rag:app", host="0.0.0.0", port=8000, reload=True)
