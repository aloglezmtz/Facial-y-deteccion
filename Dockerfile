# Dockerfile para desplegar app_streamlit.py en Render
# Sustituye a Streamlit Community Cloud: aquí controlamos nosotros el apt-get,
# así que el bug de "bullseye-security expired" de Streamlit Cloud ya no aplica.

FROM python:3.11-slim

# --- Dependencias de sistema ---
# libgl1 y libglib2.0-0 son las que le faltaban a cv2 (mediapipe exige
# opencv-contrib-python, que SÍ necesita estas librerías gráficas de Linux).
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# --- Dependencias de Python ---
# Copiamos solo requirements.txt primero para aprovechar el cache de Docker:
# si no cambian tus dependencias, Render no las reinstala en cada deploy.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Código de la app ---
COPY . .

# Convertimos el entrypoint en ejecutable
RUN chmod +x /app/docker-entrypoint.sh

# Render asigna el puerto dinámicamente vía la variable $PORT
EXPOSE 8501

ENTRYPOINT ["/app/docker-entrypoint.sh"]
