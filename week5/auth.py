import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv

# Cargamos las variables del .env (incluyendo nuestra API_KEY)
load_dotenv()

# Leemos la API key correcta desde el .env
# Esto NUNCA se escribe directo en el código (por eso usamos .env)
API_KEY_CORRECTA = os.getenv("API_KEY")

# APIKeyHeader le dice a FastAPI: "espero un header llamado X-API-Key"
# auto_error=False significa que SI el header no viene, no lanza error
# automáticamente — lo manejamos nosotros abajo para dar un mensaje mejor
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# Esta función es una "dependencia" de FastAPI.
# La vamos a "inyectar" en cualquier endpoint que queramos proteger.
def verificar_api_key(api_key: str = Security(api_key_header)):

    # Caso 1: no mandaron ningún header X-API-Key
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta la API key. Manda el header 'X-API-Key'."
        )

    # Caso 2: mandaron un header, pero el valor no coincide con el correcto
    if api_key != API_KEY_CORRECTA:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key inválida."
        )

    # Caso 3: todo correcto — no hace falta devolver nada especial,
    # simplemente dejamos que la petición continúe
    return api_key