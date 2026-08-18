"""
Fase B - Persistencia en SQLite
Reemplaza el historial en memoria/JSON por una base de datos local real:
sobrevive a errores, recargas y reinicios de Streamlit. Todo se guarda
en un único archivo local (gora_local.db) — nunca se envía a un servidor.
"""

import sqlite3
import json
import os
from datetime import datetime
from contextlib import contextmanager

RUTA_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gora_local.db")


@contextmanager
def _conexion():
    conn = sqlite3.connect(RUTA_DB)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def inicializar_db():
    with _conexion() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rol TEXT NOT NULL,                 -- 'user' | 'assistant'
                texto TEXT NOT NULL,
                emocion_estimada TEXT,
                confianza REAL,
                camara_usada INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS senales_faciales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mensaje_id INTEGER NOT NULL,
                apertura_ojo REAL,
                apertura_boca REAL,
                elevacion_cejas REAL,
                orientacion_json TEXT,
                calidad_deteccion TEXT,
                FOREIGN KEY (mensaje_id) REFERENCES mensajes(id)
            )
        """)


def guardar_mensaje(rol, texto, emocion_estimada=None, confianza=None,
                     camara_usada=False, senales_observables=None, calidad_deteccion=None):
    with _conexion() as conn:
        cur = conn.execute(
            """INSERT INTO mensajes (rol, texto, emocion_estimada, confianza, camara_usada, timestamp)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (rol, texto[:2000], emocion_estimada, confianza, int(camara_usada),
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        mensaje_id = cur.lastrowid

        if senales_observables:
            conn.execute(
                """INSERT INTO senales_faciales (mensaje_id, apertura_ojo, apertura_boca,
                                                  elevacion_cejas, orientacion_json, calidad_deteccion)
                   VALUES (?, ?, ?, ?, ?, ?)""",
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
        filas = conn.execute(
            "SELECT rol, texto, emocion_estimada FROM mensajes ORDER BY id DESC LIMIT ?",
            (limite,)
        ).fetchall()
        return [{"rol": f["rol"], "texto": f["texto"], "emocion": f["emocion_estimada"] or "neutral"}
                for f in reversed(filas)]


def emocion_mas_frecuente():
    with _conexion() as conn:
        fila = conn.execute(
            """SELECT emocion_estimada, COUNT(*) as total FROM mensajes
               WHERE rol='user' AND emocion_estimada IS NOT NULL
               GROUP BY emocion_estimada ORDER BY total DESC LIMIT 1"""
        ).fetchone()
        return fila["emocion_estimada"] if fila else None


def serie_para_grafica(ultimos_n=20):
    escala = {"tristeza": 1, "miedo": 2, "disgusto": 2, "enojo": 2, "neutral": 3, "sorpresa": 4, "felicidad": 5}
    with _conexion() as conn:
        filas = conn.execute(
            """SELECT timestamp, emocion_estimada FROM mensajes
               WHERE rol='user' AND emocion_estimada IS NOT NULL ORDER BY id DESC LIMIT ?""",
            (ultimos_n,)
        ).fetchall()
        return {f["timestamp"][-8:]: escala.get(f["emocion_estimada"], 3) for f in reversed(filas)}


def contar_mensajes_usuario():
    with _conexion() as conn:
        return conn.execute("SELECT COUNT(*) as total FROM mensajes WHERE rol='user'").fetchone()["total"]


def borrar_todo():
    """Borrado real y total (derecho de privacidad del usuario sobre sus datos)."""
    with _conexion() as conn:
        conn.execute("DELETE FROM senales_faciales")
        conn.execute("DELETE FROM mensajes")