FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Crear directorio uploads
RUN mkdir -p uploads && chmod -R 777 /app/uploads

# Exponer puerto 7860 (requerido por Hugging Face)
EXPOSE 7860

# Comando para iniciar la aplicación
# Primero inicializa PostgreSQL, luego tablas de observaciones, luego inicia la app
CMD python init_postgres.py && python init_observaciones.py && python app.py
