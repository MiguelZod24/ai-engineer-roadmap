# Imagen base: Python 3.11 en su versión "slim" (más ligera, menos cosas innecesarias)
FROM python:3.11-slim

# Carpeta de trabajo DENTRO del contenedor — aquí vivirá nuestro código
WORKDIR /app

# Copiamos requirements.txt — vendrá desde la raíz del proyecto
# gracias a que el build se ejecuta con esa raíz como "contexto" (lo vemos al final)
COPY requirements.txt .

# Instalamos todas las librerías listadas en requirements.txt
# --no-cache-dir evita guardar archivos temporales de pip, así la imagen pesa menos
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el contenido de week5/ hacia /app dentro del contenedor
# (incluye 05_auth_api_key.py, auth.py, y los demás scripts de la semana)
COPY week5/ .

# Documenta (no abre de verdad el puerto, solo informa) que el contenedor
# escuchará en el puerto 8002 — el mismo que usa 05_auth_api_key.py
EXPOSE 8002

# Comando que se ejecuta cuando el contenedor arranca
# Usamos uvicorn directamente (no "python 05_auth_api_key.py") porque
# así controlamos host y puerto de forma explícita, y sin --reload
# (reload es solo para desarrollo local, nunca en un contenedor de producción)
CMD ["uvicorn", "05_auth_api_key:app", "--host", "0.0.0.0", "--port", "8002"]