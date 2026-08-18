"""
Fase B - Persistencia en PostgreSQL (Render Cloud)
Reemplaza la base de datos local SQLite por una base de datos segura en la nube.
Sobrevive a reinicios del servidor de Streamlit y centraliza los datos en internet.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
from contextlib import contextmanager

# 🌐 PEGA AQUÍ TU URL EXTERNA DE RENDER COMPLETA:
DATABASE_URL = "postgresql://aggm:G8Oi7BLdKvw4gT8hgD4ASarZ14o4TTUg@dpg-da2e1nr7uimc73a5b290-a.oregon-postgres.render.com/gora_db"

@contextmanager
def _conexion():
    # Conexión directa a los servidores seguros de Render
    conn = psycopg2.connect(DATABASE_URL)
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
            # 1. Tabla de mensajes (Se cambió AUTOINCREMENT por SERIAL)
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
            # En Postgres usamos %s y RETURNING id para capturar la llave generada
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
