# Imagen base ligera de Python 3.11
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia todos los archivos del proyecto a /app
COPY . /app

# Actualiza pip e instala las dependencias
RUN pip install --no-cache-dir --upgrade pip &&     pip install --no-cache-dir -r requirements.txt

# Expone el puerto 8080 (Render utiliza este puerto por defecto)
EXPOSE 8080

# Comando que inicia el servidor FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
