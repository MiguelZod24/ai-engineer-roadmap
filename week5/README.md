# AI Agent API — Semana 5

API REST construida con FastAPI que expone un agente de IA (Claude vía LangChain) con streaming de respuestas, autenticación por API key y contenedorización Docker.

## Características

- 🚀 Endpoints REST con FastAPI
- 🔐 Autenticación mediante API key (header `X-API-Key`)
- 📡 Streaming de respuestas token a token
- 🐳 Dockerizado y listo para desplegar

## Requisitos

- Python 3.11+
- Docker (opcional, para correr en contenedor)
- Una API key de Anthropic ([console.anthropic.com](https://console.anthropic.com))

## Instalación local

1. Clona el repositorio y entra a la carpeta `week5/`
2. Crea un entorno virtual e instala las dependencias:
   \`\`\`bash
   pip install -r ../requirements.txt
   \`\`\`
3. Crea un archivo `.env` dentro de `week5/` con:
   \`\`\`
   ANTHROPIC_API_KEY=tu_key_de_anthropic
   API_KEY=una_clave_inventada_por_ti_para_proteger_tu_api
   \`\`\`
   ⚠️ **Nunca subas este archivo a GitHub** — ya está excluido en `.gitignore`.

   ## Uso

### Opción A — Localmente con Python

\`\`\`bash
python 05_auth_api_key.py
\`\`\`

La API queda disponible en `http://localhost:8002`.

### Opción B — Con Docker

Desde la **raíz del proyecto** (no desde `week5/`):

\`\`\`bash
# Construir la imagen
docker build -f week5/Dockerfile -t ai-agent-api .

# Correr el contenedor, inyectando las variables del .env
docker run -p 8002:8002 --env-file week5/.env ai-agent-api
\`\`\`

### Documentación interactiva

Con la API corriendo (local o en Docker), abre:

\`\`\`
http://localhost:8002/docs
\`\`\`

Ahí puedes autenticarte con el botón del candado 🔒 (pega tu `API_KEY`) y probar el endpoint directamente desde el navegador.

## Endpoint: `POST /preguntar-stream`

Envía una pregunta al agente y recibe la respuesta en streaming (texto plano, token a token).

### Headers requeridos

| Header         | Valor                      | Obligatorio |
|----------------|-----------------------------|-------------|
| `Content-Type` | `application/json`           | Sí          |
| `X-API-Key`    | tu API key (ver `.env`)      | Sí          |

### Body (JSON)

\`\`\`json
{
  "pregunta": "¿Qué es un RAG?",
  "system_prompt": "Eres un asistente útil y conciso. Responde en español."
}
\`\`\`

`system_prompt` es opcional; si no se manda, usa un valor por defecto.

### Ejemplo con curl (Git Bash / Linux / Mac)

\`\`\`bash
curl -X POST http://localhost:8002/preguntar-stream \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: tu_api_key_aqui" \\
  -d '{"pregunta": "Hola"}'
\`\`\`

### Códigos de respuesta

| Código | Significado                                    |
|--------|-------------------------------------------------|
| `200`  | Éxito — respuesta en streaming                   |
| `401`  | Falta el header `X-API-Key`                      |
| `403`  | La API key enviada no coincide con la configurada |
| `422`  | El body no cumple el esquema esperado (Pydantic)  |

## Estructura de archivos

\`\`\`
week5/
├── 01_fastapi_basico.py     # Día 1 — FastAPI básico
├── 02_api_con_claude.py     # Día 2 — FastAPI + Claude
├── 03_api_rag.py            # Día 3 — RAG como API REST
├── 04_streaming.py          # Día 4 — Streaming de respuestas
├── 05_auth_api_key.py       # Día 5 — Endpoint con autenticación (este proyecto)
├── auth.py                  # Lógica de verificación de API key
├── Dockerfile                # Día 6 — Imagen Docker
├── .env                      # Variables de entorno (NO se sube a git)
└── README.md                 # Este archivo
\`\`\`

## Seguridad

- La API key de Anthropic (`ANTHROPIC_API_KEY`) y la API key propia (`API_KEY`) viven únicamente en `.env`, que está excluido por `.gitignore`.
- El `.dockerignore` en la raíz del proyecto asegura que `.env` nunca se copie dentro de la imagen Docker — las variables se inyectan en tiempo de ejecución con `--env-file`.
- En producción real, se recomienda generar `API_KEY` con un valor aleatorio largo, por ejemplo:
  \`\`\`bash
  python -c "import secrets; print(secrets.token_hex(32))"
  \`\`\`

## Stack

- FastAPI + Uvicorn
- LangChain (`langchain-anthropic`)
- Claude (modelo `claude-haiku-4-5`)
- Docker