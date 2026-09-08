#!/bin/sh
set -e

# Tu database.py lee la conexión desde st.secrets["DATABASE_URL"], no desde
# una variable de entorno normal. Render sí maneja variables de entorno,
# así que aquí generamos el secrets.toml que Streamlit espera, a partir
# de la variable de entorno DATABASE_URL que configures en Render.
mkdir -p /app/.streamlit

if [ -n "$DATABASE_URL" ]; then
  cat > /app/.streamlit/secrets.toml <<EOF
DATABASE_URL = "$DATABASE_URL"
EOF
else
  echo "ADVERTENCIA: no se encontró la variable de entorno DATABASE_URL." >&2
fi

exec streamlit run app_streamlit.py \
  --server.port="${PORT:-8501}" \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false
