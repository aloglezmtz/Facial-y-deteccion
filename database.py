"""
Fase B - Persistencia en PostgreSQL (Render Cloud)
Reemplaza la base de datos local SQLite por una base de datos segura en la nube.
Sobrevive a reinicios del servidor de Streamlit y centraliza los datos en internet.

La URL de conexión NUNCA va escrita en este archivo: se lee desde
st.secrets, que Streamlit Cloud provee de forma segura (Settings > Secrets
en el dashboard de tu app) y que en local vive en .streamlit/secrets.toml
(archivo que debe estar en tu .gitignore, para que nunca se suba a git).
"""

import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
from contextlib import contextmanager


def _obtener_database_url():
    try:
        return st.secrets["DATABASE_URL"]
    except (KeyError, FileNotFoundError):
        raise RuntimeError(
            "No se encontró DATABASE_URL en st.secrets. "
            "En Streamlit Cloud: Settings > Secrets, agrega:\n"
            'DATABASE_URL = "postgresql://usuario:password@host/db"\n'
            "En local: crea .streamlit/secrets.toml con la misma línea "
            "(y agrega esa carpeta a tu .gitignore)."
        )


@contextmanager
def _conexion():
    conn = psycopg2.connect(_obtener_database_url())
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def inicializar_db():
    with _conexion() as conn:
        with conn.cursor() as cur:
            # 1. Tabla de mensajes
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mensajes (
                    id SERIAL PRIMARY KEY,
                    rol TEXT NOT NULL,                 -- 'user' | 'assistant'
                    texto TEXT NOT NULL,
                    emocion_estimada TEXT,
                    confianza REAL,
                    camara_usada INTEGER DEFAULT 0,
                    timestamp TEXT NOT NULL
                )
            """)
            # 2. Tabla de señales faciales
            cur.execute("""
                CREATE TABLE IF NOT EXISTS senales_faciales (
                    id SERIAL PRIMARY KEY,
                    mensaje_id INTEGER NOT NULL,
                    apertura_ojo REAL,
                    apertura_boca REAL,
                    elevacion_cejas REAL,
                    orientacion_json TEXT,
                    calidad_deteccion TEXT,
                    FOREIGN KEY (mensaje_id) REFERENCES mensajes(id) ON DELETE CASCADE
                )
            """)


def guardar_mensaje(rol, texto, emocion_estimada=None, confianza=None,
                     camara_usada=False, senales_observables=None, calidad_deteccion=None):
    with _conexion() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO mensajes (rol, texto, emocion_estimada, confianza, camara_usada, timestamp)
                   VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
                (rol, texto[:2000], emocion_estimada, confianza, int(camara_usada),
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            mensaje_id = cur.fetchone()[0]

            if senales_observables:
                cur.execute(
                    """INSERT INTO senales_faciales (mensaje_id, apertura_ojo, apertura_boca,
                                                      elevacion_cejas, orientacion_json, calidad_deteccion)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (mensaje_id,
                     senales_observables.get("apertura_ojo_promedio"),
                     senales_observables.get("apertura_boca"),
                     senales_observables.get("elevacion_cejas"),
                     json.dumps(senales_observables.get("orientacion_cabeza")),
                     calidad_deteccion)
                )
            return mensaje_id


def cargar_chat(limite=100):
    """Devuelve los últimos N mensajes en orden cronológico, listos para pintar el chat."""
    with _conexion() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT rol, texto, emocion_estimada FROM mensajes ORDER BY id DESC LIMIT %s",
                (limite,)
            )
            filas = cur.fetchall()
            return [{"rol": f["rol"], "texto": f["texto"], "emocion": f["emocion_estimada"] or "neutral"}
                    for f in reversed(filas)]


def emocion_mas_frecuente():
    with _conexion() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """SELECT emocion_estimada, COUNT(*) as total FROM mensajes
                   WHERE rol='user' AND emocion_estimada IS NOT NULL
                   GROUP BY emocion_estimada ORDER BY total DESC LIMIT 1"""
            )
            fila = cur.fetchone()
            return fila["emocion_estimada"] if fila else None


def serie_para_grafica(ultimos_n=20):
    escala = {"tristeza": 1, "miedo": 2, "disgusto": 2, "enojo": 2, "neutral": 3, "sorpresa": 4, "felicidad": 5}
    with _conexion() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """SELECT timestamp, emocion_estimada FROM mensajes
                   WHERE rol='user' AND emocion_estimada IS NOT NULL ORDER BY id DESC LIMIT %s""",
                (ultimos_n,)
            )
            filas = cur.fetchall()
            return {f["timestamp"][-8:]: escala.get(f["emocion_estimada"], 3) for f in reversed(filas)}


def contar_mensajes_usuario():
    with _conexion() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) as total FROM mensajes WHERE rol='user'")
            return cur.fetchone()["total"]


def borrar_todo():
    """Borrado real y total (derecho de privacidad del usuario sobre sus datos)."""
    with _conexion() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM senales_faciales")
            cur.execute("DELETE FROM mensajes")