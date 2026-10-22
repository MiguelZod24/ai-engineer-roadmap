# 📚 doc_rag_chatbot — Semana 3

Sistema RAG (Retrieval Augmented Generation) que carga PDFs propios,
los indexa en ChromaDB localmente y responde preguntas sobre ellos
usando Claude (claude-haiku-4-5). Embeddings y búsqueda vectorial
100% local y gratuitos. Requiere API key de Anthropic para las respuestas.

---

## 🧠 ¿Cómo funciona RAG?

```
Tu PDF
  │
  ▼
[PyPDFLoader] ──── Carga el PDF página por página
  │
  ▼
[RecursiveCharacterTextSplitter] ──── Divide en pedazos de 500 chars
  │
  ▼
[HuggingFaceEmbeddings] ──── Convierte cada pedazo en vector numérico
  │                           Modelo: paraphrase-multilingual-MiniLM-L12-v2
  ▼
[ChromaDB] ──── Guarda todos los vectores en memoria
  │
  │   Tu pregunta ──► [HuggingFaceEmbeddings] ──► vector de la pregunta
  │                                                       │
  ▼                                                       ▼
[MMR Search] ──── Busca los 3 fragmentos más relevantes y diversos
  │
  ▼
[Claude Haiku] ──── Responde usando SOLO esos fragmentos como contexto
  │
  ▼
Respuesta en español
```

---

## 📁 Archivos del proyecto

| Archivo | Día | Qué hace |
|---|---|---|
| `embeddings.py` | D1 | Concepto de embeddings: texto → números |
| `cargar_documento.py` | D2-D3 | Carga y chunking de documentos |
| `vector_store.py` | D2-D3 | Guardar y buscar en ChromaDB |
| `rag_completo.py` | D4 | Pipeline RAG completo sobre texto |
| `rag_pdf.py` | D5-D6 | RAG sobre PDF con multiidioma + MMR |
| `rag_metadata_filter.py` | D6 | Filtrado por página con metadata |

---

## ⚙️ Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/ai-engineer-roadmap.git
cd ai-engineer-roadmap

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar API key
# Crear un archivo .env en la raíz con este contenido:
# ANTHROPIC_API_KEY=tu_api_key_aquí
```

---

## 🚀 Uso

```bash
cd week3

# Pipeline RAG completo con PDF + multiidioma + MMR
python rag_pdf.py

# Comparar búsqueda con y sin filtro de página
python rag_metadata_filter.py
```

---

## 🛠️ Stack

- **LangChain** — framework para conectar todas las piezas
- **ChromaDB** — base de datos vectorial local (sin servidor)
- **HuggingFace Embeddings** — modelo multiidioma gratuito y local
- **Claude Haiku** — modelo de lenguaje vía API de Anthropic
- **PyPDF** — lectura de archivos PDF

---

## 💡 Conceptos aprendidos

- Qué son los **embeddings** y cómo representan significado
- Cómo funciona la **búsqueda por similitud coseno**
- Diferencia entre **similarity search** y **MMR**
- Qué es el **metadata filtering** y cuándo usarlo
- Soporte **multiidioma** con un solo cambio de modelo