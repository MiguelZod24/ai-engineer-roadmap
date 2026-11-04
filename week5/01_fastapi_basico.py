# week5/01_fastapi_basico.py
# Primera API con FastAPI — entender cómo funciona un endpoint

from fastapi import FastAPI  # El framework principal

# Creamos la aplicación FastAPI
# Es el objeto central — todo se registra aquí
app = FastAPI(
    title="Mi primer API",        # Nombre que aparece en la documentación
    description="API de prueba",  # Descripción en la documentación
    version="1.0.0"               # Versión de la API
)

# Un endpoint es una "puerta" de tu API
# GET es el método HTTP para obtener información (como un navegador cargando una web)
# El decorador @app.get("/") registra esta función como endpoint
@app.get("/")
def inicio():
    # Lo que devuelves aquí es lo que recibirá quien llame a tu API
    # FastAPI lo convierte automáticamente a JSON
    return {"mensaje": "¡Hola! La API está funcionando"}


# Otro endpoint GET con una ruta diferente
# {nombre} es un parámetro de ruta — viene en la URL
@app.get("/saludo/{nombre}")
def saludar(nombre: str):  # FastAPI extrae "nombre" de la URL automáticamente
    return {"mensaje": f"¡Hola {nombre}! Bienvenido a la API"}

from pydantic import BaseModel  # Para definir la estructura de los datos que entran

# Pydantic define qué datos espera el endpoint
# Es como TypedDict pero para validar datos que vienen de fuera
class PreguntaRequest(BaseModel):
    pregunta: str        # El texto de la pregunta (obligatorio)
    idioma: str = "es"  # El idioma (opcional, por defecto español)


# POST es el método HTTP para enviar datos
# Se usa cuando el cliente manda información al servidor
@app.post("/preguntar")
def preguntar(request: PreguntaRequest):
    # FastAPI valida automáticamente que "pregunta" venga en el body
    # Si no viene, devuelve error 422 automáticamente sin que tú hagas nada
    return {
        "pregunta_recibida": request.pregunta,
        "idioma": request.idioma,
        "respuesta": f"Recibí tu pregunta en {request.idioma}: '{request.pregunta}'"
    }

# Este bloque arranca el servidor cuando ejecutas el archivo directamente
# uvicorn es el servidor que ejecuta FastAPI
# host="0.0.0.0" → acepta conexiones desde cualquier IP
# port=8000 → puerto donde escucha la API
# reload=True → reinicia automáticamente cuando cambias el código
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("01_fastapi_basico:app", host="0.0.0.0", port=8000, reload=True)